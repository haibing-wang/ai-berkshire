---
name: risk-free-hurdle-valuation
description: Evaluate a stock's valuation using the risk-free hurdle rate framework (Duan Yongping/Buffett). Compares equity valuation against 10-year Treasury yield opportunity cost, calculates required earnings CAGR, and outputs complete research report to reports/{公司名}/{公司名}-risk-free-hurdle-{YYYYMMDD}.md.
---

# 无风险机会成本与增速门槛估值模型 (Risk-Free Hurdle Valuation)

本 Skill 基于**段永平与沃伦·巴菲特（Warren Buffett）的核心机会成本估值哲学**：
> “买股票就是买公司，买公司就是买其未来自由现金流的折现。如果连长期国债的无风险回报都跑不赢，那么承担商业经营与市场波动的风险就毫无意义。”

---

## Antigravity Adapter Note
- 将 `$ARGUMENTS` 视为用户在当前对话中指定的分析标的（如公司名称、美股/港股/A股代码，例如 `SpaceX`、`AAPL`、`腾讯`）。
- **投研基准日期**：开始投研前务必通过 `date` 命令确认今日日期，作为所有最新市值/估值/利率的基准，并在报告头部明确标明。
- **数据源规范**：市值、净利润/自由现金流（TTM）、10年期国债收益率必须经双独立信源交叉验证。
- **测算工具调用**：在工作区根目录下执行：
  `python3 skills_antigravity/risk-free-hurdle-valuation/scripts/valuation_calculator.py`
- **报告产出路径**：**必须保存至 `reports/{公司名}/{公司名}-risk-free-hurdle-{YYYYMMDD}.md`**，如目录不存在自动创建。

---

## 核心工作流 (Core Workflow)

### 1. 确定标的与基础数据收集 (双信源验证)
通过网络检索或相关数据工具获取当前标的的核心财务参数：
1. **当前总市值 / 估值 ($P_0$)**：
   - 上市公司：最新收盘价对应的总市值。
   - 非上市公司（如 SpaceX / ByteDance）：最新一轮融资、二级市场员工回购（tender offer）或公开发行估值。
2. **基准年度净利润 / 自由现金流 ($E_0$)**：
   - 优先采用过去 12 个月（TTM）真实归母净利润或自由现金流（Free Cash Flow）。
   - 若处于亏损或大额再投资期，需注明常态化/分业务运营利润（如 Starlink 营运利润）。
3. **10年期无风险国债收益率 ($r$)**：
   - 取当前最新的 10-Year US Treasury Yield（如 5.10% 即 0.051）。
4. **测算周期 ($n$)**：
   - 默认采用 10 年周期（与 10 年期国债期限严格匹配）。

### 2. 执行模型数值测算 (Python CLI)
运行计算脚本，完成机会成本门槛终值及倒推 CAGR 测算：

```bash
python3 skills_antigravity/risk-free-hurdle-valuation/scripts/valuation_calculator.py \
    --company "{公司名}" \
    --market-cap {市值} \
    --risk-free-rate {利率小数} \
    --current-earnings {基准利润} \
    --years 10 \
    --output "reports/{公司名}/{公司名}-risk-free-hurdle-{YYYYMMDD}.md"
```

**模型数学原理**：
1. **国债无风险终值**：$FV = P_0 \times (1 + r)^{10}$
2. **企业必须赚取的累计现金流门槛**：$\\Delta = FV - P_0$
3. **倒推隐含年复合利润增速 ($g$)**：
   $$\\sum_{t=1}^{10} E_0 \times (1 + g)^t = \\Delta$$
4. **第 10 年所需达到的单年净利润**：$E_{10} = E_0 \times (1 + g)^{10}$

### 3. 商业本质常识与可达性推演 (Qualitative Reality Check)
围绕倒推出来的增速门槛 $g$ 与第 10 年利润 $E_{10}$，进行商业常识核验：
- **行业天花板检查**：第 10 年所需的利润规模，相当于多少个当前全球行业的总利润？公司能否达到？
- **商业模式壁垒与定价权**：公司是靠量增、价增，还是靠垄断壁垒？利润率能否维持？
- **资本开支与稀释风险**：为实现该增长，需要消耗多少 Capex？自由现金流是否会被吞噬？股本是否会被股权激励大量稀释？
- **逆向思考（反面检验）**：如果达不到这一门槛，最可能的破绽在哪里（技术替代、地缘政治、竞争加剧、关键人物风险）？

### 4. 生成完整研报并持久化落盘
将深度研究成果完整写入：
`reports/{公司名}/{公司名}-risk-free-hurdle-{YYYYMMDD}.md`

---

## 报告标准结构规范 (Report Layout Template)

每个输出报告必须包含以下核心章节：

```markdown
# {公司名} 投资估值研究报告：无风险机会成本与增速门槛分析

**报告日期**：YYYY年MM月DD日  
**数据截断日期**：YYYY年MM月DD日  
**研究框架**：段永平 / 巴菲特无风险利率机会成本模型 (10-Year Risk-Free Hurdle Rate)  
**分析标的**：{公司名} ({Ticker / 资产性质})  

---

## 0. 核心结论与投资评级摘要
- **当前估值状态**：[严重透支 / 合理中枢 / 显著低估]
- **国债终值机会成本**：投入本金 $P_0$ 买 10 年国债可得 $FV$
- **企业必须赚取门槛**：未来 10 年累计必须产生 $\\Delta$ 净利润/现金流
- **倒推所需年复合增速 (CAGR)**：$g\%$
- **常识判断**：[极具挑战 / 审慎乐观 / 轻易达成]
- **段永平视角核心一句话判断**

---

## 1. 核心财务参数与无风险基准
（列出当前市值、当前TTM利润/FCF、美债收益率及双信源核验记录）

---

## 2. 机会成本测算与 10 年推演日程表
（插入 valuation_calculator.py 生成的核心参数表及逐年现金流日程表）

---

## 3. 商业模式与增长引擎解构
- 主营业务构成与现金流造血点
- 护城河深浅与商业定价权
- 资本开支强度与真实自由现金流转换率

---

## 4. 门槛可达性与逆向风险检验 (Charlie Munger Inverse Thinking)
- 规模与行业天花板测算
- 股权稀释与再融资拖累
- 最可能导致不及格的 3 个致命风险

---

## 5. 投资决策与安全边际建议
- 什么样的价格才算“便宜到不用动脑筋”？
- 理想买入价位区间与持有策略
```
