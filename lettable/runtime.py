import asyncio
import hashlib
import json
import logging
import time
from agents import Runner, RunConfig, RunState
from agents.lifecycle import RunHooksBase
from agents.exceptions import MaxTurnsExceeded, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from .contracts import Limits, Outcome, Reply
from .store import Store


class BudgetExceeded(Exception):
    pass


class BudgetHooks(RunHooksBase):
    def __init__(self, limits, store, scope, request_id, budget):
        self.limits, self.store, self.scope, self.request_id = limits, store, scope, request_id
        self.budget = {"tokens": 0, "calls": 0, "repeats": {}, **budget}

    def save(self):
        self.store.save_budget(self.scope, self.request_id, self.budget)

    def check(self):
        if self.budget["calls"] > self.limits.max_tool_calls:
            raise BudgetExceeded("tool_limit")
        if any(count > self.limits.max_identical_calls for count in self.budget["repeats"].values()):
            raise BudgetExceeded("no_progress")
        if self.budget["tokens"] > self.limits.max_tokens:
            raise BudgetExceeded("token_limit")

    async def on_llm_start(self, context, agent, system_prompt, input_items):
        self.check()
        if self.budget["tokens"] >= self.limits.max_tokens:
            raise BudgetExceeded("token_limit")

    async def on_llm_end(self, context, agent, response):
        self.budget["tokens"] += response.usage.total_tokens
        self.save()
        if self.budget["tokens"] > self.limits.max_tokens:
            raise BudgetExceeded("token_limit")

    async def on_tool_start(self, context, agent, tool):
        # Persist only a digest of arguments in budget telemetry.
        args = getattr(context, "tool_arguments", "")
        try:
            args = json.dumps(json.loads(args), sort_keys=True)
        except (ValueError, TypeError):
            pass
        digest = hashlib.sha256((tool.name + str(args)).encode()).hexdigest()
        repeats = self.budget["repeats"]
        repeats[digest] = repeats.get(digest, 0) + 1
        self.budget["calls"] += 1
        self.save()
        if self.budget["calls"] > self.limits.max_tool_calls:
            raise BudgetExceeded("tool_limit")
        if repeats[digest] > self.limits.max_identical_calls:
            raise BudgetExceeded("no_progress")


class Runtime:
    """Wrap the SDK loop; never replay an entire failed run automatically."""
    def __init__(self, agent, store: Store, limits: Limits | None = None, *, tracing=False):
        self.agent, self.store = agent, store
        self.limits = limits or Limits()
        self.config = RunConfig(tracing_disabled=not tracing, trace_include_sensitive_data=False,
                                workflow_name="Lettable")

    async def start(self, *, principal: str, conversation: str, request_id: str, message: str):
        scope = self.store.scope(principal, conversation)
        if not request_id.strip() or not message.strip() or len(message) > self.limits.max_input_chars:
            raise ValueError("Request ID and non-empty input within size limit are required")
        cached = self.store.claim(scope, request_id, message)
        if cached:
            if cached["outcome"]:
                return Outcome.model_validate_json(cached["outcome"])
            raise ValueError("Request is running; reconcile before retrying")
        history = self.store.history(scope)
        return await self._run(scope, request_id, history + [{"role": "user", "content": message}], {},
                               {"principal": principal, "conversation": conversation, "request_id": request_id})

    async def resume(self, *, principal: str, conversation: str, request_id: str, decisions: dict[str, bool]):
        scope = self.store.scope(principal, conversation)
        row = self.store.load(scope, request_id)
        if row["status"] != "awaiting_approval":
            raise ValueError("Request is not awaiting approval")
        if time.time() - row["updated"] > self.limits.approval_ttl_seconds:
            outcome = Outcome(request_id=request_id, status="escalated", code="approval_expired",
                              message="This approval expired. Please review the action again.")
            self.store.claim_resume(scope, request_id)
            self.store.finish(scope, request_id, outcome)
            return outcome
        context = {"principal": principal, "conversation": conversation, "request_id": request_id}
        state = await RunState.from_json(self.agent, json.loads(row["state"]), context_override=context)
        pending = state.get_interruptions()
        if set(decisions) != {item.call_id for item in pending} or any(type(x) is not bool for x in decisions.values()):
            raise ValueError("Provide an explicit boolean decision for each pending call ID")
        for item in pending:
            if decisions[item.call_id]:
                state.approve(item)
            else:
                state.reject(item)
        self.store.claim_resume(scope, request_id)
        return await self._run(scope, request_id, state, json.loads(row["budget"]), context)

    async def _run(self, scope, request_id, input, budget, context):
        hooks = BudgetHooks(self.limits, self.store, scope, request_id, budget)
        try:
            result = await asyncio.wait_for(
                Runner.run(self.agent, input, context=context, max_turns=self.limits.max_turns,
                           hooks=hooks, run_config=self.config), self.limits.timeout_seconds)
            hooks.check()
            if result.interruptions:
                outcome = Outcome(request_id=request_id, status="awaiting_approval",
                    message="Please review the proposed actions before they run.",
                    approvals=[{"call_id": item.call_id, "tool": item.name or "unknown",
                                "arguments": item.arguments or "{}"} for item in result.interruptions])
                self.store.finish(scope, request_id, outcome, result.to_state().to_json())
                return outcome
            reply = Reply.model_validate(result.final_output)
            outcome = Outcome(request_id=request_id, status=reply.status, message=reply.message, triage=reply.triage)
            self.store.finish(scope, request_id, outcome, history=result.to_input_list())
            return outcome
        except asyncio.CancelledError:
            self.store.finish(scope, request_id, Outcome(request_id=request_id, status="cancelled",
                              code="cancelled", message="Stopped. Check any action already in progress before retrying."))
            raise
        except Exception as exc:
            logging.getLogger(__name__).warning(
                "Agent run stopped: exception=%s, http_status=%s",
                type(exc).__name__, getattr(exc, "status_code", None),
            )
            # The SDK may wrap hook exceptions as UserError. Preserve our own
            # budget disposition without inspecting or exposing its error string.
            try:
                hooks.check()
            except BudgetExceeded as violation:
                exc = violation
            if isinstance(exc, BudgetExceeded):
                code = str(exc)
            elif isinstance(exc, MaxTurnsExceeded):
                code = "turn_limit"
            elif isinstance(exc, TimeoutError):
                code = "timeout"
            elif isinstance(exc, (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered)):
                code = "guardrail"
            else:
                code = "run_error"
            # Do not leak exception strings or retry side effects after ambiguous failures.
            outcome = Outcome(request_id=request_id, status="escalated", code=code,
                              message="I could not safely finish. Please review progress before retrying.")
            self.store.finish(scope, request_id, outcome)
            return outcome
