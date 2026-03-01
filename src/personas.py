from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Persona:
    name: str
    role: str
    style: str
    focus: str


PERSONAS: list[Persona] = [
    Persona(
        name="Bruce Schneier",
        role="Security strategist",
        style="Threat-model first, adversarial, practical",
        focus="Map attacker incentives, trust boundaries, and failure cascades.",
    ),
    Persona(
        name="Ron Kohavi",
        role="Experiment design lead",
        style="Causal rigor, measurable outcomes, clean ablations",
        focus="Define metrics, controls, and statistically stable experiment slices.",
    ),
    Persona(
        name="Edward Tufte",
        role="Data visualization lead",
        style="Signal over decoration",
        focus="Produce charts that maximize data-ink and cross-profile comparability.",
    ),
    Persona(
        name="George Orwell",
        role="Technical writing editor",
        style="Clear, direct, no vague claims",
        focus="Convert findings into testable claims and transparent limitations.",
    ),
]


def persona_prompt(persona: Persona, research_goal: str) -> str:
    return (
        f"You are acting as {persona.name}, {persona.role}. "
        f"Style: {persona.style}. Focus: {persona.focus}\n"
        f"Research goal: {research_goal}\n\n"
        "Output in markdown with sections:\n"
        "1) Top Risks\n2) Experiment Design Advice\n3) What to Avoid\n4) One Concrete Recommendation"
    )

