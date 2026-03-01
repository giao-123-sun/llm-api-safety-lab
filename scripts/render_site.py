from __future__ import annotations

from pathlib import Path
import json
import pandas as pd


def main() -> None:
    summary = pd.read_csv("results/summary.csv")
    report_md = Path("results/report.md").read_text(encoding="utf-8")
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
    image_html = "\n".join([f'<img src="../{p}" alt="{Path(p).stem}" style="max-width:100%;margin:16px 0;" />' for p in images])

    html = f"""<!doctype html>
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
  </style>
</head>
<body>
  <div class="wrap">
    <h1>LLM API Safety Lab</h1>
    <p>Closed-loop research pipeline: survey -> hypothesis -> experiment -> adjustment -> ablation -> reporting.</p>
    <div class="cards">
      <div class="card"><b>Raw Data</b><br />results/raw_results.csv</div>
      <div class="card"><b>Summary</b><br />results/summary.csv</div>
      <div class="card"><b>Report</b><br />results/report.md</div>
      <div class="card"><b>Research Log</b><br />research/research_log.md</div>
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
    <img src="../results/security_score.png" alt="security_score" style="max-width:100%;margin:16px 0;" />
    <img src="../results/tradeoff.png" alt="tradeoff" style="max-width:100%;margin:16px 0;" />
    <img src="../results/ablation_delta.png" alt="ablation_delta" style="max-width:100%;margin:16px 0;" />
    <h2>Gemini Image Outputs</h2>
    {image_html}
    <h2>Report Snapshot</h2>
    <pre>{report_md.replace("<", "&lt;").replace(">", "&gt;")}</pre>
  </div>
</body>
</html>
"""
    out = Path("docs/index.html")
    out.write_text(html, encoding="utf-8")
    print(f"Rendered {out}")


if __name__ == "__main__":
    main()

