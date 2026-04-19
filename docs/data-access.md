# Data Access Guide

This repo does not redistribute the benchmark datasets themselves. Instead, each
task reads from a local path or an authenticated upstream source configured via
environment variables.

## Benchmark Map

| Benchmark | Paper | Dataset / access link | Tasks in repo | Required env vars | Expected local format | Public release status |
| --- | --- | --- | --- | --- | --- | --- |
| `UniMoral` | [Kumar et al. 2025](https://aclanthology.org/2025.acl-long.294/) | [HF dataset](https://huggingface.co/datasets/shivaniku/UniMoral) | `unimoral_action_prediction` plus additional task builders in module | `UNIMORAL_DATA_DIR` | directory containing files such as `English_long.csv` and `English_short.csv` | benchmark-faithful |
| `SMID` | [Crone et al. 2018](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954) | [OSF project](https://osf.io/ngzwx/) | `smid_moral_rating`, `smid_foundation_classification` | `SMID_DATA_DIR` | directory containing a norms CSV plus image assets or image zip archives | benchmark-faithful |
| `Value Kaleidoscope` | [Sorensen et al. 2024 / arXiv](https://arxiv.org/abs/2310.17681) | [HF dataset](https://huggingface.co/datasets/allenai/ValuePrism) | `value_prism_relevance`, `value_prism_valence` | `VALUEPRISM_RELEVANCE_FILE`, `VALUEPRISM_VALENCE_FILE` or Hugging Face auth | local CSV / JSON / JSONL export, or gated HF dataset access | benchmark-faithful |
| `CCD-Bench` | [Rahman et al. 2025](https://arxiv.org/abs/2510.03553) | [repo](https://github.com/smartlab-nyu/CCD-Bench), [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | `ccd_bench_selection` | `CCD_BENCH_DATA_FILE` optional | local JSON file or default remote JSON URL | benchmark-faithful |
| `Denevil` | [Duan et al. 2023](https://arxiv.org/abs/2310.11905) | no stable public `MoralPrompt` download verified | `denevil_generation`, `denevil_fulcra_proxy_generation` | `DENEVIL_DATA_FILE` | MoralPrompt-style CSV / JSON / JSONL for faithful runs; FULCRA-style dialogue export only for proxy runs | proxy in current public release |

## Denevil Schema Rules

The repo supports two distinct pathways:

- `denevil_generation`: expects a benchmark-faithful MoralPrompt-style export with a prompt-like field such as `prompt`, `instruction`, `question`, or `text`
- `denevil_fulcra_proxy_generation`: expects a FULCRA-style dialogue export with `dialogue` and value annotations

Use `scripts/check_denevil_dataset.py` before launching a formal run if the schema is uncertain.

## Environment Example

```bash
cp .env.example .env
```

Populate only the paths needed for the benchmarks you want to run. Missing data
paths should block only the corresponding task, not the whole repository.

## Release Interpretation

The closed `2026-04-19 Option 1` package includes benchmark-faithful lines for
`UniMoral`, `SMID`, `Value Kaleidoscope`, and `CCD-Bench`, but only a proxy line
for `Denevil`. Treat that distinction as methodological, not cosmetic.
