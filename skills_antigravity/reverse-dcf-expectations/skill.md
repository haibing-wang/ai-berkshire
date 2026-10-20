---
name: reverse-dcf-expectations
description: Evaluate market implied expectations using Howard Marks' and Michael Mauboussin's Reverse DCF framework. Inverts DCF valuation to solve for what the current market price implies about future FCF growth, Competitive Advantage Period (CAP), and expectations gap. Outputs complete research report to reports/{公司名}/{公司名}-reverse-dcf-{YYYYMMDD}.md.
---

# 反向现金流折现与共识预期推演模型 (Reverse DCF & Implied Expectations)

本 Skill 基于**霍华德·马克斯（Howard Marks）的“钟摆理论与反射性原理”**与**迈克尔·莫布森（Michael Mauboussin）的“预期投资（Expectations Investing）”框架**：
> “绝大多数投资者做 DCF 都是‘用一堆拍脑袋的预测假设去推导一个目标价’，这往往是‘垃圾进，垃圾出’。真正专业的做法是反向推演（Reverse DCF）：**把当前市值作为已知输入，倒推市场当前定价隐含了公司未来多少年的复合增速与竞争优势期（CAP）？** 然后问自己：市场隐含的共识预期是过于悲观，还是已经完美无瑕？”

---

## Antigravity Adapter Note
- 将 `$ARGUMENTS` 视为用户在当前对话中指定的分析标的（如公司名称、美股/港股/A股代码，例如 `NVDA`、`AAPL`、`TSLA`、`腾讯`）。
- **投研基准日期**：开始投研前务必通过 `date` 命令确认今日日期，作为所有最新市值/估值/利率的基准，并在报告头部明确标明。
- **数据源规范**：总市值、自由现金流（TTM FCF）、WACC（资本成本）、长期国债收益率必须经双独立信源交叉验证。
- **测算工具调用**：在工作区根目录下执行：
  `python3 skills_antigravity/reverse-dcf-expectations/scripts/reverse_dcf_calculator.py`
- **报告产出路径**：**必须保存至 `reports/{公司名}/{公司名}-reverse-dcf-{YYYYMMDD}.md`**，如目录不存在自动创建。

---

## 核心模型理论与预期差分析 (Expectations Gap)

### 1. 传统 DCF vs 反向 DCF
- **传统 DCF 弊端**：微调折现率或第 8 年的增速假设 1%，算出来的估值可能相差 30%~50%，极易沦为给既有偏见背书的数字游戏。
- **反向 DCF 威力**：
  $$P_0 = \sum_{t=1}^{N} \frac{FCF_0 \times (1 + g_{\text{implied}})^t}{(1 + WACC)^t} + \frac{FCF_N \times (1 + g_{\text{terminal}})}{(WACC - g_{\text{terminal}}) \times (1 + WACC)^N}$$
  - 将当前股价 $P_0$ 设为锚定点，精确反解出 $g_{\text{implied}}$（市场隐含增速）；
  - 测算市场给出的显性竞争优势期（Competitive Advantage Period, CAP）跨度。

### 2. 霍华德·马克斯市场钟摆与预期差分类
- **完美无瑕（Priced for Perfection，钟摆极度乐观端）**：
  - 隐含复合增速 $g_{\text{implied}} \ge 25\% \sim 35\%$；
  - 市场假定未来 10 年行业爆发、份额垄断、利润率只升不降。任何微小的业绩放缓、Capex 超支或竞争加剧都会触发预期杀跌（戴维斯双杀）。
- **合理反映（Fairly Priced，钟摆中枢）**：
  - 隐含复合增速 $g_{\text{implied}} \approx 10\% \sim 15\%$，与公司历史复合增速和行业天花板基本吻合。
- **极度悲观（Priced for Disaster，钟摆极度悲观端）**：
  - 隐含复合增速 $g_{\text{implied}} \le 3\% \sim 6\%$（甚至负增长）；
  - 市场共识认为公司已经进入永久衰退期。只要公司实际经营“没有预想的那么糟”，即会爆发极其巨大的预期差修复暴利（戴维斯双击）。

---

## 核心工作流 (Core Workflow)

### 1. 确定标的与基础数据收集 (双信源验证)
通过网络检索或相关数据工具获取当前标的的核心财务参数：
1. **当前总市值 ($P_0$)**：最新股价对应的总对价；
2. **基准年度真实自由现金流 ($FCF_0$)**：过去 12 个月（TTM）经营活动现金流净额减去维持性资本开支；
3. **加权平均资本成本 ($WACC$)**：通常基于无风险利率（如 10Y 美债 5.1%）+ 股票 Beta $\times$ 股权风险溢价（通常在 8.5% ~ 10.0%）；
4. **永续增长率 ($g_{\text{terminal}}$)**：通常取长期宏观 GDP 名义增速（2.0% ~ 3.0%）；
5. **显性预测期 ($N$)**：默认采用 10 年（标准竞争优势周期）。

### 2. 执行反向推演测算 (Python CLI)
运行计算脚本，完成隐含增速求解、现金流推演日程表与灵敏度矩阵计算：

```bash
python3 skills_antigravity/reverse-dcf-expectations/scripts/reverse_dcf_calculator.py \
    --company "{公司名}" \
    --market-cap {当前市值} \
    --fcf {TTM自由现金流} \
    --wacc 0.09 \
    --terminal-growth 0.025 \
    --years 10 \
    --output "reports/{公司名}/{公司名}-reverse-dcf-{YYYYMMDD}.md"
```

### 3. 商业常识与预期差审计 (Expectations Gap Audit)
围绕求出的隐含增速 $g_{\text{implied}}$，进行三层穿透对比：
- **与公司历史真实增速对比**：过去 3 年、5 年的复合增速是多少？未来 10 年要求加速还是减速？
- **与行业天花板对比**：第 10 年所需的现金流规模，是否会超过整个全球细分赛道的市场空间？
- **霍华德·马克斯钟摆位置裁决**：当前共识预期处于周期的哪一段？是贪婪狂热还是恐慌抛售？

### 4. 生成完整研报并持久化落盘
将深度研究成果完整写入：
`reports/{公司名}/{公司名}-reverse-dcf-{YYYYMMDD}.md`

---

## 报告标准结构规范 (Report Layout Template)

每个输出报告必须包含以下核心章节：

```markdown
# {公司名} 投资研究报告：反向现金流折现与市场隐含预期推演 (Reverse DCF)

**报告日期**：YYYY年MM月DD日  
**数据截断日期**：YYYY年MM月DD日  
**研究框架**：迈克尔·莫布森与霍华德·马克斯反向推演模型 (Reverse DCF & Expectations Investing)  
**分析标的**：{公司名} ({Ticker / 资产性质})  

---

## 0. 核心结论与预期差评级摘要
- **市场预期定性**：[极度悲观定价 / 合理中枢定价 / 完美无瑕过度透支]
- **市场当前隐含 FCF 复合增速 ($g_{implied}$)**：未来 10 年需维持 $X.XX\%$
- **第 10 年所需自由现金流体量**：单年需创造 $X.XX 亿美元 现金流（相比基期放大 $X.XX$ 倍）
- **显性期 vs 终值价值结构**：未来 10 年折现价值占比 $X\%$，永续终值占比 $X\%$
- **预期差与霍华德·马克斯一句话裁决**

---

## 1. 核心财务参数与双信源核验记录
（列出当前市值、基准自由现金流、WACC折现率、永续增长率及信源凭证）

---

## 2. 反向推演测算与灵敏度矩阵
（插入 reverse_dcf_calculator.py 生成的核心参数表、逐年现金流推演表及跨利率灵敏度矩阵）

---

## 3. 市场隐含预期 vs 商业物理常识的三重碰撞
- **历史增速对照**：当前市场要求的增速相比历史中枢是否脱离现实？
- **行业空间与天花板检验**：第 10 年所需的 FCF 是否会突破行业渗透率天花板？
- **市场给出的竞争优势期 (CAP) 长度**：公司护城河是否能撑过这么久的衰退期？

---

## 4. 霍华德·马克斯市场钟摆与反射性风险分析
- 当前股价所处的情绪极端度（极度狂热 vs 极度冷落）
- 业绩如果发生 10%~20% 的微小 miss，市场预期的反噬烈度
- 催化剂与预期差重估的触发场景

---

## 5. 反向投资决策与赔率建议
- 什么样的价格才算具备“非对称赔率（Asymmetric Odds）”？
- 理想买入安全边际价格区间与建仓策略
```
