# Structured answers without guaranteed correctness: an exploratory study of Jev

**Personal experiment report.** Model: `jev-1.13.0`. Collection: September 17–18, 2026. These are historical observations, not claims about later model versions.

## Abstract

We examine a retrospectively selected set of structured-question experiments involving character counting, a 4×4 Sudoku, primality, Semgrep rule interpretation, family-role reasoning, and multilingual interpretation. Recorded answers include exact-computation errors, a globally inconsistent Sudoku, and a Semgrep error with reported confidence 0.92. Two identical primality requests returned different Noul values for 27 of 60 questions and different binary decisions for two. In the multilingual probe, Jev identified an explicit refund request in four languages but missed it in Guarani. The study examines answer accuracy, joint consistency, confidence, and repeatability.

## Methodology

Each experiment supplies an input and explicit questions to `jev-1.13.0` through `/v1/systemone`. Questions specify their answer type and, for Choice questions, the available alternatives. Related questions share the same input within a request, such as the 16 cells of a Sudoku or the roles in the family puzzle. Reference answers are kept outside the request and used only for evaluation.

The tasks evaluated here use **Choice**, **Noul**, and **Score**. Choice answers are evaluated by exact agreement between the returned `choice` and the reference label. Noul values are converted to binary decisions at `p >= 0.5`. Correctness and confidence are recorded separately: Choice uses the API's confidence field, while Noul's `max(p, 1-p)` is reported as **derived confidence**. These two measures are not assumed to be equivalent. In the multilingual experiment, Score measures anger on an ordered 0–2 scale; fractional values are compared across languages rather than graded by exact equality.

Evaluation covers answer accuracy, consistency across related answers, confidence on correct and incorrect answers, and repeatability. Sudoku cells are checked against the unique solution; family-role assignments are also inspected for contradictions. Repeatability is assessed by comparing the Noul values and binary decisions from two identical primality requests. Results are reported separately by task and run, rather than pooled into one accuracy score.

### Reference answers

- **Character counts:** case-insensitive local character counting; counts above five use an overflow category.
- **Sudoku:** exhaustive enumeration of valid 4×4 boards, filtered by the given clues. Exactly one board fits. Jev receives 16 Choice questions in one request, without the answer key.
- **Primality:** deterministic Miller–Rabin for unsigned 64-bit integers. Six groups contain ten numbers each, balanced between primes and non-primes. Larger examples use selected seeds and nearby composites, not random sampling.
- **Semgrep:** recorded Semgrep CE 1.176.1 execution on 80 independent snippets yields a 20-question key. Offline analysis reads that key; regenerating it requires Semgrep. This measures rule interpretation, not rule generation.
- **Family puzzle:** the intended reference assumes both parents are older than their children. That assumption is implicit in the API prompt. Results are separated from the unambiguous tasks.
- **Multilingual interpretation:** the working reference is an informal consensus on the message's explicit meaning: strong anger, a request for a refund, and a need for an answer today. The same three questions are applied to Chinese, Spanish, English, Basque, and Guarani versions. There is no external answer key or formal annotator study; this is an agreed interpretation used to compare responses across languages, not an independently measured ground truth. Anger scores are compared for consistency without assuming one exact fractional value is uniquely correct.

## Results

No pooled accuracy is reported: tasks differ, questions within requests are related, and repeats are not independent samples.

### Exact computation and global consistency

Character counting scored **11/18** initially. Examples include *strawberry* → 2 instead of 3, *blueberry* → 1 instead of 2 (confidence 0.87), and *error* → 1 instead of 3 (confidence 0.89). A later strawberry request returned 3 with confidence 0.38, compared with 0.43 on the earlier wrong answer.

The Sudoku scored **10/16 cells**, including all four clues: only **6/12 empty cells** were correct. The board was invalid. The input, unique solution, and returned choices were:

```text
Input (0 = blank)    Unique solution     Jev response
1 0 3 0             1 2 3 4             1 2 3 2
0 4 0 0             3 4 2 1             2 4 2 1
0 0 0 2             4 3 1 2             4 1 4 2
0 0 0 0             2 1 4 3             2 2 4 1
```

For example, the first row contains two 2s and no 4. The returned cells therefore fail the Sudoku constraints even without comparison to the reference solution.

Both primality runs scored **47/60**. Each group contains five primes and five non-primes:

| Group | Number size | First run | Second run |
|---|---|---:|---:|
| Basic | 0–30 | 10/10 | 10/10 |
| Small | 2–3 digits | 10/10 | 10/10 |
| Medium | 4–6 digits | 8/10 | 8/10 |
| Large | 7–9 digits | 8/10 | 7/10 |
| Very large | 10–12 digits | 6/10 | 7/10 |
| Huge | 15–18 digits | 5/10 | 5/10 |

### Repeatability

The second primality run had an identical saved request body and again scored **47/60**. However, **27/60 Noul values changed** and **2/60 classifications flipped** at 0.5. One answer became correct and another incorrect. Equal aggregate scores concealed answer-level variation.

### Confidence is not a correctness guarantee

The Semgrep exam scored **18/20**. On `q06`, expected snippets were B, C, D; Jev selected B, D with **confidence 0.92**. Accepting answers at confidence ≥0.90 would retain that error. Correct answers also had low confidence: 0.27 on `q01` and 0.45 on `q16`.

The relevant matching clauses for `q06` were:

```yaml
patterns:
  - pattern: send(...)
  - pattern-not: send(safe)
```

Each snippet was scanned in a separate Python file:

| Label | Snippet | Semgrep CE 1.176.1 finding |
|---|---|---|
| A | `send(safe)` | No |
| B | `send(unsafe)` | Yes |
| C | `send(safe, extra)` | Yes |
| D | `send()` | Yes |

The offered answers were `B, C, D`, `D`, `C`, and `B, D`. Jev selected `B, D`, omitting C. The exact exclusion `send(safe)` does not exclude the two-argument call `send(safe, extra)`. The [exercise definitions](scenarios/core/semgrep_exam_cases.py) and [reference rules](evidence/semgrep_exam/rules.yaml) provide the full context.

### Interpretation-dependent probes

The family puzzle scored **2/5** against its intended reference, which assumes the parents are older than their children:

| Question | Expected | Jev response |
|---|---|---|
| Who was the murderer? | Mother | Mother |
| Father's role | Accessory | Accessory |
| Mother's role | Murderer | Accessory |
| Son's role | Victim | Murderer |
| Daughter's role | Witness | Accessory |

There is also a separate consistency failure: Jev names the mother as murderer, assigns her the accessory role, and assigns the murderer role to the son. These answers contradict each other under the puzzle's distinct-role setup, regardless of the age assumption or the intended solution.

### Multilingual interpretation

Five independent requests used the same English questions and answer options, changing only the message's language. The English message was:

> I am very angry. I want my money back. I need an answer today.

All five inputs are in [the multilingual scenario](scenarios/06_multilingual.py). Anger uses Score (0 = neutral, 1 = annoyed, 2 = very angry); intent uses Choice; urgency uses Noul for whether an answer is required today.

| Language | Anger score (0–2) | Intent | Intent confidence | Urgency Noul |
|---|---:|---|---:|---:|
| Chinese | 2.00 | refund | 1.00 | 0.98 |
| Spanish | 2.00 | refund | 1.00 | 0.98 |
| English | 2.00 | refund | 1.00 | 0.99 |
| Basque | 1.65 | refund | 1.00 | 0.98 |
| Guarani | 1.02 | other | 0.27 | 0.90 |

Jev identified the explicit refund request in four languages but missed it in Guarani. Basque and Guarani also received lower anger scores. These are distinct observations: the refund classification can be checked against the explicit request, while the anger scores show variation in the assigned intensity.


## Limitations

- **Selection bias:** scenarios were selected for investigating failures rather than sampled to represent general usage. Some successful and subjective experiments from the broader exploration are omitted; these results are not a general accuracy estimate.
- **Small, dependent samples:** one Sudoku, one family puzzle, one Semgrep exam, two primality runs, and one message per language. Questions sharing state are not independent trials.
- **Confidence and magnitude:** these samples do not establish calibration, a reliable confidence cutoff, or a general relationship between integer size and accuracy. Such claims require independently selected evaluation sets.
- **Prompt sensitivity:** alternate descriptions, explicit assumptions, and different answer options were not systematically controlled.
- **Environment provenance:** model identifiers and requests are saved, but provider backend revisions, account identifiers, and full historical dependency versions are not. A fixed model name does not guarantee unchanged service behavior. The observed variation does not identify its internal cause, and these observations do not establish behavior of later model versions.
- **Reference scope:** primality is checked by code, Semgrep references are version-specific, and the family puzzle is interpretation-dependent. The multilingual interpretation was agreed during experiment design, not measured through independent annotation. One translated message does not characterize overall language competence.
- **No controlled model comparison:** OpenRouter and Bonsai runs are outside this cohort. Different prompts, response protocols, and runtime conditions require a separate comparison.
