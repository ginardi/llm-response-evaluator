import csv
from collections import defaultdict
from pathlib import Path

CRITERIA = ["accuracy", "reasoning", "clarity", "completeness", "hallucination"]

def load_evaluations(file_path):
    evaluations = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                item = {
                    "id": row["id"],
                    "prompt_id": row["prompt_id"],
                    "model": row["model"],
                    "accuracy": float(row["accuracy"]),
                    "reasoning": float(row["reasoning"]),
                    "clarity": float(row["clarity"]),
                    "completeness": float(row["completeness"]),
                    "hallucination": float(row["hallucination"]),
                    "notes": row.get("notes", "")
                }
                item["total_score"] = (
                    item["accuracy"]
                    + item["reasoning"]
                    + item["clarity"]
                    + item["completeness"]
                    - item["hallucination"]
                )
                evaluations.append(item)
            except:
                continue
    return evaluations

def compute_model_averages(evaluations):
    model_scores = defaultdict(lambda: defaultdict(list))

    for e in evaluations:
        model = e["model"]
        for c in CRITERIA:
            model_scores[model][c].append(e[c])
        model_scores[model]["total_score"].append(e["total_score"])

    averages = {}
    for model, metrics in model_scores.items():
        averages[model] = {
            metric: round(sum(values) / len(values), 2)
            for metric, values in metrics.items()
        }
    return averages

def compute_prompt_winners(evaluations):
    by_prompt = defaultdict(dict)

    for e in evaluations:
        by_prompt[e["prompt_id"]][e["model"]] = e

    results = []
    wins = {"LLM_A": 0, "LLM_B": 0, "Tie": 0}

    for prompt_id, models in sorted(by_prompt.items(), key=lambda x: int(x[0])):
        a = models.get("LLM_A")
        b = models.get("LLM_B")

        if not a or not b:
            continue

        a_score = a["total_score"]
        b_score = b["total_score"]

        if a_score > b_score:
            winner = "LLM_A"
            wins["LLM_A"] += 1
        elif b_score > a_score:
            winner = "LLM_B"
            wins["LLM_B"] += 1
        else:
            winner = "Tie"
            wins["Tie"] += 1

        results.append({
            "prompt_id": prompt_id,
            "LLM_A_score": a_score,
            "LLM_B_score": b_score,
            "winner": winner
        })

    return results, wins

def generate_report(report_path, averages, prompt_results, wins):
    best_model = max(averages, key=lambda m: averages[m]["total_score"])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LLM Evaluation Report\n\n")

        f.write("## Overall Results\n\n")
        f.write(f"- **LLM_A average total score:** {averages['LLM_A']['total_score']}\n")
        f.write(f"- **LLM_B average total score:** {averages['LLM_B']['total_score']}\n")
        f.write(f"- **Prompt wins — LLM_A:** {wins['LLM_A']}\n")
        f.write(f"- **Prompt wins — LLM_B:** {wins['LLM_B']}\n")
        f.write(f"- **Ties:** {wins['Tie']}\n")
        f.write(f"- **Best overall model:** {best_model}\n\n")

        f.write("## Per-Criterion Averages\n\n")
        f.write("| Criterion | LLM_A | LLM_B |\n")
        f.write("|---|---:|---:|\n")
        for c in CRITERIA:
            f.write(f"| {c} | {averages['LLM_A'][c]} | {averages['LLM_B'][c]} |\n")
        f.write("\n")

        f.write("## Prompt-Level Winners\n\n")
        f.write("| Prompt ID | LLM_A Score | LLM_B Score | Winner |\n")
        f.write("|---|---:|---:|---|\n")
        for row in prompt_results:
            f.write(f"| {row['prompt_id']} | {row['LLM_A_score']} | {row['LLM_B_score']} | {row['winner']} |\n")
        f.write("\n")

        f.write("## Final Takeaways\n\n")
        f.write(f"- {best_model} achieved the strongest average performance across the evaluation set.\n")
        f.write("- The analysis combines aggregate scoring with prompt-level pairwise comparison.\n")
        f.write("- Hallucination is treated as a penalty in the final scoring logic.\n")

def main():
    base = Path(__file__).resolve().parent.parent
    data_file = base / "evaluations" / "evaluation_template.csv"
    reports_dir = base / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / "evaluation_report.md"

    evaluations = load_evaluations(data_file)
    averages = compute_model_averages(evaluations)
    prompt_results, wins = compute_prompt_winners(evaluations)
    generate_report(report_path, averages, prompt_results, wins)

    print("\n=== MODEL TOTAL SCORES ===")
    for model in sorted(averages):
        print(f"{model}: {averages[model]['total_score']}")

    print("\n=== PER-CRITERION AVERAGES ===")
    for model in sorted(averages):
        print(f"\n{model}")
        for c in CRITERIA:
            print(f"- {c}: {averages[model][c]}")

    print("\n=== PROMPT WINS ===")
    print(wins)

    print(f"\nReport created at: {report_path}")

if __name__ == "__main__":
    main()
