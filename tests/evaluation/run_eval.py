"""Runs questions.json through the assistant and writes report.md.

    python -m tests.evaluation.run_eval
    python -m tests.evaluation.run_eval --ids 1,2,3
    python -m tests.evaluation.run_eval --no-judge     # skip the faithfulness check
"""
import argparse
import json
import time
from pathlib import Path

from app.services.assistant import ask
from tests.evaluation.judge import JUDGE_MODEL, get_judge, judge_answer
from tests.evaluation.metrics import retrieval_scores, run_checks, summarize
from tests.evaluation.report import score, write_report

HERE = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", help="comma separated question ids")
    parser.add_argument("--no-judge", action="store_true", help="skip the LLM faithfulness check")
    args = parser.parse_args()

    cases = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    if args.ids:
        ids = {int(i) for i in args.ids.split(",")}
        cases = [c for c in cases if c["id"] in ids]

    judge = None if args.no_judge else get_judge()
    rows = []

    for case in cases:
        start = time.time()
        result = ask(case["user_id"], case["question"])
        seconds = time.time() - start

        checks = run_checks(case, result)
        passed = all(ok for _, ok, _ in checks)

        faithful, reason, judge_cost = None, "", 0.0
        if judge:
            faithful, reason, judge_cost = judge_answer(
                judge, case["question"], result["answer"], result.get("context", []))

        rows.append({
            "case": case,
            "result": result,
            "checks": checks,
            "passed": passed,
            "retrieval": retrieval_scores(case, result),
            "faithful": faithful,
            "judge_reason": reason,
            "judge_cost": judge_cost,
            "seconds": seconds,
        })

        mark = {True: "faithful", False: "NOT FAITHFUL", None: "-"}[faithful]
        print(f"[{'PASS' if passed else 'FAIL'}] {case['id']:>2} {case['user_id']} {case['question']}  ({mark})")
        for _, ok, message in checks:
            if not ok:
                print(f"        {message}")
        if faithful is False:
            print(f"        judge: {reason}")

    s = summarize(rows)
    print()
    print(f"Accuracy:          {score(s['passed'], s['total'])}")
    print(f"Retrieval hits:    {score(*s['retrieval_hits'])}, MRR {s['mrr']:.2f}" if s["mrr"] is not None
          else "Retrieval hits:    -")
    print(f"Faithfulness:      {score(*s['faithful'])}")
    print(f"Cost:              ${s['cost']:.4f} assistant + ${s['judge_cost']:.4f} judge")

    write_report(rows, s, HERE / "report.md", JUDGE_MODEL if judge else "not run")
    print("Report written to", HERE / "report.md")


if __name__ == "__main__":
    main()
