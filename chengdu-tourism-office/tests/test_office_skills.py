"""Behavior checks for new local collaboration skills."""
from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from skill_runtime import Runtime


class OfficeSkillTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.runtime = Runtime(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def run_example(self, skill_id):
        manifest = self.runtime.skill(skill_id)
        result = self.runtime.submit(skill_id, copy.deepcopy(manifest["example"]))
        self.assertEqual(result["status"], "completed", result["output"])
        return result["output"]

    def test_responsibility_matrix_checks_roster_and_writes_workbook(self):
        output = self.run_example("responsibility-matrix")
        self.assertEqual(output["rows"][0]["accountable"], "Chen")
        self.assertTrue(self.runtime.file(output["artifacts"][0]["id"])[1].is_file())
        bad = self.runtime.skill("responsibility-matrix")["example"]
        bad["assignments"][0]["accountable"] = "unknown-person"
        result = self.runtime.submit("responsibility-matrix", bad)
        self.assertEqual(result["status"], "failed")
        self.assertIn("Unknown colleague", result["output"]["error"])

    def test_rebalance_assigns_by_skill_and_reports_unfilled_work(self):
        output = self.run_example("workload-rebalance")
        self.assertEqual(len(output["assignments"]), 2)
        self.assertFalse(output["needs_manager_attention"])
        payload = {"tasks": [{"task": "Uncovered", "required_skill": "missing-skill", "hours": 4}]}
        result = self.runtime.submit("workload-rebalance", payload)
        self.assertTrue(result["output"]["needs_manager_attention"])
        self.assertEqual(result["output"]["unassigned"][0]["task"], "Uncovered")

    def test_scenario_scores_visible_components_and_missing_values(self):
        output = self.run_example("scenario-compare")
        self.assertEqual(output["recommended"], "Option A")
        self.assertEqual(output["ranking"][0]["score"], 60)
        self.assertEqual(len(output["ranking"][0]["components"]), 2)
        bad = self.runtime.skill("scenario-compare")["example"]
        del bad["options"][0]["measures"]["Price CNY"]
        result = self.runtime.submit("scenario-compare", bad)
        self.assertEqual(result["status"], "failed")
        self.assertIn("Missing Price CNY", result["output"]["error"])

    def test_management_handoff_flags_blocker_and_creates_docx(self):
        output = self.run_example("management-handoff")
        self.assertEqual(output["counts"]["blocked"], 1)
        self.assertEqual(len(output["blockers"]), 1)
        self.assertTrue(self.runtime.file(output["artifacts"][0]["id"])[1].is_file())
        bad = self.runtime.skill("management-handoff")["example"]
        bad["items"][0]["blocker"] = ""
        result = self.runtime.submit("management-handoff", bad)
        self.assertEqual(result["status"], "failed")
        self.assertIn("Describe the blocker", result["output"]["error"])


if __name__ == "__main__":
    unittest.main()
