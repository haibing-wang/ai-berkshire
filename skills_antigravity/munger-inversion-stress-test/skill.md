---
name: munger-inversion-stress-test
description: Evaluate a company using Charlie Munger's Inversion and Checklist stress test framework. Instead of predicting how much money a company will make, stress tests the fatal thresholds: breakeven gross margin, revenue drop tolerance, and debt refinancing fatal interest rate. Outputs complete research report to reports/{公司名}/{公司名}-munger-inversion-{YYYYMMDD}.md.
---

# 查理·芒格逆向思维与负面清单压力测试 (Munger Inversion & Checklist Stress Test)

本 Skill 基于**查理·芒格（Charlie Munger）终身践行的“反转思维与负面清单”核心哲学**：
> “反过来想，总是反过来想（Invert, always invert）。如果我知道自己会死在哪里，我将永远不去那个地方。很多人试图通过预测未来能赚多少钱来投资，而我们试图发现什么事情会让我们‘在半夜惊醒或彻底毁灭’，然后像避开瘟疫一样避开它们。” —— 查理·芒格

---

## Antigravity Adapter Note
- 将 `$ARGUMENTS` 视为用户在当前对话中指定的分析标的（如公司名称、美股/港股/A股代码，例如 `TSLA`、`SpaceX`、`波音`、`万科`）。
- **投研基准日期**：开始投研前务必通过 `date` 命令确认今日日期，作为所有最新市值/财报/利率的基准，并在报告头部明确标明。
- **数据源规范**：营业收入、毛利润/营业成本、营业利润（EBIT）、利息支出、有息总负债、现金与等价物、资本开支（Capex）必须经双独立信源交叉验证。
- **测算工具调用**：在工作区根目录下执行：
  `python3 skills_antigravity/munger-inversion-stress-test/scripts/inversion_stress_calculator.py`
- **报告产出路径**：**必须保存至 `reports/{公司名}/{公司名}-munger-inversion-{YYYYMMDD}.md`**，如目录不存在自动创建。

---

## 核心模型理论与逆向检验防线 (Inversion Framework)

传统投研往往陷入“乐观预测陷阱”——假设收入年年增长、利润率持续扩张。芒格逆向模型彻底反其道而行之：**假设暴风雨已经来临，测算企业的结构性弱点与破产临界点**。

### 1. 第一道防线：毛利率破产临界点 (Breakeven Margin)
- **经营性保本点**：毛利率下跌几个百分点，营业利润（EBIT）直接归零？
  $$\Delta GM_{EBIT=0} = \text{Current Operating Margin} = \frac{EBIT}{Revenue}$$
- **现金流失血断裂点**：在固定营运费用、利息支出与维持性 Capex 的刚性刚兑下，毛利率跌到什么程度，企业将无法依靠自身造血维系生存？
  $$\text{Cash Breakeven GM} = \frac{\text{Fixed Opex} + \text{Interest} + \text{Capex}}{Revenue}$$

### 2. 第二道防线：营收断崖容忍极限 (Revenue Drop Tolerance)
- 假设变动成本率可控，但折旧、房租、核心研发与管理费用等固定支出刚性粘性存在：
  $$\text{营收允许下滑极限} = 1 - \frac{\text{Fixed Opex}}{\text{Gross Margin}} = \frac{EBIT}{\text{Gross Profit}}$$
- 检验：在遭遇行业寒冬、制裁、技术替代或大客户流失时，营收最多允许跌多少比例企业才不至于陷入实质性亏损？

### 3. 第三道防线：高息环境负债展期与“致命借款利率” (Debt Shock & Fatal Interest Rate)
- 在长期高利率宏观环境下，存量低息有息负债到期必须以当前高利率（如 7.5%~9.0%）重新展期发债：
  - 新增额外利息支出：$\Delta Interest = \text{Total Debt} \times (r_{refinance} - r_{current})$
  - 利息侵蚀度：新增利息占当前 EBIT 的百分比；
- **致命借款利率 ($r_{fatal}$)**：
  $$r_{fatal} = \frac{EBIT}{\text{Total Debt}}$$
  当企业负债展期重定价利率达到 $r_{fatal}$ 时，**企业所有辛辛苦苦赚来的经营利润，将全部被利息开支吃光**，沦为为银行打工的“僵尸企业”。

### 4. 芒格反面清单排查 (Checklist of Deadly Sins)
不仅核算财务硬指标，更需核查以下毁灭商业价值的**四大致命病灶**：
1. **短债长投与流动性错配**：短期债务是否远超现金储备？
2. **大客户与单一供应链集中度**：前五大客户营收占比是否 > 50%？关键零部件是否存在单点卡脖子？
3. **技术颠覆脆弱性 (Disruption Fragility)**：核心现金牛是否面临颠覆性降维打击（如算力架构演进、大模型替代、颠覆性材料）？
4. **管理层道德风险与治理赤字**：大额关联交易、激进商誉并购、核心技术人员依赖度。

---

## 核心工作流 (Core Workflow)

### 1. 确定标的与基础数据收集 (双信源验证)
通过网络检索或相关数据工具获取当前标的的核心财务参数：
1. **营业收入 ($Revenue$) 与毛利润 ($Gross Profit$)**（TTM 口径）
2. **息税前营业利润 ($EBIT / Operating Income$)**
3. **利息支出 ($Interest Expense$) 与有息总负债 ($Total Debt$)**（短期借款 + 长期借款 + 应付债券）
4. **现金及等价物 ($Cash$) 与资本开支 ($Capex$)**
5. **当前宏观基准再融资利率 ($r_{refinance}$)**（默认取 7.5% 优质企业发债或高息借贷基准）

### 2. 执行模型数值测算 (Python CLI)
运行计算脚本，完成压力测试指标计算与毛利率侵蚀情景矩阵推演：

```bash
python3 skills_antigravity/munger-inversion-stress-test/scripts/inversion_stress_calculator.py \
    --company "{公司名}" \
    --revenue {营收} \
    --gross-profit {毛利润} \
    --operating-income {营业利润} \
    --interest-expense {利息支出} \
    --total-debt {有息负债} \
    --cash {现金储备} \
    --capex {资本开支} \
    --refinance-rate 0.075 \
    --output "reports/{公司名}/{公司名}-munger-inversion-{YYYYMMDD}.md"
```

### 3. 展开负面清单核查与逆向破产推演 (Inversion Scenario Analysis)
围绕测算出的临界阈值，展开针对性情景推演：
- **如果毛利率被同行价格战蚕食 5~8 个百分点，公司会怎样？**
- **如果存量债务在今年或明年集中到期，再融资成本上升，利息保障倍数会跌破 3x 吗？**
- **最可能让这家公司在 5 年内走向重组或破产的三种致命情景是什么？**

### 4. 生成完整研报并持久化落盘
将逆向压力测试完整成果写入：
`reports/{公司名}/{公司名}-munger-inversion-{YYYYMMDD}.md`

---

## 报告标准结构规范 (Report Layout Template)

每个输出报告必须包含以下核心章节：

```markdown
# {公司名} 投资研究报告：查理·芒格逆向思维与负面清单压力测试 (Inversion & Checklist)

**报告日期**：YYYY年MM月DD日  
**数据截断日期**：YYYY年MM月DD日  
**研究框架**：查理·芒格反转思维模型 (Charlie Munger Inversion & Stress Test Framework)  
**分析标的**：{公司名} ({Ticker / 资产性质})  

---

## 0. 核心结论与生存韧性评级摘要
- **生存韧性评级**：[坚不可摧 / 良好抗压 / 脆弱高危 / 处于失血边缘]
- **毛利率破产红线**：毛利率下跌 $X.XX\%$ 营业利润归零；下跌 $X.XX\%$ 现金流彻底断裂
- **营收断崖容忍极限**：营收最多允许下滑 $-X.XX\%$
- **高息展期致命利率 ($r_{fatal}$)**：借款利率达到 $X.XX\%$ 时营业利润被利息吞光
- **净现金防御垫**：净现金 / 净负债为 $X.XX 亿美元
- **芒格一句话警示**

---

## 1. 核心财务参数与双信源核验记录
（列出当前营收、毛利、营业利润、负债结构、利息支出及双信源核验凭据）

---

## 2. 破产临界点测算与压力测试矩阵
（插入 inversion_stress_calculator.py 生成的三道防线对比表、高息展期侵蚀表及毛利下行模拟矩阵）

---

## 3. 负债结构与再融资失血压力剖析
- 债务到期时间表分布（是否存在未来 12-24 个月集中到期偿债高峰）
- 宏观高利率环境下，存量发债重定价对当期净利润的刚性挤压
- 银行授信额度与外部救助假设的脆弱性

---

## 4. 芒格负面清单深度核查 (Checklist of Fatal Vulnerabilities)
- **价格战 / 成本通胀防御力**：上游涨价或下游压价时，谁在承受挤压？
- **技术颠覆与护城河蒸发风险**：是否存在“技术突然变轨”使重资产投入变成废铁的隐患？
- **单点故障与集中度风险**：关键客户、关键供应商、关键高管单一依赖风险
- **隐性资产负债表地雷**：商誉、存货跌价、质押借款、表外担保排查

---

## 5. 芒格反面裁决与安全边际准则
- 什么样的价格才足以补偿潜在的毁灭性风险？
- 触发“一票否决（Pass / Run Away）”的硬性条件
- 投资持有期间的“生命体征监测指标”（警报信号）
```
