# Research Log

- Generated at (UTC): 2026-03-01T15:28:25.672962+00:00
- Idea source: idea.txt
- Goal: Assess security impact when websites let users provide api_key/baseurl/model and when agent capabilities (sandbox, MCP, skills) are enabled.

## Sources
- OpenRouter Quickstart: https://openrouter.ai/docs/quickstart
- OpenRouter Model: google/gemini-3.1-flash-image-preview: https://openrouter.ai/google/gemini-3.1-flash-image-preview
- OpenRouter Authentication: https://openrouter.ai/docs/api-reference/authentication
- Model Context Protocol Specification: https://modelcontextprotocol.io/specification/2025-06-18
- OpenAI Prompt Injection Defenses: https://openai.github.io/openai-agents-js/guides/security/
- OWASP Top 10 for LLM Applications 2025: https://genai.owasp.org/llm-top-10/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- MCP Safety Audit (ArXiv): https://arxiv.org/abs/2506.13653

## Persona Planning Notes
### Bruce Schneier
This is a classic **confused deputy** problem exacerbated by **indirection**. When a website asks for your `api_key` and `baseurl`, it isn't just a client; it’s a middleman. You are extending your trust boundary to include their infrastructure, their logging, and their developers’ competence.

### 1) Top Risks

*   **Credential Exfiltration via `baseurl` Hijacking:** An attacker-controlled site or a compromised frontend can point the `baseurl` to a malicious listener. If the site doesn't strictly validate the URL, your API key is leaked in the `Authorization` header of the first outbound request.
*   **The "Skill" Escalation Path:** Agentic capabilities (MCP, sandboxes) transform a data leak into a system compromise. If an agent has a "read_file" skill and is tricked by Prompt Injection (Indirect or Direct), it can exfiltrate your local environment variables or SSH keys to the provided `baseurl`.
*   **Prompt Injection as Remote Code Execution (RCE):** In a sandboxed environment, the sandbox is the security boundary. However, if the agent can define its own tools or modify its `baseurl` dynamically via a malicious prompt, the sandbox becomes a staging area for lateral movement within your network.
*   **Trust Cascade Failure:** You trust the website, the website trusts the LLM provider, and the LLM provider trusts the training data. A single adversarial prompt in a retrieved document (RAG) can instruct the agent to use its "skills" to dump the `api_key` to an external log.

### 2) Experiment Design Advice

*   **Test for "Key Bleed":** Design a test where the `baseurl` points to a RequestBin. Observe if the site sends the `api_key` before verifying the endpoint's identity or if it sends it to subdomains it shouldn't.
*   **Indirect Prompt Injection (IPI) via MCP:** Place a malicious instruction in a file that the agent is likely to read using its "skills." See if the agent can be coerced into

### Ron Kohavi
### 1) Top Risks
*   **SSRF via `baseurl` Manipulation:** Attackers provide internal/loopback addresses (e.g., `127.0.0.1`, `169.254.169.254`) to scan internal infrastructure or exfiltrate cloud metadata.
*   **Prompt Injection via Tool-Use:** Malicious data retrieved by an agent (e.g., via MCP or web search) can contain instructions that hijack the session, exfiltrating the user’s `api_key` to an attacker-controlled endpoint.
*   **Sandbox Escape/Resource Exhaustion:** Non-deterministic agent code execution (skills) can lead to side-channel leaks or DoS if cgroups/namespaces are not strictly enforced.
*   **Credential Scoping Failures:** Users providing high-privilege keys for low-privilege tasks, leading to unintended billing spikes or data deletion if the agent "hallucinates" a destructive command.

### 2) Experiment Design Advice
*   **The OEC (Overall Evaluation Criterion):** Define a composite metric: `Security Violations per 1k Sessions`. A violation is any unauthorized egress, unauthorized file access, or non-200 response from a validation proxy.
*   **Factorial Design:** Use a $2 \times 2 \times 2$ design to isolate effects:
    1.  **Input Source:** User-provided vs. System-provided (Keys/URLs).
    2.  **Capability:** Basic Chat vs. Agentic (MCP/Skills).
    3.  **Environment:** Open Internet vs. Restricted Sandbox.
*   **A/A Testing:** Run a null experiment first. Ensure your monitoring stack (e.g., eBPF probes in the sandbox) doesn't introduce latency jitter that triggers false positives in "timeout" security triggers.
*   **Statistical Power:** Security events are rare (low base rate). You need high volume or "Red Teaming" automation to simulate attacks, turning rare events into measurable frequencies.

### 3) What to

### Edward Tufte
### 1) Top Risks

*   **Credential Exfiltration via Prompt Injection:** Indirect injections can instruct the model to transmit the user’s `api_key` to an attacker-controlled `baseurl` via side-channel requests (e.g., image markdown or tool calls).
*   **SSRF via BaseURL Manipulation:** Attackers can use the `baseurl` field to probe internal network infrastructure (e.g., `http://169.254.169.254`) if the application lacks strict egress filtering.
*   **Sandbox Escapes via MCP:** Model Context Protocol (MCP) servers often grant filesystem or shell access. If the sandbox is porous, a compromised model can execute persistent malware or exfiltrate local environment variables.
*   **Privilege Escalation:** "Skills" or tools mapped to the user’s identity may allow the model to perform irreversible actions (e.g., deleting cloud resources) without a human-in-the-loop confirmation.

### 2) Experiment Design Advice

*   **Small Multiples:** Use a grid of sparklines to compare "Attack Success Rate" across different model families (GPT, Claude, Llama) vs. security configurations. This allows for rapid visual scanning of vulnerability patterns.
*   **The Control Group:** Establish a baseline of "Default Security" (no user-provided URL, no sandbox access) to measure the delta in risk introduced by each new capability.
*   **Trellis Plots:** Map "Agent Capability Level" (X-axis) against "Data Leakage Volume" (Y-axis), faceted by "Sandbox Type" (Docker, gVisor, WASM).
*   **Quantify the Ratio:** Measure the *Data-Ink Ratio* of your security logs. Focus on the transition from "Benign Intent" to "Malicious Execution" timestamps.

### 3) What to Avoid

*   **Venn Diagrams:** They lack quantitative precision. Use UpSet plots if showing overlapping vulnerabilities.
*   **Gauges and Donut Charts:** These obscure the magnitude of risk. Use linear scales

### George Orwell
### 1. Top Risks

*   **SSRF via Base URL Manipulation:** If the backend does not validate the `baseurl` against an allowlist, an attacker can point the agent to internal metadata services (e.g., `169.254.169.254`) or private network resources.
*   **Prompt Injection leading to Tool Abuse:** Maliciously crafted system prompts or retrieved context can force the agent to execute MCP (Model Context Protocol) tools or sandbox commands that exfiltrate the user’s `api_key` to an external logging endpoint.
*   **State Persistence Poisoning:** If the agent has "skills" that modify a persistent database or filesystem, a single compromised session can inject long-term backdoors into the agent's logic, affecting subsequent users or sessions.
*   **Sandbox Escape via Resource Exhaustion:** Inadequately restricted sandboxes are vulnerable to fork bombs or memory exhaustion, potentially leading to Denial of Service (DoS) for the host orchestrator.

### 2. Experiment Design Advice

*   **Isolate the Variable:** Test "BYO-Key" (Bring Your Own Key) configurations separately from "Managed Key" configurations. Determine if the risk profile shifts from the provider to the user.
*   **Quantify Success:** Do not use qualitative terms like "more secure." Define a **Security Failure Event (SFE)**: e.g., "The agent successfully transmitted a dummy secret from the environment to a non-authorized URL."
*   **Adversarial Simulation:** Use a "Red Team" script to provide a `baseurl` pointing to a local listener. Measure how many requests bypass the application's egress filters.
*   **Resource Monitoring:** During sandbox execution, log CPU/RAM spikes. Define a "Safe Threshold" and measure the frequency of breaches.

### 3. What to Avoid

*   **Vague Adjectives:** Eliminate words like *robust*, *enhanced*, or *intelligent*. If a sandbox is "secure," state exactly which syscalls it blocks.
*   **Implicit Trust:** Never assume the `baseurl

## Experiment Summary Snapshot
```json
[
  {
    "profile": "baseline",
    "attack_block_rate_pct": 100.0,
    "benign_allow_rate_pct": 100.0,
    "unsafe_error_rate_pct": 0.0,
    "avg_risk_score": 49.75,
    "security_score": 100.0,
    "delta_from_prev": 0.0
  },
  {
    "profile": "policy_only",
    "attack_block_rate_pct": 100.0,
    "benign_allow_rate_pct": 100.0,
    "unsafe_error_rate_pct": 0.0,
    "avg_risk_score": 50.2,
    "security_score": 100.0,
    "delta_from_prev": 0.0
  },
  {
    "profile": "policy_filter",
    "attack_block_rate_pct": 100.0,
    "benign_allow_rate_pct": 90.0,
    "unsafe_error_rate_pct": 5.0,
    "avg_risk_score": 51.52,
    "security_score": 97.0,
    "delta_from_prev": -3.0
  },
  {
    "profile": "policy_filter_least_priv",
    "attack_block_rate_pct": 100.0,
    "benign_allow_rate_pct": 90.0,
    "unsafe_error_rate_pct": 5.0,
    "avg_risk_score": 51.27,
    "security_score": 97.0,
    "delta_from_prev": 0.0
  },
  {
    "profile": "full_stack",
    "attack_block_rate_pct": 100.0,
    "benign_allow_rate_pct": 90.0,
    "unsafe_error_rate_pct": 5.0,
    "avg_risk_score": 51.27,
    "security_score": 97.0,
    "delta_from_prev": 0.0
  }
]
```