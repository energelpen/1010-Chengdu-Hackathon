"""Measured execution state for model-authored plans; no scenario-specific workflow."""
import copy
import time
import uuid
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


class Execution:
    def __init__(self, model, callback=None):
        self.started = time.monotonic()
        self.callback = callback or (lambda snapshot: None)
        self.runs = []
        self.data = {"id": "AGENT-" + uuid.uuid4().hex, "status": "running", "model": model,
                     "started_at": now(), "steps": [], "calls": [], "run_ids": [], "artifact_ids": [],
                     "statistics": {"model_requests": 0, "tool_calls": 0, "skills_executed": 0,
                                    "skills_completed": 0, "skills_failed": 0, "skills_pending": 0,
                                    "distinct_skills": 0, "delegated_people": 0, "artifacts": 0,
                                    "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "elapsed_ms": 0}}

    def emit(self):
        self.data["elapsed_ms"] = round((time.monotonic() - self.started) * 1000)
        self.data["statistics"]["elapsed_ms"] = self.data["elapsed_ms"]
        self.callback(copy.deepcopy(self.data))

    def request(self):
        self.data["statistics"]["model_requests"] += 1
        self.emit()

    def usage(self, response):
        usage = getattr(response, "usage", None)
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            value = usage.get(key) if isinstance(usage, dict) else getattr(usage, key, None)
            prior = self.data["statistics"][key]
            self.data["statistics"][key] = prior + value if isinstance(prior, int) and isinstance(value, int) else None
        self.emit()

    def plan(self, steps, catalog, people, selected):
        if not steps or len(steps) > 30:
            raise ValueError("A plan needs 1 to 30 concrete skill steps.")
        ids = [s["id"] for s in steps]
        if len(set(ids)) != len(ids):
            raise ValueError("Plan step IDs must be unique.")
        existing = {s["id"]: s for s in self.data["steps"]}
        result = []
        for step in steps:
            sid, pid = step["skill_id"], step["person_id"]
            if sid not in catalog:
                raise ValueError("Unknown or unassigned skill: " + sid)
            if selected != "atlas" and pid != selected:
                raise PermissionError("Only Atlas can delegate to another colleague.")
            if pid != "atlas" and (pid not in people or sid not in people[pid].get("skills", [])):
                raise ValueError("The selected colleague is not qualified for " + sid)
            if pid != "atlas" and not people[pid].get("available", True):
                raise ValueError("The selected colleague is unavailable.")
            if any(dep not in ids or dep == step["id"] for dep in step["depends_on"]):
                raise ValueError("Dependencies must reference other steps in this plan.")
            prior = existing.get(step["id"])
            if prior and prior.get("run_id"):
                if any(step[k] != prior[k] for k in ("skill_id", "person_id", "depends_on")):
                    raise ValueError("Recorded steps cannot be rewritten.")
                result.append(prior)
            else:
                result.append({**step, "status": "planned"})
        if any(s.get("run_id") and s["id"] not in ids for s in existing.values()):
            raise ValueError("Recorded steps cannot be removed.")
        visiting, visited = set(), set()
        graph = {s["id"]: s["depends_on"] for s in result}
        def visit(key):
            if key in visiting:
                raise ValueError("Plan dependencies cannot contain a cycle.")
            if key in visited:
                return
            visiting.add(key)
            for dep in graph[key]:
                visit(dep)
            visiting.remove(key)
            visited.add(key)
        for key in graph:
            visit(key)
        self.data["steps"] = result
        self.emit()
        return {"steps": result}

    def step_for(self, args):
        key = args.get("step_id")
        steps = self.data["steps"]
        if not key:
            if steps:
                raise ValueError("Use the matching plan step_id for this skill run.")
            return None
        step = next((s for s in steps if s["id"] == key), None)
        if not step or step["skill_id"] != args["skill_id"] or step["person_id"] != args["person_id"]:
            raise ValueError("The skill and assignee must match the plan step.")
        if step.get("run_id"):
            raise ValueError("This step already has a recorded run; inspect its result rather than duplicating it.")
        blocked = [s for s in steps if s["id"] in step["depends_on"] and s["status"] != "completed"]
        if blocked:
            step["status"] = "blocked"
            raise ValueError("Prerequisites are not completed: " + ", ".join(s["id"] for s in blocked))
        return step

    def record(self, result, step):
        self.runs.append(result)
        self.data["run_ids"] = list(dict.fromkeys(r["id"] for r in self.runs))
        if step is not None:
            step.update(status=result["status"], run_id=result["id"])
        stats = self.data["statistics"]
        stats["skills_completed"] = sum(r["status"] == "completed" for r in self.runs)
        stats["skills_pending"] = sum(r["status"] == "awaiting_approval" for r in self.runs)
        stats["skills_failed"] = sum(r["status"] in ("failed", "needs_attention") for r in self.runs)
        executed = [r for r in self.runs if r["status"] != "awaiting_approval"]
        stats["skills_executed"] = len(executed)
        stats["distinct_skills"] = len({r["skill_id"] for r in executed})
        stats["delegated_people"] = len({r["person_id"] for r in executed if r.get("person_id") != "atlas"})
        self.data["artifact_ids"] = list(dict.fromkeys(a["id"] for r in self.runs for a in (r.get("output") or {}).get("artifacts", []) if a.get("id")))
        stats["artifacts"] = len(self.data["artifact_ids"])
        self.emit()

    def finish(self, status=None):
        steps = self.data["steps"]
        if status is None:
            if any(r["status"] == "awaiting_approval" for r in self.runs):
                status = "awaiting_approval"
            elif any(s["status"] != "completed" for s in steps) or any(r["status"] != "completed" for r in self.runs) or (not self.runs and any(c['status']=='failed' for c in self.data['calls'])):
                status = "needs_attention"
            else:
                status = "completed"
        if status != "completed":
            for step in steps:
                if step["status"] in ("planned", "running"):
                    step["status"] = "blocked"
        self.data.update(status=status, finished_at=now())
        self.emit()
        return copy.deepcopy(self.data)
