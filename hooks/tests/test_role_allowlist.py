"""Rule 6 (role read allowlist) and its code-window exception in guard_context_budget.

Run from the repo root:  python -m unittest discover -s hooks/tests -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "guard_context_budget.py")


def run_hook(agent, path, **window):
    payload = {
        "tool_name": "Read",
        "tool_input": dict({"file_path": path}, **window),
        "agent_type": f"flutter-sdlc-pipeline:{agent}",
    }
    env = dict(os.environ, SDLC_GUARD="1")
    out = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                         capture_output=True, text=True, env=env)
    return out.stdout + out.stderr


class RoleAllowlistTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dart = os.path.join(self._tmp.name, "lib", "orders_repository.dart")
        self.task = os.path.join(self._tmp.name, "docs", "plans", "x", "task-03-orders.md")
        for p in (self.dart, self.task):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write("x\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_eng_reviewer_may_window_read_source(self):
        self.assertNotIn("BLOCKED", run_hook("eng-reviewer", self.dart, offset=1, limit=40))

    def test_eng_reviewer_full_read_of_source_is_still_blocked(self):
        self.assertIn("BLOCKED", run_hook("eng-reviewer", self.dart))

    def test_eng_reviewer_task_file_is_still_blocked_even_windowed(self):
        self.assertIn("BLOCKED", run_hook("eng-reviewer", self.task, offset=1, limit=40))

    def test_ceo_reviewer_gets_no_code_window(self):
        self.assertIn("BLOCKED", run_hook("ceo-reviewer", self.dart, offset=1, limit=40))


if __name__ == "__main__":
    unittest.main()
