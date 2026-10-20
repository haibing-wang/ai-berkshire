"""
Supply Chain Bottleneck Hunter Evaluator
Evaluates bottleneck positioning, TAM valuation lights (Red/Yellow/Green),
pricing power, expansion lead-time, and 10-year exit return.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


def evaluate_bottleneck(
    trend: str,
    company: str,
    market_cap: float,
    revenue: float,
    tam: float,
    revenue_growth: float,
    ps: Optional[float] = None,
    pe: Optional[float] = None,
    gross_margin_trend: str = "up",
    expansion_lead_time_months: int = 18,
    market_share: float = 0.50,
    exit_pe: float = 25.0,
    net_margin_estimate: float = 0.20,
) -> Dict[str, Any]:
    """
    Evaluates bottleneck quality and valuation safety margin:
    1. Valuation Lights (Red/Yellow/Green)
    2. 10-Year 25x Exit PE Annualized Return (IRR)
    3. Bottleneck Star Rating (1 to 5 Stars)
    """
    if ps is None:
        ps = market_cap / revenue if revenue > 0 else 0.0

    red_flags: List[str] = []
    yellow_flags: List[str] = []
    green_flags: List[str] = []

    # 1. 估值红灯排查
    # 红灯 1: 市值 > TAM 的 20%
    tam_cap_ratio = (market_cap / tam * 100) if tam > 0 else 0.0
    if tam > 0 and market_cap > 0.20 * tam:
        red_flags.append(f"市值占 TAM 比例达到 {tam_cap_ratio:.1f}% (超过 20% 警戒红线，预期过度内化)")

    # 红灯 2: PS > 30x 且 收入增速 < 100%
    if ps > 30.0 and revenue_growth < 1.0:
        red_flags.append(f"PS 高达 {ps:.1f}x 且收入增速仅 {revenue_growth*100:.1f}% (不足 100% 豁免门槛，估值严重透支)")

    # 红灯 3: 市值 > 5年乐观收入预测的 10 倍 (假定前5年维持当前增速复合增长)
    proj_rev_5y = revenue * ((1.0 + min(revenue_growth, 0.60)) ** 5)
    if market_cap > 10.0 * proj_rev_5y:
        red_flags.append(f"市值 ({market_cap:.1f}亿) 超过 5 年乐观收入预测 ({proj_rev_5y:.1f}亿) 的 10 倍")

    # 2. 估值黄灯排查
    if pe is not None and pe > 80.0:
        yellow_flags.append(f"静态 PE 达 {pe:.1f}x (超过 80x，需超高 PEG 支撑)")
    if ps > 15.0 and (pe is None or pe <= 0):
        yellow_flags.append(f"亏损状态下 PS 达 {ps:.1f}x (超过 15x，须明确盈利拐点时间表)")

    # 3. 估值绿灯排查
    if ps < 10.0 and revenue_growth > 0.15:
        green_flags.append(f"PS 为 {ps:.1f}x (< 10x) 且收入正向增长，具备估值安全垫")
    if pe is not None and 0 < pe < 30.0:
        green_flags.append(f"PE 为 {pe:.1f}x (< 30x) 具备合理估值安全边际")

    # 4. 10 年 25x PE 退出年化复合回报率 (IRR) 测算
    # 假设前 5 年复合增速为 revenue_growth (封顶 35%)，后 5 年放缓至 15%
    growth_phase1 = min(revenue_growth, 0.35)
    growth_phase2 = 0.15
    terminal_rev = revenue * ((1.0 + growth_phase1) ** 5) * ((1.0 + growth_phase2) ** 5)
    terminal_profit = terminal_rev * net_margin_estimate
    terminal_market_cap = terminal_profit * exit_pe
    annualized_return = (
        ((terminal_market_cap / market_cap) ** 0.10) - 1.0 if market_cap > 0 else 0.0
    )

    exit_return_safe = annualized_return >= 0.10

    # 5. 瓶颈信号强度评级 (1 - 5 星)
    score = 3
    if market_share >= 0.50:
        score += 1
    if expansion_lead_time_months >= 18:
        score += 1
    if gross_margin_trend.lower() == "up":
        score += 1
    if red_flags:
        score = min(score, 2)  # 有红灯强制封顶 2 星

    score = max(1, min(5, score))
    star_str = "★" * score + "☆" * (5 - score)

    return {
        "trend": trend,
        "company": company,
        "market_cap": market_cap,
        "revenue": revenue,
        "tam": tam,
        "tam_cap_ratio_pct": round(tam_cap_ratio, 1),
        "revenue_growth_pct": round(revenue_growth * 100, 1),
        "ps": round(ps, 2),
        "pe": round(pe, 2) if pe is not None else None,
        "gross_margin_trend": gross_margin_trend,
        "expansion_lead_time_months": expansion_lead_time_months,
        "market_share_pct": round(market_share * 100, 1),
        "exit_pe": exit_pe,
        "annualized_return_pct": round(annualized_return * 100, 2),
        "exit_return_safe": exit_return_safe,
        "star_rating": star_str,
        "score": score,
        "red_flags": red_flags,
        "yellow_flags": yellow_flags,
        "green_flags": green_flags,
    }


def format_markdown_report(
    results: Dict[str, Any],
    unit: str = "亿美元 ($B)",
) -> str:
    """Format evaluation into structured GitHub Markdown."""
    lines = [
        f"### 🔬 供应链瓶颈扫描与估值检验报告：{results['company']}",
        "",
        f"**所属超级趋势**：{results['trend']}",
        f"**瓶颈信号综合评级**：`{results['star_rating']}` ({results['score']} 星)",
        "",
        "#### 1. 核心瓶颈参数与财务画像",
        "",
        f"| 指标项目 | 测算数值 | 评估基准与含义 |",
        f"|---|---|---|",
        f"| **标的公司 / 代码** | {results['company']} | 供应链关键卡脖子环节 |",
        f"| **当前总市值** | {results['market_cap']:.2f} {unit} | - |",
        f"| **细分赛道 TAM 规模** | {results['tam']:.2f} {unit} | 市值占 TAM: {results['tam_cap_ratio_pct']}% (红线: 20%) |",
        f"| **年度营业收入** | {results['revenue']:.2f} {unit} | 同比增速: +{results['revenue_growth_pct']}% |",
        f"| **估值倍数 (P/S & P/E)** | PS: {results['ps']}x | PE: {results['pe'] if results['pe'] is not None else 'N/A'}x |",
        f"| **全球细分市场份额** | **{results['market_share_pct']}%** | > 50% 具备绝对定价权 |",
        f"| **产能扩建周期 (Lead Time)** | **{results['expansion_lead_time_months']} 个月** | > 18 个月供给刚性极强 |",
        f"| **毛利率演变趋势** | **{results['gross_margin_trend'].upper()} (上升态势)** | 验证“量价齐升”与转嫁成本能力 |",
        f"| **10年 25x PE 退出年化回报** | **{results['annualized_return_pct']}%** | {'✅ 达标 (>=10%)' if results['exit_return_safe'] else '⚠️ 不达标 (<10%，安全边际薄弱)'} |",
        "",
        "#### 2. 估值红黄绿灯诊断",
        "",
    ]

    if results["red_flags"]:
        lines.append("**🚨 估值红灯（信号强度受限）：**")
        for f in results["red_flags"]:
            lines.append(f"- ❌ {f}")
        lines.append("")

    if results["yellow_flags"]:
        lines.append("**⚠️ 估值黄灯（需重点跟踪解释）：**")
        for f in results["yellow_flags"]:
            lines.append(f"- 🔸 {f}")
        lines.append("")

    if results["green_flags"]:
        lines.append("**🟢 估值绿灯（加分项）：**")
        for f in results["green_flags"]:
            lines.append(f"- ✅ {f}")
        lines.append("")

    if not results["red_flags"] and not results["yellow_flags"]:
        lines.append("未触发任何估值红黄灯，估值处于合理或低估区间。\n")

    lines.extend([
        "#### 3. 瓶颈套利决策判定",
        f"- **信号强度判定**：当前标的获评 **{results['star_rating']}**；",
        f"- **估值安全边际**：{'当前价格提供良好投资安全垫，10年退出年化回报超过 10%。' if results['exit_return_safe'] else '当前估值已经过度透支了未来 3~5 年的高速增长，缺乏充分的安全边际。'}",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Supply Chain Bottleneck Hunter Evaluator."
    )
    parser.add_argument("--trend", type=str, required=True, help="Super-trend name (e.g. 'AI Infrastructure').")
    parser.add_argument("--company", type=str, required=True, help="Target company name or ticker.")
    parser.add_argument("--market-cap", type=float, required=True, help="Current market capitalization.")
    parser.add_argument("--revenue", type=float, required=True, help="Annual Revenue (TTM).")
    parser.add_argument("--tam", type=float, required=True, help="TAM of the specific bottleneck subsector.")
    parser.add_argument("--revenue-growth", type=float, required=True, help="Revenue YoY growth (decimal, e.g. 0.45).")
    parser.add_argument("--ps", type=float, default=None, help="Price-to-Sales multiple (optional).")
    parser.add_argument("--pe", type=float, default=None, help="Price-to-Earnings multiple (optional).")
    parser.add_argument("--gross-margin-trend", type=str, default="up", choices=["up", "flat", "down"], help="Gross margin trend.")
    parser.add_argument("--lead-time", type=int, default=18, help="Capacity expansion lead time in months (default 18).")
    parser.add_argument("--market-share", type=float, default=0.50, help="Global market share (decimal, default 0.50).")
    parser.add_argument("--exit-pe", type=float, default=25.0, help="Terminal exit PE (default 25.0).")
    parser.add_argument("--unit", type=str, default="亿美元 ($B)", help="Monetary unit (default: 亿美元 ($B)).")
    parser.add_argument("--output", type=str, default="", help="Path to write Markdown output report.")

    args = parser.parse_args()

    results = evaluate_bottleneck(
        trend=args.trend,
        company=args.company,
        market_cap=args.market_cap,
        revenue=args.revenue,
        tam=args.tam,
        revenue_growth=args.revenue_growth,
        ps=args.ps,
        pe=args.pe,
        gross_margin_trend=args.gross_margin_trend,
        expansion_lead_time_months=args.lead_time,
        market_share=args.market_share,
        exit_pe=args.exit_pe,
    )

    print("=" * 66)
    print(f"   供应链瓶颈评估结果 [{args.company}] - 评级: {results['star_rating']}")
    print("=" * 66)
    print(f"所属超级趋势                 : {results['trend']}")
    print(f"当前市值 / 细分 TAM          : {results['market_cap']:.2f} / {results['tam']:.2f} {args.unit} (占 TAM {results['tam_cap_ratio_pct']}%)")
    print(f"年营收 / 同比增速            : {results['revenue']:.2f} {args.unit} (增速: +{results['revenue_growth_pct']}%)")
    print(f"估值倍数 (P/S & P/E)         : PS: {results['ps']}x | PE: {results['pe'] if results['pe'] is not None else 'N/A'}x")
    print(f"全球市场份额 / 扩产周期      : {results['market_share_pct']}% / {results['expansion_lead_time_months']} 个月")
    print(f"毛利率走势                   : {results['gross_margin_trend'].upper()}")
    print(f"10年 25x PE 退出年化预期回报 : {results['annualized_return_pct']}% ({'达标 >=10%' if results['exit_return_safe'] else '未达标 <10%'})")
    if results["red_flags"]:
        print("-" * 66)
        print("🚨 估值红灯告警:")
        for rf in results["red_flags"]:
            print(f"  * {rf}")
    if results["yellow_flags"]:
        print("⚠️ 估值黄灯提示:")
        for yf in results["yellow_flags"]:
            print(f"  * {yf}")
    print("=" * 66)

    if args.output:
        md_text = format_markdown_report(results, unit=args.unit)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_text, encoding="utf-8")
        print(f"\n[+] 瓶颈猎手评估 Markdown 结果已保存至: {out_path.resolve()}")


if __name__ == "__main__":
    main()
