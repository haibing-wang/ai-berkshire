"""
Equity as an Equity Bond Calculator
Based on the valuation framework of John Burr Williams, Warren Buffett, and Charlie Munger.
Treats equity as a bond with a variable coupon, calculating long-term expected returns
based on Free Cash Flow Yield, Retained Earnings Reinvestment, and ROIC/ROE.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


def calculate_equity_bond_yield(
    market_cap: float,
    current_fcf: float,
    roe: float,
    roic: Optional[float] = None,
    payout_ratio: Optional[float] = None,
    pb_entry: Optional[float] = None,
    pb_exit: Optional[float] = None,
    holding_years: int = 10,
    risk_free_rate: float = 0.051,
) -> Dict[str, Any]:
    """
    Calculates equity bond yield components:
    1. Cash return yield (FCF / Market Cap or Shareholder Yield)
    2. Growth from retained earnings reinvested at ROIC (b * ROIC)
    3. Valuation multiple change effect (P/B contraction or expansion)
    4. Total expected annual return (CAGR) and Equity Risk Premium over Treasuries.
    """
    if roic is None:
        roic = roe

    # 1. 初始现金收益率 (FCF Yield / Cash Yield)
    fcf_yield = current_fcf / market_cap if market_cap > 0 else 0.0

    # 2. 留存比率 (b) 与 分红/回购回馈比率 (payout_ratio)
    # 若未指定 payout_ratio，默认假设现金分红与回购相当于 FCF 发放，或取合理估算
    if payout_ratio is None:
        # 默认推导：如果 FCF/净利润比例合理，则留存率 = 1 - (FCF发放率)
        payout_ratio = 0.50

    payout_ratio = max(0.0, min(1.0, payout_ratio))
    reinvestment_rate = 1.0 - payout_ratio

    # 3. 留存收益复利增长率 (g = b * ROIC)
    growth_from_reinvestment = reinvestment_rate * roic

    # 4. 内在基础股权债券收益率 (Perpetual / Constant Multiple Equity Bond Yield)
    # Expected Return = FCF Yield + (1 - Payout) * ROIC
    intrinsic_equity_bond_yield = fcf_yield + growth_from_reinvestment

    # 5. 估值乘数变化年化效应 (P/B or P/E Multiple Expansion / Compression)
    valuation_annual_impact = 0.0
    total_expected_cagr = intrinsic_equity_bond_yield

    if pb_entry is not None and pb_exit is not None and pb_entry > 0 and pb_exit > 0:
        multiple_factor = pb_exit / pb_entry
        valuation_annual_impact = (multiple_factor ** (1.0 / holding_years)) - 1.0
        # 综合年化复合收益率: (1 + 基础收益率) * (1 + 估值变化) - 1
        total_expected_cagr = (1.0 + intrinsic_equity_bond_yield) * (1.0 + valuation_annual_impact) - 1.0

    # 6. 股权风险溢价 (Equity Risk Premium, ERP = 股权回报 - 10年期美债)
    equity_risk_premium = total_expected_cagr - risk_free_rate

    # 7. 灵敏度矩阵：不同 ROE/ROIC 与 留存比率下的预期收益率对照
    sensitivity_roe_rates = [0.08, 0.12, 0.15, 0.20, 0.25, 0.30]
    sensitivity_payout_ratios = [0.0, 0.30, 0.50, 0.70, 1.0]
    sensitivity_matrix: List[Dict[str, Any]] = []

    for r_cand in sensitivity_roe_rates:
        row = {"roe": round(r_cand * 100, 1), "yields": []}
        for p_cand in sensitivity_payout_ratios:
            # 假定该情景下现金收益率为 (p_cand * current_fcf / market_cap)，留存按 r_cand 复利
            est_yield = (p_cand * fcf_yield) + ((1.0 - p_cand) * r_cand)
            if valuation_annual_impact != 0.0:
                est_yield = (1.0 + est_yield) * (1.0 + valuation_annual_impact) - 1.0
            row["yields"].append(round(est_yield * 100, 2))
        sensitivity_matrix.append(row)

    return {
        "market_cap": market_cap,
        "current_fcf": current_fcf,
        "fcf_yield_pct": round(fcf_yield * 100, 2),
        "roe_pct": round(roe * 100, 2),
        "roic_pct": round(roic * 100, 2),
        "payout_ratio_pct": round(payout_ratio * 100, 2),
        "reinvestment_rate_pct": round(reinvestment_rate * 100, 2),
        "growth_from_reinvestment_pct": round(growth_from_reinvestment * 100, 2),
        "intrinsic_equity_bond_yield_pct": round(intrinsic_equity_bond_yield * 100, 2),
        "pb_entry": pb_entry,
        "pb_exit": pb_exit,
        "holding_years": holding_years,
        "valuation_annual_impact_pct": round(valuation_annual_impact * 100, 2) if pb_entry else None,
        "total_expected_cagr_pct": round(total_expected_cagr * 100, 2),
        "risk_free_rate_pct": round(risk_free_rate * 100, 2),
        "equity_risk_premium_pct": round(equity_risk_premium * 100, 2),
        "sensitivity_payout_headers": [int(p * 100) for p in sensitivity_payout_ratios],
        "sensitivity_matrix": sensitivity_matrix,
    }


def format_markdown_report(
    results: Dict[str, Any],
    company: str = "目标标的",
    unit: str = "亿美元 ($B)",
) -> str:
    """Format calculation results into a comprehensive GitHub Markdown section."""
    lines = [
        f"### 📈 股权债券化模型 (Equity as an Equity Bond) 测算报告：{company}",
        "",
        "> “股票本质上是一张息票率会浮动的长期债券。企业的账面净资产是债券面值，ROE 是它的票面息率，留存收益再投资则是利息按 ROIC 自动滚存。” —— 沃伦·巴菲特 (1977)",
        "",
        "#### 1. 核心模型测算不等式与拆解",
        "$$\\text{长期股权回报率} \\approx \\text{自由现金流回报率} + \\text{留存收益比率} \\times \\text{增量投入资本回报率 (ROIC)} \\pm \\text{估值乘数变化}$$",
        "",
        "#### 2. 核心指标与回报分解表",
        "",
        f"| 指标项目 | 测算数值 | 商业含义与公式 |",
        f"|---|---|---|",
        f"| **评估公司 / 标的** | {company} | - |",
        f"| **当前总市值 ($P_0$)** | {results['market_cap']:.2f} {unit} | 买下公司的当前总对价 |",
        f"| **基准自由现金流 ($FCF_0$)** | {results['current_fcf']:.2f} {unit} | 过去12个月（TTM）真实真金白银造血 |",
        f"| **① 当期自由现金流回报率** | **{results['fcf_yield_pct']:.2f}%** | $FCF / MarketCap$（股东当期落袋回报） |",
        f"| **企业资本回报率 (ROE / ROIC)** | **{results['roe_pct']:.2f}% / {results['roic_pct']:.2f}%** | 商业护城河核心，衡量资本增殖效率 |",
        f"| **股利与回购发放比率 ($1-b$)** | {results['payout_ratio_pct']:.2f}% | 现金回报股东比例 |",
        f"| **留存收益再投资比率 ($b$)** | {results['reinvestment_rate_pct']:.2f}% | 留存在企业内部继续滚存比例 |",
        f"| **② 留存收益内生复合增速** | **{results['growth_from_reinvestment_pct']:.2f}%** | $b \\times \\text{{ROIC}}$（由高资本效率驱动的成长） |",
        f"| **内在基础股权债券收益率 (① + ②)** | **{results['intrinsic_equity_bond_yield_pct']:.2f}%** | **估值乘数不变情况下的年化复合回报率** |",
    ]

    if results["pb_entry"] is not None and results["pb_exit"] is not None:
        lines.extend([
            f"| **买入市净率 ($P/B_{{entry}}$) $\\to$ 卖出 ($P/B_{{exit}}$)** | {results['pb_entry']:.2f} $\\to$ {results['pb_exit']:.2f} | 假设 {results['holding_years']} 年后估值倍数变动 |",
            f"| **③ 估值倍数年化影响** | **{results['valuation_annual_impact_pct']:+.2f}%** | $(P/B_{{exit}} / P/B_{{entry}})^{{1/n}} - 1$ |",
            f"| **综合预期年化总复合回报率 (CAGR)** | **{results['total_expected_cagr_pct']:.2f}%** | 考虑分红、内生复利与估值均值回归的总回报 |",
        ])
    else:
        lines.append(
            f"| **综合预期年化总复合回报率 (CAGR)** | **{results['total_expected_cagr_pct']:.2f}%** | 稳态估值下的年化复合回报率 |"
        )

    lines.extend([
        f"| **10年期无风险国债基准 ($r$)** | **{results['risk_free_rate_pct']:.2f}%** | 机会成本基准线 (10Y US Treasury) |",
        f"| **股权风险溢价 (Equity Risk Premium)** | **{results['equity_risk_premium_pct']:+.2f}%** | $\\text{{预期股权回报}} - \\text{{国债利率}}$ |",
        "",
        "#### 3. 股权风险溢价 (ERP) 评定标尺",
        "- **ERP >= +5.0%**：极具吸引力，股权回报显著跑赢国债，安全边际深厚；",
        "- **+2.0% <= ERP < +5.0%**：合理配置区间，具备正常股权超额补偿；",
        "- **0.0% <= ERP < +2.0%**：吸引力微弱，承担商业风险却几乎没有超额回报；",
        "- **ERP < 0.0%**：**严重透支 / 负风险溢价**，买股票的预期回报甚至低于买国债，违背投资机会成本原则。",
        "",
        "#### 4. 灵敏度矩阵：不同 ROIC/ROE 与分红留存政策下的年化回报率",
        "",
        "下表展示在不同**企业内生资本回报率 (ROIC)** 与 **现金分红发放率 (Payout Ratio)** 组合下，持有该股票的长期年化预期回报率（%）：",
        "",
    ])

    payout_headers = results["sensitivity_payout_headers"]
    header_str = "| ROIC \\ 分红率 | " + " | ".join([f"发放 {p}% (留存 {100-p}%)" for p in payout_headers]) + " |"
    divider_str = "|---| " + " | ".join(["---"] * len(payout_headers)) + " |"
    lines.append(header_str)
    lines.append(divider_str)

    for row in results["sensitivity_matrix"]:
        row_str = f"| **ROIC = {row['roe']}%** | " + " | ".join([f"{y:.2f}%" for y in row["yields"]]) + " |"
        lines.append(row_str)

    lines.extend([
        "",
        "> **巴菲特 ROE 铁律启示**：当一家公司的 ROIC 长期处于高位（如 20%+）时，企业多留存再投资（更低的分红率）能创造出更高的长期年化复合回报；反之，若公司 ROIC 低于资金成本（如低于 8%~10%），继续留存资金是在‘毁灭股东价值’，必须将利润 100% 分红才能勉强保障投资者收益。",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate Equity as an Equity Bond Yield (Buffett-Williams Framework)."
    )
    parser.add_argument("--market-cap", type=float, required=True, help="Current market capitalization.")
    parser.add_argument("--fcf", type=float, required=True, help="Trailing Free Cash Flow or normalized net profit.")
    parser.add_argument("--roe", type=float, required=True, help="Long-term normalized ROE (decimal, e.g. 0.20 for 20%).")
    parser.add_argument("--roic", type=float, default=None, help="Incremental ROIC (decimal, defaults to ROE).")
    parser.add_argument("--payout-ratio", type=float, default=0.50, help="Fraction of earnings paid out (default 0.50).")
    parser.add_argument("--pb-entry", type=float, default=None, help="Entry Price-to-Book multiple (optional).")
    parser.add_argument("--pb-exit", type=float, default=None, help="Exit Price-to-Book multiple after N years (optional).")
    parser.add_argument("--years", type=int, default=10, help="Holding years (default 10).")
    parser.add_argument("--risk-free-rate", type=float, default=0.051, help="10-Year Treasury Yield (default 0.051).")
    parser.add_argument("--company", type=str, default="目标标的", help="Company name or ticker.")
    parser.add_argument("--unit", type=str, default="亿美元 ($B)", help="Monetary unit (default: 亿美元 ($B)).")
    parser.add_argument("--output", type=str, default="", help="Path to write Markdown output report.")

    args = parser.parse_args()

    results = calculate_equity_bond_yield(
        market_cap=args.market_cap,
        current_fcf=args.fcf,
        roe=args.roe,
        roic=args.roic,
        payout_ratio=args.payout_ratio,
        pb_entry=args.pb_entry,
        pb_exit=args.pb_exit,
        holding_years=args.years,
        risk_free_rate=args.risk_free_rate,
    )

    print("=" * 66)
    print(f"      股权债券化 (Equity as an Equity Bond) 测算结果 [{args.company}]")
    print("=" * 66)
    print(f"当前市值 (P0)                   : {results['market_cap']:.2f} {args.unit}")
    print(f"基准自由现金流 (FCF0)           : {results['current_fcf']:.2f} {args.unit}")
    print(f"当期自由现金流回报率 (FCF Yield) : {results['fcf_yield_pct']:.2f}%")
    print(f"内生资本回报率 (ROE / ROIC)     : {results['roe_pct']:.2f}% / {results['roic_pct']:.2f}%")
    print(f"利润留存再投资率 (b)            : {results['reinvestment_rate_pct']:.2f}% (分红回购率: {results['payout_ratio_pct']:.2f}%)")
    print(f"留存收益驱动复合增速 (b*ROIC)   : {results['growth_from_reinvestment_pct']:.2f}%")
    print("-" * 66)
    print(f"内在基础股权债券收益率          : {results['intrinsic_equity_bond_yield_pct']:.2f}%")
    if results["pb_entry"] and results["pb_exit"]:
        print(f"估值乘数变化年化影响 (P/B 变动)  : {results['valuation_annual_impact_pct']:+.2f}% ({results['pb_entry']} -> {results['pb_exit']})")
    print(f"预期年化总复合回报率 (CAGR)     : {results['total_expected_cagr_pct']:.2f}%")
    print(f"基准 10 年期美债无风险收益率    : {results['risk_free_rate_pct']:.2f}%")
    print(f"股权风险溢价 (Equity Risk Premium): {results['equity_risk_premium_pct']:+.2f}%")
    print("=" * 66)

    if args.output:
        md_text = format_markdown_report(results, company=args.company, unit=args.unit)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_text, encoding="utf-8")
        print(f"\n[+] 测算 Markdown 结果已保存至: {out_path.resolve()}")


if __name__ == "__main__":
    main()
