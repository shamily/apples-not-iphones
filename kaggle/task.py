import os
import re
import pandas as pd
import kaggle_benchmarks as kbench

os.environ["RENDER_SUBRUNS"] = "False"

# ================================================================================
# 1. LOAD THE DATASET
# ================================================================================

DATASET_PATH = "/kaggle/input/datasets/thegrey/agi-apple-benchmark-dataset-v2/benchmark_dataset_v2.csv"

# HERE YOU SHOULD SELECT THE SUBSET OF EVALS per TASK:
# Task 1: [0:100]
# Task 2: [100:200]
# Task 3: [200:300]
# Task 4: [300:400]
# Task 5: [400:500]

df = pd.read_csv(DATASET_PATH) #[0:100]

# Use the pre-rendered prompts and exact ground truth answers
eval_df = df[["prompt", "ground_truth_answer"]].reset_index(drop=True).copy()
eval_df["ground_truth_answer"] = eval_df["ground_truth_answer"].astype(int)

print(f"Task: Full AGI Attention Benchmark — {len(eval_df)} examples")

# ================================================================================
# 2. SINGLE-ROW SUB-TASK
# ================================================================================

@kbench.task(store_task=False)
def evaluate_single_story(llm, prompt: str, ground_truth_answer: int) -> dict:
    """Prompt the LLM with the pre-rendered robust string and evaluate."""
    
    predicted = None
    format_clean = False
    raw_response = ""

    try:
        response = llm.prompt(prompt)
        full_text = str(response).strip() if response else ""
        
        # Optimize regex by slicing only the final 500 characters of massive reasoning chains
        tail_text = full_text[-500:] if len(full_text) > 500 else full_text
        digits = re.findall(r'-?\d+', tail_text)
        
        if digits:
            predicted = int(digits[-1])
            # Check if it was tightly formatted
            format_clean = len(full_text) <= 15
        else:
            format_clean = False
            
        raw_response = full_text  # Log entire reasoning chain intact for diagnostic review
            
    except Exception:
        # API/Timeout failure — treat as wrong answer, don't crash
        pass

    is_correct = (predicted == ground_truth_answer)
    score = 1.0 if is_correct else 0.0

    return {
        "correct_answer": ground_truth_answer,
        "predicted_answer": predicted,
        "raw_response": raw_response,
        "is_correct": is_correct,
        "format_clean": format_clean,
        "score": score,
    }

# ================================================================================
# 3. MAIN TASK
# ================================================================================

TASK_NAME = "agi_attention_diagnostic_v2_task4"

@kbench.task(
    name=TASK_NAME,
    description=(
        f"AGI Attention Diagnostic Benchmark v2 | "
        f"({len(eval_df)} strict logic examples). "
        f"Deterministic, dynamic scaling multi-target bounds logic."
    ),
)
def agi_attention_benchmark_task(llm) -> tuple[float, float]:
    with kbench.client.enable_cache():
        runs = evaluate_single_story.evaluate(
            stop_condition=lambda runs: len(runs) == eval_df.shape[0],
            max_attempts=1,
            llm=[llm],
            evaluation_data=eval_df,
            n_jobs=2,  # Adjust locally if allowed
            timeout=1200,
            remove_run_files=True,
        )
    results_df = runs.as_dataframe()
    accuracy = float(results_df.result.str.get("score").mean())
    std = float(results_df.result.str.get("score").std())

    # Track format compliance as diagnostic
    format_rate = float(results_df.result.str.get("format_clean").mean())

    kbench.assertions.assert_true(
        0.0 <= accuracy <= 1.0,
        expectation=f"Accuracy ({accuracy:.1%}) must be between 0% and 100%."
    )
    kbench.assertions.assert_true(
        True,
        expectation=f"Format compliance: {format_rate:.0%} of models followed strict integer response formats."
    )
    return accuracy, std

# ================================================================================
# 4. RUN
# ================================================================================

run = agi_attention_benchmark_task.run(kbench.llm)

# ================================================================================
# 5. SELECT THIS TASK FOR THE LEADERBOARD
# ================================================================================

# %choose agi_attention_benchmark_task