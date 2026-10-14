from datetime import date

from app.core import config


def score(passed, total):
    if not total:
        return "not run"
    return f"{passed} / {total} ({passed / total:.0%})"


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", "<br>")


def yes_no(value):
    if value is None:
        return "-"
    return "yes" if value else "**no**"


def retrieval_cell(retrieval):
    if retrieval is None:
        return "-"
    hit, reciprocal_rank = retrieval
    if not hit:
        return "**miss**"
    return f"rank {round(1 / reciprocal_rank)}"


def write_report(rows, s, path, judge_model):
    mrr = f"{s['mrr']:.2f}" if s["mrr"] is not None else "-"
    avg, median, slowest = s["latency"]

    lines = [
        "# Evaluation report",
        "",
        f"{date.today()} | assistant `{config.CHAT_MODEL}` | judge `{judge_model}` | {s['total']} questions",
        "",
        "## Summary",
        "",
        "| Metric | Result |",
        "|---|---|",
        f"| **Accuracy** (every check passes) | **{score(s['passed'], s['total'])}** |",
        f"| Route correct | {score(*s['by_check']['route'])} |",
        f"| Required facts present | {score(*s['by_check']['facts'])} |",
        f"| Forbidden content absent | {score(*s['by_check']['forbidden'])} |",
        f"| Correct sources cited | {score(*s['by_check']['sources'])} |",
        f"| Retrieval hit rate | {score(*s['retrieval_hits'])} |",
        f"| Retrieval MRR | {mrr} |",
        f"| Faithfulness (LLM judge) | {score(*s['faithful'])} |",
        f"| Answer time (avg / median / max) | {avg:.1f}s / {median:.1f}s / {slowest:.1f}s |",
        f"| Tokens (in / out) | {s['input_tokens']:,} / {s['output_tokens']:,} |",
        f"| Cost (assistant + judge) | ${s['cost']:.4f} + ${s['judge_cost']:.4f} |",
        "",
        "## By question type",
        "",
        "| Type | Passed |",
        "|---|---|",
    ]
    for category, (passed, total) in s["by_category"].items():
        lines.append(f"| {category} | {score(passed, total)} |")

    lines += [
        "",
        "## What the metrics mean",
        "",
        "- **Accuracy**: a question passes only if all its checks pass.",
        "- **Route correct**: the assistant used documents, data or refused, as expected.",
        "- **Required facts present**: the exact figures and key facts are in the answer (e.g. `33,34,200`).",
        "- **Forbidden content absent**: no old limits, other companies' figures or leaked numbers.",
        "- **Correct sources cited**: the answer names the right document, and cites nothing when it has no answer.",
        "- **Retrieval hit rate**: for questions that expect a document, it was among the retrieved chunks (top 4 per search).",
        "- **Retrieval MRR**: mean of 1 / position of the first expected document in the retrieved list (1.0 = always first).",
        "- **Faithfulness**: a second model checks that every fact in the answer is backed by what the tools returned. "
        "Questions refused before the LLM are not judged.",
        "",
        "## Questions",
        "",
        "| # | User | Type | Question | Expected | Answer | Route | Sources | Retrieval | Faithful | Time | Result |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        case, result = row["case"], row["result"]
        failed = [message for _, ok, message in row["checks"] if not ok]
        status = "PASS" if row["passed"] else "FAIL: " + "; ".join(failed)
        faithful = yes_no(row["faithful"])
        if row["faithful"] is False:
            faithful += f" ({row['judge_reason']})"
        lines.append(
            f"| {case['id']} | {case['user_id']} | {case['category']} | {cell(case['question'])} | "
            f"{cell(case['expected_answer'])} | {cell(result['answer'])} | {result['route']} | "
            f"{cell(', '.join(result['sources']))} | {retrieval_cell(row['retrieval'])} | {cell(faithful)} | "
            f"{row['seconds']:.1f}s | {cell(status)} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
