# 让用户自填 `api_key/baseurl/model` 的 LLM Agent 接入风险研究

## 摘要
本文研究一种正在流行的产品形态: 网站要求用户自行填写 `api_key`、`baseurl`、`model` 来调用模型 API。该模式降低了平台方推理成本, 但可能把密钥管理、请求路由和能力边界转移给终端用户, 并扩大攻击面。我们构建了一个闭环评估流水线, 针对 Prompt Injection、密钥外传、SSRF、工具滥用、MCP 连接器滥用、逆向系统提示等场景进行基线与防御对比实验。实验共包含 20 个场景、5 个防御配置、每场景 2 次重复, 共 200 条决策样本。结果显示: 在当前样本中, 所有配置对攻击样本均达到 100% 拦截/升级率; 但启用确定性预过滤后, 对良性请求存在 10% 误拦截, 使综合评分从 100 降至 97。结论是: 与其盲目叠加规则, 更应优先做“策略判定+最小权限+可审计升级”的分层设计, 并控制误报成本。

## 1. 研究背景
大量 Demo 与工具站采用“用户自带模型配置”模式:
1. 用户输入密钥与模型参数后即刻可用, 降低平台运营成本。
2. 平台不必托管所有模型账号, 减少账单与配额压力。
3. 但信任边界从“平台内”扩展到“用户输入+外部路由+工具系统”。

在 Agent 化趋势下, 风险不再只来自提示词文本, 还来自:
1. 工具调用权限 (shell/filesystem/network)。
2. MCP 外部连接器提供的跨系统能力。
3. 自动循环执行带来的误操作放大。

## 2. 研究问题
我们聚焦三个问题:
1. 当用户可控 `baseurl/model` 时, 是否会显著增加越权与外传风险?
2. 在 Agent 能力开启后, 哪类防御组合在“安全性/可用性”之间更优?
3. 规则预过滤、最小权限、人工审批(HITL)分别贡献多大边际收益?

## 3. 威胁模型与实验设置
### 3.1 威胁模型
攻击者可通过以下入口注入恶意意图:
1. 直接提示词诱导 (泄漏密钥、绕过审计、执行高危命令)。
2. 间接注入 (来自文档/工具返回内容/MCP 数据源)。
3. 路由层滥用 (诱导访问 `169.254.169.254` 等敏感地址)。

### 3.2 数据与样本
1. 攻击场景 10 个: 覆盖 Prompt Injection、Secret Exfiltration、Privilege Escalation、SSRF-like、Tool Abuse、MCP Abuse、Model Swap、Reverse Engineering、Autonomous Loop Attack 等。
2. 良性场景 10 个: 覆盖总结、编码、调试、翻译、测试用例、文档改写等常规任务。
3. 每场景重复 2 次, 总样本 200。

### 3.3 防御配置 (Ablation Profiles)
1. `baseline`: 无策略、无预过滤、无最小权限、无 HITL。
2. `policy_only`: 仅策略判定器。
3. `policy_filter`: 策略 + 确定性高危预过滤。
4. `policy_filter_least_priv`: 策略 + 预过滤 + 最小权限。
5. `full_stack`: 策略 + 预过滤 + 最小权限 + HITL。

### 3.4 指标
1. `attack_block_rate`: 攻击样本中被 `BLOCK/ASK_HUMAN` 的比例。
2. `benign_allow_rate`: 良性样本中被 `ALLOW` 的比例。
3. `unsafe_error_rate`: 不安全决策比例。
4. `security_score = 0.7 * attack_block_rate + 0.3 * benign_allow_rate`。

## 4. 结果
### 4.1 主结果
| Profile | Attack Block (n=20) | 95% CI | Benign Allow (n=20) | 95% CI | Safe Decision (n=40) | 95% CI | Avg Risk | Security Score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 20/20 (100%) | [83.9%, 100.0%] | 20/20 (100%) | [83.9%, 100.0%] | 40/40 (100%) | [91.2%, 100.0%] | 49.75 | 100.0 |
| policy_only | 20/20 (100%) | [83.9%, 100.0%] | 20/20 (100%) | [83.9%, 100.0%] | 40/40 (100%) | [91.2%, 100.0%] | 50.20 | 100.0 |
| policy_filter | 20/20 (100%) | [83.9%, 100.0%] | 18/20 (90%) | [69.9%, 97.2%] | 38/40 (95%) | [83.5%, 98.6%] | 51.52 | 97.0 |
| policy_filter_least_priv | 20/20 (100%) | [83.9%, 100.0%] | 18/20 (90%) | [69.9%, 97.2%] | 38/40 (95%) | [83.5%, 98.6%] | 51.28 | 97.0 |
| full_stack | 20/20 (100%) | [83.9%, 100.0%] | 18/20 (90%) | [69.9%, 97.2%] | 38/40 (95%) | [83.5%, 98.6%] | 51.28 | 97.0 |

### 4.2 消融结论
1. 本轮数据下, 各配置对攻击样本均保持 100% 防护动作, 差异主要来自良性误拦截。
2. `policy_only` 在当前任务集上优于 `policy_filter`, 说明硬规则预过滤可能过于保守。
3. `least_privilege` 与 `HITL` 在本次静态判定实验中未体现额外收益, 但在真实执行链路中仍具必要性 (见局限性)。

### 4.3 图表
已生成:
1. `results/security_score.png`
2. `results/tradeoff.png`
3. `results/ablation_delta.png`
4. `assets/generated/threat_architecture.png` (OpenRouter + Gemini image model)
5. `assets/generated/risk_matrix.png` (OpenRouter + Gemini image model)

## 5. 讨论
### 5.1 为什么“过滤更多”反而得分更低
确定性规则可快速兜底, 但对自然语言任务容易过拟合高危关键词, 把“讨论安全”误判为“执行攻击”。这会直接降低可用性, 并导致用户绕过安全层。

### 5.2 对产品架构的启示
推荐采用分层防御:
1. 入站层: URL allowlist + metadata endpoint 拦截 + token scope 检查。
2. 决策层: LLM 策略判定器 (结构化 JSON 输出 + 审计原因)。
3. 执行层: 最小权限工具箱 + 强制审计日志 + 高危动作 HITL。
4. 观测层: 针对“外传尝试、越权调用、异常循环”建立告警指标。

## 6. 局限性
1. 当前实验是“策略决策级”评估, 并非真实主机/容器上的完整攻击执行。
2. 样本规模较小 (每配置 40 条), 对细粒度差异的统计检验能力有限。
3. 攻击语料仍以手工构造为主, 需增加自适应红队自动生成。
4. 模型与提供商会迭代, 结果具有时效性。

## 7. 复现与开源
仓库与项目页:
1. https://github.com/giao-123-sun/llm-api-safety-lab
2. https://giao-123-sun.github.io/llm-api-safety-lab/

关键文件:
1. `run_pipeline.py`: 闭环主流程。
2. `src/experiment_runner.py`: 场景执行与消融统计。
3. `results/raw_results.csv`: 原始决策日志。
4. `results/summary.csv`: 聚合指标。

## 8. 伦理与安全声明
本文仅用于防御研究与安全评估。所有“攻击提示”均在受控实验中用于检测防护能力, 不用于未授权入侵。部署到生产前, 需进行法务与合规审查, 并落实最小权限和日志留存策略。

## 参考资料
1. OpenRouter Quickstart: https://openrouter.ai/docs/quickstart
2. OpenRouter Authentication: https://openrouter.ai/docs/api-reference/authentication
3. OpenRouter Model Page (Gemini 3.1 Flash Image Preview): https://openrouter.ai/google/gemini-3.1-flash-image-preview
4. Model Context Protocol Specification (2025-06-18): https://modelcontextprotocol.io/specification/2025-06-18
5. OWASP Top 10 for LLM Applications 2025: https://genai.owasp.org/llm-top-10/
6. OpenAI Agents Security Guide: https://openai.github.io/openai-agents-js/guides/security/
7. NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
8. MCP Safety Audit (arXiv): https://arxiv.org/abs/2506.13653

