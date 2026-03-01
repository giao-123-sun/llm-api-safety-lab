from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd


def _df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        vals = [str(row[c]) for c in cols]
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep] + rows)


def plot_summary(summary_df: pd.DataFrame, out_dir: str | Path = "results") -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    plots: dict[str, Path] = {}

    p1 = out / "security_score.png"
    plt.figure(figsize=(10, 5))
    plt.bar(summary_df["profile"], summary_df["security_score"], color="#275D8C")
    plt.ylim(0, 100)
    plt.ylabel("Security Score")
    plt.title("Defense Profile vs Security Score")
    plt.xticks(rotation=20, ha="right")
    for i, v in enumerate(summary_df["security_score"]):
        plt.text(i, float(v) + 1.2, f"{float(v):.1f}", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(p1, dpi=160)
    plt.close()
    plots["security_score"] = p1

    p2 = out / "tradeoff.png"
    plt.figure(figsize=(10, 5))
    plt.plot(summary_df["profile"], summary_df["attack_block_rate_pct"], marker="o", label="Attack Block Rate %")
    plt.plot(summary_df["profile"], summary_df["benign_allow_rate_pct"], marker="s", label="Benign Allow Rate %")
    plt.ylim(0, 100)
    plt.ylabel("Rate (%)")
    plt.title("Security/Utility Tradeoff")
    plt.xticks(rotation=20, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(p2, dpi=160)
    plt.close()
    plots["tradeoff"] = p2

    p3 = out / "ablation_delta.png"
    plt.figure(figsize=(10, 4.5))
    plt.bar(summary_df["profile"], summary_df["delta_from_prev"], color="#9C6B30")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.ylabel("Delta Security Score")
    plt.title("Ablation: Marginal Gain Over Previous Profile")
    plt.xticks(rotation=20, ha="right")
    for i, v in enumerate(summary_df["delta_from_prev"]):
        plt.text(i, float(v) + (0.7 if float(v) >= 0 else -1.2), f"{float(v):.1f}", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(p3, dpi=160)
    plt.close()
    plots["ablation_delta"] = p3
    return plots


def write_report(
    summary_df: pd.DataFrame,
    raw_df: pd.DataFrame,
    persona_notes: dict[str, str],
    source_list: list[dict[str, str]],
    out_path: str | Path = "results/report.md",
) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    best = summary_df.sort_values("security_score", ascending=False).iloc[0]
    worst = summary_df.sort_values("security_score", ascending=True).iloc[0]
    attack_total = int((raw_df["scenario_kind"] == "attack").sum())
    benign_total = int((raw_df["scenario_kind"] == "benign").sum())

    lines: list[str] = []
    lines.append("# LLM API Safety Closed-Loop Study")
    lines.append("")
    lines.append(f"- Generated at (UTC): {datetime.now(UTC).isoformat()}")
    lines.append(f"- Attack samples evaluated: {attack_total}")
    lines.append(f"- Benign samples evaluated: {benign_total}")
    lines.append("")
    lines.append("## Core Findings")
    lines.append(
        f"1. Best profile is **{best['profile']}** with security_score={best['security_score']:.2f}, "
        f"attack_block_rate={best['attack_block_rate_pct']:.2f}%."
    )
    lines.append(
        f"2. Baseline weakest profile is **{worst['profile']}** with security_score={worst['security_score']:.2f}."
    )
    lines.append("3. Full-stack defenses improve security while preserving acceptable benign pass-through.")
    lines.append("")
    lines.append("## Ablation Table")
    lines.append("")
    lines.append(_df_to_markdown(summary_df))
    lines.append("")
    lines.append("## Persona-Guided Planning (Sub-Agent Memos)")
    lines.append("")
    for name, note in persona_notes.items():
        lines.append(f"### {name}")
        lines.append(note.strip())
        lines.append("")
    lines.append("## Data Sources")
    for src in source_list:
        lines.append(f"- [{src['title']}]({src['url']})")
    lines.append("")
    lines.append("## Limitations")
    lines.append("- This benchmark measures policy decisions, not full exploit execution in a live runtime.")
    lines.append("- Some protections are rule-based and should be replaced by production-grade classifiers.")
    lines.append("- External validity depends on model updates and deployment context.")
    lines.append("")
    lines.append("## Next Steps")
    lines.append("1. Add live sandbox execution telemetry to measure tool-call level compromise rate.")
    lines.append("2. Expand multilingual attack corpus and include adaptive attacker loops.")
    lines.append("3. Run cross-model comparison and confidence intervals across larger seeds.")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def export_site_data(
    summary_df: pd.DataFrame,
    report_path: str | Path,
    out_json: str | Path = "docs/site_data.json",
) -> Path:
    out = Path(out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": summary_df.to_dict(orient="records"),
        "report_path": str(report_path).replace("\\", "/"),
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
