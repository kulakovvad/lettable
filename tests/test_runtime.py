import asyncio
import json
import pytest
from agents import Model, ModelResponse, Usage, function_tool
from openai.types.responses import ResponseOutputMessage, ResponseOutputText, ResponseFunctionToolCall
from lettable.agent import create_agent
from lettable.contracts import Limits
from lettable.runtime import Runtime
from lettable.store import Store
from lettable.tools import retry_read, TransientReadError


class ScriptedModel(Model):
    """Drive the real SDK with deterministic Responses items, without an API key."""
    def __init__(self, *steps):
        self.steps = list(steps)
        self.inputs = []

    async def get_response(self, system_instructions, input, *args, **kwargs):
        self.inputs.append(input)
        step = self.steps.pop(0)
        if callable(step):
            step = await step()
        if isinstance(step, Exception):
            raise step
        return ModelResponse(output=[step], usage=Usage(requests=1, total_tokens=10), response_id=None)

    async def stream_response(self, *args, **kwargs):
        raise NotImplementedError
        yield


def answer(status="completed", message="Done", triage=None):
    return ResponseOutputMessage(id="message", role="assistant", status="completed",
        content=[ResponseOutputText(type="output_text", text=json.dumps({"status":status,"message":message,"triage":triage or {"priority":"P3", "urgency":"routine", "reason":"Routine synthetic check", "next_action":"No further action"}}), annotations=[])], type="message")


def call(name="lookup", call_id="call-1", arguments="{}"):
    return ResponseFunctionToolCall(type="function_call", name=name, call_id=call_id, arguments=arguments)


def runtime(tmp_path, model, tools=(), limits=None):
    return Runtime(create_agent(model=model, tools=tools), Store(str(tmp_path / "state.sqlite")), limits)


async def start(rt, **kwargs):
    return await rt.start(**{"principal":"alice", "conversation":"chat", "request_id":"request", "message":"help", **kwargs})


@pytest.mark.parametrize("status", ["completed", "needs_input", "escalated"])
async def test_dispositions_and_replay(tmp_path, status):
    model = ScriptedModel(answer(status))
    rt = runtime(tmp_path, model)
    assert (await start(rt)).status == status
    assert (await start(rt)).status == status
    assert len(model.inputs) == 1
    with pytest.raises(ValueError, match="different input"):
        await start(rt, message="changed")


async def test_real_sdk_tool_observation(tmp_path):
    seen = []
    @function_tool
    async def lookup() -> str:
        seen.append("lookup")
        return "verified-result"
    model = ScriptedModel(call(), answer())
    assert (await start(runtime(tmp_path, model, [lookup]))).status == "completed"
    assert seen == ["lookup"]
    assert "verified-result" in json.dumps(model.inputs[1])


@pytest.mark.parametrize("allow", [True, False])
async def test_approval_survives_restart_and_is_single_use(tmp_path, allow):
    seen = []
    @function_tool(needs_approval=True)
    async def update_record() -> str:
        seen.append("updated")
        return "verified"
    rt = runtime(tmp_path, ScriptedModel(call("update_record")), [update_record])
    outcome = await start(rt)
    assert outcome.status == "awaiting_approval"
    assert seen == []
    # Reconstruct the runtime as after process restart, using the same registered tool.
    rt = runtime(tmp_path, ScriptedModel(answer()), [update_record])
    args = dict(principal="alice", conversation="chat", request_id="request", decisions={"call-1":allow})
    with pytest.raises(ValueError, match="Unknown request"):
        await rt.resume(**{**args, "principal":"bob"})
    with pytest.raises(ValueError, match="explicit boolean"):
        await rt.resume(**{**args, "decisions":{}})
    result = await rt.resume(**args)
    assert result.status == "completed"
    assert seen == (["updated"] if allow else [])
    with pytest.raises(ValueError):
        await rt.resume(**args)


async def test_approval_expires_without_execution(tmp_path):
    @function_tool(needs_approval=True)
    async def update_record() -> str:
        pytest.fail("Expired action executed")
    rt = runtime(tmp_path, ScriptedModel(call("update_record")), [update_record], Limits(approval_ttl_seconds=0.001))
    await start(rt)
    await asyncio.sleep(0.01)
    result = await rt.resume(principal="alice", conversation="chat", request_id="request", decisions={"call-1":True})
    assert result.code == "approval_expired"


async def test_conversation_isolation(tmp_path):
    model = ScriptedModel(answer(message="secret"), answer(), answer())
    rt = runtime(tmp_path, model)
    await start(rt)
    await start(rt, principal="bob")
    assert "secret" not in json.dumps(model.inputs[1])
    await start(rt, request_id="next")
    assert "secret" in json.dumps(model.inputs[2])


async def test_repeated_action_stops_before_third_execution(tmp_path):
    seen = []
    @function_tool
    async def lookup() -> str:
        seen.append(1)
        return "unchanged"
    rt = runtime(tmp_path, ScriptedModel(call(call_id="a"),call(call_id="b"),call(call_id="c")), [lookup])
    result = await start(rt)
    assert result.code == "no_progress"
    assert len(seen) == 2


async def test_turn_limit(tmp_path):
    @function_tool
    async def lookup() -> str:
        return "found"
    result = await start(runtime(tmp_path, ScriptedModel(call()), [lookup], Limits(max_turns=1)))
    assert result.code == "turn_limit"


async def test_token_limit_blocks_action(tmp_path):
    @function_tool
    async def lookup() -> str:
        pytest.fail("Tool executed after budget exceeded")
    result = await start(runtime(tmp_path, ScriptedModel(call()), [lookup], Limits(max_tokens=5)))
    assert result.code == "token_limit"


async def test_timeout_and_cancellation(tmp_path):
    async def slow():
        await asyncio.sleep(60)
    rt = runtime(tmp_path, ScriptedModel(slow), limits=Limits(timeout_seconds=0.01))
    assert (await start(rt)).code == "timeout"
    rt = runtime(tmp_path, ScriptedModel(slow))
    task = asyncio.create_task(start(rt, request_id="cancel"))
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert rt.store.load(rt.store.scope("alice", "chat"), "cancel")["status"] == "cancelled"


async def test_concurrent_duplicate_does_not_execute_twice(tmp_path):
    entered, release = asyncio.Event(), asyncio.Event()
    async def slow():
        entered.set()
        await release.wait()
        return answer()
    rt = runtime(tmp_path, ScriptedModel(slow))
    task = asyncio.create_task(start(rt))
    await entered.wait()
    with pytest.raises(ValueError, match="running"):
        await start(rt)
    with pytest.raises(ValueError, match="active request"):
        await start(rt, request_id="another")
    release.set()
    await task


async def test_errors_are_redacted_and_not_replayed(tmp_path):
    model = ScriptedModel(RuntimeError("secret credential"))
    rt = runtime(tmp_path, model)
    result = await start(rt)
    assert result.code == "run_error"
    assert "secret" not in result.model_dump_json()
    await start(rt)
    assert len(model.inputs) == 1


async def test_read_retry_only_for_transient_errors():
    seen = []
    async def transient():
        seen.append(1)
        if len(seen) < 3:
            raise TransientReadError()
        return "found"
    assert await retry_read(transient, base_delay=0) == "found"
    assert len(seen) == 3
    async def permanent():
        raise ValueError("not retryable")
    with pytest.raises(ValueError):
        await retry_read(permanent)


async def test_read_retry_exhaustion():
    seen = []
    async def fail():
        seen.append(1)
        raise TransientReadError()
    with pytest.raises(TransientReadError):
        await retry_read(fail, attempts=2, base_delay=0)
    assert len(seen) == 2


async def test_invalid_structured_output(tmp_path):
    result = await start(runtime(tmp_path, ScriptedModel(answer(status="invented_status"))))
    assert result.code == "run_error"


async def test_unknown_tool_does_not_claim_success(tmp_path):
    result = await start(runtime(tmp_path, ScriptedModel(call("nonexistent"))))
    assert result.status == "escalated"


async def test_tool_budget(tmp_path):
    seen = []
    @function_tool
    async def lookup(value: int) -> str:
        seen.append(value)
        return "result"
    model = ScriptedModel(call(arguments='{"value":1}'), call(call_id="b", arguments='{"value":2}'))
    result = await start(runtime(tmp_path, model, [lookup], Limits(max_tool_calls=1)))
    assert result.code == "tool_limit"
    assert seen == [1]


async def test_authenticated_context_is_available_to_tools(tmp_path):
    from agents import RunContextWrapper
    @function_tool
    async def lookup(context: RunContextWrapper[dict]) -> str:
        assert context.context["principal"] == "alice"
        assert context.context["request_id"] == "request"
        return "authorized lookup"
    assert (await start(runtime(tmp_path, ScriptedModel(call(), answer()), [lookup]))).status == "completed"


async def test_input_validation_before_claim(tmp_path):
    rt = runtime(tmp_path, ScriptedModel())
    for change in [{"message":" "}, {"message":"x"*12001}, {"principal":""}, {"request_id":""}]:
        with pytest.raises(ValueError):
            await start(rt, **change)


async def test_triage_survives_persistence_and_replay(tmp_path):
    triage = {"priority": "P0", "urgency": "immediate",
              "reason": "Reported active threat to occupant",
              "next_action": "Immediate human safety response required"}
    model = ScriptedModel(answer(status="escalated", triage=triage))
    rt = runtime(tmp_path, model)
    first = await start(rt)
    assert first.triage.model_dump() == triage
    replay = await start(rt)
    assert replay.triage == first.triage
    assert len(model.inputs) == 1


async def test_invalid_triage_does_not_complete(tmp_path):
    triage = {"priority": "P9", "urgency": "routine", "reason": "Unknown", "next_action": "Review"}
    result = await start(runtime(tmp_path, ScriptedModel(answer(triage=triage))))
    assert result.status == "escalated"
    assert result.code == "run_error"
    assert result.triage is None
