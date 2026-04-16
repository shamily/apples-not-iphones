import json
import csv
import sys
from AttentionTestGenerator import AttentionTestGenerator

def load_json(filename):
    import os
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, f"input/{filename}"), 'r') as f:
        return json.load(f)

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "generator/config/eval_config.csv"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "dataset/dataset.csv"

    print("Loading JSON deterministic architectures...")
    items = load_json("items.json")
    gain_loss = load_json("gain_loss.json")
    actors = load_json("actors.json")
    abstract = load_json("abstract.json")
    numbers = load_json("numbers.json")
    prompts = load_json("prompt_templates.json")

    generator = AttentionTestGenerator(items, gain_loss, actors, abstract, numbers, prompts)

    print(f"Reading CSV config matrix from {config_file}...")
    with open(config_file, 'r') as f:
        reader = csv.DictReader(f)
        configs = list(reader)

    print(f"Initiating Generation of {len(configs)} tests...")

    with open(output_file, 'w', newline='', encoding='utf-8') as out_f:
        fieldnames = [
            "test_id", "prompt", "ground_truth_answer", "target_words", "story",
            "num_statements", "allow_negative", "distractor_ratio",
            "abstract_ratio", "word_number_ratio", "multi_digit_ratio",
            "target_max_length", "target_min_length", "num_targets",
            "statements_grouping_max",
        ]
        writer = csv.DictWriter(out_f, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()

        for row in configs:
            seed = 42 + int(row["test_id"])
            test_data = generator.generate(row, seed=seed)

            csv_row = {
                "test_id":                 row["test_id"],
                "prompt":                  test_data["prompt"],
                "ground_truth_answer":     test_data["ground_truth_answer"],
                "target_words":            ", ".join(test_data["target_words"]),
                "story":                   test_data["story"],
                "num_statements":          row["num_statements"],
                "allow_negative":          row["allow_negative"],
                "distractor_ratio":        row["distractor_ratio"],
                "abstract_ratio":          row["abstract_ratio"],
                "word_number_ratio":       row["word_number_ratio"],
                "multi_digit_ratio":       row["multi_digit_ratio"],
                "target_max_length":       row["target_max_length"],
                "target_min_length":       row.get("target_min_length", 1),
                "num_targets":             row["num_targets"],
                "statements_grouping_max": row.get("statements_grouping_max", 1),
            }
            writer.writerow(csv_row)

    print(f"\n[SUCCESS] Generated dataset with {len(configs)} tests saved to {output_file}!")

if __name__ == "__main__":
    main()
