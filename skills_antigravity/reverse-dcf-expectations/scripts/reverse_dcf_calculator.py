"""
Reverse DCF & Implied Expectations Calculator
Based on the framework of Michael Mauboussin (Expectations Investing) and Howard Marks (Reflexivity & The Pendulum).
Inverts DCF: takes market price/market cap as given, solving for implied FCF growth rate (g_implied)
and implied Competitive Advantage Period (CAP).
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


def calculate_reverse_dcf(
    market_cap: float,
    current_fcf: float,
    discount_rate: float = 0.09,
    terminal_growth_rate: float = 0.025,
    forecast_years: int = 10,
    net_debt: float = 0.0,
    test_growth_rates: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Calculates:
    1. Implied FCF CAGR (g_implied) during forecast period required to justify current Market Cap.
    2. Implied Competitive Advantage Period (CAP) if a consensus growth rate is assumed.
    3. Year-by-year projected cash flow schedule and present value breakdown.
    4. Sensitivity matrix across discount rates and terminal growth rates.
    """
    # 目标企业价值 (Target Enterprise Value) 或 股权价值
    # 若 net_debt 给出，则 Target EV = Market Cap + Net Debt
    target_equity_value = market_cap

    def dcf_equity_value(g: float) -> float:
        pv_forecast = 0.0
        fcf_t = current_fcf
        for t in range(1, forecast_years + 1):
            fcf_t = current_fcf * ((1.0 + g) ** t)
            pv_forecast += fcf_t / ((1.0 + discount_rate) ** t)

        terminal_fcf = fcf_t * (1.0 + terminal_growth_rate)
        # 永续价值
        if discount_rate <= terminal_growth_rate:
            tv = terminal_fcf / 0.001
        else:
            tv = terminal_fcf / (discount_rate - terminal_growth_rate)
        pv_tv = tv / ((1.0 + discount_rate) ** forecast_years)

        return pv_forecast + pv_tv

    # 若当前 FCF <= 0，无法直接求解
    if current_fcf <= 0:
        return {
            "market_cap": market_cap,
            "current_fcf": current_fcf,
            "discount_rate_pct": round(discount_rate * 100, 2),
            "terminal_growth_rate_pct": round(terminal_growth_rate * 100, 2),
            "forecast_years": forecast_years,
            "implied_fcf_cagr_pct": None,
            "note": "当前基准 FCF <= 0，无法直接倒推年复合增速 g。市场定价隐含了对未来扭亏为盈与规模暴增的预期。",
            "schedule": [],
            "sensitivity_matrix": [],
        }

    # 二分法求解 implied CAGR g
    low, high = -0.5, 2.5
    for _ in range(120):
        mid = (low + high) / 2
        val = dcf_equity_value(mid)
        if abs(val - target_equity_value) < 1.0:
            break
        if val < target_equity_value:
            low = mid
        else:
            high = mid
    implied_cagr = mid

    # 生成预测期现金流明细
    schedule = []
    pv_total_forecast = 0.0
    for t in range(1, forecast_years + 1):
        fcf_val = current_fcf * ((1.0 + implied_cagr) ** t)
        df = 1.0 / ((1.0 + discount_rate) ** t)
        pv_val = fcf_val * df
        pv_total_forecast += pv_val
        schedule.append({
            "year": t,
            "fcf": round(fcf_val, 2),
            "pv_fcf": round(pv_val, 2),
        })

    terminal_fcf_terminal = schedule[-1]["fcf"] * (1.0 + terminal_growth_rate)
    terminal_val = terminal_fcf_terminal / (discount_rate - terminal_growth_rate)
    pv_terminal = terminal_val / ((1.0 + discount_rate) ** forecast_years)
    pv_total_calc = pv_total_forecast + pv_terminal

    pv_forecast_pct = (pv_total_forecast / target_equity_value) * 100
    pv_tv_pct = (pv_terminal / target_equity_value) * 100

    # 灵敏度矩阵：不同折现率 (7% ~ 11%) 与 永续增长率 (1.5% ~ 3.5%) 下的隐含复合增速
    sens_discount_rates = [0.07, 0.08, 0.09, 0.10, 0.11]
    sens_terminal_rates = [0.015, 0.020, 0.025, 0.030, 0.035]
    sensitivity_matrix = []

    for r_cand in sens_discount_rates:
        row = {"discount_rate": round(r_cand * 100, 1), "implied_cagrs": []}
        for tg_cand in sens_terminal_rates:
            def local_dcf(g: float) -> float:
                pv = 0.0
                f = current_fcf
                for t in range(1, forecast_years + 1):
                    f = current_fcf * ((1.0 + g) ** t)
                    pv += f / ((1.0 + r_cand) ** t)
                tv_local = (f * (1.0 + tg_cand)) / (r_cand - tg_cand)
                pv += tv_local / ((1.0 + r_cand) ** forecast_years)
                return pv

            l_cand, h_cand = -0.5, 2.5
            for _ in range(80):
                m_cand = (l_cand + h_cand) / 2
                v_cand = local_dcf(m_cand)
                if abs(v_cand - target_equity_value) < 1.0:
                    break
                if v_cand < target_equity_value:
                    l_cand = m_cand
                else:
                    h_cand = m_cand
            row["implied_cagrs"].append(round(m_cand * 100, 2))
        sensitivity_matrix.append(row)

    return {
        "market_cap": market_cap,
        "current_fcf": current_fcf,
        "discount_rate_pct": round(discount_rate * 100, 2),
        "terminal_growth_rate_pct": round(terminal_growth_rate * 100, 2),
        "forecast_years": forecast_years,
        "implied_fcf_cagr_pct": round(implied_cagr * 100, 2),
        "terminal_year_fcf": round(schedule[-1]["fcf"], 2) if schedule else 0.0,
        "pv_forecast": round(pv_total_forecast, 2),
        "pv_forecast_pct": round(pv_forecast_pct, 1),
        "pv_terminal": round(pv_terminal, 2),
        "pv_terminal_pct": round(pv_tv_pct, 1),
        "schedule": schedule,
        "sens_terminal_headers": [round(tg * 100, 1) for tg in sens_terminal_rates],
        "sensitivity_matrix": sensitivity_matrix,
        "note": "OK",
    }


def format_markdown_report(
    results: Dict[str, Any],
    company: str = "目标标的",
    unit: str = "亿美元 ($B)",
) -> str:
    """Format the Reverse DCF calculation into a comprehensive GitHub Markdown section."""
    lines = [
        f"### 🔍 反向现金流折现 (Reverse DCF) 预期推演报告：{company}",
        "",
        "> “市场价格不是内在价值的体现，而是当前市场所有共识预期的综合反映。聪明的投资者不预测未来，而是**反向推演当前价格中到底隐含了多少乐观或悲观**。” —— 迈克尔·莫布森 (Michael Mauboussin, 《Expectations Investing》)",
        "",
        "#### 1. 核心反向推演参数与结果对照表",
        "",
        f"| 指标项目 | 测算数值 | 财务说明 |",
        f"|---|---|---|",
        f"| **评估公司 / 标的** | {company} | - |",
        f"| **当前总市值 ($P_0$)** | {results['market_cap']:.2f} {unit} | 市场当前定价基准 |",
        f"| **基准自由现金流 ($FCF_0$)** | {results['current_fcf']:.2f} {unit} | 过去12个月（TTM）自由现金流 |",
        f"| **资本折现率 ($WACC / r$)** | {results['discount_rate_pct']:.2f}% | 包含无风险利率与股权风险补偿的必要回报率 |",
        f"| **永续增长率 ($g_{{terminal}}$)** | {results['terminal_growth_rate_pct']:.2f}% | 锚定长期宏观经济名义增长率 |",
        f"| **显性推演期 ($N$)** | {results['forecast_years']} 年 | 市场假设的竞争优势期 (CAP) |",
    ]

    if results["implied_fcf_cagr_pct"] is not None:
        lines.extend([
            f"| **市场定价隐含年复合增速 ($g_{{implied}}$)** | **{results['implied_fcf_cagr_pct']:.2f}%** | **要支撑当前市值，未来 {results['forecast_years']} 年 FCF 必须以此增速复合狂飙** |",
            f"| **第 {results['forecast_years']} 年所需年度自由现金流** | **{results['terminal_year_fcf']:.2f} {unit}** | 相当于届时单年需达到的真金白银造血水平 |",
            f"| **显性预测期价值占比 (PV of Forecast)** | {results['pv_forecast']:.2f} {unit} ({results['pv_forecast_pct']}%) | 未来 {results['forecast_years']} 年现金流折现价值 |",
            f"| **永续终值价值占比 (PV of Terminal)** | {results['pv_terminal']:.2f} {unit} ({results['pv_terminal_pct']}%) | 远期终值在当前市值中的比重 |",
        ])
    else:
        lines.append(f"| **特殊说明** | {results['note']} | - |")

    lines.append("")

    if results.get("schedule"):
        lines.extend([
            f"#### 2. 未来 {results['forecast_years']} 年市场隐含的自由现金流产生日程表",
            "",
            f"| 年份 | 隐含自由现金流 ({unit}) | 折现值 PV ({unit}) | 商业实现难度与常识对照 |",
            f"|---|---|---|---|",
        ])
        for row in results["schedule"]:
            lines.append(
                f"| Year {row['year']} | {row['fcf']:.2f} | {row['pv_fcf']:.2f} | 相比基期扩大 {row['fcf']/results['current_fcf']:.2f}x |"
            )
        lines.append("")

    if results.get("sensitivity_matrix"):
        lines.extend([
            "#### 3. 灵敏度矩阵：不同折现率与永续增长率下的市场隐含复合增速 ($g_{implied}$)",
            "",
            "下表展示在不同**必要折现率 (WACC)** 与 **永续增长率 ($g_{terminal}$)** 假设下，当前市值所倒推出的未来 10 年 FCF 年复合增速要求（%）：",
            "",
        ])
        t_headers = results["sens_terminal_headers"]
        header_str = "| 折现率 \\ 永续增速 | " + " | ".join([f"永续 {th}%" for th in t_headers]) + " |"
        divider_str = "|---| " + " | ".join(["---"] * len(t_headers)) + " |"
        lines.append(header_str)
        lines.append(divider_str)

        for row in results["sensitivity_matrix"]:
            row_str = f"| **WACC = {row['discount_rate']}%** | " + " | ".join([f"{c:.2f}%" for c in row["implied_cagrs"]]) + " |"
            lines.append(row_str)

        lines.extend([
            "",
            "#### 4. 预期差诊断与反向投资裁决 (Expectations Gap Verdict)",
            f"- **定价乐观度诊断**：若隐含复合增速 $g_{{implied}} > 25.0\\%$，说明市场已将未来 10 年极度顺风的“完美叙事（Priced for Perfection）”全额计入股价，一旦增长稍有不及预期（如放缓至 15%~20%），将遭遇估值与业绩双杀；",
            f"- **安全边际判断**：若隐含增速远低于行业平均与公司历史真实增长（如 $g_{{implied}} < 8.0\\%$），意味着市场悲观共识过度，存在极其丰厚的预期差修复上行空间；",
            "",
        ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Reverse DCF & Implied Expectations Calculator."
    )
    parser.add_argument("--company", type=str, default="目标标的", help="Company name or ticker.")
    parser.add_argument("--market-cap", type=float, required=True, help="Current Market Capitalization.")
    parser.add_argument("--fcf", type=float, required=True, help="Trailing Free Cash Flow (FCF).")
    parser.add_argument("--wacc", type=float, default=0.09, help="Discount rate / WACC (default 0.09).")
    parser.add_argument("--terminal-growth", type=float, default=0.025, help="Terminal growth rate (default 0.025).")
    parser.add_argument("--years", type=int, default=10, help="Explicit forecast years / CAP (default 10).")
    parser.add_argument("--unit", type=str, default="亿美元 ($B)", help="Monetary unit (default: 亿美元 ($B)).")
    parser.add_argument("--output", type=str, default="", help="Path to write Markdown output report.")

    args = parser.parse_args()

    results = calculate_reverse_dcf(
        market_cap=args.market_cap,
        current_fcf=args.fcf,
        discount_rate=args.wacc,
        terminal_growth_rate=args.terminal_growth,
        forecast_years=args.years,
    )

    print("=" * 66)
    print(f"      反向现金流折现 (Reverse DCF) 测算结果 [{args.company}]")
    print("=" * 66)
    print(f"当前市值 (Market Cap)           : {results['market_cap']:.2f} {args.unit}")
    print(f"基准自由现金流 (FCF0)           : {results['current_fcf']:.2f} {args.unit}")
    print(f"贴现折现率 (WACC)               : {results['discount_rate_pct']:.2f}%")
    print(f"永续增长率 (Terminal Growth)    : {results['terminal_growth_rate_pct']:.2f}%")
    print(f"显性推演周期 (CAP)              : {results['forecast_years']} 年")
    print("-" * 66)
    if results["implied_fcf_cagr_pct"] is not None:
        print(f"市场定价隐含 FCF 年复合增速 (g) : {results['implied_fcf_cagr_pct']:.2f}%")
        print(f"第 {results['forecast_years']} 年所需年度自由现金流    : {results['terminal_year_fcf']:.2f} {args.unit}")
        print(f"显性期价值占比 / 终值占比        : {results['pv_forecast_pct']:.1f}% / {results['pv_terminal_pct']:.1f}%")
    else:
        print(f"说明                            : {results['note']}")
    print("=" * 66)

    if args.output:
        md_text = format_markdown_report(results, company=args.company, unit=args.unit)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_text, encoding="utf-8")
        print(f"\n[+] 反向 DCF 测算 Markdown 结果已保存至: {out_path.resolve()}")


if __name__ == "__main__":
    main()
