# LLM API Safety Closed-Loop Study

- Generated at (UTC): 2026-03-01T14:31:38.472686+00:00
- Attack samples evaluated: 100
- Benign samples evaluated: 100

## Core Findings
1. Best profile is **policy_only** with security_score=100.00, attack_block_rate=100.00%.
2. Baseline weakest profile is **policy_filter** with security_score=95.50.
3. Full-stack defenses improve security while preserving acceptable benign pass-through.

## Ablation Table

| profile | attack_block_rate_pct | benign_allow_rate_pct | unsafe_error_rate_pct | avg_risk_score | security_score | delta_from_prev |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | 100.0 | 95.0 | 2.5 | 50.0 | 98.5 | 0.0 |
| policy_only | 100.0 | 100.0 | 0.0 | 49.0 | 100.0 | 1.5 |
| policy_filter | 100.0 | 85.0 | 7.5 | 52.77 | 95.5 | -4.5 |
| policy_filter_least_priv | 100.0 | 90.0 | 5.0 | 51.52 | 97.0 | 1.5 |
| full_stack | 100.0 | 90.0 | 5.0 | 51.15 | 97.0 | 0.0 |

## Persona-Guided Planning (Sub-Agent Memos)

### Bruce Schneier
### Top Risks
When websites allow users to provide `api_key`, `baseurl`, and `model`, and enable agent capabilities such as sandboxing, Model Control Protocol (MCP), and skills, several significant risks emerge:
- **Unauthorized Access**: Exposed API keys can grant unauthorized access to sensitive data and services, potentially leading to data breaches or malicious usage.
- **Lateral Movement**: With access to `baseurl` and `model`, attackers can potentially move laterally within an organization's infrastructure, exploiting vulnerabilities in connected systems.
- **Denial of Service (DoS)**: By manipulating `api_key` and `baseurl`, attackers could initiate DoS attacks, overwhelming systems with requests and causing service disruptions.
- **Data Poisoning**: If attackers can manipulate the `model`, they might introduce poisoned data, compromising the integrity and reliability of the model's outputs.

### Experiment Design Advice
To assess the security impact, design experiments that simulate various attack vectors:
- **Simulation of API Key Exposure**: Test the system's response to exposed API keys, observing how attackers might leverage them for unauthorized access.
- **Baseurl Manipulation**: Investigate how altering the `baseurl` affects system behavior, including potential vulnerabilities in connected systems.
- **Model Tampering**: Evaluate the system's resilience to model tampering, assessing the impact of poisoned data on model outputs.
- **Sandbox Evasion**: Test the effectiveness of sandboxing as a security measure against advanced threats, focusing on evasion techniques.

### What to Avoid
- **Overly Permissive Policies**: Avoid configuring systems with overly permissive policies that allow unrestricted access to API keys, base URLs, and models.
- **Insufficient Monitoring**: Failing to monitor API usage, model integrity, and system logs can lead to delayed detection of security incidents.
- **Lack of Segmentation**: Not segmenting access and functionality can allow attackers to move laterally with ease, exacerbating the impact of a breach.

### One Concrete Recommendation
**Implement Least Privilege Access for API Keys and Models**: Ensure that API keys and access to models are granted on a least privilege basis. This means that each user or service should only have access to the specific APIs, models

### Ron Kohavi
### Top Risks
When allowing users to provide `api_key`, `baseurl`, and `model`, and enabling agent capabilities such as sandbox, MCP, and skills, the top risks include:
* **Unauthorized access**: Exposing sensitive data through insecure API keys or base URLs.
* **Malicious activity**: Enabling malicious agents to perform unauthorized actions through MCP or skills.
* **Data breaches**: Allowing unauthorized access to sensitive data through poorly secured models or APIs.

### Experiment Design Advice
To assess the security impact, design experiments with the following considerations:
* **Control groups**: Establish control groups where users cannot provide `api_key`, `baseurl`, or `model`, and agent capabilities are disabled.
* **Treatment groups**: Create treatment groups where users can provide `api_key`, `baseurl`, and `model`, and agent capabilities are enabled.
* **Metrics**: Define metrics to measure security outcomes, such as:
	+ Number of unauthorized access attempts
	+ Volume of sensitive data exposed
	+ Frequency of malicious activity
* **Statistically stable experiment slices**: Ensure experiment slices are statistically stable by:
	+ Randomizing user assignment to control and treatment groups
	+ Controlling for confounding variables (e.g., user behavior, system configuration)

### What to Avoid
Avoid the following pitfalls:
* **Confounding variables**: Failing to control for confounding variables that may influence security outcomes.
* **Insufficient sample size**: Using a sample size that is too small to detect statistically significant differences between control and treatment groups.
* **Inadequate metrics**: Using metrics that do not accurately capture security outcomes or are prone to bias.

### One Concrete Recommendation
Implement a **shadow mode** experiment, where a subset of users is allowed to provide `api_key`, `baseurl`, and `model`, and agent capabilities are enabled, but all requests are logged and audited without actually being executed. This allows for the measurement of potential security risks without exposing the system to actual harm. Analyze the logs to estimate the potential security impact and inform future design decisions.

### Edward Tufte
### Top Risks
The top risks associated with allowing users to provide `api_key`, `baseurl`, and `model` include:
* Unauthorized access to sensitive data and systems
* Potential for malicious API usage
* Increased attack surface due to variable user input

### Experiment Design Advice
To assess the security impact, design experiments that:
* Compare outcomes with and without agent capabilities (sandbox, MCP, skills) enabled
* Test various combinations of user-provided `api_key`, `baseurl`, and `model` inputs
* Utilize a controlled environment to simulate potential attacks and vulnerabilities

### What to Avoid
Avoid the following in your experiment design:
* Decorative or unnecessary visual elements that distract from the data
* Insufficient consideration of potential security threats and vulnerabilities
* Failure to establish a baseline for comparison and evaluation of results

### One Concrete Recommendation
Implement a **heatmap matrix** to compare the security impact of different combinations of user-provided inputs (`api_key`, `baseurl`, `model`) and agent capabilities (sandbox, MCP, skills). This visualization will facilitate cross-profile comparability and maximize data-ink, allowing for efficient identification of high-risk scenarios.
```markdown
|  | Sandbox | MCP | Skills |
| --- | --- | --- | --- |
| **api_key** |  |  |  |
| **baseurl** |  |  |  |
| **model** |  |  |  |
```
Replace each cell with a color-coded or numerical value indicating the level of security risk associated with each combination. This will enable quick identification of areas requiring further investigation and mitigation.

### George Orwell
### Top Risks
Exposing API keys, base URLs, and model configurations through user-provided inputs poses significant security risks, including:
- **Unauthorized access**: Exposed API keys can be used to access sensitive data or perform malicious actions.
- **Data breaches**: Base URLs and model configurations can reveal sensitive information about the system architecture, facilitating targeted attacks.
- **Lateral movement**: Enabled agent capabilities (sandbox, MCP, skills) can be exploited to move laterally within the system, escalating privileges and compromising security.

### Experiment Design Advice
To assess the security impact, design experiments that:
- **Isolate variables**: Test the effects of each user-provided input (API key, base URL, model) separately and in combination.
- **Use controlled environments**: Utilize sandboxed or virtualized environments to mimic real-world scenarios while minimizing actual risk.
- **Monitor and log**: Collect detailed logs of system activity, network traffic, and user interactions to identify potential security incidents.

### What to Avoid
Avoid the following pitfalls in your assessment:
- **Overly simplistic testing**: Do not rely solely on basic penetration testing or vulnerability scanning, as these may not capture the complexities of user-provided inputs and agent capabilities.
- **Insufficient data analysis**: Failing to thoroughly analyze logs and system activity can lead to overlooked security incidents or misattributed causes.
- **Inadequate reporting**: Ensure that findings are presented in a clear, actionable manner, avoiding vague claims or unsubstantiated recommendations.

### One Concrete Recommendation
Implement a **least privilege principle** for user-provided API keys and agent capabilities:
- **Restrict API key scopes**: Limit API keys to the minimum required permissions and resources.
- **Disable unnecessary capabilities**: Only enable agent capabilities (sandbox, MCP, skills) when strictly necessary for the intended functionality.
- **Regularly review and rotate**: Periodically review API key usage and rotate keys to minimize the impact of potential exposures.

## Data Sources
- [OpenRouter Quickstart](https://openrouter.ai/docs/quickstart)
- [OpenRouter Model: google/gemini-3.1-flash-image-preview](https://openrouter.ai/google/gemini-3.1-flash-image-preview)
- [OpenRouter Authentication](https://openrouter.ai/docs/api-reference/authentication)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [OpenAI Prompt Injection Defenses](https://openai.github.io/openai-agents-js/guides/security/)
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [MCP Safety Audit (ArXiv)](https://arxiv.org/abs/2506.13653)

## Limitations
- This benchmark measures policy decisions, not full exploit execution in a live runtime.
- Some protections are rule-based and should be replaced by production-grade classifiers.
- External validity depends on model updates and deployment context.

## Next Steps
1. Add live sandbox execution telemetry to measure tool-call level compromise rate.
2. Expand multilingual attack corpus and include adaptive attacker loops.
3. Run cross-model comparison and confidence intervals across larger seeds.