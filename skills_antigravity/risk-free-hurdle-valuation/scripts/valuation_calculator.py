"""
Risk-Free Opportunity Cost & Equity Hurdle Rate Calculator
Based on the valuation framework popularized by Duan Yongping and Warren Buffett.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List


def calculate_hurdle(
    market_cap: float,
    risk_free_rate: float,
    current_earnings: float,
    years: int = 10,
    compounding_frequency: int = 1,
) -> Dict[str, Any]:
    """
    Calculates treasury benchmark value, hurdle profit, implied required CAGR,
    and year-by-year projected cash flow schedule.
    """
    if compounding_frequency == 1:
        treasury_future_value = market_cap * ((1 + risk_free_rate) ** years)
    else:
        treasury_future_value = market_cap * (
            (1 + risk_free_rate / compounding_frequency) ** (years * compounding_frequency)
        )

    hurdle_profit = treasury_future_value - market_cap

    # If current_earnings <= 0, geometric compounding solver is invalid.
    if current_earnings <= 0:
        return {
            "market_cap": market_cap,
            "risk_free_rate_pct": risk_free_rate * 100,
            "years": years,
            "treasury_future_value": round(treasury_future_value, 2),
            "hurdle_profit": round(hurdle_profit, 2),
            "current_earnings": current_earnings,
            "required_cagr_pct": None,
            "terminal_year_earnings": None,
            "schedule": [],
            "note": "当前基准净利润/自由现金流 <= 0，无法直接求解复合增速 g。累计需产生净现金流为 hurdle_profit。",
        }

    def cumulative_profit(g: float) -> float:
        if abs(g) < 1e-9:
            return current_earnings * years
        return current_earnings * (1 + g) * (((1 + g) ** years) - 1) / g

    # Binary search solver for required CAGR g
    low, high = -0.5, 3.0
    for _ in range(120):
        mid = (low + high) / 2
        val = cumulative_profit(mid)
        if abs(val - hurdle_profit) < 1e-4:
            break
        if val < hurdle_profit:
            low = mid
        else:
            high = mid

    required_cagr = mid
    projected_terminal_profit = current_earnings * ((1 + required_cagr) ** years)

    # Generate 10-year projected schedule
    schedule: List[Dict[str, Any]] = []
    running_total = 0.0
    for y in range(1, years + 1):
        year_earning = current_earnings * ((1 + required_cagr) ** y)
        running_total += year_earning
        schedule.append({
            "year": y,
            "annual_profit": round(year_earning, 2),
            "cumulative_profit": round(running_total, 2),
        })

    return {
        "market_cap": market_cap,
        "risk_free_rate_pct": risk_free_rate * 100,
        "years": years,
        "treasury_future_value": round(treasury_future_value, 2),
        "hurdle_profit": round(hurdle_profit, 2),
        "current_earnings": current_earnings,
        "required_cagr_pct": round(required_cagr * 100, 2),
        "terminal_year_earnings": round(projected_terminal_profit, 2),
        "schedule": schedule,
        "note": "OK",
    }


def format_markdown_report(
    results: Dict[str, Any],
    company: str = "目标标的",
    unit: str = "亿美元 ($B)",
) -> str:
    """Format the calculation results as a GitHub-flavored Markdown section."""
    lines = [
        f"### 📊 无风险机会成本与增长门槛测算：{company}",
        "",
        f"**核心测算公式**：",
        f"- 国债到期本息和：$FV = P_0 \\times (1 + r)^n$",
        f"- 累计利润门槛：$\\Delta = FV - P_0$",
        f"- 倒推隐含复合增速：$\\sum_{{t=1}}^{{n}} E_0 \\times (1 + g)^t = \\Delta$",
        "",
        "#### 1. 核心测算参数与结果对照表",
        "",
        f"| 指标参数 | 数值 | 单位 / 说明 |",
        f"|---|---|---|",
        f"| **评估公司 / 标的** | {company} | - |",
        f"| **当前估值 / 市值 ($P_0$)** | {results['market_cap']:.2f} | {unit} |",
        f"| **无风险机会成本利率 ($r$)** | {results['risk_free_rate_pct']:.2f}% | 10年期国债收益率 |",
        f"| **测算期限 ($n$)** | {results['years']} | 年 |",
        f"| **国债到期本息和 ($FV$)** | **{results['treasury_future_value']:.2f}** | {unit} (买国债的无风险回报) |",
        f"| **10年累计需赚取利润门槛 ($\\Delta$)** | **{results['hurdle_profit']:.2f}** | {unit} (企业必须赚回的现金流底线) |",
        f"| **当前基准利润/现金流 ($E_0$)** | {results['current_earnings']:.2f} | {unit} (TTM 净利润或自由现金流) |",
    ]

    if results["required_cagr_pct"] is not None:
        lines.extend([
            f"| **倒推企业所需年复合利润增速 ($g$)** | **{results['required_cagr_pct']:.2f}%** | 达成机会成本的利润年复合增速要求 |",
            f"| **第 {results['years']} 年所需年度净利润 ($E_{{10}}$)** | **{results['terminal_year_earnings']:.2f}** | {unit} |",
        ])
    else:
        lines.append(f"| **特殊说明** | {results['note']} | - |")

    lines.append("")

    if results.get("schedule"):
        lines.extend([
            f"#### 2. 未来 {results['years']} 年利润与累计现金流推演日程表",
            "",
            f"| 年份 | 当年预期净利润 ({unit}) | 累计赚取利润 ({unit}) | 占机会成本门槛比例 |",
            f"|---|---|---|---|",
        ])
        for row in results["schedule"]:
            pct = (row["cumulative_profit"] / results["hurdle_profit"]) * 100
            lines.append(
                f"| Year {row['year']} | {row['annual_profit']:.2f} | {row['cumulative_profit']:.2f} | {pct:.1f}% |"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate equity required growth rate vs 10Y Treasury yield."
    )
    parser.add_argument("--market-cap", type=float, required=True, help="Current market cap.")
    parser.add_argument("--risk-free-rate", type=float, required=True, help="Risk-free rate (decimal, e.g. 0.052).")
    parser.add_argument("--current-earnings", type=float, required=True, help="Current baseline annual earnings.")
    parser.add_argument("--years", type=int, default=10, help="Investment period in years (default 10).")
    parser.add_argument("--company", type=str, default="", help="Company name (e.g. SpaceX).")
    parser.add_argument("--unit", type=str, default="亿美元 ($B)", help="Unit of money (e.g. 亿美元 ($B)).")
    parser.add_argument("--output", type=str, default="", help="File path to output markdown report.")

    args = parser.parse_args()

    results = calculate_hurdle(
        market_cap=args.market_cap,
        risk_free_rate=args.risk_free_rate,
        current_earnings=args.current_earnings,
        years=args.years,
    )

    company_title = args.company if args.company else "目标标的"

    print("=" * 64)
    print(f"      无风险机会成本与企业增速门槛测算结果 [{company_title}]")
    print("=" * 64)
    print(f"当前市值 / 估值 (本金 P0)     : {results['market_cap']:.2f} {args.unit}")
    print(f"基准无风险利率 (r)             : {results['risk_free_rate_pct']:.2f}%")
    print(f"投资测算周期 (n)               : {results['years']} 年")
    print("-" * 64)
    print(f"期末国债本息和 (FV)            : {results['treasury_future_value']:.2f} {args.unit}")
    print(f"需赚取的累计利润门槛 (Delta)    : {results['hurdle_profit']:.2f} {args.unit}")
    print(f"当前年度基准净利润/FCF (E0)     : {results['current_earnings']:.2f} {args.unit}")
    if results["required_cagr_pct"] is not None:
        print(f"推演隐含利润年复合增速 (g)     : {results['required_cagr_pct']:.2f}%")
        print(f"第 {results['years']} 年所需年度净利润         : {results['terminal_year_earnings']:.2f} {args.unit}")
    else:
        print(f"说明                           : {results['note']}")
    print("=" * 64)

    if args.output:
        md_text = format_markdown_report(results, company=company_title, unit=args.unit)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_text, encoding="utf-8")
        print(f"\n[+] 测算 Markdown 结果已保存至: {out_path.resolve()}")


if __name__ == "__main__":
    main()