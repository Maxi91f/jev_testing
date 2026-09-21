# Jev: an exploratory failure analysis

A research note with runnable experiment scripts on failures observed in **Jev `jev-1.13.0`** through its structured-question API on September 17–18, 2026.

Scenarios were selected retrospectively because they exposed errors. This is a collection of counterexamples, not a representative benchmark or an estimate of general accuracy.

Read the [experiment report](REPORT_jev-1.13.0.md) for methodology and recorded results. The public repository includes scenario scripts and reference material. Raw Jev exchanges, the historical selection manifest, and offline analysis are not included in this repo, but you can request them. Readers can run new experiments with their own API key.

## Experiments

We ran a series of experiments, described in more detail in the [experiment report](REPORT_jev-1.13.0.md).

1. Count Rs: Count the number of 'R' characters in a string
2. Solve 4x4 Sudoku: Fill in a 4x4 Sudoku grid
3. Prime numbers: Determine if a number is prime
4. Semgrep rule reading: Interpret a Semgrep rule
5. Family murder puzzle: Solve a logic puzzle about a family
6. Multilingual comparison: Compare answers to the same three English questions about the same message in five languages (Chinese, Spanish, English, Basque, and Guarani)

| Task | Recorded result |
|---|---|
| Count R characters | 11/18 right |
| 4×4 Sudoku | 10/16 cells, including 4 clues; invalid board |
| Prime numbers | 47/60 twice; 27 Noul values and 2 classifications changed |
| Semgrep rule reading | 18/20; one error had confidence 0.92 |
| Family murder puzzle | 2/5 under the intended interpretation; inconsistent roles |
| Multilingual comparison | Identified the refund request in 4/5 languages; failed in Guarani despite a verified translation. |

Finally, I compared it against an inexpensive LLM (GPT-OSS 20B with low reasoning effort), and the LLM made no errors.

## Personal conclusions

My conclusions:

- It is fast—really, really fast. More than 10 times faster.
- It is parallel. That's amazing and totally different.
- It is cheap, pretty cheap. This is harder to compare, but it is always the cheaper option.
- The confidence works. Low-confidence answers should be treated as unknown. In the few tests I ran, answers with confidence below 0.9 were full of errors.
- Jev failed to identify an explicit refund request in Guarani, despite correctly identifying it in the other four languages. I verified the Guarani translation.
- It doesn't work with math or logic at all. It couldn't solve a 4x4 Sudoku or a small logic problem. It couldn't count letters.
- The difficulty with counting letters could be a tokenization problem or a counting problem. I didn't test which.
- In the comparison with LLMs, GPT-OSS 20B with low reasoning effort solved every scenario that Jev failed, and it is a small, inexpensive model.

For a first version, it's really good. For the price and speed, it's fantastic. You have to know where it fails. For twice the price and ten times the wait, pick GPT-OSS 20B with low reasoning effort, and you will get better results.


## Live experiments

Export your own `TYPESAFE_API_KEY`, then run a scenario:

```bash
python3 scenarios/02_sudoku.py
```

Scripts: `scenarios/01_count_r.py`, `scenarios/02_sudoku.py`, `scenarios/03_primes.py`, `scenarios/04_semgrep_exam.py`, `scenarios/05_murder_in_the_family.py`, and `scenarios/06_multilingual.py`. Edit constants to change inputs. Live runs contact the vendor and may incur charges. `scenarios/core/jev_poc.py` pins the model; continued availability of that version is not guaranteed.

The Semgrep exam additionally requires PyYAML and `semgrep` on PATH. The historical reference used **Semgrep CE 1.176.1**. Use that version for comparison; the script records the installed version when generating a new key. Historical Python/PyYAML versions were not recorded.

New runs save timestamped exchanges locally in `results/jev/`, which is excluded from Git. They do not automatically update the published summary.

## Files

- [REPORT_jev-1.13.0.md](REPORT_jev-1.13.0.md): methodology, summarized results, and limitations.
- `scenarios/`: runnable experiments and shared code.
- `evidence/`: Sudoku uniqueness evidence, Semgrep fixtures and scans, source metadata, and attribution.

Original code and documentation are licensed under [MIT](LICENSE). Third-party material retains its own notices and applicable terms.

No credentials are included.
