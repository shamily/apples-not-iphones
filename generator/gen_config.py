"""
Generates testset_config_v2.csv: a 500-evals benchmark matrix.

500 tests across 5 tasks of 100 evaluations each:
  Task 1 (1-100):   sizes 1-25    — warm-up groups of increasing difficulty
  Task 2 (101-200): sizes 26-75   — 2 tests/size, distraction levels 1→10 per batch
  Task 3 (201-300): sizes 76-175  — 1 test/size, growing multi-target complexity
  Task 4 (301-400): sizes 176-275 — 1 test/size, mostly 3-target with 2+ word items
  Task 5 (401-500): sizes 276-375 — 1 test/size, all multi-target, max distractors
"""

import sys
import csv
import os

OUTPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "generator/config/eval_config.csv"

FIELDNAMES = [
    "test_id",
    "num_statements",
    "allow_negative",
    "distractor_ratio",
    "abstract_ratio",
    "word_number_ratio",
    "multi_digit_ratio",
    "target_max_length",
    "target_min_length",
    "num_targets",
    "statements_grouping_max",
]

# Distraction level 0-10 → (distractor_ratio, abstract_ratio, word_number_ratio, multi_digit_ratio)
DIST = {
    0: (0.0, 0.0, 0.0, 0.0),
    1: (0.1, 0.0, 0.0, 0.0),
    2: (0.2, 0.1, 0.2, 0.0),
    3: (0.3, 0.2, 0.3, 0.0),
    4: (0.4, 0.3, 0.4, 0.1),
    5: (0.5, 0.3, 0.5, 0.2),
    6: (0.6, 0.4, 0.5, 0.3),
    7: (0.7, 0.5, 0.6, 0.4),
    8: (0.8, 0.6, 0.7, 0.5),
    9: (0.9, 0.7, 0.8, 0.6),
    10: (1.0, 0.8, 0.9, 0.7),
}


def make_row(
    tid,
    num_statements,
    allow_negative,
    dist_level,
    target_max_length=2,
    target_min_length=1,
    num_targets=1,
    statements_grouping_max=1,
    wnr_override=None,
    mdr_override=None,
):
    dr, ar, wnr, mdr = DIST[dist_level]
    if wnr_override is not None:
        wnr = wnr_override
    if mdr_override is not None:
        mdr = mdr_override
    return {
        "test_id": tid,
        "num_statements": num_statements,
        "allow_negative": allow_negative,
        "distractor_ratio": round(dr, 1),
        "abstract_ratio": round(ar, 1),
        "word_number_ratio": round(wnr, 1),
        "multi_digit_ratio": round(mdr, 1),
        "target_max_length": target_max_length,
        "target_min_length": target_min_length,
        "num_targets": num_targets,
        "statements_grouping_max": statements_grouping_max,
    }


rows = []
tid = 1

# ─────────────────────────────────────────────────────────────
# TASK 1 (tests 1-100): sizes 1-25
# ─────────────────────────────────────────────────────────────

# GROUP 1.1 (20 tests): sizes 1-5, 4 tests per size
# Simplest: no negatives, minimal/no distractors, single target
# grouping_max: 1,1,1,2 — last test in each bucket introduces grouping
for size in range(1, 6):
    rows.append(
        make_row(
            tid,
            size,
            "False",
            0,
            target_max_length=1,
            num_targets=1,
            statements_grouping_max=1,
        )
    )
    tid += 1
    rows.append(
        make_row(
            tid,
            size,
            "False",
            0,
            target_max_length=2,
            num_targets=1,
            statements_grouping_max=1,
        )
    )
    tid += 1
    rows.append(
        make_row(
            tid,
            size,
            "False",
            1,
            target_max_length=1,
            num_targets=1,
            statements_grouping_max=1,
            wnr_override=0.3,
        )
    )
    tid += 1
    rows.append(
        make_row(
            tid,
            size,
            "False",
            1,
            target_max_length=2,
            num_targets=1,
            statements_grouping_max=2,
            wnr_override=0.3,
        )
    )
    tid += 1

# GROUP 1.2 (40 tests): sizes 6-15, 4 tests per size
# t1: positive-only with distractors; t2-t3: mixed pos+neg; t3: mixed number forms; t4: double target
# grouping_max: 1,1,2,2
for size in range(6, 16):
    rows.append(
        make_row(
            tid,
            size,
            "False",
            3,
            target_max_length=1,
            num_targets=1,
            statements_grouping_max=1,
        )
    )
    tid += 1
    rows.append(
        make_row(
            tid,
            size,
            "True",
            3,
            target_max_length=1,
            num_targets=1,
            statements_grouping_max=1,
        )
    )
    tid += 1
    rows.append(
        make_row(
            tid,
            size,
            "True",
            3,
            target_max_length=2,
            num_targets=1,
            statements_grouping_max=2,
            wnr_override=0.5,
            mdr_override=0.2,
        )
    )
    tid += 1
    rows.append(
        make_row(
            tid,
            size,
            "True",
            3,
            target_max_length=2,
            num_targets=2,
            statements_grouping_max=2,
        )
    )
    tid += 1

# GROUP 1.3 (40 tests): sizes 16-25, 4 tests per size
# Same structure as 1.2 but with more distractors (level 5 vs 3)
# grouping_max: 1,2,2,3
for size in range(16, 26):
    rows.append(
        make_row(
            tid,
            size,
            "False",
            5,
            target_max_length=1,
            num_targets=1,
            statements_grouping_max=1,
        )
    )
    tid += 1
    rows.append(
        make_row(
            tid,
            size,
            "True",
            5,
            target_max_length=1,
            num_targets=1,
            statements_grouping_max=2,
        )
    )
    tid += 1
    rows.append(
        make_row(
            tid,
            size,
            "True",
            5,
            target_max_length=2,
            num_targets=1,
            statements_grouping_max=2,
            wnr_override=0.6,
            mdr_override=0.3,
        )
    )
    tid += 1
    rows.append(
        make_row(
            tid,
            size,
            "True",
            5,
            target_max_length=2,
            num_targets=2,
            statements_grouping_max=3,
        )
    )
    tid += 1

# ─────────────────────────────────────────────────────────────
# TASK 2 (tests 101-200): sizes 26-75, 2 per size, batches of 10
#
# Batch layout: [s,s, s+1,s+1, s+2,s+2, s+3,s+3, s+4,s+4]
#   pos 1-5:  single target, distraction levels 1→5; pos 1 = allow_neg=False
#   pos 6-10: multi target (2), distraction levels 6→10
# ─────────────────────────────────────────────────────────────
for batch in range(10):
    base_size = 26 + batch * 5
    batch_sizes = []
    for i in range(5):
        batch_sizes += [base_size + i, base_size + i]  # 2 per size

    # grouping_max per position: 1,1,2,2,3 | 2,2,3,3,4
    SGM_T2 = [1, 1, 2, 2, 3, 2, 2, 3, 3, 4]
    for pos in range(10):
        size = batch_sizes[pos]
        sgm = SGM_T2[pos]
        if pos < 5:
            level = pos + 1  # 1-5
            neg = "False" if pos == 0 else "True"
            rows.append(
                make_row(
                    tid,
                    size,
                    neg,
                    level,
                    target_max_length=1,
                    num_targets=1,
                    statements_grouping_max=sgm,
                )
            )
            tid += 1
        else:
            level = pos + 1  # 6-10
            rows.append(
                make_row(
                    tid,
                    size,
                    "True",
                    level,
                    target_max_length=2,
                    num_targets=2,
                    statements_grouping_max=sgm,
                )
            )
            tid += 1

# ─────────────────────────────────────────────────────────────
# TASK 3 (tests 201-300): sizes 76-175, 1 per size, batches of 10
#
# Batch layout:
#   pos 1-3:  single target
#   pos 4-7:  2 targets
#   pos 8-10: 3 targets, all items must be 2+ words (target_min_length=2)
# Distraction level grows from 5 (first batch) to 10 (last batch)
# ─────────────────────────────────────────────────────────────
# grouping_max per position: 2,2,2,3,3,3,3,4,4,4
SGM_T3 = [2, 2, 2, 3, 3, 3, 3, 4, 4, 4]
size = 76
for batch in range(10):
    level = min(5 + batch, 10)
    for pos in range(1, 11):
        neg = "False" if pos == 1 else "True"
        sgm = SGM_T3[pos - 1]
        if pos <= 3:
            nt, tml, tminl = 1, 2, 1
        elif pos <= 7:
            nt, tml, tminl = 2, 2, 1
        else:  # pos 8-10
            nt, tml, tminl = 3, 2, 2
        rows.append(
            make_row(
                tid,
                size,
                neg,
                level,
                target_max_length=tml,
                target_min_length=tminl,
                num_targets=nt,
                statements_grouping_max=sgm,
            )
        )
        tid += 1
        size += 1

# ─────────────────────────────────────────────────────────────
# TASK 4 (tests 301-400): sizes 176-275, 1 per size, batches of 10
#
# Batch layout:
#   pos 1:    single target
#   pos 2-5:  2 targets
#   pos 6-10: 3 targets, all items must be 2+ words (target_min_length=2)
# Distraction: high throughout (levels 7-10)
# ─────────────────────────────────────────────────────────────
# grouping_max per position: 2,3,3,3,3,4,4,4,4,4
SGM_T4 = [2, 3, 3, 3, 3, 4, 4, 4, 4, 4]
size = 176
for batch in range(10):
    level = min(7 + batch // 3, 10)  # 7,7,7,8,8,8,9,9,10,10
    for pos in range(1, 11):
        neg = "False" if pos == 1 and batch == 0 else "True"
        sgm = SGM_T4[pos - 1]
        if pos == 1:
            nt, tml, tminl = 1, 2, 1
        elif pos <= 5:
            nt, tml, tminl = 2, 2, 1
        else:  # pos 6-10
            nt, tml, tminl = 3, 2, 2
        rows.append(
            make_row(
                tid,
                size,
                neg,
                level,
                target_max_length=tml,
                target_min_length=tminl,
                num_targets=nt,
                statements_grouping_max=sgm,
            )
        )
        tid += 1
        size += 1

# ─────────────────────────────────────────────────────────────
# TASK 5 (tests 401-500): sizes 276-375, 1 per size, batches of 10
#
# Batch layout:
#   pos 1-3:  2 targets, moderate distraction (level 5)
#   pos 4-5:  3 targets (min 2 words), moderate distraction (level 5)
#   pos 6-10: 3 targets (min 2 words), maximum distraction (level 10)
# ─────────────────────────────────────────────────────────────
# grouping_max per position: 3,3,3,4,4,5,5,5,5,5
SGM_T5 = [3, 3, 3, 4, 4, 5, 5, 5, 5, 5]
size = 276
for batch in range(10):
    for pos in range(1, 11):
        sgm = SGM_T5[pos - 1]
        if pos <= 3:
            nt, tml, tminl, level = 2, 2, 1, 5
        elif pos <= 5:
            nt, tml, tminl, level = 3, 2, 2, 5
        else:  # pos 6-10
            nt, tml, tminl, level = 3, 2, 2, 10
        rows.append(
            make_row(
                tid,
                size,
                "True",
                level,
                target_max_length=tml,
                target_min_length=tminl,
                num_targets=nt,
                statements_grouping_max=sgm,
            )
        )
        tid += 1
        size += 1

# ─────────────────────────────────────────────────────────────
# Write output
# ─────────────────────────────────────────────────────────────
assert len(rows) == 500, f"Expected 500 rows, got {len(rows)}"

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} tests → {OUTPUT_PATH}")

# Quick sanity check
task_counts = [0] * 5
for r in rows:
    t = int(r["test_id"])
    if t <= 100:
        task_counts[0] += 1
    elif t <= 200:
        task_counts[1] += 1
    elif t <= 300:
        task_counts[2] += 1
    elif t <= 400:
        task_counts[3] += 1
    else:
        task_counts[4] += 1
for i, c in enumerate(task_counts, 1):
    print(f"  Task {i}: {c} tests")
