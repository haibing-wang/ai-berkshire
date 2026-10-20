---
name: magic-formula-evaluator
description: Evaluate a company using Joel Greenblatt's Magic Formula framework. Combines Return on Capital (ROC = EBIT / Tangible Capital) and Earnings Yield (EY = EBIT / Enterprise Value) to diagnose business quality vs bargain pricing. Outputs complete research report to reports/{公司名}/{公司名}-magic-formula-{YYYYMMDD}.md.
---

# 乔尔·格林布拉特神奇公式估值模型 (Joel Greenblatt's Magic Formula)

本 Skill 基于**乔尔·格林布拉特（Joel Greenblatt）在《股市稳赢秘密（The Little Book That Still Beats the Market）》中开创的“神奇公式”投资哲学**：
> “把投资简化到最纯粹的本质：**在保证高商业质量（高资本回报率 ROC）的前提下，以尽可能低廉的价格（高盈利收益率 Earnings Yield）买入**。买好公司（高 ROC）能确保资本以高效率复利，以便宜的价格买入（高 EY）能提供深厚的安全边际。将两者双因子排序，就是战胜市场的核心武器。”

---

## Antigravity Adapter Note
- 将 `$ARGUMENTS` 视为用户在当前对话中指定的分析标的（如公司名称、美股/港股/A股代码，例如 `GOOGL`、`AAPL`、`茅台`、`腾讯`）。
- **投研基准日期**：开始投研前务必通过 `date` 命令确认今日日期，作为所有最新市值/估值/财报的基准，并在报告头部明确标明。
- **数据源规范**：总市值、息税前利润（EBIT）、总有息负债、现金及等价物、净营运资本（NWC）与固定资产净值（Net PP&E）、10年期美债收益率必须经双独立信源交叉验证。
- **测算工具调用**：在工作区根目录下执行：
  `python3 skills_antigravity/magic-formula-evaluator/scripts/magic_formula_calculator.py`
- **报告产出路径**：**必须保存至 `reports/{公司名}/{公司名}-magic-formula-{YYYYMMDD}.md`**，如目录不存在自动创建。

---

## 核心模型理论与双核心指标拆解 (Mathematical Framework)

### 1. 指标一：资本回报率 (Return on Capital, ROC) —— 衡量“公司有多好”
格林布拉特对传统 ROE 与 ROA 进行了彻底净化，剔除财务杠杆与无息流动负债的扭曲：

$$ROC = \frac{EBIT}{\text{有形资本占用 (Tangible Capital Employed)}}$$

- **分子：息税前利润 ($EBIT$)**
  - 反映企业主营业务本身赚取的经营利润，不受不同资本结构（负债利息）和不同税收管辖区（所得税率）的会计失真影响。
- **分母：有形资本占用 ($Tangible Capital$)**
  - $\text{有形资本占用} = \text{净营运资本 (Net Working Capital)} + \text{净固定资产 (Net PP&E)}$；
  - 净营运资本 = (流动资产 - 超额现金) - (流动负债 - 短期有息负债)；
  - **核心剔除**：剔除无形资产与商誉（防范并购粉饰），剔除超额现金（现金不计入实体运营资本占用）。
- **商业意义**：衡量企业每投入 1 块钱的实体厂房、设备与流动资金，能净赚回多少钱。**$ROC > 25\%$** 是识别超级护城河的黄金硬指标。

### 2. 指标二：盈利收益率 (Earnings Yield, EY) —— 衡量“价格有多便宜”
格林布拉特用企业价值倍数反转替代了传统的市盈率（P/E），消除了不同杠杆企业的估值不可比性：

$$Earnings Yield = \frac{EBIT}{\text{企业价值 (Enterprise Value, EV)}}$$

- **分母：企业价值 ($EV$)**
  - $EV = \text{总市值 (Market Cap)} + \text{有息总负债 (Total Debt)} - \text{现金与等价物 (Cash)}$；
  - 代表全资买断该公司的总收购成本（买下全部股权并清偿全部债务）。
- **商业意义**：相当于你如果把整家公司全部买下，该公司的经营活动每年能为你创造的现金回报率。**$EY > 8\% \sim 10\%$** 且显著超越 10 年期美债收益率，是识别定价洼地与安全边际的关键。

### 3. 神奇公式四象限综合定性

```
         高盈利收益率 EY (便宜)
                  ▲
  [困境反转/周期低估] │  [神奇公式黄金区 💎]
  (低 ROC, 高 EY)   │  (高 ROC, 高 EY) <── 最佳买入击球区
 ──────────────────┼──────────────────► 高资本回报率 ROC (优质护城河)
  [价值陷阱/低效平庸] │  [好公司但不便宜 🌟]
  (低 ROC, 低 EY)   │  (高 ROC, 低 EY) <── 需等待估值均值回归
                  │
         低盈利收益率 EY (昂贵)
```

---

## 核心工作流 (Core Workflow)

### 1. 确定标的与基础数据收集 (双信源验证)
通过网络检索或相关数据工具获取当前标的的核心财务参数：
1. **当前总市值 ($Market\\,Cap$)**
2. **息税前营业利润 ($EBIT$)**（TTM 口径）
3. **资产负债表负债与现金**：有息总负债（短期+长期借款+应付债券）、现金及短投资产；
4. **有形资本占用 ($Tangible\\,Capital$)**：
   - 净营运资本（经营性流动资产 - 经营性流动负债）
   - 固定资产净值（Net Property, Plant & Equipment）
5. **10年期无风险国债收益率 ($r$)**（基准机会成本）

### 2. 执行模型数值测算 (Python CLI)
运行计算脚本，完成 ROC、Earnings Yield、EV/EBIT 与四象限定位：

```bash
python3 skills_antigravity/magic-formula-evaluator/scripts/magic_formula_calculator.py \
    --company "{公司名}" \
    --market-cap {当前市值} \
    --ebit {EBIT} \
    --total-debt {总负债} \
    --cash {现金储备} \
    --tangible-capital {有形资本占用} \
    --risk-free-rate 0.051 \
    --output "reports/{公司名}/{公司名}-magic-formula-{YYYYMMDD}.md"
```

### 3. 商业本质与防伪排查 (Quality & Value False Signal Checks)
- **防伪检查 1：ROC 是否被轻资产外包与商誉掩盖虚高？**
  - 检查公司是否通过轻资产代工将重资产剥离给供应链，导致分母极小？
- **防伪检查 2：EY 是否处于周期繁荣顶点的假象？**
  - 周期股在景气度顶点时 EBIT 极其庞大，导致静态 EY 极高，但往往预示行业拐点即将到来；
- **防伪检查 3：全资买断视角检验**：
  - 如果私人资本以当前 EV 全资买下这家公司，每年的经营现金流能否在 8~10 年内完全收回本金？

### 4. 生成完整研报并持久化落盘
将深度研究成果完整写入：
`reports/{公司名}/{公司名}-magic-formula-{YYYYMMDD}.md`

---

## 报告标准结构规范 (Report Layout Template)

每个输出报告必须包含以下核心章节：

```markdown
# {公司名} 投资研究报告：乔尔·格林布拉特神奇公式估值分析 (Magic Formula)

**报告日期**：YYYY年MM月DD日  
**数据截断日期**：YYYY年MM月DD日  
**研究框架**：乔尔·格林布拉特神奇公式模型 (Joel Greenblatt Magic Formula: ROC & Earnings Yield)  
**分析标的**：{公司名} ({Ticker / 资产性质})  

---

## 0. 核心结论与神奇公式评级摘要
- **神奇公式综合定位**：[黄金标的(Good & Cheap) / 好公司但不便宜 / 价值陷阱 / 昂贵平庸]
- **资本回报率 ($ROC$)**：$X.XX\%$（商业质量与护城河评级）
- **盈利收益率 ($Earnings Yield$)**：$X.XX\%$（全资收购口径实际回报率）
- **企业价值倍数 ($EV / EBIT$)**：$X.XX$x
- **盈利收益率利差 ($EY - r$)**：相比 10 年美债超额 $+X.XX\%$
- **格林布拉特一句话投资裁决**

---

## 1. 核心财务参数与双信源核验记录
（列出当前市值、EV、EBIT、有形资本占用、负债结构及双信源凭证）

---

## 2. 神奇公式双核心指标诊断与四象限定位
（插入 magic_formula_calculator.py 生成的双核心指标诊断表与综合评定）

---

## 3. 商业质量深度穿透：资本回报率 (ROC) 护城河成色
- 有形资本占用的真实结构（存货、应收、固定资产运转效率）
- 极高 ROC 的来源分析：垄断定价权、规模效应、品牌溢价还是无形资产？
- 资本回报率防伪测试：是否存在研发资本化、资产出表或周期峰值扭曲？

---

## 4. 估值便宜度检验：盈利收益率 (Earnings Yield) 与资本结构穿透
- EV 对比总市值：净现金还是净负债拖累？
- 全资收购视角：若以当前 EV 买下整家公司，经营回报能否稳健跑赢国债？
- EV/EBIT 相比历史中枢与同业龙头的折溢价幅度

---

## 5. 神奇公式投资决策与击球点建议
- 达到“黄金标的（ROC > 25% 且 EY > 8%）”所允许的最高买入股价与市值
- 理想买入价格区间与组合配置建议
```
