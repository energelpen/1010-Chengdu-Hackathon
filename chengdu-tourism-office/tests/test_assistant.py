"""Assistant history, provider isolation and company-review integration tests."""
from __future__ import annotations

import copy
import json
import os
import tempfile
import threading
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import app
from scripts.assistant_service import public_config, reply, save_api_key, settings
from scripts.conversation_store import ConversationStore
from scripts.tourism_core import COMPANY, demo


class HistoryTests(unittest.TestCase):
    def test_history_survives_reload_and_preserves_persona_case(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "history.sqlite"
            store = ConversationStore(path)
            conversation = store.create("Review our Chengdu proposal")
            cid = conversation["id"]
            store.append(cid, "user", "Who is leading?", mode="user")
            store.link_case(cid, "SIM-example")
            store.append(cid, "assistant", "I can review the quote.", person_id="finance_manager",
                         name="Finance Manager Deng", mode="local", request_id="SIM-example")
            loaded = ConversationStore(path).get(cid)
            self.assertEqual([m["role"] for m in loaded["messages"]], ["user", "assistant"])
            self.assertEqual(loaded["person_id"], "finance_manager")
            self.assertEqual(loaded["request_id"], "SIM-example")
            self.assertEqual(store.list()[0]["preview"], "I can review the quote.")

    def test_legacy_import_is_idempotent_and_skips_damaged_trace(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            case = demo()
            (folder / "SIM-legacy-trace.json").write_text(json.dumps(case), encoding="utf-8")
            (folder / "bad-trace.json").write_text("{broken", encoding="utf-8")
            store = ConversationStore(folder / "history.sqlite")
            store.import_cases(folder)
            store.import_cases(folder)
            self.assertEqual(len(store.list()), 1)
            self.assertEqual(len(store.get(store.list()[0]["id"])["messages"]), 2)

    def test_ids_cannot_select_files_or_other_queries(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ConversationStore(Path(folder) / "history.sqlite")
            for value in ("../.env", "' OR 1=1", [], None):
                with self.assertRaises(ValueError):
                    store.get(value)
            with self.assertRaises(FileNotFoundError):
                store.get("unknown")


class ProviderTests(unittest.TestCase):
    def test_key_form_saves_server_side_without_returning_secret(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            root = Path(folder)
            (root / ".env").write_text("OPENAI_MODEL=test-model\nCUSTOM_SETTING=keep-me\n", encoding="utf-8")
            new_key = "sk-" + "test" * 12
            save_api_key(root, new_key)
            self.assertEqual(settings(root)["api_key"], new_key)
            self.assertIn("CUSTOM_SETTING=keep-me", (root / ".env").read_text(encoding="utf-8"))
            self.assertNotIn(new_key, json.dumps(public_config(root, COMPANY)))
            self.assertEqual(public_config(root, COMPANY)["key_source"], ".env")
            with self.assertRaises(ValueError): save_api_key(root, "not-a-key")

    def test_env_override_and_public_config_do_not_expose_secret(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {}, clear=True):
            root = Path(folder)
            (root / ".env").write_text('OPENAI_API_KEY="local-test-secret"\nOPENAI_MODEL=example-model\nUNRELATED=ignored', encoding="utf-8")
            self.assertEqual(settings(root)["api_key"], "local-test-secret")
            with patch.dict(os.environ, {"OPENAI_API_KEY": "environment-test-secret"}):
                self.assertEqual(settings(root)["api_key"], "environment-test-secret")
                public = public_config(root, COMPANY)
                self.assertTrue(public["ai_configured"])
                self.assertEqual(public["mode"], "openai")
                self.assertNotIn("secret", json.dumps(public))
                self.assertNotIn("api_key", public)

    def test_openai_uses_grounded_history_without_provider_storage(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"OPENAI_API_KEY": "unit-test-secret", "OPENAI_MODEL": "test-model"}):
            factory = MagicMock()
            client = factory.return_value.__enter__.return_value
            client.responses.create.return_value = SimpleNamespace(output_text="I can help review that quote.")
            conversation = {"messages": [{"role": "user", "content": "What is my role?", "mode": "user"}]}
            answer = reply(Path(folder), conversation, COMPANY["people"][1], COMPANY, None, client_factory=factory)
            call = client.responses.create.call_args.kwargs
            self.assertEqual(answer["mode"], "openai")
            self.assertEqual(call["model"], "test-model")
            self.assertFalse(call["store"])
            self.assertEqual(call["input"][0]["content"], "What is my role?")
            self.assertIn("Sales Manager", call["instructions"])
            self.assertNotIn("unit-test-secret", call["instructions"])
            self.assertLessEqual(call["max_output_tokens"], 2000)
            self.assertEqual(factory.call_args.kwargs["timeout"], 30.0)

    def test_provider_failure_hides_exception_and_credentials(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"OPENAI_API_KEY": "private-unit-key"}):
            factory = MagicMock()
            factory.return_value.__enter__.return_value.responses.create.side_effect = RuntimeError("network failure private-unit-key")
            answer = reply(Path(folder), {"messages": [{"role": "user", "content": "Hello"}]},
                           COMPANY["people"][0], COMPANY, None, client_factory=factory)
            self.assertEqual(answer["mode"], "error")
            self.assertIn("Your message is saved", answer["content"])
            self.assertNotIn("private-unit-key", json.dumps(answer))
            self.assertNotIn("network failure", answer["content"])


class ApplicationAssistantTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        # These tests exercise the preserved tourism workflow; general company tests use their own fixture.
        (self.root / "company.json").write_text(json.dumps(COMPANY), encoding="utf-8")
        self.patches = [patch("app.DATA", self.root), patch("app.COMPANY_FILE", self.root / "company.json"),
                        patch("app.ROOT", self.root), patch.dict(os.environ, {"OPENAI_API_KEY": ""})]
        for item in self.patches:
            item.start()
        self.task = f"RFQ: 30 travelers for a 3 day Chengdu food and tea tour from {(date.today() + timedelta(days=30)).isoformat()}, budget CNY 200000."

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.temporary.cleanup()

    def test_generic_chat_and_persona_switch_keep_history(self):
        first = app.chat({"message": "Who is in the company?"})
        cid = first["conversation"]["id"]
        second = app.chat({"message": "What do you do?", "conversation_id": cid, "person_id": "finance_manager"})
        self.assertEqual(second["conversation"]["person_id"], "finance_manager")
        self.assertEqual(len(second["conversation"]["messages"]), 4)
        self.assertEqual(second["conversation"]["messages"][-1]["mode"], "local")
        self.assertNotIn("case", second)
        self.assertEqual(len(app.history_store().list()), 1)

    def test_proposal_approval_and_reopening_case(self):
        result = app.chat({"message": self.task, "run_workflow": True, "auto_execute": True})
        cid = result["conversation"]["id"]
        self.assertEqual(result["proposal"]["status"], "pending_review")
        self.assertEqual(result["case"]["execution"]["data"]["completed"], {})
        approved = app.review({"conversation_id": cid, "action": "approve", "comment": "Proceed with this plan."})
        self.assertEqual(approved["proposal"]["status"], "completed")
        self.assertEqual(approved["case"]["outcome"]["data"]["decision"], "ready_for_human_review")
        followup = app.chat({"conversation_id": cid, "person_id": "finance_manager", "message": "What is the quote?"})
        self.assertIn("CNY", followup["conversation"]["messages"][-1]["content"])
        self.assertEqual(followup["case"]["request"]["request_id"], result["case"]["request"]["request_id"])
        self.assertEqual(len(app.history_store().list()), 1)

    def test_return_comments_resubmit_then_manager_escalation(self):
        result = app.chat({"message": self.task, "run_workflow": True})
        cid = result["conversation"]["id"]
        changed = app.review({"conversation_id": cid, "action": "request_changes", "comment": "Review the pacing."})
        self.assertEqual(changed["proposal"]["status"], "changes_requested")
        submitted = app.review({"conversation_id": cid, "action": "resubmit", "comment": "Pacing reviewed; retaining this option."})
        self.assertEqual(submitted["proposal"]["revision"], 2)
        escalated = app.review({"conversation_id": cid, "action": "escalate", "comment": "Need manager decision on the schedule."})
        self.assertEqual(escalated["proposal"]["status"], "escalated")
        self.assertTrue(escalated["proposal"]["manager"]["name"])
        resolved = app.review({"conversation_id": cid, "action": "resolve", "comment": "Manager confirmed this schedule."})
        self.assertEqual(resolved["proposal"]["status"], "ready_to_resubmit")

    def test_invalid_chat_does_not_create_an_empty_thread(self):
        for body in ({"message": ""}, {"message": "hello", "run_workflow": "yes"},
                     {"message": "hello", "person_id": "missing_staff"}):
            with self.assertRaises(ValueError):
                app.chat(body)
        self.assertEqual(app.history_store().list(), [])

    def test_partial_request_keeps_extracted_values(self):
        request, assumptions = app.prepare_request({"message": "Quote a 4 day food tour for 16 travelers, budget CNY 180000."})
        parsed = app.inquiry_intake(request)["data"]
        self.assertEqual((parsed["group_size"], parsed["duration_days"], parsed["budget_cny"]), (16, 4, 180000))
        self.assertTrue(any("travel_start=" in item for item in assumptions))
        self.assertFalse(any(item.startswith("group_size=") for item in assumptions))

    def test_revision_keeps_case_facts_and_review_history(self):
        first = app.chat({"message": self.task, "run_workflow": True})
        cid = first["conversation"]["id"]
        app.review({"conversation_id": cid, "action": "request_changes", "comment": "Please lower the budget."})
        revised = app.chat({"conversation_id": cid, "message": "Revise the budget to CNY 190000.", "run_workflow": True})
        facts = revised["case"]["inquiry"]["data"]
        self.assertEqual((facts["group_size"], facts["duration_days"], facts["budget_cny"]), (30, 3, 190000))
        self.assertEqual(facts["travel_start"], first["case"]["inquiry"]["data"]["travel_start"])
        self.assertEqual(revised["proposal"]["id"], first["proposal"]["id"])
        self.assertEqual(revised["proposal"]["revision"], 2)
        self.assertTrue(any(item["text"] == "Please lower the budget." for item in revised["proposal"]["comments"]))

    def test_task_board_cannot_bypass_review_and_option_edit_reopens_plan(self):
        first = app.chat({"message": self.task, "run_workflow": True})
        rid, cid = first["case"]["request"]["request_id"], first["conversation"]["id"]
        with self.assertRaises(PermissionError):
            app.update_case({"request_id": rid, "task_id": "INTAKE", "action": "complete"}, "event")
        app.review({"conversation_id": cid, "action": "approve"})
        alternative = first["case"]["comparison"]["data"]["alternatives"][0]["id"]
        app.update_case({"request_id": rid, "option_id": alternative}, "option")
        changed = app.history_store().get(cid)["proposal"]
        self.assertEqual(changed["status"], "changes_requested")
        self.assertIsNone(changed["approval_source"])
        self.assertTrue(any(item["action"] == "approve" for item in changed["audit"]))

    def test_provider_error_still_persists_user_message(self):
        with patch("company_chat.reply", return_value={"content": "OpenAI is unavailable. Your message is saved.", "mode": "error"}):
            result = app.chat({"message": "Please explain the company."})
        saved = app.history_store().get(result["conversation"]["id"])
        self.assertEqual(saved["messages"][0]["content"], "Please explain the company.")
        self.assertEqual(saved["messages"][1]["mode"], "error")

    def test_http_routes_reject_cross_origin_and_never_serve_env(self):
        server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            request = Request(base + "/api/chat", data=b'{"message":"hello"}',
                              headers={"Content-Type": "application/json", "Origin": "https://other.example"})
            with self.assertRaises(HTTPError) as denied:
                urlopen(request)
            self.assertEqual(denied.exception.code, 403)
            with urlopen(base + "/api/config") as response:
                config = json.load(response)
            self.assertFalse(config["ai_configured"])
            with self.assertRaises(HTTPError) as missing:
                urlopen(base + "/.env")
            self.assertEqual(missing.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_local_key_endpoint_saves_secret_without_echoing_it(self):
        server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        base = f"http://127.0.0.1:{server.server_port}"
        key = "sk-" + "replacement" * 5
        try:
            request = Request(base + "/api/config/key", data=json.dumps({"api_key": key}).encode(),
                              headers={"Content-Type": "application/json", "Origin": base})
            with urlopen(request) as response:
                public = json.load(response)
            self.assertTrue(public["ai_configured"])
            self.assertNotIn(key, json.dumps(public))
            self.assertEqual(public["key_source"], ".env")
            self.assertEqual(settings(self.root)["api_key"], key)
            with self.assertRaises(HTTPError) as missing:
                urlopen(base + "/.env")
            self.assertEqual(missing.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
