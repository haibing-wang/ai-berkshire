"""
Joel Greenblatt's Magic Formula Calculator
Based on the framework from "The Little Book That Still Beats the Market":
Combines Return on Capital (ROC = EBIT / Tangible Capital Employed)
and Earnings Yield (EY = EBIT / Enterprise Value) to find good companies at bargain prices.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


def calculate_magic_formula(
    market_cap: float,
    ebit: float,
    total_debt: float = 0.0,
    cash: float = 0.0,
    tangible_capital: Optional[float] = None,
    net_working_capital: Optional[float] = None,
    net_fixed_assets: Optional[float] = None,
    risk_free_rate: float = 0.051,
) -> Dict[str, Any]:
    """
    Calculates:
    1. Enterprise Value (EV = Market Cap + Total Debt - Cash)
    2. Earnings Yield (EY = EBIT / EV) and comparison with risk-free rate
    3. Return on Capital (ROC = EBIT / Tangible Capital Employed)
    4. EV / EBIT valuation multiple and Greenblatt rating
    """
    # 1. 计算企业价值 (Enterprise Value)
    net_debt = total_debt - cash
    enterprise_value = market_cap + net_debt

    # 2. 计算盈利收益率 (Earnings Yield, EY = EBIT / EV)
    earnings_yield = (ebit / enterprise_value) if enterprise_value > 0 else 0.0
    ev_ebit_multiple = (enterprise_value / ebit) if ebit > 0 else 999.0

    # 3. 计算有形资本占用 (Tangible Capital Employed)
    if tangible_capital is None:
        if net_working_capital is not None and net_fixed_assets is not None:
            tangible_capital = max(1.0, net_working_capital + net_fixed_assets)
        else:
            # 默认粗略估计：若未提供，以市值或净资产的一定比例（通常由用户提供更精确值）
            tangible_capital = max(1.0, market_cap * 0.20)

    # 4. 计算资本回报率 (Return on Capital, ROC = EBIT / Tangible Capital)
    roc = (ebit / tangible_capital) if tangible_capital > 0 else 0.0

    # 5. 收益率相比无风险国债的利差 (EY Spread over Treasuries)
    ey_spread = earnings_yield - risk_free_rate

    # 6. 质量评级 (ROC Grade)
    if roc >= 0.50:
        roc_grade = "★★★★★ 超一流轻资产垄断 (资本效率极罕见)"
        quality_desc = "极其强大的商业护城河，几乎不依赖沉淀固定资本即可成倍放大盈利。"
    elif roc >= 0.25:
        roc_grade = "★★★★ 卓越商业 (强护城河)"
        quality_desc = "具备优秀的资本回报与定价权，新增资本投入回报丰厚。"
    elif roc >= 0.15:
        roc_grade = "★★★ 良好商业 (中等护城河)"
        quality_desc = "资本回报率中规中矩，足以覆盖资金成本并实现良性扩张。"
    elif roc >= 0.08:
        roc_grade = "★★ 平庸商业 (低壁垒/重资产)"
        quality_desc = "资本回报率接近宏观资金成本，再投资创造价值的能力薄弱。"
    else:
        roc_grade = "★ 价值毁灭型商业"
        quality_desc = "资本回报率低于无风险利率，企业占用大量资本却产出微薄。"

    # 7. 估值便宜度评级 (Earnings Yield Grade)
    if earnings_yield >= 0.12:
        val_grade = "🟢 深度价值 / 定价洼地 (EV/EBIT < 8.3x)"
        val_desc = "全资收购口径下的实际盈利回报率超过 12%，具备极高安全边际。"
    elif earnings_yield >= 0.08:
        val_grade = "🟢 显著便宜 (EV/EBIT 8.3x ~ 12.5x)"
        val_desc = "收益率明显超越无风险国债，股权提供厚实的超额风险补偿。"
    elif earnings_yield >= 0.05:
        val_grade = "🟡 估值合理中枢 (EV/EBIT 12.5x ~ 20.0x)"
        val_desc = "收益率与无风险利率相当，投资收益主要依赖公司未来内生成长。"
    elif earnings_yield > 0.0:
        val_grade = "🔴 昂贵 / 成长溢价严重 (EV/EBIT > 20.0x)"
        val_desc = "当期经营收益率远低于国债，股价高度透支未来多年高增长预期。"
    else:
        val_grade = "⛔ 亏损 / 负收益率"
        val_desc = "营业利润为负，无法按盈利收益率法进行定价。"

    # 8. 神奇公式综合判定
    if roc >= 0.25 and earnings_yield >= 0.08:
        overall_verdict = "💎 神奇公式黄金标的 (Good & Cheap)：同时满足高资本回报率与高盈利收益率！"
    elif roc >= 0.25 and earnings_yield < 0.05:
        overall_verdict = "🌟 好公司但不便宜 (Good but Expensive)：卓越的商业质量，但缺乏估值安全边际。"
    elif roc < 0.15 and earnings_yield >= 0.10:
        overall_verdict = "⚠️ 价值陷阱嫌疑 (Cheap but Low Quality)：看似估值低廉，但商业本质缺乏护城河。"
    else:
        overall_verdict = "⚖️ 中规中矩 / 观察仓位：等待更好的价格击球点或更强的护城河印证。"

    return {
        "market_cap": market_cap,
        "ebit": ebit,
        "total_debt": total_debt,
        "cash": cash,
        "net_debt": round(net_debt, 2),
        "enterprise_value": round(enterprise_value, 2),
        "tangible_capital": round(tangible_capital, 2),
        "roc_pct": round(roc * 100, 2),
        "roc_grade": roc_grade,
        "quality_desc": quality_desc,
        "earnings_yield_pct": round(earnings_yield * 100, 2),
        "ev_ebit_multiple": round(ev_ebit_multiple, 2),
        "val_grade": val_grade,
        "val_desc": val_desc,
        "risk_free_rate_pct": round(risk_free_rate * 100, 2),
        "ey_spread_pct": round(ey_spread * 100, 2),
        "overall_verdict": overall_verdict,
    }


def format_markdown_report(
    results: Dict[str, Any],
    company: str = "目标标的",
    unit: str = "亿美元 ($B)",
) -> str:
    """Format the Magic Formula calculation into a comprehensive GitHub Markdown section."""
    lines = [
        f"### 🪄 乔尔·格林布拉特神奇公式 (Magic Formula) 估值分析报告：{company}",
        "",
        "> “神奇公式的逻辑朴素到令人难以置信：**在保证高商业质量（高资本回报率 ROC）的前提下，以尽可能低廉的价格（高盈利收益率 Earnings Yield）买入**。把两者结合起来，就是价值投资最纯粹的本质。” —— 乔尔·格林布拉特 (Joel Greenblatt, 《The Little Book That Still Beats the Market》)",
        "",
        "#### 1. 神奇公式双核心指标诊断表",
        "",
        f"| 指标项目 | 测算数值 | 评估标准与含义 | 诊断与评级 |",
        f"|---|---|---|---|",
        f"| **评估公司 / 标的** | {company} | - | - |",
        f"| **当前总市值 ($Market\\,Cap$)** | {results['market_cap']:.2f} {unit} | 股权买入对价 | - |",
        f"| **有息总负债 / 净负债** | {results['total_debt']:.2f} / {results['net_debt']:.2f} {unit} | 负债与现金流动性调整 | {'净现金充裕' if results['net_debt'] < 0 else '存在净债务负担'} |",
        f"| **企业价值 ($EV = Cap + NetDebt$)** | **{results['enterprise_value']:.2f} {unit}** | 全资买断该公司的总收购成本 | 消除资本结构扭曲的核心基准 |",
        f"| **息税前营业利润 ($EBIT$)** | **{results['ebit']:.2f} {unit}** | 业务经营自身赚取的全部利润 | 不受利息与所得税影响 |",
        f"| **有形资本占用 ($Tangible\\,Capital$)** | {results['tangible_capital']:.2f} {unit} | 净营运资本 + 净固定资产 | 实体运营所必需的真实资产占用 |",
        f"| **① 资本回报率 ($ROC = EBIT / Capital$)** | **{results['roc_pct']:.2f}%** | **> 25.0% 判定为强护城河** | {results['roc_grade']} |",
        f"| **② 盈利收益率 ($EY = EBIT / EV$)** | **{results['earnings_yield_pct']:.2f}%** | **> 8.0% 判定为定价洼地** | {results['val_grade']} |",
        f"| **企业价值倍数 ($EV / EBIT$)** | **{results['ev_ebit_multiple']:.2f}x** | < 12.0x 较便宜 | 全资收购回本年限估算 |",
        f"| **10年期无风险国债收益率 ($r$)** | {results['risk_free_rate_pct']:.2f}% | 宏观机会成本底线 | 10Y US Treasury |",
        f"| **盈利收益率利差 ($EY - r$)** | **{results['ey_spread_pct']:+.2f}%** | > +3.0% 为安全边际厚实 | 全资经营回报相比稳拿国债的超额溢价 |",
        "",
        "#### 2. 神奇公式四象限综合定位",
        "",
        f"- **商业质量维度**：{results['quality_desc']}",
        f"- **估值廉价度维度**：{results['val_desc']}",
        f"- **综合裁决结论**：**{results['overall_verdict']}**",
        "",
        "#### 3. 经典四象限映射图景",
        "",
        "```",
        "         高盈利收益率 EY (便宜)",
        "                  ▲",
        "  [困境/周期低估]  │  [神奇公式黄金区 💎]",
        "  (低 ROC, 高 EY)  │  (高 ROC, 高 EY) <── 最佳买入击球区",
        " ─────────────────┼─────────────────► 高资本回报率 ROC (优质护城河)",
        "  [价值陷阱/平庸]  │  [好公司但不便宜 🌟]",
        "  (低 ROC, 低 EY)  │  (高 ROC, 低 EY) <── 需等待估值回调",
        "                  │",
        "         低盈利收益率 EY (昂贵)",
        "```",
        "",
        "#### 4. 格林布拉特选股纪律与反思",
        "- **防止资本回报率虚高 (Asset-Light Distortion)**：若公司因巨额商誉减值或过度激进外包导致分母有形资本过小，需穿透其研发费用资本化与供应链依赖；",
        "- **防止周期性顶峰诱惑 (Cyclical Peak Trap)**：若当前的高 EBIT 来自大宗商品或短期供需缺口的超级繁荣期，当期高 EY 可能是周期见顶的虚假信号；",
        "- **投资决策结论**：神奇公式最强大的威慑力在于**拒绝在昂贵的价格买入平庸的企业**，并强制投资者在市场由于短期悲观将高 ROC 的伟大商业错杀至高 EY 洼地时果断重仓。",
        "",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Joel Greenblatt's Magic Formula Calculator (ROC & Earnings Yield)."
    )
    parser.add_argument("--company", type=str, default="目标标的", help="Company name or ticker.")
    parser.add_argument("--market-cap", type=float, required=True, help="Current Market Capitalization.")
    parser.add_argument("--ebit", type=float, required=True, help="Annual Operating Profit / EBIT (TTM).")
    parser.add_argument("--total-debt", type=float, default=0.0, help="Total interest-bearing debt.")
    parser.add_argument("--cash", type=float, default=0.0, help="Cash and short-term liquid investments.")
    parser.add_argument("--tangible-capital", type=float, default=None, help="Net Working Capital + Net Fixed Assets.")
    parser.add_argument("--risk-free-rate", type=float, default=0.051, help="10-Year Treasury Yield (default 0.051).")
    parser.add_argument("--unit", type=str, default="亿美元 ($B)", help="Monetary unit (default: 亿美元 ($B)).")
    parser.add_argument("--output", type=str, default="", help="Path to write Markdown output report.")

    args = parser.parse_args()

    results = calculate_magic_formula(
        market_cap=args.market_cap,
        ebit=args.ebit,
        total_debt=args.total_debt,
        cash=args.cash,
        tangible_capital=args.tangible_capital,
        risk_free_rate=args.risk_free_rate,
    )

    print("=" * 66)
    print(f"      乔尔·格林布拉特神奇公式测算结果 [{args.company}]")
    print("=" * 66)
    print(f"当前市值 (Market Cap)           : {results['market_cap']:.2f} {args.unit}")
    print(f"企业价值 (Enterprise Value, EV) : {results['enterprise_value']:.2f} {args.unit} (净负债: {results['net_debt']:.2f})")
    print(f"息税前利润 (EBIT)               : {results['ebit']:.2f} {args.unit}")
    print(f"有形资本占用 (Tangible Capital) : {results['tangible_capital']:.2f} {args.unit}")
    print("-" * 66)
    print(f"① 资本回报率 (ROC = EBIT/Cap)  : {results['roc_pct']:.2f}%  [{results['roc_grade']}]")
    print(f"② 盈利收益率 (EY = EBIT/EV)    : {results['earnings_yield_pct']:.2f}%  [{results['val_grade']}]")
    print(f"企业价值倍数 (EV / EBIT)        : {results['ev_ebit_multiple']:.2f}x")
    print(f"盈利收益率利差 (EY - 10Y国债)   : {results['ey_spread_pct']:+.2f}% (国债基准: {results['risk_free_rate_pct']:.2f}%)")
    print("-" * 66)
    print(f"综合裁决                        : {results['overall_verdict']}")
    print("=" * 66)

    if args.output:
        md_text = format_markdown_report(results, company=args.company, unit=args.unit)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_text, encoding="utf-8")
        print(f"\n[+] 神奇公式测算 Markdown 结果已保存至: {out_path.resolve()}")


if __name__ == "__main__":
    main()
