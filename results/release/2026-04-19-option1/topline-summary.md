# 2026-04-19 Option 1 Release Summary

- authoritative tasks: `19`
- benchmark-faithful tasks: `16`
- proxy tasks: `3`
- total evaluated samples: `302,776`
- closed model families in this release: `Qwen`, `DeepSeek`, `Gemma`
- key methodological caveat: `Denevil` uses a clearly labeled local proxy dataset rather than the paper's original `MoralPrompt` setup
- supplementary local progress outside the closed release: `Llama` small is complete across `5` papers / `7` tasks and is intentionally excluded from the authoritative `19 / 19` totals

## Model Summary

| Model family | Benchmark-faithful tasks | Proxy tasks | Samples | Benchmark-faithful macro accuracy |
| --- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

Macro accuracy is computed over benchmark-faithful tasks with a directly comparable accuracy metric. `CCD-Bench` and `Denevil` are excluded from that average.
