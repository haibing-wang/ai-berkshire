## 📁 **Skill 目录**：`skills_antigravity/bottleneck-hunter/`
- 📄 [skill.md](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/bottleneck-hunter/skill.md)：供应链分层物理拆解、S/A级瓶颈判定、估值红黄绿灯检验与研报落盘工作流。
- 🐍 [bottleneck_evaluator.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/bottleneck-hunter/scripts/bottleneck_evaluator.py)：TAM估值红灯排查、10年25x PE退出年化回报测算与瓶颈星级评估脚本。
- 🐍 [twstock_data.py](file:///Users/wanghaibing/code/ai/ai-berkshire/skills_antigravity/bottleneck-hunter/scripts/twstock_data.py)：台股供应链标的实时财务、行情与关键月营收抓取工具。

---

### 一、核心理念与评估逻辑

不问"AI推荐什么股票"，问**"如果这个超级趋势继续扩张，物理世界哪一环会先不够用？"**
- 避开第一层已被充分定价的龙头（GPU/电力/整机）；
- 深挖第二层、第三层卡脖子环节（光模块/激光器/特种材料/先进封装载板）；
- **瓶颈真实 ≠ 投资机会**：强制执行估值红黄绿灯与 10 年退出回报测算，防止在 100 倍 PS 接盘亏损炒作标的。

### 二、标准调用命令示例

```bash
# 1. 测算标的瓶颈评级与估值安全边际
python3 skills_antigravity/bottleneck-hunter/scripts/bottleneck_evaluator.py \
  --trend "AI Infrastructure" \
  --company "Coherent (COHR)" \
  --market-cap 150 \
  --revenue 50 \
  --tam 500 \
  --revenue-growth 0.35 \
  --ps 3.0 \
  --pe 35.0 \
  --gross-margin-trend "up" \
  --lead-time 18 \
  --market-share 0.40 \
  --output "reports/bottleneck-map/COHR-eval-20261020.md"

# 2. 查询台股供应链标的（如台积电2330、世芯3661）行情与月营收验证量价齐升
python3 skills_antigravity/bottleneck-hunter/scripts/twstock_data.py quote 2330
python3 skills_antigravity/bottleneck-hunter/scripts/twstock_data.py revenue 2330
```
