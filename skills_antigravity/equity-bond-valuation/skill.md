---
name: equity-bond-valuation
description: Evaluate a company using Warren Buffett and John Burr Williams' Equity as an Equity Bond valuation model. Treats equity as a bond with a variable coupon, calculating long-term returns from FCF yield, retained earnings reinvestment at ROIC, and multiple reversion. Outputs complete research report to reports/{公司名}/{公司名}-equity-bond-{YYYYMMDD}.md.
---

# 股权债券化估值模型 (Equity as an Equity Bond Valuation)

本 Skill 基于**约翰·伯尔·威廉姆斯（John Burr Williams）、沃伦·巴菲特（Warren Buffett）与查理·芒格（Charlie Munger）的核心投资模型**：
> “股票从本质上讲，是一张息票率会浮动的‘股权债券’（Equity Bond）。企业的账面净资产是债券面值，ROE 是它的票面息率，留存收益以增量 ROIC 在企业内部再投资，相当于利息按高利率自动滚存。” —— 沃伦·巴菲特 (1977, 《How Inflation Swindles the Equity Investor》)

---

## Antigravity Adapter Note
- 将 `$ARGUMENTS` 视为用户在当前对话中指定的分析标的（如公司名称、美股/港股/A股代码，例如 `AAPL`、`腾讯`、`茅台`、`MSFT`）。
- **投研基准日期**：开始投研前务必通过 `date` 命令确认今日日期，作为所有最新价格/市值/利率的基准，并在报告头部明确标明。
- **数据源规范**：市值、净利润/自由现金流（TTM）、长期均值 ROE/ROIC、股利分红率与回购规模、10年期国债收益率必须经双独立信源交叉验证。
- **测算工具调用**：在工作区根目录下执行：
  `python3 skills_antigravity/equity-bond-valuation/scripts/equity_bond_calculator.py`
- **报告产出路径**：**必须保存至 `reports/{公司名}/{公司名}-equity-bond-{YYYYMMDD}.md`**，如目录不存在自动创建。

---

## 核心模型理论与数学不等式 (Mathematical Framework)

### 1. 股权债券的三重现金流回报分解
长期持有股票的年化复合回报率（CAGR）可以严格拆解为三大驱动因子：

$$\text{长期年化持有回报率} \approx \underbrace{\frac{\text{自由现金流}}{\text{买入市值}}}_{\text{① 当期现金回报率 (FCF Yield)}} + \underbrace{(1 - \text{分红率}) \times \text{增量资本回报率 (ROIC)}}_{\text{② 留存收益内生复合增速}} \pm \underbrace{\Delta \left(\frac{P}{B}\right)^{1/n}}_{\text{③ 估值倍数均值回归}}$$

- **因子 ①：当期现金回报率 (FCF / Shareholder Yield)**
  - 企业每年以现金分红和股票回购形式真金白银返还给股东的收益率（$\\frac{\\text{Dividends + Buybacks}}{P_0}$ 或 $\\frac{\\text{FCF}}{P_0}$）。
- **因子 ②：留存收益内生复利增速 (Retained Earnings Growth)**
  - 留存比率 $b = 1 - \\text{Payout Ratio}$。
  - 企业不分红的留存收益，如果能在内部以高增量资本回报率（Incremental ROIC）继续运转，将驱动每股内在价值按 $b \\times \\text{ROIC}$ 的速率复利增长。
- **因子 ③：估值乘数均值回归 (Multiple Expansion / Compression)**
  - 若买入时市净率 $P/B_{entry}$ 极高，到期末向合理中枢 $P/B_{exit}$ 回归，每年将产生估值收缩拖累：$(P/B_{exit} / P/B_{entry})^{1/n} - 1$。

### 2. 查理·芒格的 ROE 长期铁律
> “拉长周期（20~30年）来看，股票持有者的最终复合回报率，很难显著超过该商业本身所赚取的资本回报率（ROE）。如果一家公司长期 ROE 只有 6%~8%，哪怕你当初以很便宜的市盈率买入，最终回报也只能趋于 6%~8%；反之，如果一家公司长期 ROIC 能维持在 20%+，即便当初买入价看似昂贵，最终回报率也会惊人地接近 20%。”

### 3. 机会成本对标：股权风险溢价 (Equity Risk Premium, ERP)
将模型测算出的**股权债券预期年化复合收益率**与**10年期无风险国债收益率**直接比拼：
$$\text{ERP} = \text{预期股权债券年化收益率} - \text{10年期国债收益率}$$
- **ERP $\ge +5.0\%$**：极具吸引力，拥有高额商业风险补偿与安全边际；
- **$+2.0\% \le \text{ERP} < +5.0\%$**：合理回报区间；
- **$0.0\% \le \text{ERP} < +2.0\%$**：吸引力微弱，承担商业波动风险却仅获国债级回报；
- **ERP $< 0.0\%$**：**严重透支 / 负风险溢价**，买股票不如买国债，坚决不碰。

---

## 核心工作流 (Core Workflow)

### 1. 确定标的与基础数据收集 (双信源验证)
通过网络检索或相关数据工具获取当前标的的核心财务参数：
1. **当前总市值 ($P_0$)**：最新收盘价对应的总市值。
2. **基准自由现金流 ($FCF_0$) 或归母净利润 ($E_0$)**：取过去 12 个月（TTM）真实可自由支配现金流。
3. **长期稳态资本回报率 (ROE 与 ROIC)**：
   - 过去 5 年至 10 年的中枢 ROE（排除杠杆粉饰）。
   - 增量投入资本回报率（Incremental ROIC = $\\frac{\\Delta NOPAT}{\\Delta Invested Capital}$）。
4. **资本分配政策 (Payout Ratio)**：
   - 现金分红率与股份回购力度（$Payout = \\frac{\\text{Dividends + Net Buybacks}}{\\text{Net Income}}$）。
   - 留存再投资比率 $b = 1 - Payout$。
5. **当前估值倍数与合理中枢 ($P/B$ 或 $P/E$)**：
   - 当前买入倍数 $P/B_{entry}$，以及未来 10 年合理常态化估值中枢 $P/B_{exit}$。
6. **10年期无风险国债收益率 ($r$)**：取当前最新 10-Year Treasury Yield（如 5.10%）。

### 2. 执行模型数值测算 (Python CLI)
运行专用计算脚本，完成回报三要素分解、ERP 测算以及灵敏度矩阵推演：

```bash
python3 skills_antigravity/equity-bond-valuation/scripts/equity_bond_calculator.py \
    --company "{公司名}" \
    --market-cap {当前市值} \
    --fcf {TTM自由现金流} \
    --roe {长期ROE小数} \
    --roic {增量ROIC小数} \
    --payout-ratio {分红回购率小数} \
    --pb-entry {当前PB} \
    --pb-exit {期末合理PB} \
    --years 10 \
    --risk-free-rate {国债利率小数} \
    --output "reports/{公司名}/{公司名}-equity-bond-{YYYYMMDD}.md"
```

### 3. 商业本质与资本分配审计 (Capital Allocation Audit)
围绕模型关键变量，展开深度商业常识审计：
- **留存收益是在“创造价值”还是在“毁灭价值”？**
  - 若 $\text{ROIC} > \text{资本成本 (WACC)}$：企业留存再投资是在给股东造肉，应鼓励低分红、高再投资；
  - 若 $\text{ROIC} < \text{资本成本}$：企业盲目扩张是把金子换成铜，必须 100% 分红回购，否则留存越多毁灭价值越快。
- **高 ROIC 护城河的持久性 (Fade Rate 衰退分析)**：
  - 当前的高资本回报率是来自品牌壁垒、网络效应、转换成本，还是周期性顺风？
  - 未来 10 年竞争对手是否会拉平这种超额收益？
- **估值乘数风险**：
  - 当前是否支付了过高的商誉溢价？如果未来市净率/市盈率腰斩回归均值，内生增长能否消化估值压缩？

### 4. 生成完整研报并持久化落盘
将深度研究成果完整写入：
`reports/{公司名}/{公司名}-equity-bond-{YYYYMMDD}.md`

---

## 报告标准结构规范 (Report Layout Template)

每个输出报告必须包含以下核心章节：

```markdown
# {公司名} 投资估值研究报告：股权债券化模型分析 (Equity as an Equity Bond)

**报告日期**：YYYY年MM月DD日  
**数据截断日期**：YYYY年MM月DD日  
**研究框架**：巴菲特-威廉姆斯股权债券化模型 (Equity as an Equity Bond Framework)  
**分析标的**：{公司名} ({Ticker / 资产性质})  

---

## 0. 核心结论与股权评级摘要
- **股权债券性质**：[极高息票永续现金牛 / 周期波动息票 / 价值毁灭型低息券]
- **当期现金分红/FCF收益率**：$X.XX\%$
- **留存收益内生增长率**：$b \times \text{ROIC} = X.XX\%$
- **预期年化综合复合回报 (CAGR)**：$X.XX\%$（含/不含估值均值回归影响）
- **股权风险溢价 (ERP)**：相比 10 年美债超额 $+X.XX\%$
- **投资评级与巴菲特一句话裁决**

---

## 1. 核心财务参数与双信源核验记录
（列出当前市值、自由现金流、长期ROE/ROIC、分红回购率、美债收益率等核心参数）

---

## 2. 股权债券化回报拆解与灵敏度矩阵
（插入 equity_bond_calculator.py 生成的三要素拆解表及不同 ROIC 与分红率组合下的回报率矩阵）

---

## 3. 资本分配效率审计：留存收益创造价值还是毁灭价值？
- 增量资本回报率 (ROIC) vs 加权资本成本 (WACC) 对比
- 历史上“赚到的钱都去哪了”：分红、回购、资本开支还是盲目并购？
- 留存收益转化为每股内在价值的实际效率（巴菲特的“留存一美元原则”）

---

## 4. 护城河可持续性与估值压缩压力测试 (Multiple Fade Test)
- 护城河能否在未来 10~20 年抵御资本收益率均值回归？
- 如果买入估值（P/B 或 P/E）在未来 10 年回落至历史中枢，年化回报会被侵蚀多少？
- 芒格铁律检验：最终投资回报率是否会不可避免地锚定在其 ROE 水平？

---

## 5. 投资决策与安全边际建议
- 达到期望投资收益率（如年化 12%~15% 或国债 +5% ERP）所允许的最高买入估值
- 理想买入价格区间与操作建议
```
