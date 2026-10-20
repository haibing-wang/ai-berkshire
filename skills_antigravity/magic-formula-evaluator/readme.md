## 📁 **Skill 目录**：`skills_antigravity/magic-formula-evaluator/`
- 📄 [skill.md](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/magic-formula-evaluator/skill.md)：工作流规范、神奇公式理论模型、报告章节模板与落盘规范。
- 🐍 [magic_formula_calculator.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/magic-formula-evaluator/scripts/magic_formula_calculator.py)：资本回报率 (ROC) 与盈利收益率 (Earnings Yield) 测算、四象限定位与报告导出脚本。

---

### 一、模型核心逻辑与双核心指标

该 Skill 贯彻乔尔·格林布拉特**“好公司（高 ROC）+ 便宜价格（高 EY）”**的经典神奇公式哲学：
> “把投资简化到最纯粹的本质：**在保证高商业质量（高资本回报率 ROC）的前提下，以尽可能低廉的价格（高盈利收益率 Earnings Yield）买入**。”

1. **资本回报率 (Return on Capital, ROC = EBIT / Tangible Capital)**
   - 衡量每占用 1 块钱的实体厂房、设备与流动资金，能净赚多少息税前利润；
   - 排除负债杠杆与税率扭曲，**ROC > 25%** 是衡量顶级护城河的黄金指标。
2. **盈利收益率 (Earnings Yield, EY = EBIT / EV)**
   - 衡量全资买断该公司总价值（EV）后的真实经营现金回报率；
   - 排除杠杆不可比性，**EY > 8%~10%** 且大幅跑赢 10 年美债，是安全边际与定价洼地标志。
3. **四象限定位图景**：
   - 💎 **神奇公式黄金区 (Good & Cheap)**：高 ROC + 高 EY（最佳击球区）；
   - 🌟 **好公司但不便宜 (Good but Expensive)**：高 ROC + 低 EY（需等待回调）；
   - ⚠️ **价值陷阱 (Cheap but Low Quality)**：低 ROC + 高 EY（谨防低效与周期顶）；
   - ⛔ **平庸昂贵**：低 ROC + 低 EY（坚决不碰）。

---

### 二、Skill 架构与核心功能

#### 1. 测算工具能力 ([magic_formula_calculator.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/magic-formula-evaluator/scripts/magic_formula_calculator.py))
- **企业价值 (EV) 与净负债测算**：自动消除资本结构失真；
- **资本回报率 (ROC) 质量分级**：自动映射至 1~5 星商业质量诊断；
- **盈利收益率 (EY) 估值分级**：自动计算全资收购倍数 (EV/EBIT) 与美债利差 (EY - r)；
- **四象限综合判定**：输出是否属于“神奇公式黄金标的”的一键裁决；
- **Markdown 报告直接输出**：支持 `--output` 参数将测算表格落盘至研报。

#### 2. 标准调用命令示例

```bash
python3 skills_antigravity/magic-formula-evaluator/scripts/magic_formula_calculator.py \
  --company "Apple (AAPL)" \
  --market-cap 35000 \
  --ebit 1200 \
  --total-debt 1050 \
  --cash 650 \
  --tangible-capital 600 \
  --risk-free-rate 0.051 \
  --output "reports/Apple/Apple-magic-formula-20261020.md"
```

#### 3. 研报标准落盘规范
执行分析后必须自动在 `reports/` 目录下生成独立研报：
`reports/{公司名}/{公司名}-magic-formula-{YYYYMMDD}.md`，包含以下五大章节：
1. **核心结论与神奇公式评级摘要**（神奇公式综合定位、ROC 与 EY 数值、EV/EBIT、国债利差、格林布拉特一句话裁决）
2. **核心财务参数与双信源核验记录**
3. **神奇公式双核心指标诊断与四象限定位**
4. **商业质量深度穿透：资本回报率 (ROC) 护城河成色**
5. **估值便宜度检验：盈利收益率 (Earnings Yield) 与安全边际**
6. **神奇公式投资决策与击球点建议**
