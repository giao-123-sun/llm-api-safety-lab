# LLM API Safety Lab

Closed-loop research pipeline for your idea:

1. Security research and source logging  
2. Hypothesis generation with expert-style sub-agent personas  
3. Baseline and defense experiments  
4. Ablation analysis  
5. Data visualization  
6. Image generation via `google/gemini-3.1-flash-image-preview` on OpenRouter  
7. Open-source publication + GitHub Pages project URL

## Quick Start

```bash
pip install -r requirements.txt
python run_pipeline.py
python scripts/render_site.py
python scripts/publish_github.py
```

## Inputs

- `idea.txt`: your research idea statement.
- `config/key.txt`: OpenRouter settings (`baseurl`, `model_name`, `api_key`).
- `config/github_key.txt`: GitHub PAT (for auto publishing).

## Outputs

- `results/raw_results.csv`: full run-level decisions.
- `results/summary.csv`: aggregated metrics by defense profile.
- `results/*.png`: charts (security score, tradeoff, ablation delta).
- `results/report.md`: full report.
- `research/research_log.md`: complete research log and source list.
- `assets/generated/*.png`: images generated through Gemini image-preview model.
- `docs/index.html`: simple project website.

## Experiment Profiles

- `baseline`
- `policy_only`
- `policy_filter`
- `policy_filter_least_priv`
- `full_stack`

The default score is:

`security_score = 0.7 * attack_block_rate + 0.3 * benign_allow_rate`

## Notes

- The pipeline is defensive and focuses on API/agent safety evaluation.
- Do not commit local key files.

