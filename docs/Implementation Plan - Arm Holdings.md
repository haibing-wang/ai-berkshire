# Arm Holdings (NASDAQ: ARM) 投资研究分析实施计划

本计划严格依据 [skills_antigravity/investment-research.md](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/investment-research.md) 的标准流程，对芯片架构 IP 巨头 **Arm Holdings plc (NASDAQ: ARM)** 展开系统化投资研究，全面融合巴菲特、芒格、段永平、李录四位投资大师的方法论，并执行严格的程序化金融数据交叉核验与准出流程。

## User Review Required

> [!IMPORTANT]
> **关于数据基准日与报告存放路径**：
> - **基准日期**：已通过系统 `date` 命令确认为 **2026-09-06**。
> - **报告保存路径**：按照 Antigravity 规范，将保存至 `reports_antigravity/Arm/Arm-research-20260906.md`。
> - **核心矛盾预判**：Arm 是典型的“极品商业模式（垄断级护城河）+ 极高估值定价（PE 200+，PS 50+）”。本次研究将重点聚焦在段永平式的“商业确定性”与芒格式的“极端估值容错率”之间的博弈。

## Open Questions

无阻断性问题。本次分析将完全遵从四大师投研流程与数据交叉准出规范自动推进。

---

## Proposed Research & Implementation Steps

### 1. 前置步骤：AI 研究偏见自觉
- **信息丰富度评级**：评定为 **A 级（信息充裕）**（上市超3年、券商覆盖极其密集、媒体报道海量、全球半导体核心标的）。
- **AI 偏见防范策略**：防范“市场共识过强与极度乐观叙事”陷阱，重点执行芒格式逆向思考——“聪明人为什么不买/做空 Arm？在当前 2500 亿美元以上市值下，隐含的预期有多脆弱？”

### 2. 第一步：数据收集与程序化交叉验证
- **双源数据检索**：
  - 数据源：SEC Form 20-F、StockAnalysis、Yahoo Finance / Morningstar。
- **强制程序化验证（调用本地 Python 工具）**：
  - Step 1: `python3 tools/financial_rigor.py verify-market-cap`（股价 $252.09 × 1.07B 股本 = $269.25B 市值）
  - Step 2: `python3 tools/financial_rigor.py cross-validate`（核验 FY2026/FY2025 营业收入、净利润、自由现金流 FCF、净现金储备）
  - Step 3: `python3 tools/financial_rigor.py verify-valuation`（PE、PB、FCF Yield 等估值指标验算）

### 3. 第二步至第六步：四大师深度分析框架
- **第二步：生意本质分析（段永平）**：
  - 定义生意本质：“半导体行业的数字化版税收割机与中立军火商”。
  - 拆解 License（技术授权）与 Royalty（芯片出货版税）双轮驱动模式，95%+ 毛利率与极高自由现金流转化率。
- **第三步：护城河评估（巴菲特）**：
  - 评估五类护城河：生态系统与架构指令集（ISA）迁移天堑、软件工具链（LLVM/GCC/OS）网络效应、v9 架构双倍版税率定价权、CSS（计算子系统）对单芯片价值量的提升。
- **第四步：逆向思考与风险清单（芒格）**：
  - “可能失败的所有路径”：RISC-V 开源生态在微控制器与数据中心的替代侵蚀；软银（持有约 90% 股份）质押与潜在减持的流动性抽血；与高通（Qualcomm）的授权诉讼后续；Arm China（安谋科技）的治理与地缘政治风险；超高估值对任何轻微增速下滑的毁灭性惩罚。
- **第五步：管理层评估（段永平 + 巴菲特）**：
  - CEO Rene Haas 的战略转型执行力（推进 v9 渗透与 CSS 战略）；软银孙正义在控制权、资本配置和 AI 战略中的双刃剑角色。
- **第六步：行业与文明趋势（李录）**：
  - 文明级范式演进：AI 算力从集中式云端向边缘端（Edge AI：手机、PC、汽车、机器人）渗透，能效比（Perf/Watt）成为终极硬约束；云原生自研芯片（AWS Graviton、Google Axion、微软 Cobalt）全部转向 Arm。

### 4. 第七步：估值与安全边际（巴菲特 + 段永平）
- **反向 DCF 计算**：测算当前市值隐含了未来 10 年多高的复合增长率与利润率假设。
- **三情景估值（3年维度）**：
  - 运行 `python3 tools/financial_rigor.py three-scenario` 精确计算乐观、中性、悲观情景下的合理市值与目标价。
- **长期折现与终值推演（10年尺度）**：
  - 执行 `python3 tools/terminal_value.py audit` 审查币种一致性、分母宽度及离散风险。
  - 执行 `python3 tools/terminal_value.py pe` 与 `irr` 推演 10 年确定性调整后回报。

### 5. 第八步：综合决策备忘录
- 汇总四大师六维度评分表与决策建议（空仓者、持仓者、加仓/减仓触发信号）。
- 四位大师的拟真锐评。

### 6. 输出与准出审计流程（Quality Audit）
- 完整报告生成并保存至 `reports_antigravity/Arm/Arm-research-20260906.md`。
- 执行 `python3 tools/report_audit.py extract --report ...` 抽取 15% 随机样本。
- 执行 `python3 tools/report_audit.py verdict` 输出数据核验准出判决。
- 执行 `python3 tools/terminal_value.py audit` 完成终值模型复检。

---

## Verification Plan

### Automated Tests & Rigorous Tool Execution
```bash
# 1. 验证市值与股本
python3 tools/financial_rigor.py verify-market-cap --price 252.09 --shares 1.068e9 --reported 269.25e9 --currency USD

# 2. 多源交叉验证关键财务指标
python3 tools/financial_rigor.py cross-validate --field revenue --values '{"Form 20-F": 4.92, "StockAnalysis": 4.92}' --unit "B USD"
python3 tools/financial_rigor.py cross-validate --field net_income --values '{"Form 20-F": 0.904, "StockAnalysis": 0.904}' --unit "B USD"

# 3. 三情景估值
python3 tools/financial_rigor.py three-scenario --price 252.09 --eps 0.85 --shares 1.068 --growth 0.35 0.25 0.15 --pe 80 50 30 --years 3 --currency USD

# 4. 终值估值硬约束准出检查
python3 tools/terminal_value.py audit --currency USD --r 0.10 --roic 0.30 --g 0.02,0.035,0.045 --rf 0.04 --beta 1.0 --discrete-risks "RISC-V替代:情景,软银减持:尾部档,ArmChina断供:情景"

# 5. 准出抽检与裁决
python3 tools/report_audit.py extract --report reports_antigravity/Arm/Arm-research-20260906.md
python3 tools/report_audit.py verdict --results '<verified_json>' --report reports_antigravity/Arm/Arm-research-20260906.md
```

### Manual Verification
- 检查报告结构是否完整满足 `skills_antigravity/investment-research.md` 9 项输出要求。
- 确认报告开头具备信息丰富度评级与局限性声明，结尾明确区分“AI 分析置信度”与“实际投资确定性”。
