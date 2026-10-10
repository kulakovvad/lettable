import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from agent.ui import (MAX_FILE, ReviewError, UnreadableCase, case_dir, case_view, list_cases, make_server, save_review,
                      step_summary)


def decision(cid, **over):
    d = {"case_id": cid, "action": "ESCALATE", "reason": "See event-003 and event-013/015.", "source": "model",
         "message": "", "unknowns": ["Who attended"], "options": ["Ask the provider", "Ask the tenant"],
         "confidence": 0.8, "hazard": False, "waiting_on": None, "waiting_days": None, "events_seen": 19,
         "gate_notes": [], "proposed_action": None, "cause": None, "warnings": [], "priority": "P2",
         "title": "Front Door Repair", "request": "Door sticks.", "as_of": "2025-01-12T09:37:00+00:00",
         "model": "claude", "steps": 2, "tokens": 1000, "evidence_refs": ["event-003"], "unrelated_issues": [],
         "actions": [{"id": "escalation-1", "kind": "escalation", "state": "committed", "priority": "P2", "route": "accounts"}],
         "blocked": [],
         "trace": [{"step": 1, "tool": "read_events", "args": {"first": 15, "last": 19}, "result": {"status": "ok", "events": "5 item(s)"}},
                   {"step": 1, "thought": "Looking at the invoice."},
                   {"step": 2, "tool": "submit_decision", "args": {"action": "ESCALATE", "priority": "P2", "confidence": 0.8,
                                                                    "amount_gbp": 68.97}, "result": {"status": "accepted"}}]}
    d.update(over)
    return d


def make_run(root: Path, decisions):
    out = root / "out"
    for d in decisions:
        (out / d["case_id"]).mkdir(parents=True)
        (out / d["case_id"] / "decision.json").write_text(json.dumps(d))
    (out / "summary.json").write_text(json.dumps({"total": len(decisions), "written": len(decisions), "skipped": 0,
                                                  "by_action": {}, "seconds": 3.2}))
    (out / "trace.jsonl").write_text('{"case_id": "015", "seconds": 9.0}\nnot json\n{"case_id": "015", "seconds": 10.57}\n')
    return out


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_case_list_puts_escalations_first_then_priority(self):
        out = make_run(self.root, [decision("001", action="WAIT", priority="P1"), decision("002", priority="P3"),
                                   decision("003", priority="P1")])
        (out / "no-decision").mkdir()
        run = list_cases(out)
        self.assertEqual([c["id"] for c in run["cases"]], ["003", "002", "001"])
        self.assertEqual(run["summary"]["seconds"], 3.2)

    def test_view_derives_the_mockup_fields(self):
        out = make_run(self.root, [decision("015")])
        x = case_view(out, "015")["derived"]
        self.assertEqual(x["action_label"], "Escalate to a person")
        self.assertEqual(x["amount"], 68.97)
        self.assertEqual(x["route"], {"route": "accounts", "state": "committed"})
        self.assertEqual(x["seconds"], 10.57)
        self.assertFalse(x["followup_missing"])
        self.assertEqual(x["calls"], 2)
        self.assertEqual([p["t"] for p in x["reason_parts"] if p["ref"]], ["event-003", "event-013/015"])
        self.assertEqual(x["steps"][0]["arg"], "events 15–19 · 5 items")
        self.assertEqual(x["steps"][1], {"step": 1, "thought": "Looking at the invoice."})
        self.assertEqual(x["steps"][2]["arg"], "ESCALATE · P2 · conf 0.80")

    def test_view_exposes_property_handover_and_red_flags(self):
        ticket = {"id": "escalation-1", "kind": "escalation", "state": "committed", "priority": "P1", "route": "accounts",
                  "respond_by": "2025-01-12T13:37:00+00:00", "summary": "Suspected new payee.",
                  "known": ["Title: Front Door Repair (index)", "Property: Flat 2, 1 Test Road (index)", 7],
                  "tried": ["Checked the events"], "failed": None, "recommended": "Recommended: Call accounts",
                  "conflicts": [{"field": "payee", "values": [{"value": "Keystone", "refs": ["event-010"]},
                                                              {"value": "Meadow", "refs": ["event-029"]}]}, "junk"]}
        flags = [{"category": "payment", "force": True, "ref": "event-029", "excerpt": "Direct Debit",
                  "guidance": "Escalate to accounts.", "route": "accounts", "priority": "P1"}, "junk"]
        out = make_run(self.root, [decision("015", actions=[ticket], red_flags=flags, answer="Do not pay.")])
        view = case_view(out, "015")
        x = view["derived"]
        self.assertEqual(x["property"], "Flat 2, 1 Test Road")
        e = x["escalation"]
        self.assertEqual((e["respond_by"], e["recommended"]), ("2025-01-12T13:37:00+00:00", "Recommended: Call accounts"))
        self.assertEqual(e["known"][-1], "7")
        self.assertEqual(e["failed"], [])
        self.assertEqual(e["conflicts"], [{"field": "payee", "values": [{"value": "Keystone", "refs": ["event-010"]},
                                                                         {"value": "Meadow", "refs": ["event-029"]}]}])
        self.assertEqual(len(x["red_flags"]), 1)
        self.assertTrue(x["red_flags"][0]["force"])
        self.assertEqual(view["decision"]["answer"], "Do not pay.")

    def test_case_card_address_wins_over_ticket_line(self):
        ticket = {"kind": "escalation", "known": ["Property: Old address (index)"]}
        details = {"property": {"address": "Flat 9, 3 New Street", "address_variants": [], "references": []}}
        out = make_run(self.root, [decision("015", details=details, actions=[ticket])])
        self.assertEqual(case_view(out, "015")["derived"]["property"], "Flat 9, 3 New Street")

    def test_skipped_followup_is_flagged(self):
        trace = [{"step": 3, "tool": "schedule_followup", "args": {"after_hours": 72, "waiting_on": "tenant"},
                  "result": {"status": "skipped", "error": "decision already submitted"}}]
        out = make_run(self.root, [decision("014", action="WAIT", trace=trace, actions=[])])
        x = case_view(out, "014")["derived"]
        self.assertTrue(x["followup_missing"])
        self.assertIsNone(x["route"])
        self.assertEqual(x["steps"][0]["arg"], "72 h · waiting on tenant — decision already submitted")

    def test_fallback_with_empty_fields_renders(self):
        fb = decision("009", source="fallback", cause="timeout", priority=None, confidence=None, title="", request="",
                      as_of="", model="", steps=0, tokens=0, evidence_refs=[], actions=[], trace=[])
        out = make_run(self.root, [fb])
        view = case_view(out, "009")
        self.assertIsNone(view["derived"]["amount"])
        self.assertEqual(view["derived"]["steps"], [])
        self.assertEqual(list_cases(out)["cases"][0]["source"], "fallback")

    def test_step_summaries(self):
        self.assertEqual(step_summary({"tool": "search_case", "args": {"query": "quote"}, "result": {"hits": "1 item(s)"}}),
                         "“quote” · 1 hit")
        self.assertEqual(step_summary({"tool": "case_facts", "args": {}, "result": {"status": "ok"}}), "—")
        self.assertEqual(step_summary({"tool": "send_message", "args": {"to": "landlord", "purpose": "chase"},
                                       "result": {"status": "blocked", "why": "too early"}}), "to landlord · chase — too early")

    def test_case_ids_cannot_escape_the_run(self):
        out = make_run(self.root, [decision("015")])
        (self.root / "decision.json").write_text("{}")
        for bad in ("..", ".", "", "../out/015", "015/../..", "a\\b", "missing"):
            self.assertIsNone(case_dir(out, bad), bad)
            self.assertIsNone(case_view(out, bad), bad)
        self.assertIsNotNone(case_dir(out, "015"))

    def test_symlinked_case_folders_and_files_are_ignored(self):
        out = make_run(self.root, [decision("015")])
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (elsewhere / "decision.json").write_text(json.dumps(decision("999")))
        (out / "link").symlink_to(elsewhere, target_is_directory=True)
        (out / "016").mkdir()
        (out / "016" / "decision.json").symlink_to(elsewhere / "decision.json")
        for cid in ("link", "016"):
            self.assertIsNone(case_dir(out, cid), cid)
            with self.assertRaises(ReviewError):
                save_review(out, cid, {"choice": "take_over"})
        self.assertEqual([c["id"] for c in list_cases(out)["cases"]], ["015"])
        self.assertFalse((elsewhere / "review.json").exists())

    def test_unreadable_decision_is_listed_not_hidden(self):
        out = make_run(self.root, [decision("015")])
        (out / "020").mkdir()
        (out / "020" / "decision.json").write_bytes(b'{"case_id": "020", "act')
        (out / "021").mkdir()
        (out / "021" / "decision.json").write_bytes(b"\xff\xfe not utf-8")
        rows = {c["id"]: c for c in list_cases(out)["cases"]}
        self.assertTrue(rows["020"].get("unreadable"))
        self.assertTrue(rows["021"].get("unreadable"))
        self.assertNotIn("unreadable", rows["015"])
        with self.assertRaises(UnreadableCase):
            case_view(out, "020")
        with self.assertRaises(ReviewError) as ctx:
            save_review(out, "020", {"choice": "take_over"})
        self.assertEqual(ctx.exception.status, 422)

    def test_oversized_decision_is_unreadable(self):
        out = make_run(self.root, [decision("015", reason="x" * (MAX_FILE + 1))])
        self.assertTrue(list_cases(out)["cases"][0].get("unreadable"))

    def test_malformed_trace_and_fields_do_not_break_the_view(self):
        trace = [{"step": 1, "tool": "read_events", "args": "s", "result": "r"},
                 {"step": 2, "tool": "consistency_check", "args": {}, "result": {"checks": "bad"}},
                 {"step": 3, "tool": "submit_decision", "args": ["x"]}, "not a dict", 7]
        out = make_run(self.root, [decision("015", trace=trace, options="oops", unknowns=None, reason=5,
                                            actions=[{"kind": "escalation"}, "x"])])
        view = case_view(out, "015")
        self.assertEqual([s["tool"] for s in view["derived"]["steps"]], ["read_events", "consistency_check", "submit_decision"])
        self.assertEqual(view["derived"]["steps"][1]["arg"], "no differences")
        self.assertEqual(view["decision"]["options"], [])
        self.assertEqual(view["decision"]["unknowns"], [])
        self.assertEqual(view["derived"]["reason_parts"], [])
        self.assertIsNone(view["derived"]["amount"])


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = make_run(Path(self.tmp.name), [decision("015", unrelated_issues=["Flat 10 door"])])

    def tearDown(self):
        self.tmp.cleanup()

    def test_choices_are_appended_and_latest_wins(self):
        save_review(self.out, "015", {"choice": "option", "option": 2})
        save_review(self.out, "015", {"choice": "new_case", "text": "Flat 10 door"})
        review = save_review(self.out, "015", {"choice": "take_over"})
        self.assertEqual(review["latest"]["choice"], "take_over")
        self.assertEqual(review["new_cases"], ["Flat 10 door"])
        data = json.loads((self.out / "015" / "review.json").read_text())
        self.assertEqual(data["entries"][0]["option_text"], "Ask the tenant")
        self.assertEqual(len(data["entries"]), 3)
        self.assertEqual(case_view(self.out, "015")["review"]["latest"]["choice"], "take_over")

    def test_decision_json_is_never_touched(self):
        before = (self.out / "015" / "decision.json").read_bytes()
        save_review(self.out, "015", {"choice": "take_over"})
        self.assertEqual((self.out / "015" / "decision.json").read_bytes(), before)

    def test_bad_reviews_are_refused(self):
        for payload in ({"choice": "delete"}, {"choice": "option", "option": 3}, {"choice": "option", "option": True},
                        {"choice": "option", "option": "1"}, {"choice": "new_case", "text": " "},
                        {"choice": "new_case", "text": "x" * 2001}, []):
            with self.assertRaises(ReviewError, msg=payload):
                save_review(self.out, "015", payload)
        with self.assertRaises(ReviewError):
            save_review(self.out, "..", {"choice": "take_over"})
        self.assertFalse((self.out / "015" / "review.json").exists())


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = make_run(Path(self.tmp.name), [decision("015")])
        self.server = make_server(self.out, 0)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body=body, headers=headers or {})
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return res.status, res.getheader("Content-Type"), data

    def test_page_and_api(self):
        status, ctype, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn(b"/static/app.js", body)
        for name in ("app.js", "styles.css"):
            self.assertEqual(self.request("GET", "/static/" + name)[0], 200)
        status, _, body = self.request("GET", "/api/run")
        self.assertEqual(json.loads(body)["cases"][0]["id"], "015")
        status, _, body = self.request("GET", "/api/cases/015")
        self.assertEqual(json.loads(body)["decision"]["case_id"], "015")

    def test_review_post(self):
        payload = json.dumps({"choice": "option", "option": 1})
        status, _, body = self.request("POST", "/api/cases/015/review", payload, {"Content-Type": "application/json"})
        self.assertEqual(status, 200, body)
        self.assertEqual(json.loads(body)["latest"]["option"], 1)
        status, _, _ = self.request("POST", "/api/cases/015/review", payload, {"Content-Type": "text/plain"})
        self.assertEqual(status, 415)
        status, _, _ = self.request("POST", "/api/cases/015/review", "{", {"Content-Type": "application/json"})
        self.assertEqual(status, 400)

    def test_unknown_paths_and_traversal_are_404(self):
        for path in ("/api/cases/%2e%2e", "/api/cases/..%2Fsummary.json", "/static/..%2Fui.py", "/static/.hidden",
                     "/../agent/ui.py", "/api/cases/missing", "/nope"):
            self.assertEqual(self.request("GET", path)[0], 404, path)

    def test_csp_header_is_sent(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/")
        res = conn.getresponse()
        res.read()
        conn.close()
        self.assertIn("default-src 'self'", res.getheader("Content-Security-Policy"))

    def test_broken_case_files_get_json_errors_not_dropped_connections(self):
        (self.out / "020").mkdir()
        (self.out / "020" / "decision.json").write_bytes(b"{half")
        status, ctype, body = self.request("GET", "/api/cases/020")
        self.assertEqual(status, 422)
        self.assertIn("could not be read", json.loads(body)["error"])
        (self.out / "021").mkdir()
        (self.out / "021" / "decision.json").write_text(json.dumps(decision("021", trace=[{"tool": "read_events", "args": "s"}])))
        self.assertEqual(self.request("GET", "/api/cases/021")[0], 200)
        status, _, body = self.request("POST", "/api/cases/020/review", '{"choice": "take_over"}', {"Content-Type": "application/json"})
        self.assertEqual(status, 422)

    def test_unexpected_errors_become_500_json(self):
        import agent.ui as ui

        original = ui.list_cases
        ui.list_cases = lambda out: 1 / 0
        try:
            status, ctype, body = self.request("GET", "/api/run")
        finally:
            ui.list_cases = original
        self.assertEqual(status, 500)
        self.assertIn("ZeroDivisionError", json.loads(body)["error"])

    def test_foreign_host_is_refused(self):
        self.assertEqual(self.request("GET", "/api/run", headers={"Host": "evil.example"})[0], 403)


class CallsPanelTests(unittest.TestCase):
    """The page shows what a call said and what was agreed; the transcript is untrusted speech."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def view(self, **over):
        return case_view(make_run(self.root, [decision("015", **over)]), "015")["decision"]

    def call(self, **over):
        c = {"id": "call-1", "kind": "call", "to": "provider", "purpose": "chase", "state": "committed", "call_status": "started",
             "conversation_id": "conv_1", "objective": "Ask for a date."}
        c.update(over)
        return c

    def test_the_payload_has_the_calls_with_what_was_agreed(self):
        result = {"status": "done", "summary": "They agreed.", "outcome": "confirmed", "duration_s": 24,
                  "decisions": {"confirmed_date": "Friday", "confirmed_date_iso": "2026-10-17", "quoted_amount_gbp": 0},
                  "transcript": [{"role": "agent", "message": "Hello"}, {"role": "other_party", "message": "Friday"}],
                  "transcript_turns": 2, "truncated": False, "record": "calls/conv_1.json"}
        calls = self.view(calls=[{"id": "call-1", "party": "provider", "purpose": "chase", "call_status": "started",
                                  "conversation_id": "conv_1", "dry_run": False, "result": result}])["calls"]
        self.assertEqual(calls[0]["result"]["decisions"]["confirmed_date_iso"], "2026-10-17")
        self.assertEqual([t["role"] for t in calls[0]["result"]["transcript"]], ["agent", "other_party"])
        self.assertEqual(calls[0]["result"]["duration_s"], 24)

    def test_an_older_decision_without_calls_gets_them_from_its_actions(self):
        action = self.call(call_result={"status": "done", "summary": "old style", "data": {"outcome": "declined"}})
        calls = self.view(actions=[action])["calls"]
        self.assertEqual((calls[0]["party"], calls[0]["conversation_id"]), ("provider", "conv_1"))
        self.assertEqual(calls[0]["result"]["summary"], "old style")
        empty = case_view(make_run(self.root, [decision("016", actions=[])]), "016")["decision"]["calls"]
        self.assertEqual(empty, [])

    def test_a_dry_run_call_has_no_result_and_a_started_one_without_a_result_is_waiting(self):
        calls = self.view(actions=[self.call(call_status="dry_run", conversation_id="dryrun-ab"), self.call(id="call-2")])["calls"]
        self.assertEqual([(c["dry_run"], c["result"]) for c in calls], [(True, None), (False, None)])

    def test_hostile_or_wrong_typed_call_fields_are_forced_to_safe_types(self):
        hostile = {"id": {"x": 1}, "party": ["a"], "result": {"summary": "<img src=x onerror=alert(1)>", "duration_s": "long",
                   "transcript": [{"role": "user", "message": "<script>alert(1)</script>" + "x" * 900}] + [{"role": "agent", "message": "m"}] * 80,
                   "decisions": {"confirmed_date_iso": "not a date", "quoted_amount_gbp": "lots"}}}
        c = self.view(calls=[hostile, "junk", None, 5] + [hostile] * 20)["calls"]
        self.assertEqual(len(c), 10)  # capped
        self.assertIsInstance(c[0]["id"], str)
        r = c[0]["result"]
        self.assertIsNone(r["duration_s"])
        self.assertIsNone(r["decisions"]["confirmed_date_iso"])
        self.assertIsNone(r["decisions"]["quoted_amount_gbp"])
        self.assertEqual(len(r["transcript"]), 60)
        self.assertTrue(r["truncated"])
        self.assertLessEqual(len(r["transcript"][0]["message"]), 501)
        json.dumps(c)  # still plain JSON

    def test_the_page_only_ever_puts_call_text_in_as_text(self):
        js = (Path(__file__).resolve().parent.parent / "agent" / "ui_static" / "app.js").read_text()
        for banned in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"):
            self.assertNotIn(banned, js)
        block = js[js.index("function callBlock"):js.index("function renderDecision")]
        self.assertEqual(block.count("("), block.count(")"))
        self.assertEqual(block.count("{"), block.count("}"))
        self.assertEqual(block.count("["), block.count("]"))
        self.assertIn("t.message", block)  # reaches the page as a child of h(), which creates text nodes
        self.assertIn("Waiting for the call result", block)
        self.assertIn("Nothing to collect", block)
        self.assertIn("(d.calls || []).length > 0", js)
        css = (Path(__file__).resolve().parent.parent / "agent" / "ui_static" / "styles.css").read_text()
        self.assertNotRegex(css[css.index("/* calls:"):], r"https?://")  # no new external hosts


if __name__ == "__main__":
    unittest.main()
