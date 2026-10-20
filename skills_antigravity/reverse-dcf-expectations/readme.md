## 📁 **Skill 目录**：`skills_antigravity/reverse-dcf-expectations/`
- 📄 [skill.md](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/reverse-dcf-expectations/skill.md)：工作流规范、预期投资理论框架、报告章节模板与落盘规范。
- 🐍 [reverse_dcf_calculator.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/reverse-dcf-expectations/scripts/reverse_dcf_calculator.py)：反向 DCF 隐含复合增速求解、显性期现金流推演日程表与跨利率灵敏度矩阵计算脚本。

---

### 一、模型核心逻辑与反转视角

该 Skill 贯彻霍华德·马克斯与迈克尔·莫布森的**“预期投资与反向推演”**核心哲学：
> “聪明的投资者不拍脑袋预测未来，而是**用当前价格倒推市场在定价什么**。然后问自己：市场当前隐含的预期是过于悲观，还是已经完美无瑕？”

- **传统 DCF 弊端**：预测假设失真导致“垃圾进，垃圾出”；
- **反向 DCF 优势**：以当前市值作为锚定输入，二分法精确求解市场定价所隐含的未来 10 年自由现金流复合增速 $g_{implied}$，以及显性竞争优势期（CAP）；
- **预期差（Expectations Gap）定位**：
  - **完美无瑕（Priced for Perfection）**：$g_{implied} > 25\%$，市场透支未来所有利好，任何轻微不及预期即遭暴跌；
  - **合理定价（Fairly Priced）**：$g_{implied} \approx 10\% \sim 15\%$，与公司历史及行业均值匹配；
  - **极度悲观（Priced for Disaster）**：$g_{implied} \le 5\%$，市场过度恐慌，具备巨大的预期差修复暴利空间。

---

### 二、Skill 架构与核心功能

#### 1. 测算工具能力 ([reverse_dcf_calculator.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/reverse-dcf-expectations/scripts/reverse_dcf_calculator.py))
- **倒推市场隐含复合增速**：输入市值与基期 FCF，高精度求解 $g_{implied}$；
- **显性期 vs 永续期价值拆解**：输出预测期折现现金流占比与永续终值占比；
- **10年逐年现金流产生日程表**：推演未来 10 年公司单年所需达到的真金白银现金流；
- **多维度灵敏度矩阵**：交叉生成不同 WACC（7% ~ 11%）与永续增长率（1.5% ~ 3.5%）下的隐含增速矩阵；
- **Markdown 报告直接输出**：支持 `--output` 参数将测算表格落盘至研报。

#### 2. 标准调用命令示例

```bash
python3 skills_antigravity/reverse-dcf-expectations/scripts/reverse_dcf_calculator.py \
  --company "Apple (AAPL)" \
  --market-cap 35000 \
  --fcf 1080 \
  --wacc 0.09 \
  --terminal-growth 0.025 \
  --years 10 \
  --output "reports/Apple/Apple-reverse-dcf-20261020.md"
```

#### 3. 研报标准落盘规范
执行分析后必须自动在 `reports/` 目录下生成独立研报：
`reports/{公司名}/{公司名}-reverse-dcf-{YYYYMMDD}.md`，包含以下五大章节：
1. **核心结论与预期差评级摘要**（市场预期定性、隐含 FCF 复合增速、第 10 年所需现金流、终值占比、预期差裁决）
2. **核心财务参数与双信源核验记录**
3. **反向推演测算与灵敏度矩阵表**
4. **市场隐含预期 vs 商业物理常识的三重碰撞**
5. **霍华德·马克斯市场钟摆与反向投资赔率建议**
