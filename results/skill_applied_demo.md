# Scientific Skills 应用演示（基于 K-Dense-AI/claude-scientific-skills）

## 1) `literature-review` 的直接用处
该 skill 的价值不在“多找几篇文献”，而在把文献工作标准化为可复现流程：检索策略、纳排标准、去重、主题归纳、证据缺口识别。  
下面是针对当前课题（LLM API/Agent Safety）的已落地结果。

### 1.1 已下载核心文献（本地）
1. `papers/2023_Greshake_IndirectPromptInjection.pdf`
2. `papers/2023_Liu_FormalizingBenchmarkingPI.pdf`
3. `papers/2023_Ruan_ToolEmu.pdf`
4. `papers/2024_Debenedetti_AgentDojo.pdf`
5. `papers/2025_Debenedetti_CaMeL.pdf`
6. `papers/2025_Alizadeh_DataLeakageAgentDojo.pdf`
7. `papers/2025_Choudhary_DataFlipKAD.pdf`
8. `papers/2025_Shi_PromptArmor.pdf`
9. `papers/2025_Wang_AGENTVIGIL.pdf`

### 1.2 主题化综合（而非逐篇摘要）
现有研究可分四层成熟度：
1. 攻击可行性层（2023）：证明间接提示注入与工具链污染真实可行。
2. Benchmark 层（2023-2025）：建立动态任务与攻击基准，量化 ASR/utility tradeoff。
3. 防御架构层（2025）：能力隔离（CaMeL）与分层检测（PromptArmor）。
4. 部署工程层（本项目）：BYO `api_key/baseurl/model` 网关策略与审计闭环。

这让我们清楚知道：你的项目定位不是“再造一个 benchmark”，而是“把安全策略做成可上线的 API 网关能力”。

## 2) `statistical-analysis` 的直接用处
该 skill 的核心价值是：把“看起来有效”升级为“统计上可解释且可审稿”。

### 2.1 当前结果的统计表达（已可进论文）
以当前 `results/raw_results.csv`（每 profile 40 样本）为例：
1. `baseline/policy_only`：Attack block 20/20，Benign allow 20/20，Security score=100。
2. `policy_filter` 系列：Attack block 20/20，Benign allow 18/20，Security score=97。
3. 95% CI（Wilson）显示：在小样本下区间仍较宽，提示“当前差异有方向性，但证据强度仍有限”。

### 2.2 对下一轮实验的统计改造建议
1. 扩大样本到每配置至少 200+（而不是 40），提升检验功效。
2. 对 `benign_allow_rate` 的 profile 差异做两比例检验并报告效应量。
3. 报告不止均值：同时给出 CI、显著性、以及实际效应大小。
4. 增加“自适应攻击者”分层，避免只在静态攻击集上乐观。

## 3) `scientific-writing` 的直接用处
该 skill 的关键是把“点状要点”改造成“可发表段落叙事”（IMRAD + 流畅段落 + 引用逻辑）。  
下面给出对你论文摘要与讨论的改写示例。

### 3.1 摘要改写示例（段落体）
本研究关注一种高频产品模式：平台允许用户自行提供 `api_key`、`baseurl` 与 `model` 以接入大模型 API。该模式虽然降低了平台推理成本，却将密钥管理、路由完整性与能力边界的风险转移到了更脆弱的部署链路上。我们构建了一个闭环评估流程，对提示注入、密钥外传、SSRF-like 路由滥用、工具与 MCP 能力滥用等场景进行系统实验，并在五种防御配置下完成消融分析。结果表明，在当前样本中各配置对攻击样本均实现了高拦截率，但确定性预过滤策略带来了可观的良性误拦截，导致整体安全-可用性综合得分下降。该结果说明，真实工程中应优先采用“策略判定 + 最小权限 + 审计升级”的分层架构，而非单纯堆叠规则过滤。

### 3.2 讨论改写示例（段落体）
与已有研究相比，本工作并不试图替代 AgentDojo、ToolEmu 或 AGENTVIGIL 这类运行时基准，而是补足部署侧缺口：当用户可控 `baseurl/model` 且系统开放工具权限时，API 网关应如何进行前置风险判定与可审计拒绝。我们的消融结果显示，过强的硬规则过滤会把“安全讨论类正常请求”误判为攻击，从而牺牲系统可用性并诱发绕过行为。这一观察与近期关于检测器脆弱性及防御-可用性权衡的结论一致。下一步应把当前决策级评估扩展到真实执行链路，测量工具调用层面的泄露率、越权率与恢复能力，并在更大样本和多模型环境下报告稳健的置信区间与显著性结果。

## 4) 结论：这个 skill 的实用价值
1. `literature-review`：把“找资料”升级成“可复现综述方法学”。  
2. `statistical-analysis`：把“结果表格”升级成“可审稿统计证据”。  
3. `scientific-writing`：把“要点罗列”升级成“可投稿段落叙事”。  

你的项目已经具备数据和工程闭环，这三个 skill 的组合价值是：把它快速推到“更接近可发表/可评审”的标准。

