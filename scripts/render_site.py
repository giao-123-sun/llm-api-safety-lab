from __future__ import annotations

from pathlib import Path
import json
import shutil
import html
import pandas as pd


def _copy_to_static(src: Path, static_dir: Path, name: str | None = None) -> str:
    if not src.exists():
        return ""
    static_dir.mkdir(parents=True, exist_ok=True)
    target_name = name or src.name
    dst = static_dir / target_name
    shutil.copy2(src, dst)
    return f"static/{target_name}"


def main() -> None:
    summary = pd.read_csv("results/summary.csv")
    report_path = Path("results/paper_v2.md") if Path("results/paper_v2.md").exists() else Path("results/report.md")
    report_md = report_path.read_text(encoding="utf-8")
    related_work_path = Path("research/related_work_comparison.md")
    related_work_md = related_work_path.read_text(encoding="utf-8") if related_work_path.exists() else "N/A"
    docs_dir = Path("docs")
    static_dir = docs_dir / "static"
    docs_dir.mkdir(parents=True, exist_ok=True)

    logo_web = _copy_to_static(Path("assets/brand/project-logo.svg"), static_dir)
    summary_web = _copy_to_static(Path("results/summary.csv"), static_dir)
    raw_web = _copy_to_static(Path("results/raw_results.csv"), static_dir)
    report_web = _copy_to_static(report_path, static_dir, "paper.md")
    related_web = _copy_to_static(related_work_path, static_dir)
    research_log_web = _copy_to_static(Path("research/research_log.md"), static_dir)

    chart_paths = {
        "security_score": _copy_to_static(Path("results/security_score.png"), static_dir),
        "tradeoff": _copy_to_static(Path("results/tradeoff.png"), static_dir),
        "ablation_delta": _copy_to_static(Path("results/ablation_delta.png"), static_dir),
    }

    manifest_path = Path("assets/generated/manifest.json")
    images: list[str] = []
    if manifest_path.exists():
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        images = payload.get("images", [])

    rows = []
    for _, r in summary.iterrows():
        rows.append(
            "<tr>"
            f"<td>{r['profile']}</td>"
            f"<td>{r['attack_block_rate_pct']:.2f}</td>"
            f"<td>{r['benign_allow_rate_pct']:.2f}</td>"
            f"<td>{r['unsafe_error_rate_pct']:.2f}</td>"
            f"<td><b>{r['security_score']:.2f}</b></td>"
            "</tr>"
        )
    table_html = "\n".join(rows)
    generated_image_tags: list[str] = []
    for p in images:
        src = Path(p)
        web = _copy_to_static(src, static_dir)
        if web:
            generated_image_tags.append(
                f'<img src="{web}" alt="{src.stem}" style="max-width:100%;margin:16px 0;" />'
            )
    image_html = "\n".join(generated_image_tags)

    report_md_escaped = html.escape(report_md)
    related_work_md_escaped = html.escape(related_work_md)

    page_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LLM API Safety Lab</title>
  <style>
    :root {{
      --bg: #f8fbff;
      --paper: #ffffff;
      --ink: #0e2a47;
      --accent: #c96a20;
      --line: #d2dde8;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", sans-serif;
      background: radial-gradient(circle at 0% 0%, #e8f2ff 0, var(--bg) 48%);
      color: var(--ink);
    }}
    .wrap {{
      max-width: 1024px;
      margin: 24px auto;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 12px 34px rgba(0, 0, 0, 0.06);
    }}
    h1, h2 {{ margin-top: 0; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 20px;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 8px 10px;
      text-align: left;
      font-size: 14px;
    }}
    th {{ background: #eef4fb; }}
    img {{
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fff;
    }}
    pre {{
      white-space: pre-wrap;
      background: #f5f8fc;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 12px;
      font-size: 13px;
      line-height: 1.5;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin: 16px 0;
    }}
    .card {{
      border: 1px solid var(--line);
      border-left: 5px solid var(--accent);
      border-radius: 10px;
      padding: 10px 12px;
      background: #fff;
    }}
    .hero {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 10px;
    }}
    .logo {{
      width: 58px;
      height: 58px;
      border: none;
      border-radius: 12px;
      background: transparent;
    }}
    a.file {{
      color: var(--ink);
      text-decoration: none;
      border-bottom: 1px dashed var(--accent);
    }}
    a.file:hover {{
      color: #153f67;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <img class="logo" src="{logo_web}" alt="LLM API Safety Lab logo" />
      <h1>LLM API Safety Lab</h1>
    </div>
    <p>Closed-loop research pipeline: survey -> hypothesis -> experiment -> adjustment -> ablation -> reporting.</p>
    <div class="cards">
      <div class="card"><b>Raw Data</b><br /><a class="file" href="{raw_web}">Download CSV</a></div>
      <div class="card"><b>Summary</b><br /><a class="file" href="{summary_web}">Download CSV</a></div>
      <div class="card"><b>Report</b><br /><a class="file" href="{report_web}">Open Markdown</a></div>
      <div class="card"><b>Related Work</b><br /><a class="file" href="{related_web}">Open Markdown</a></div>
      <div class="card"><b>Research Log</b><br /><a class="file" href="{research_log_web}">Open Markdown</a></div>
    </div>
    <h2>Ablation Summary</h2>
    <table>
      <thead>
        <tr>
          <th>Profile</th>
          <th>Attack Block %</th>
          <th>Benign Allow %</th>
          <th>Unsafe Error %</th>
          <th>Security Score</th>
        </tr>
      </thead>
      <tbody>
        {table_html}
      </tbody>
    </table>
    <h2>Charts</h2>
    <img src="{chart_paths['security_score']}" alt="security_score" style="max-width:100%;margin:16px 0;" />
    <img src="{chart_paths['tradeoff']}" alt="tradeoff" style="max-width:100%;margin:16px 0;" />
    <img src="{chart_paths['ablation_delta']}" alt="ablation_delta" style="max-width:100%;margin:16px 0;" />
    <h2>Gemini Image Outputs</h2>
    {image_html}
    <h2>Report Snapshot</h2>
    <pre>{report_md_escaped}</pre>
    <h2>Related Work Snapshot</h2>
    <pre>{related_work_md_escaped}</pre>
  </div>
</body>
</html>
"""
    out = docs_dir / "index.html"
    out.write_text(page_html, encoding="utf-8")
    print(f"Rendered {out}")


if __name__ == "__main__":
    main()
