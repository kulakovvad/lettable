"use strict";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const state = { run: null, view: null, picked: null, opt: 0, error: "" };

function fill(el, ...children) {
  el.replaceChildren();
  for (const c of children.flat(Infinity)) {
    if (c == null || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "style") el.style.cssText = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  return fill(el, ...children);
}

function fmtDate(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(iso || "");
  return m ? `${Number(m[3])} ${MONTHS[Number(m[2]) - 1]} ${m[1]}, ${m[4]}:${m[5]}` : "";
}

const dash = (v) => (v == null || v === "" ? "—" : v);
const words = (s) => String(s).toLowerCase().replace(/_/g, " ");

async function api(path, body) {
  const res = await fetch(path, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

async function load() {
  try {
    state.run = await api("/api/run");
  } catch (e) {
    return renderEmpty(`Could not read the run: ${e.message}`);
  }
  const ids = state.run.cases.map((c) => c.id);
  if (!ids.length) return renderEmpty(`No finished cases in ${state.run.out_dir}. Run \`python3 -m agent run\` first.`);
  const fromHash = decodeURIComponent(location.hash.slice(1));
  await pick(ids.includes(fromHash) ? fromHash : ids[0], false);
}

async function pick(id, focus) {
  state.picked = id;
  state.opt = 0;
  state.error = "";
  history.replaceState(null, "", `#${encodeURIComponent(id)}`);
  try {
    state.view = await api(`/api/cases/${encodeURIComponent(id)}`);
  } catch (e) {
    state.view = null;
    state.error = e.message;
  }
  const latest = state.view && state.view.review.latest;
  if (latest && latest.choice === "option") state.opt = latest.option - 1;
  render();
  if (focus) document.querySelector(`.case-row[aria-checked="true"]`)?.focus();
}

function renderEmpty(text) {
  document.getElementById("main").replaceChildren(h("p", { class: "empty" }, text));
}

function render() {
  renderList();
  const v = state.view;
  const top = document.getElementById("top-case");
  top.textContent = state.picked ? `Case ${state.picked}` : "No case";
  if (!v) {
    document.getElementById("top-asof").textContent = "";
    for (const id of ["info", "decision", "reasoning"]) document.getElementById(id).replaceChildren();
    document.getElementById("decision").append(h("p", { class: "empty" }, `Could not load case: ${state.error}`));
    return;
  }
  const d = v.decision;
  const asOf = fmtDate(d.as_of || d.decided_at);
  document.getElementById("top-asof").textContent = asOf ? `as of ${asOf}` : "";
  renderInfo(v);
  renderDecision(v);
  renderReasoning(v);
}

function renderList() {
  const run = state.run;
  const s = run.summary;
  document.getElementById("run-secs").textContent = s && s.seconds != null ? `run · ${s.seconds.toFixed(1)} s` : "";
  const counts = [];
  if (s) {
    counts.push(`${s.written ?? run.cases.length} decided`);
    for (const [a, n] of Object.entries(s.by_action || {})) counts.push(`${n} ${words(a)}`);
    const fb = Object.values(s.fallbacks || {}).reduce((a, b) => a + b, 0);
    if (fb) counts.push(`${fb} fallback`);
    counts.push(`${s.skipped ?? 0} skipped`);
  } else {
    counts.push(`${run.cases.length} cases`);
  }
  document.getElementById("run-counts").textContent = counts.join(" · ");

  const list = document.getElementById("case-list");
  fill(list, run.cases.map((c, i) => {
    const on = c.id === state.picked;
    return h("button", {
      type: "button", role: "radio", class: "case-row", "aria-checked": on ? "true" : "false", tabindex: on ? "0" : "-1",
      onclick: () => pick(c.id, true),
      onkeydown: (e) => {
        const step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
        if (!step) return;
        e.preventDefault();
        const next = run.cases[(i + step + run.cases.length) % run.cases.length];
        pick(next.id, true);
      },
    },
      h("span", { class: "case-dot", "aria-hidden": "true" }),
      h("span", { class: "case-body" },
        h("span", { class: "case-title" }, c.title || `Case ${c.id}`),
        h("span", { class: "case-meta" },
          h("span", { class: "mono" }, [c.id, c.priority].filter(Boolean).join(" · ")),
          h("span", { class: "case-action" },
            h("span", { class: `mark mark-${c.unreadable ? "UNREADABLE" : c.action}`, "aria-hidden": "true" }),
            c.unreadable ? "UNREADABLE" : dash(c.action)))));
  }));
}

function renderInfo(v) {
  const d = v.decision, x = v.derived;
  const unknowns = d.unknowns || [];
  const unrelated = d.unrelated_issues || [];
  const requested = new Set(v.review.new_cases);
  const el = document.getElementById("info");
  fill(el,
    h("div", { class: "info-top" },
      h("h2", { class: "label" }, "Info"),
      h("p", { class: "case-heading" }, d.title || `Case ${d.case_id}`),
      d.request && [
        h("p", { class: "field-label" }, "Initial request"),
        h("blockquote", { class: "request" }, `“${d.request}”`),
      ],
      h("dl", { class: "facts" },
        h("div", {}, h("dt", {}, "Events"), h("dd", {}, dash(d.events_seen))),
        h("div", {}, h("dt", {}, "Evidence"), h("dd", {}, `${(d.evidence_refs || []).length} cited`)),
        h("div", {}, h("dt", {}, "Amount"), h("dd", {}, x.amount == null ? "—" : `GBP ${x.amount.toFixed(2)}`)))),
    h("div", { class: "unknowns" },
      h("div", { class: "row-between" },
        h("h2", { class: "label" }, "Not known"),
        h("span", { class: "unknown-count" }, String(unknowns.length))),
      unknowns.length
        ? h("ul", { class: "bullets" }, unknowns.map((u) => h("li", {}, h("span", { class: "square", "aria-hidden": "true" }), h("span", {}, u))))
        : h("p", { class: "none" }, "Nothing listed.")),
    (d.warnings || []).length > 0 && h("p", { class: "warnings" }, `Input warnings: ${d.warnings.join(" · ")}`),
    unrelated.length > 0 && h("div", { class: "separate" },
      h("h2", { class: "label" }, "Separate issues"),
      unrelated.map((text) => [
        h("p", { class: "separate-item" }, text),
        requested.has(text)
          ? h("p", { class: "requested" }, "Requested as a new case")
          : h("button", { type: "button", class: "btn-small", onclick: () => review({ choice: "new_case", text }) }, "Open as new case"),
      ])),
  );
}

function stagedLine(a) {
  let what;
  if (a.kind === "message" || a.kind === "call") what = `to ${a.to} · ${words(a.purpose || "")}`;
  else if (a.kind === "approval_request") what = `landlord · GBP ${Number(a.amount_gbp).toFixed(2)}`;
  else if (a.kind === "followup") what = `review ${fmtDate(a.review_at)} · waiting on ${a.waiting_on}`;
  else if (a.kind === "escalation") what = `${a.priority} → ${a.route}`;
  else if (a.kind === "closure") what = `invoice ${a.invoice_status} · keys ${a.keys_status}`;
  return `${a.id} · ${what || a.kind} · ${words(a.state || "")}`;
}

function callBlock(c) {
  const r = c.result, dec = (r && r.decisions) || {};
  const status = c.dry_run ? "not dialled (dry run)" : words(c.call_status || c.state || "");
  const facts = [
    ["Outcome", r && r.outcome], ["Visit date", dec.confirmed_date], ["Exact date", dec.confirmed_date_iso],
    ["Amount quoted", dec.quoted_amount_gbp == null ? null : `GBP ${Number(dec.quoted_amount_gbp).toFixed(2)}`],
    ["Call back on", dec.callback_number], ["Duration", r && r.duration_s != null ? `${Math.round(r.duration_s)} s` : null],
  ].filter(([, value]) => value);
  const turns = (r && r.transcript) || [];
  return h("div", { class: "call" },
    h("div", { class: "row-between" },
      h("p", { class: "kv-v" }, `Call to ${dash(c.party)} · ${words(c.purpose || "")}`),
      h("span", { class: `call-badge${c.dry_run ? " call-dry" : ""}` }, status)),
    c.objective && h("p", { class: "call-objective" }, c.objective),
    r
      ? [
        facts.length > 0 && h("dl", { class: "facts call-facts" },
          facts.map(([k, value]) => h("div", {}, h("dt", {}, k), h("dd", {}, String(value))))),
        r.summary && h("p", { class: "call-summary" }, r.summary),
        turns.length > 0 && h("div", { class: "transcript", tabindex: "0", role: "log", "aria-label": "Call transcript (automatic, untrusted)" },
          turns.map((t) => h("p", { class: `turn turn-${t.role === "agent" ? "agent" : "other"}` },
            h("span", { class: "who" }, t.role === "agent" ? "Agent" : "Other party"), t.message)),
          r.truncated && h("p", { class: "muted small" }, `… ${r.transcript_turns - turns.length} more turns in ${dash(r.record)}`)),
      ]
      : h("p", { class: "none" }, c.dry_run ? "Nothing to collect: no call was made." : "Waiting for the call result."));
}

function renderDecision(v) {
  const d = v.decision, x = v.derived;
  const blocked = d.blocked || [];
  const hasBlock = blocked.length > 0 || d.hazard;
  const blockText = hasBlock
    ? [...(d.hazard ? ["Open hazard found by code"] : []), ...blocked.map((b) => `${b.tool}: ${b.why || b.code}`)].join(" · ")
    : "None recorded · no hazard";
  const options = d.options || [];
  const latest = v.review.latest;
  const conf = typeof d.confidence === "number" ? d.confidence : null;
  const gateChanged = (d.gate_notes || []).length > 0 || d.proposed_action;
  const approval = (d.actions || []).find((a) => a.kind === "approval_request");
  const body = d.message || (approval && approval.body) || "";

  const el = document.getElementById("decision");
  fill(el,
    d.source === "fallback" && h("div", { class: "banner" },
      `System fallback (${dash(d.cause)}): the model did not finish, so plain code wrote this escalation.`),
    h("div", { class: `blockers${hasBlock ? " on" : ""}` },
      h("h2", { class: "label" }, "Blockers"), h("span", { class: "blockers-text" }, blockText)),
    h("div", { class: "decision-top" },
      h("div", { class: "row-between", style: "flex-wrap: wrap; gap: 8px 16px" },
        h("h2", { class: "label primary" }, "Decision"),
        h("span", { class: "mono small muted" }, d.source === "fallback" ? "by code · fallback" : "by model · checked by code")),
      h("div", { class: "action-line" },
        h("p", { class: "action-label" }, x.action_label),
        d.priority && h("span", { class: `prio prio-${d.priority}` }, d.priority)),
      h("div", { class: "decision-meta" },
        h("div", { class: "conf" },
          h("span", { class: "muted" }, "Confidence"),
          h("span", { class: "conf-track", "aria-hidden": "true" },
            h("span", { class: "conf-fill", style: `width: ${Math.round((conf || 0) * 100)}%` })),
          h("span", { class: "mono" }, conf == null ? "—" : conf.toFixed(2))),
        x.route && h("span", { class: "route" }, `→ ${x.route.route} `, h("span", { class: "route-state" }, `· ${x.route.state}`))),
      h("p", { class: "reason" }, x.reason_parts.map((p) => (p.ref ? h("span", { class: "ref" }, p.t) : p.t))),
      gateChanged && h("div", { class: "gates" },
        d.proposed_action ? `Gates changed the model's answer: it proposed ${d.proposed_action}.` : "Gate notes:",
        (d.gate_notes || []).length > 0 && h("ul", {}, d.gate_notes.map((n) => h("li", {}, n))))),
    h("div", { class: "section" },
      h("h2", { class: "label" }, "Wait"),
      h("div", { class: "grid-2" },
        h("div", {}, h("p", { class: "kv-k" }, "Waiting on"), h("p", { class: "kv-v" }, dash(d.waiting_on))),
        h("div", {}, h("p", { class: "kv-k" }, "For"),
          h("p", { class: "kv-v" }, d.waiting_days == null ? "—" : `${Number(d.waiting_days).toFixed(1).replace(/\.0$/, "")} days`))),
      x.followup_missing && h("p", { class: "alert" },
        "Follow-up was not scheduled: schedule_followup was skipped after the decision was submitted.")),
    (d.calls || []).length > 0 && h("div", { class: "section" },
      h("h2", { class: "label" }, "Calls"),
      d.calls.map((c) => callBlock(c))),
    h("div", { class: "action-block" },
      options.length
        ? [
          h("h2", { class: "label" }, "Action · pick an option"),
          h("div", { role: "radiogroup", "aria-label": "Options", class: "options" },
            options.map((text, i) => h("button", {
              type: "button", role: "radio", class: "option", "aria-checked": i === state.opt ? "true" : "false",
              onclick: () => { state.opt = i; renderDecision(state.view); },
            }, h("span", { class: "option-n" }, String(i + 1)), h("span", {}, text)))),
        ]
        : [
          h("h2", { class: "label" }, "Action · staged"),
          body ? h("p", { class: "message" }, body) : null,
          (d.actions || []).length
            ? h("ul", { class: "staged" }, d.actions.map((a) => h("li", {}, stagedLine(a))))
            : h("p", { class: "none" }, "Nothing staged."),
        ],
      h("div", { class: "buttons" },
        options.length > 0 && h("button", { type: "button", class: "btn-primary", onclick: () => review({ choice: "option", option: state.opt + 1 }) },
          `Go with option ${state.opt + 1}`),
        h("button", { type: "button", class: "btn-secondary", onclick: () => review({ choice: "take_over" }) }, "Take over case")),
      latest && h("p", { class: "chosen" }, latest.choice === "option"
        ? `Chosen: option ${latest.option} · ${fmtDate(latest.at)} UTC`
        : `Taken over by a person · ${fmtDate(latest.at)} UTC`),
      state.error && h("p", { class: "error-text", role: "alert" }, state.error)),
  );
}

function renderReasoning(v) {
  const d = v.decision, x = v.derived;
  const meta = d.model
    ? [d.model, `${d.steps} turns`, `${Number(d.tokens || 0).toLocaleString("en-GB")} tok`, x.seconds == null ? null : `${x.seconds.toFixed(1)} s`]
    : ["no model run", x.seconds == null ? null : `${x.seconds.toFixed(1)} s`];
  const el = document.getElementById("reasoning");
  fill(el,
    h("div", { class: "reasoning-head" },
      h("div", { class: "row-between" },
        h("h2", { class: "label" }, "Reasoning"),
        h("span", { class: "mono small muted" }, `${x.calls} calls`)),
      h("p", { class: "mono small reasoning-meta" }, meta.filter(Boolean).join(" · "))),
    x.steps.length
      ? h("ol", { class: "trace" }, x.steps.map((t) => h("li", {},
        h("span", { class: "step-n" }, String(t.step ?? "").padStart(2, "0")),
        t.thought != null
          ? h("details", { class: "step-body thought" }, h("summary", {}, "thought"), h("p", {}, t.thought))
          : h("div", { class: "step-body" },
            h("div", { class: "row-between", style: "align-items: baseline" },
              h("span", { class: "step-tool" }, t.tool),
              h("span", { class: `step-status st-${t.status}` }, t.status)),
            h("p", { class: "step-arg" }, t.arg)))))
      : h("p", { class: "none", style: "padding: 0 18px" }, "No trace recorded."),
    h("div", { class: "ask" },
      h("label", { for: "ask", class: "sr-only" }, "Ask the agent about this case"),
      h("input", { id: "ask", type: "text", placeholder: "Ask about this case", disabled: true, title: "Coming later" }),
      h("button", { type: "button", "aria-label": "Send question", disabled: true, title: "Coming later" },
        sendIcon())),
  );
}

function sendIcon() {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  for (const [k, val] of Object.entries({ width: 18, height: 18, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor",
    "stroke-width": 2, "stroke-linecap": "round", "stroke-linejoin": "round", "aria-hidden": "true" })) svg.setAttribute(k, val);
  for (const dPath of ["M5 12h14", "M13 6l6 6-6 6"]) {
    const p = document.createElementNS(ns, "path");
    p.setAttribute("d", dPath);
    svg.append(p);
  }
  return svg;
}

async function review(body) {
  state.error = "";
  try {
    state.view.review = await api(`/api/cases/${encodeURIComponent(state.picked)}/review`, body);
  } catch (e) {
    state.error = `Could not save: ${e.message}`;
  }
  render();
}

window.addEventListener("hashchange", () => {
  const id = decodeURIComponent(location.hash.slice(1));
  if (state.run && id !== state.picked && state.run.cases.some((c) => c.id === id)) pick(id, false);
});

load();
