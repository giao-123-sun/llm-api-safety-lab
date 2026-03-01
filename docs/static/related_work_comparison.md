# Related Work Comparison for LLM API / Agent Safety

## Scope
This note compares representative papers around prompt injection, agent tool-use risk, and defenses, then positions our current work.

## Paper-by-Paper Comparison
| Paper | What they did | Evaluation scale / setting | How far they got | Difference vs our work |
| --- | --- | --- | --- | --- |
| Greshake et al., 2023, *Not What You've Signed Up For* ([arXiv:2302.12173](https://arxiv.org/abs/2302.12173)) | First systematic framing of **indirect prompt injection** against LLM-integrated apps and plugins. | Real-world case-style attacks on then-deployed LLM app patterns. | Established that indirect instructions in untrusted content can steer model behavior across tool boundaries. | Their focus is attack discovery; ours is a deployable policy-gateway experiment for BYO `api_key/baseurl/model` deployments. |
| Liu et al., 2023, *Formalizing and Benchmarking Prompt Injection Attacks and Defenses* ([arXiv:2310.12815](https://arxiv.org/abs/2310.12815)) | Formalized PI threats and built a benchmark with attacks and defenses. | 10 LLMs, 5 attack methods, 10 defenses, across 7 tasks and 5 real-world scenarios. | Provided broad cross-model evidence that no single defense dominates all settings. | Their breadth is larger; ours is narrower but targets practical API-gateway policy design and ablation under agent tooling assumptions. |
| Ruan et al., 2023, *ToolEmu* ([arXiv:2309.15817](https://arxiv.org/abs/2309.15817)) | Built a simulator to evaluate risky tool-use behavior of LLM agents without real-world harm. | 36 tools, 144 cases, evaluated 5 advanced agents. | Showed substantial emergent risks in tool-use and safety policy gaps. | ToolEmu emphasizes simulated execution risk; ours emphasizes inbound-request policy decisions for hosted/API products. |
| Debenedetti et al., 2024, *AgentDojo* ([OpenReview](https://openreview.net/forum?id=m1YYAQjO3w)) | Created a dynamic benchmark for PI resilience of LLM agents. | Interactive tasks with tool-enabled agents (function-calling and ReAct). | Reported high attack success rates: up to 97.16% (function-calling), 83.39% (ReAct). | AgentDojo is a stronger runtime benchmark; our current pipeline is lighter-weight and easier to operationalize but less execution-realistic. |
| Debenedetti et al., 2025, *CaMeL* ([arXiv:2503.18813](https://arxiv.org/abs/2503.18813)) | Proposed capability-based confinement for LLM agents. | New benchmark + capability-oriented defense architecture. | Found baseline defenses still leave large unresolved risk/utility tradeoff; CaMeL improves but does not eliminate risk. | We currently approximate least-privilege at policy level; CaMeL goes deeper on capability confinement semantics. |
| Alizadeh et al., 2025, *Simple Prompt Injection Attacks can Leak Personal Data from AI Agents* ([arXiv:2506.01055](https://arxiv.org/abs/2506.01055)) | Measured privacy leakage from realistic PI attacks. | AgentDojo-style setups with simple and adaptive attacks. | Reported 15-50 pp drops in privacy preservation; ASR around 20% (simple) and 15% (adaptive). | Their emphasis is privacy leakage quantification; ours tracks broader API-gateway safety decisions (exfiltration, SSRF-like, tool abuse, etc.). |
| Choudhary et al., 2025, *How Not to Detect Prompt Injections* ([arXiv:2507.05630](https://arxiv.org/abs/2507.05630)) | Studied detector failure under attack and proposed DataFlip-style evasion. | Tested against KAD and PI detector pipelines. | Claimed >91% attack success with effectively 0% detection in some conditions. | This directly stresses our rule-heavy profile: naive filtering can be bypassed or overblock benign traffic. |
| Shi et al., 2025, *PromptArmor* ([arXiv:2507.15219](https://arxiv.org/abs/2507.15219)) | Layered defense pipeline for prompt-injection. | Controlled benchmarks across multiple prompt types. | Reported ASR <1% and FPR/FNR <1% in their setting. | Their defense stack is stronger than our current deterministic prefilter; we can adapt PromptArmor-style staged checks in next revision. |
| Wang et al., 2025, *AGENTVIGIL* ([ACL Anthology](https://aclanthology.org/2025.findings-emnlp.1258/)) | Benchmarked malicious prompt injections and mitigation for autonomous agents. | 71 malicious patterns + 70 tasks, with 3-stage mitigation pipeline. | Demonstrated meaningful security gain with only minor utility tradeoff. | Closest to our applied goal; our contribution is BYO API configuration threat boundary and web/API gateway deployment workflow. |

## Current Maturity Map (What level each line of work reaches)
1. `Attack discovery phase`: 2023 PI papers established exploitability and attack taxonomy.
2. `Benchmark phase`: ToolEmu / AgentDojo / AGENTVIGIL quantify risk at scale.
3. `Defense architecture phase`: CaMeL / PromptArmor propose structured mitigations.
4. `Operational deployment phase` (our current focus): API gateway policy + auditable controls for products where users bring their own key/baseurl/model.

## Main gaps still open
1. Runtime-grounded, end-to-end compromise metrics for real tool execution and MCP connectors.
2. Standardized utility-security tradeoff reporting under adaptive attackers.
3. Cross-provider reproducibility when model/provider behavior changes rapidly.

## Local paper files downloaded
1. `papers/2023_Greshake_IndirectPromptInjection.pdf`
2. `papers/2023_Liu_FormalizingBenchmarkingPI.pdf`
3. `papers/2023_Ruan_ToolEmu.pdf`
4. `papers/2024_Debenedetti_AgentDojo.pdf`
5. `papers/2025_Debenedetti_CaMeL.pdf`
6. `papers/2025_Alizadeh_DataLeakageAgentDojo.pdf`
7. `papers/2025_Choudhary_DataFlipKAD.pdf`
8. `papers/2025_Shi_PromptArmor.pdf`
9. `papers/2025_Wang_AGENTVIGIL.pdf`

