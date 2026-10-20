## 📁 **Skill 目录**：`skills_antigravity/munger-inversion-stress-test/`
- 📄 [skill.md](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/munger-inversion-stress-test/skill.md)：工作流规范、逆向思维防线推演、报告章节模板与落盘规范。
- 🐍 [inversion_stress_calculator.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/munger-inversion-stress-test/scripts/inversion_stress_calculator.py)：破产临界点（毛利/营收容忍极限）、负债高息展期侵蚀与压力情景测试脚本。

---

### 一、模型核心逻辑与反转视角

该 Skill 贯彻查理·芒格**“反过来想，总是反过来想”**的投资哲学：
> “如果我知道自己会死在哪里，我将永远不去那个地方。”
不测算公司在顺风时能赚多少钱，而是测算**在遭遇暴风雨时，什么样的极端条件会让企业失血致死或投资逻辑彻底破裂**。

- **第一道防线：毛利率破产临界点（Breakeven Margin）**
  - 毛利率下跌几个百分点，营业利润（EBIT）直接清零？
  - 毛利率跌破多少，在刚性费用、利息与维持 Capex 下企业现金流彻底断裂？
- **第二道防线：营收断崖容忍极限（Revenue Drop Tolerance）**
  - 在固定成本粘性下，外部黑天鹅最多允许营收缩水多少比例？
- **第三道防线：高息再融资负债吞噬与致命利率（$r_{fatal}$）**
  - 存量负债到期重定价，利息会吃掉百分之多少的营业利润？借款利率达到多少时全公司营业利润被利息吞光？
- **芒格负面清单排查（Checklist of Deadly Sins）**
  - 短债长投、大客户/供应商集中度、技术颠覆脆弱性、隐性负债地雷。

---

### 二、Skill 架构与核心功能

#### 1. 测算工具能力 ([inversion_stress_calculator.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/munger-inversion-stress-test/scripts/inversion_stress_calculator.py))
- **破产与失血双临界点**：自动求解 $\Delta GM_{EBIT=0}$ 与 $\Delta GM_{Cash}$；
- **高息展期重定价侵蚀**：测算新增利息支出及对 EBIT 的吞噬比例；
- **求解致命借款利率 ($r_{fatal}$)**：输出企业负债承载极限；
- **毛利蚕食多情景矩阵**：动态推演价格战/成本上涨下经营与现金流的健康状态；
- **Markdown 报告直接输出**：支持 `--output` 参数将测算表格落盘至研报。

#### 2. 标准调用命令示例

```bash
python3 skills_antigravity/munger-inversion-stress-test/scripts/inversion_stress_calculator.py \
  --company "Apple (AAPL)" \
  --revenue 3900 \
  --gross-profit 1800 \
  --operating-income 1200 \
  --interest-expense 35 \
  --total-debt 1050 \
  --cash 650 \
  --capex 110 \
  --refinance-rate 0.075 \
  --output "reports/Apple/Apple-munger-inversion-20261020.md"
```

#### 3. 研报标准落盘规范
与前序模型保持一致，执行分析后必须自动在 `reports/` 目录下生成独立研报：
`reports/{公司名}/{公司名}-munger-inversion-{YYYYMMDD}.md`，包含以下标准章节：
1. **核心结论与生存韧性评级摘要**（生存韧性评级、毛利率破产红线、营收断崖极限、致命借款利率、芒格一句话警示）
2. **核心财务参数与双信源核验记录**
3. **破产临界点测算与压力测试矩阵**
4. **负债结构与再融资失血压力剖析**
5. **芒格负面清单深度核查（四大致命病灶）**
6. **芒格反面裁决与一票否决准则**
