## 📁 **Skill 目录**：`skills_antigravity/equity-bond-valuation/`
- 📄 [skill.md](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/equity-bond-valuation/skill.md)：工作流规范、数学不等式推演、报告章节模板与落盘规范。
- 🐍 [equity_bond_calculator.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/equity-bond-valuation/scripts/equity_bond_calculator.py)：股权债券预期回报分解与灵敏度矩阵测算脚本。

---

### 一、模型核心逻辑与数学不等式

该 Skill 将股票穿透为一张**“息票率会浮动的长期债券”**：
- 企业的账面净资产（Book Value）相当于债券面值；
- 企业的资本回报率（$ROE / ROIC$）相当于其票面息率；
- 投资者的长期复合回报率可严格拆解为三大驱动因子：

$$\text{长期年化持有回报率} \approx \underbrace{\frac{\text{自由现金流}}{\text{买入市值}}}_{\text{① 当期现金回报率 (FCF Yield)}} + \underbrace{(1 - \text{分红率}) \times \text{增量资本回报率 (ROIC)}}_{\text{② 留存收益内生复利增速}} \pm \underbrace{\Delta \left(\frac{P}{B}\right)^{1/n}}_{\text{③ 估值倍数均值回归}}$$

- **芒格铁律检验**：拉长 20~30 年来看，持有者的最终回报率将牢牢锚定在企业的长期资本回报率（$ROE$）附近；
- **机会成本裁决**：将测算出的综合年化收益率与当前 10 年期美债收益率直接对标，计算**股权风险溢价（Equity Risk Premium, ERP）**。若 $\text{ERP} < 0$，说明买股票的预期回报连稳拿国债都不如，坚决不碰。

---

### 二、Skill 架构与核心功能

#### 1. 测算工具能力 ([equity_bond_calculator.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/equity-bond-valuation/scripts/equity_bond_calculator.py))
- **回报三要素拆解**：自动计算 `当期 FCF Yield`、`留存收益驱动增速 (b × ROIC)`、以及可选项 `估值倍数 (P/B) 压缩/扩张影响`；
- **股权风险溢价 (ERP) 评定**：对比 10 年期美债基准，自动分级（极具吸引力 / 合理配置 / 吸引力微弱 / 负溢价严重透支）；
- **全维度灵敏度矩阵**：交叉生成不同 $ROIC$（8% ~ 30%）与不同分红留存比例（0% ~ 100%）下的年化收益矩阵；
- **Markdown 报告直接输出**：支持 `--output` 参数将测算表格与结论自动追加或落盘至 Markdown 研报。

#### 2. 标准调用命令示例

```bash
python3 skills_antigravity/equity-bond-valuation/scripts/equity_bond_calculator.py \
  --company "Apple (AAPL)" \
  --market-cap 35000 \
  --fcf 1080 \
  --roe 1.45 \
  --roic 0.55 \
  --payout-ratio 0.85 \
  --pb-entry 45.0 \
  --pb-exit 30.0 \
  --years 10 \
  --risk-free-rate 0.051 \
  --output "reports/Apple/Apple-equity-bond-20261020.md"
```

#### 3. 研报标准落盘规范
与 `risk-free-hurdle-valuation` 保持一致，执行分析后必须自动在 `reports/` 目录下生成独立研报：
`reports/{公司名}/{公司名}-equity-bond-{YYYYMMDD}.md`，包含以下标准章节：
1. **核心结论与股权评级摘要**（股权债券性质、综合年化回报、ERP、巴菲特一句话裁决）
2. **核心财务参数与双信源核验记录**
3. **股权债券化回报拆解与灵敏度矩阵表**
4. **资本分配效率审计**（留存收益是在“创造价值”还是在“毁灭价值”？ROIC 是否跑赢 WACC？）
5. **护城河可持续性与估值压缩压力测试**
6. **投资决策与安全边际买入价建议**
