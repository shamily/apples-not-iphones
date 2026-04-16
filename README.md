# Apples, Not iPhones: AGI Attention Benchmark

[Kaggle Benchmark](https://www.kaggle.com/benchmarks/thegrey/agi-apple-benchmark/leaderboard)

### Problem Statement
Current leaderboards index heavily on complex reasoning, taking lower-level cognitive primitives for granted. However, the DeepMind Cognitive Framework highlights **Attention** as a foundational prerequisite for AGI. Without robust attention, high-level reasoning collapses over long contexts (an AI cannot solve physics if it forgets how many apples it just counted). 

To address this, I built a benchmark to evaluate the Attention faculty in isolation, measuring how architectures maintain focus, filter noise, and progress toward AGI.

### Task & benchmark construction
Models must calculate the final total of target items possessed by actors following a series of narrative operations. The system must maintain isolated mathematical counts for specific targets while actively suppressing semantic distractors. Regardless of the number of targets tracked, the model must merge totals via multiplication and uniformly output a single scalar integer.

#### Complexity levels
Basic complexity is defined by the number of statements in a test. The benchmark includes several distractors:
1. **Categorical Sibling Distractors** (tracking "apples" while ignoring "oranges").
2. **Lexical Overlap Distractors** (tracking "apples" while ignoring "Apple iPhones").
3. **Adjectival Constraints** (tracking "green apples" while ignoring "red apples").
4. **Abstract Interferences** (ignoring hypothetical statements like "Scientists believe 2 apples...").

I integrated structural complexity multipliers:
1. **Syntactic Density:** Embedding multiple, distinct statements within a single sentence frame.
2. **Parallel Target Tracking:** Requiring the model to focus on multiple distinct target items simultaneously and multiply them at the end.
3. **Alphanumeric Lexical Mixing:** Substituting digits ("2") with English words ("two") to prevent simple regex pattern matching.

#### Mapping the DeepMind Cognitive Framework
By burying target items deep within dense semantic noise, the benchmark forces the LLM to actively engage specific components of the DeepMind Attention faculty ([2, Section 7.3]):
* **Attention Capacity (7.3.1):** Evaluated by tracking multiple independent physical items simultaneously (scaling up to multiple targets).
* **Selective Attention (7.3.2):** This overarching control faculty is stress-tested across three metrics:
  * **Sustained Attention:** Measured by massively scaling narrative size (up to 375 statements) to define the boundary where focus collapses over time.
  * **Perceptual Inhibition:** Tested by injecting high-salience semantic distractors (e.g., "Apple iPhones" when tracking "apples") that the model must actively ignore.
  * **Attention Shifting:** Measured by dynamically swapping operational polarity (adding via "purchased" vs. subtracting via "ate"), forcing the model to continuously shift task logic.

#### Validation
The model must output a single integer. For models that fail to follow formatting instructions and generate explanations, I parse the final number from the output using a regex fallback.

### Dataset
The generated dataset contains 500 formatted evaluations, though the central Kaggle benchmark explicitly utilizes only the first 300. The underlying evaluations scale across five distinct tasks of increasing size, complexity, and distractor density (100 evaluations each).

| Task Level | Narrative Size | Empirical Characteristics |
| :--- | :--- | :--- |
| **Task 1** | 1 – 25 | Warm-up sequences scaling in baseline tracking difficulty |
| **Task 2** | 26 – 75 | 2 tests/size; distraction thresholds gradually scaling 1→10 |
| **Task 3** | 76 – 175 | 1 test/size; growing multi-target tracking requirements |
| **Task 4** | 176 – 275 | 1 test/size; primarily 3-target tracking with 2+ word items |
| **Task 5** | 276 – 375 | 1 test/size; absolute maximum multi-target distractor boundaries |

#### Building dataset
I generated the dataset programmatically for two reasons:
1. **Scale:** Measuring sustained attention requires long-context narratives tracking target items across hundreds of sentences. Doing this manually is impractical.
2. **Correctness:** Programmatic generation guarantees perfect mathematical tracking of target items, avoiding human arithmetic errors.

The generator uses structured JSON dictionaries containing predefined actors, items, and mathematical operators. It maps abstract templates to these data points to assemble the narratives deterministically. 

#### Dataset Schema 
The `.csv` utilizes the following columns:
- **`test_id`:** Sequence index.
- **`prompt`:** Monolithic input block pre-formatted for `kaggle_benchmarks`.
- **`ground_truth_answer`:** Baseline integer.
- **`target_words`:** Item(s) to track.
- **`story`:** Raw narrative.
- **`num_statements`:** Count of statements (size).
- **`allow_negative`:** Flag enabling item loss.
- **`distractor_ratio`, `abstract_ratio`, `word_number_ratio`, `multi_digit_ratio`:** Probability weights controlling distractor density, lexical mixing, and parallel tracking targets.
- **`target_max_length` / `target_min_length`:** Number of words in the target items.
- **`num_targets`:** Number of items to track.
- **`statements_grouping_max`:** Max number of statements grouped in a sentence.


#### Correctness & Validation
I implemented layers of validation:
1. **Templated Determinism:** Using strict templates populated by these JSON configurations ensures syntax and arithmetic are sound by design.
2. **Empirical Baseline:** High-end models (like Gemini 3.1 Pro) correctly solved >95% of the shortest sequences (Task 1). This confirms the dataset language is parseable and the logic is solvable.
3. **Manual Review:** Sequences where models reliably failed early underwent manual human review.
4. **Consensus Validation:** Every evaluation in Task 1 was correctly solved by at least 4 out of the top 10 models.

### Technical details 
* **Dataset Generation:** The data generation pipeline was written in Python and authored with the assistance of an AI coding agent.
* **Data Source:** The pre-generated `.csv` dataset is uploaded directly to Kaggle Datasets.
* **Benchmark Composition:** I created distinct Kaggle Tasks using the `kaggle_benchmarks` library, slicing the `.csv` into discrete 100-evaluation blocks. The first three tasks were then unified into a centralized Kaggle Benchmark and evaluated natively against 16 LLMs available on the platform.

### Results, insights, and conclusions
The benchmark consists of the three Primary Tasks (Tasks 1–3). Tasks 4 and 5 experienced exhausting maximum token allowance limits, when testing on all models. The table below lists accuracy scores (0.0 to 1.0) per model and task, as well as the overall average.

| Model | Task 1 | Task 2 | Task 3 | Overall (Tasks 1-3) |
| :--- | :--- | :--- | :--- | :--- |
| **gemini-3.1-pro-preview** | 0.99 | 0.89 | 0.95 | **0.9433** |
| **gemma-4-31b-it** | 0.90 | 0.66 | 0.54 | **0.7000** |
| **claude-opus-4-6-default** | 0.91 | 0.59 | 0.45 | **0.6500** |
| **gemma-4-26b-a4b-it** | 0.93 | 0.63 | 0.36 | **0.6400** |
| **gemini-2.5-flash** | 0.88 | 0.59 | 0.42 | **0.6300** |
| **glm-5** | 0.91 | 0.73 | 0.24 | **0.6267** |
| **qwen3-next-80b-a3b-thinking** | 0.91 | 0.57 | 0.36 | **0.6133** |
| **claude-sonnet-4-6-default** | 0.89 | 0.44 | 0.35 | **0.5600** |
| **qwen3-next-80b-a3b-instruct** | 0.77 | 0.54 | 0.19 | **0.5000** |
| **gpt-oss-20b** | 0.76 | 0.44 | 0.08 | **0.4267** |
| **gpt-oss-120b** | 0.74 | 0.41 | 0.11 | **0.4200** |
| **deepseek-v3.2** | 0.35 | 0.13 | 0.08 | **0.1867** |
| **gpt-5.4-2026-03-05** | 0.39 | 0.03 | 0.11 | **0.1767** |
| **gemini-3.1-flash-lite-preview** | 0.28 | 0.01 | 0.09 | **0.1267** |
| **gpt-5.4-mini-2026-03-17** | 0.19 | 0.00 | 0.04 | **0.0767** |
| **gpt-5.4-nano-2026-03-17** | 0.19 | 0.00 | 0.01 | **0.0667** |

#### Insight 1: The Four Cognitive Topologies of LLM Attention

In attachments I give different types of per-evaluation analysis. One of those is analysis
of the correlation between the boolean outputs and the parameters of the tests (e.g., `num_targets`, `allow_negative`). Here I put the parameters that affects the most the performance of each model, and 
determine which attention ability it maps to.

| Attention Ability | Model  | Primary Failure Vector | Correlation Severity |
| :--- | :--- | :--- | :--- |
| **Attention Shifting** | gpt-5.4-nano-2026-03-17 | `allow_negative` | $r = -0.467$ |
| **Attention Shifting** | gpt-5.4-mini-2026-03-17 | `allow_negative` | $r = -0.419$ |
| **Attention Shifting** | gemini-3.1-flash-lite-preview | `allow_negative` | $r = -0.410$ |
| **Attention Shifting** | gpt-5.4-2026-03-05 | `allow_negative` | $r = -0.380$ |
| **Perceptual Inhibition** | gpt-oss-20b | `distractor_ratio` | $r = -0.660$ |
| **Perceptual Inhibition** | gpt-oss-120b | `distractor_ratio` | $r = -0.623$ |
| **Perceptual Inhibition** | gemma-4-26b-a4b-it | `abstract_ratio` | $r = -0.593$ |
| **Sustained Attention** | glm-5 | `num_statements` | $r = -0.602$ |
| **Sustained Attention** | qwen3-next-80b-a3b-instruct | `num_statements` | $r = -0.446$ |
| **Sustained Attention** | deepseek-v3.2 | `num_statements` | $r = -0.270$ |
| **Attention Capacity** | gemini-2.5-flash | `num_targets` | $r = -0.590$ |
| **Attention Capacity** | gemma-4-31b-it | `num_targets` | $r = -0.533$ |
| **Attention Capacity** | claude-opus-4-6-default | `num_targets` | $r = -0.497$ |
| **Attention Capacity** | claude-sonnet-4-6-default | `num_targets` | $r = -0.464$ |
| **Attention Capacity** | qwen3-next-80b-a3b-thinking | `statements_group` | $r = -0.423$ |
| **Attention Capacity** | gemini-3.1-pro-preview | `target_max_len` | $r = -0.142$ |

Indeed, different models have different weak points. While there is one more improtant thing to 
say about **gemini-3.1-pro-preview**: having `target_max_len` as the parameter that affects the most 
its performance, it has positive correlation with `target_min_len` which makes me think, that the LLM struggles with _different_ length of target items (like "apples" vs "squared oranges").

Small models struggle with `allow_negative` - which is loss of items ("Anna ate an apple").

#### Insight 2: Task 4/5 Capability Scaling
While excluded from the primary aggregate, I retrieved scores for a few models on Task 4:
- **gemini-3.1-pro-preview:** 0.93
- **gemma-4-31b-it:** 0.22
- **glm-5:** 0.13
- **claude-opus-4-6-default:** 0.12

For Task 5:
- **gemini-3.1-pro-preview:** 0.86
- **gemini-3-flash-preview:** 0.34

`gemini-3.1-pro-preview` still shows excellent results even on the more complex task, while the others experience expected degradation. 

#### Insight 3: Task Correlation
Computing the Pearson correlation coefficient between the performance scores of all 16 benchmarked models provides structural stability metrics:
- **Task 1 vs 2:** 0.96
- **Task 2 vs 3:** 0.80
- **Task 1 vs 3:** 0.73

The 0.96 & 0.80 correlation between adjacent tasks confirms structural consistency.

#### Insight 4: Lexical Traps
The benchmark exposed model vulnerability to "attentional capture" via semantic overlap. For example, in Evaluation 38, models were instructed to exclusively track physical chips. However, the narrative injected: "Mila lost 1 poker chips at the casino." Several architectures failed to maintain boundary filtering and incorrectly subtracted the irrelevant poker chips, revealing attention layers are biased by localized token-matching.

#### Insight 5: Local Quantization
I evaluated some models locally via `llama.cpp` using `Q8_0` and `Q4_K_M` settings. Across the primary tests, `gemma-4-E2B-Q8_0` scored 0.31 overall, and `gemma-4-E4B-Q4_K_M` scored 0.40. `Qwen3.5-0.8B-Q8_0` correctly resolved 3.33% of evaluations. Because the earliest sequences in Task 1 are explicitly designed to be simple, the benchmark effectively acts as a graduated floor, capable of gifting non-zero scores even to heavily constrained sub-billion architectures. Notably, `Qwen3.5-35B-A3B-Q4_K_M` scored 0.4667, beating the 120B `gpt-oss` baseline.

#### Insight 6: MoE Overthinking Anomaly
I noted severe performance decay in the quantized Mixture of Experts variant `gemma-4-26B-A4B-Q4_K_M`. It achieved a final score of only 0.1433 because it repeatedly collapsed into an endless "overthinking" token loop. The exact technical cause was not fully isolated, though it is potentially the result of localized broken quantization parameters.

#### Insight 7: Discriminatory Power
Model performance spans a clear spectrum—starting at roughly 0.0333 score for ultra-tiny constraints (`Qwen3.5-0.8B`), scaling cleanly through the 40–70% mid-tier range (`gpt-oss-120b`, `gemma-4-31b-it`), up to 94.33% for `gemini-3.1-pro-preview`. This gradient indicates the benchmark successfully distinguishes working memory constraints across models.

#### Future Work
1. **Distractor Profiling:** Investigating what type of localized semantic structure (e.g., hypothetical statements, pluralization traps) causes the highest rate of attentional capture.
2. **Targeting the Upper Bound:** Analyze the exact boundaries where `gemini-3.1-pro-preview` collapses, moving beyond sheer context length to design specialized tests targeting its specific logic vulnerabilities.
3. **Attention Shifting (Dynamic Rules):** Implement mid-evaluation rule modifications (e.g., instructing the model that actors have stopped collecting "real apples" and exclusively started tracking "squared bananas") to explicitly stress-test DeepMind's "Attention Shifting" metric.
4. **Information Density vs. Length:** Design smaller but denser tests. Current benchmarking indicates that limiting evaluations to a maximum size of 150 is sufficient if the distractors and mathematical abstractions are highly concentrated.

### Organizational affiliations
N/A

### References & citations
1. Morris, M. R., et al. (2023). [Levels of AGI: Operationalizing Progress on the Path to AGI](https://arxiv.org/abs/2311.02462). *arXiv*.
2. Burnell, R., et al. (2026). [Measuring Progress Toward AGI: A Cognitive Framework](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf). Google DeepMind.