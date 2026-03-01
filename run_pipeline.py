from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import json
import requests

from src.config_loader import load_openrouter_config
from src.experiment_runner import RunConfig, run_experiments
from src.openrouter_client import OpenRouterClient
from src.personas import PERSONAS, persona_prompt
from src.reporting import export_site_data, plot_summary, write_report
from src.scenarios import SCENARIOS


RESEARCH_GOAL = (
    "Assess security impact when websites let users provide api_key/baseurl/model and when agent capabilities "
    "(sandbox, MCP, skills) are enabled."
)

SOURCES: list[dict[str, str]] = [
    {"title": "OpenRouter Quickstart", "url": "https://openrouter.ai/docs/quickstart"},
    {
        "title": "OpenRouter Model: google/gemini-3.1-flash-image-preview",
        "url": "https://openrouter.ai/google/gemini-3.1-flash-image-preview",
    },
    {"title": "OpenRouter Authentication", "url": "https://openrouter.ai/docs/api-reference/authentication"},
    {"title": "Model Context Protocol Specification", "url": "https://modelcontextprotocol.io/specification/2025-06-18"},
    {"title": "OpenAI Prompt Injection Defenses", "url": "https://openai.github.io/openai-agents-js/guides/security/"},
    {"title": "OWASP Top 10 for LLM Applications 2025", "url": "https://genai.owasp.org/llm-top-10/"},
    {"title": "NIST AI Risk Management Framework", "url": "https://www.nist.gov/itl/ai-risk-management-framework"},
    {"title": "MCP Safety Audit (ArXiv)", "url": "https://arxiv.org/abs/2506.13653"},
]


def _write_research_log(path: str | Path, persona_notes: dict[str, str], summary_rows: list[dict]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Research Log")
    lines.append("")
    lines.append(f"- Generated at (UTC): {datetime.now(UTC).isoformat()}")
    lines.append("- Idea source: idea.txt")
    lines.append(f"- Goal: {RESEARCH_GOAL}")
    lines.append("")
    lines.append("## Sources")
    for src in SOURCES:
        lines.append(f"- {src['title']}: {src['url']}")
    lines.append("")
    lines.append("## Persona Planning Notes")
    for name, note in persona_notes.items():
        lines.append(f"### {name}")
        lines.append(note.strip())
        lines.append("")
    lines.append("## Experiment Summary Snapshot")
    lines.append("```json")
    lines.append(json.dumps(summary_rows, ensure_ascii=False, indent=2))
    lines.append("```")
    p.write_text("\n".join(lines), encoding="utf-8")


def _generate_persona_notes(client: OpenRouterClient, model: str) -> dict[str, str]:
    notes: dict[str, str] = {}
    for persona in PERSONAS:
        prompt = persona_prompt(persona, RESEARCH_GOAL)
        try:
            result = client.chat(
                model=model,
                temperature=0.4,
                max_tokens=450,
                messages=[
                    {"role": "system", "content": "Be concise and technically rigorous."},
                    {"role": "user", "content": prompt},
                ],
            )
            notes[persona.name] = result.text.strip() or "_No response._"
        except Exception as exc:
            notes[persona.name] = f"_Persona call failed: {type(exc).__name__}. Fallback to internal planning._"
    return notes


def _generate_images(client: OpenRouterClient) -> list[Path]:
    generated: list[Path] = []
    errors: list[str] = []
    img_dir = Path("assets/generated")
    img_dir.mkdir(parents=True, exist_ok=True)

    threat_prompt = (
        "Create a clean security architecture illustration for LLM API safety. "
        "Show: User -> Web App -> LLM API Gateway -> Model Provider. "
        "Also show security controls: key vault, allowlist, policy engine, HITL approval, audit log. "
        "Style: white background, blue and orange accents, readable labels, professional diagram."
    )
    image_models = [
        "google/gemini-3.1-flash-image-preview",
        "google/gemini-3-pro-image-preview",
        "google/gemini-2.5-flash-image",
        "openai/gpt-5-image-mini",
    ]
    for idx, prompt in enumerate([threat_prompt], start=1):
        success = False
        for image_model in image_models:
            try:
                out_name = "threat_architecture.png" if idx == 1 else f"image_{idx}.png"
                p = client.generate_image(prompt, img_dir / out_name, model=image_model)
                generated.append(p)
                success = True
                break
            except Exception as exc:
                errors.append(f"{image_model}: {type(exc).__name__}")
        if not success:
            errors.append("All image models failed for threat architecture prompt.")

    matrix_prompt = (
        "Generate a visual risk matrix chart image for LLM agent attacks. "
        "Axes: likelihood vs impact. Include points for prompt injection, key exfiltration, tool abuse, "
        "MCP connector abuse, model swap attack. Minimalist and publication-ready."
    )
    for idx, prompt in enumerate([matrix_prompt], start=1):
        success = False
        for image_model in image_models:
            try:
                out_name = "risk_matrix.png" if idx == 1 else f"risk_{idx}.png"
                p = client.generate_image(prompt, img_dir / out_name, model=image_model)
                generated.append(p)
                success = True
                break
            except Exception as exc:
                errors.append(f"{image_model}: {type(exc).__name__}")
        if not success:
            errors.append("All image models failed for risk matrix prompt.")
    if errors:
        Path("assets/generated/image_errors.log").write_text("\n".join(errors), encoding="utf-8")
    return generated


def _pick_text_model(client: OpenRouterClient, default_model: str) -> str:
    candidates = [
        default_model,
        "meta-llama/llama-3.3-70b-instruct",
        "qwen/qwen-2.5-72b-instruct",
        "deepseek/deepseek-chat-v3-0324",
        "google/gemini-2.0-flash-001",
    ]
    headers = client._headers()
    baseurl = client._cfg.baseurl
    for model in candidates:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Reply with OK."}],
                "max_tokens": 8,
                "temperature": 0,
            }
            r = client._session.post(f"{baseurl}/chat/completions", headers=headers, json=payload, timeout=45)
            if r.status_code == 200:
                return model
        except requests.RequestException:
            continue
    raise RuntimeError("No available text model found for this region/account.")


def main() -> None:
    cfg = load_openrouter_config("config/key.txt")
    client = OpenRouterClient(cfg)

    selected_text_model = _pick_text_model(client, cfg.default_model)
    run_cfg = RunConfig(model=selected_text_model, temperature=0.5, runs_per_scenario=2)
    persona_notes = _generate_persona_notes(client, model=selected_text_model)
    raw_df, summary_df = run_experiments(client, SCENARIOS, run_cfg, out_dir="results")
    plot_summary(summary_df, out_dir="results")
    report_path = write_report(
        summary_df=summary_df,
        raw_df=raw_df,
        persona_notes=persona_notes,
        source_list=SOURCES,
        out_path="results/report.md",
    )
    export_site_data(summary_df, report_path, out_json="docs/site_data.json")
    _write_research_log("research/research_log.md", persona_notes, summary_df.to_dict(orient="records"))

    generated_images = _generate_images(client)
    image_manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "images": [str(p).replace("\\", "/") for p in generated_images],
        "model": "google/gemini-3.1-flash-image-preview",
        "selected_text_model": selected_text_model,
    }
    Path("assets/generated/manifest.json").write_text(
        json.dumps(image_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Pipeline completed.")
    print(f"Report: {report_path}")
    print("Summary CSV: results/summary.csv")
    print("Raw CSV: results/raw_results.csv")
    print("Images:", ", ".join(image_manifest["images"]))


if __name__ == "__main__":
    main()
