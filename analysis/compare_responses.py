import csv

def load_evaluations(file_path):
    evaluations = []
    with open(file_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                evaluations.append({
                    "model": row["model"],
                    "accuracy": float(row["accuracy"]),
                    "reasoning": float(row["reasoning"]),
                    "clarity": float(row["clarity"]),
                    "completeness": float(row["completeness"]),
                    "hallucination": float(row["hallucination"])
                })
            except:
                pass
    return evaluations


def compute_scores(evaluations):
    scores = {}

    for e in evaluations:
        model = e["model"]
        total = (
            e["accuracy"]
            + e["reasoning"]
            + e["clarity"]
            + e["completeness"]
            - e["hallucination"]  # penalize hallucination
        )

        if model not in scores:
            scores[model] = []

        scores[model].append(total)

    avg_scores = {
        model: sum(vals) / len(vals)
        for model, vals in scores.items()
    }

    return avg_scores


def main():
    file_path = "../evaluations/evaluation_template.csv"
    evaluations = load_evaluations(file_path)
    scores = compute_scores(evaluations)

    print("Average Model Scores:\n")
    for model, score in scores.items():
        print(f"{model}: {round(score, 2)}")


if __name__ == "__main__":
    main()
    