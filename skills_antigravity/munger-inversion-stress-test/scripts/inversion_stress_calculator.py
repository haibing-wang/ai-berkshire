"""
Munger Inversion & Checklist Stress Test Calculator
Based on Charlie Munger's mental model:
"Invert, always invert. All I want to know is where I'm going to die so I'll never go there."
Calculates breakeven margins, revenue drop tolerance, and debt refinancing fatal thresholds.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


def calculate_inversion_stress(
    revenue: float,
    gross_profit: float,
    operating_income: float,
    interest_expense: float,
    total_debt: float,
    cash_and_equivalents: float = 0.0,
    capex: float = 0.0,
    current_fcf: Optional[float] = None,
    refinance_rate: float = 0.075,
) -> Dict[str, Any]:
    """
    Calculates key inversion thresholds:
    1. Breakeven Gross Margin (毛利率下跌多少利润归零 / 现金流断裂)
    2. Revenue Drop Tolerance (营收断崖式下滑多大比例击穿固定成本)
    3. Debt Refinancing Shock (高息展期利息侵蚀与致命利率 r_fatal)
    4. Extreme Cash Runway (极端逆境无外部输血下的抗风险韧性)
    """
    # 1. 基础比率
    gross_margin = gross_profit / revenue if revenue > 0 else 0.0
    operating_margin = operating_income / revenue if revenue > 0 else 0.0
    fixed_opex = gross_profit - operating_income  # 粗略估计固定及半固定营运费用

    # 2. 毛利率安全垫 (Gross Margin Breakeven)
    # EBIT = 0 的临界毛利率: GM_ebit_zero = Opex / Revenue
    gm_ebit_zero = fixed_opex / revenue if revenue > 0 else 0.0
    gm_drop_to_zero_ebit = gross_margin - gm_ebit_zero  # 即 operating_margin

    # 包含利息与维持性 Capex 的现金流断裂临界毛利率:
    # 现金开支 = fixed_opex + interest_expense + capex
    cash_drain = fixed_opex + interest_expense + capex
    gm_cash_breakeven = cash_drain / revenue if revenue > 0 else 0.0
    gm_drop_to_cash_drain = gross_margin - gm_cash_breakeven

    # 3. 营收断崖容忍度 (Revenue Drop Tolerance to EBIT = 0)
    # 假设变动成本率维持 (1 - GM)，固定营运费用 sticky:
    # 新营收 * GM = fixed_opex  =>  新营收 = fixed_opex / GM
    rev_at_ebit_zero = fixed_opex / gross_margin if gross_margin > 0 else revenue
    max_rev_drop_pct = (revenue - rev_at_ebit_zero) / revenue if revenue > 0 else 0.0

    # 4. 存量负债高息展期压力测试 (Debt Refinancing Stress Test)
    current_implied_debt_rate = interest_expense / total_debt if total_debt > 0 else 0.0
    new_interest_expense = total_debt * refinance_rate
    extra_interest = max(0.0, new_interest_expense - interest_expense)
    ebit_consumed_pct = (extra_interest / operating_income * 100) if operating_income > 0 else 100.0

    current_coverage = operating_income / interest_expense if interest_expense > 0 else 999.0
    new_coverage = operating_income / new_interest_expense if new_interest_expense > 0 else 999.0

    # 致命利率 (Fatal Interest Rate): 当 New Interest == Operating Income 时
    # 即借款利率达到多少，全部经营营业利润被利息吞噬殆尽
    fatal_interest_rate = (operating_income / total_debt) if total_debt > 0 else 9.99

    # 5. 极端逆境现金储备防御缓冲 (Net Debt & Cash Defense)
    net_debt = total_debt - cash_and_equivalents

    # 6. 逆境压力情景矩阵 (Stress Scenario Matrix)
    # 模拟：毛利率下降 3%, 5%, 8%, 10% 时的 EBIT 与现金流变化
    scenarios = []
    for gm_cut in [0.02, 0.05, 0.08, 0.10, 0.15]:
        new_gm = gross_margin - gm_cut
        simulated_ebit = (revenue * new_gm) - fixed_opex
        simulated_fcf = simulated_ebit - interest_expense - capex
        scenarios.append({
            "cut_pct": round(gm_cut * 100, 1),
            "new_gm_pct": round(new_gm * 100, 2),
            "sim_ebit": round(simulated_ebit, 2),
            "sim_fcf": round(simulated_fcf, 2),
            "status": "安全造血" if simulated_fcf > 0 else ("微利维系" if simulated_ebit > 0 else "致命失血"),
        })

    return {
        "revenue": revenue,
        "gross_profit": gross_profit,
        "gross_margin_pct": round(gross_margin * 100, 2),
        "operating_income": operating_income,
        "operating_margin_pct": round(operating_margin * 100, 2),
        "fixed_opex": round(fixed_opex, 2),
        "interest_expense": interest_expense,
        "total_debt": total_debt,
        "cash_and_equivalents": cash_and_equivalents,
        "net_debt": round(net_debt, 2),
        "capex": capex,
        "current_fcf": current_fcf,
        "gm_ebit_zero_pct": round(gm_ebit_zero * 100, 2),
        "gm_drop_to_zero_ebit_pct": round(gm_drop_to_zero_ebit * 100, 2),
        "gm_cash_breakeven_pct": round(gm_cash_breakeven * 100, 2),
        "gm_drop_to_cash_drain_pct": round(gm_drop_to_cash_drain * 100, 2),
        "max_rev_drop_pct": round(max_rev_drop_pct * 100, 2),
        "current_implied_debt_rate_pct": round(current_implied_debt_rate * 100, 2),
        "refinance_rate_pct": round(refinance_rate * 100, 2),
        "extra_interest": round(extra_interest, 2),
        "ebit_consumed_pct": round(ebit_consumed_pct, 2),
        "current_coverage": round(current_coverage, 2),
        "new_coverage": round(new_coverage, 2),
        "fatal_interest_rate_pct": round(fatal_interest_rate * 100, 2),
        "scenarios": scenarios,
    }


def format_markdown_report(
    results: Dict[str, Any],
    company: str = "目标标的",
    unit: str = "亿美元 ($B)",
) -> str:
    """Format inversion stress calculation into structured GitHub Markdown."""
    lines = [
        f"### 🛡️ 查理·芒格逆向思维与负面清单压力测试：{company}",
        "",
        "> “如果我知道自己会死在哪里，我将永远不去那个地方。” —— 查理·芒格 (Charlie Munger)",
        "> 本模型不测算企业在阳光灿烂时能赚多少钱，而是测算**在遭遇暴风雨时，什么样的极端条件会让企业失血致死或投资逻辑破裂**。",
        "",
        "#### 1. 核心防线与破产临界点 (Breakeven Defense Thresholds)",
        "",
        f"| 压力测试维度 | 测算数值 | 安全阈值参考 | 风险评级与商业含义 |",
        f"|---|---|---|---|",
        f"| **当前营收基数 ($Revenue$)** | {results['revenue']:.2f} {unit} | - | 现有经营规模 |",
        f"| **当前毛利率 ($Gross\\,Margin$)** | **{results['gross_margin_pct']:.2f}%** | - | 商业护城河第一道定价权防线 |",
        f"| **当前营业利润率 ($EBIT\\,Margin$)** | **{results['operating_margin_pct']:.2f}%** | > 15.0% 为健康 | 经营缓冲垫厚度 |",
        f"| **毛利率下跌临界点 ($\\Delta GM_{{EBIT=0}}$)** | **{results['gm_drop_to_zero_ebit_pct']:.2f}%** | 跌幅 > 10% 较安全 | **毛利率下跌该幅度后营业利润将全军覆没** |",
        f"| **现金流断裂临界毛利率** | **{results['gm_cash_breakeven_pct']:.2f}%** | 距当前越远越好 | 包含固定费用、利息与维持 Capex 的现金底线 |",
        f"| **毛利率失血缓冲区 ($\\Delta GM_{{Cash}}$)** | **{results['gm_drop_to_cash_drain_pct']:.2f}%** | > 8.0% 具备韧性 | **毛利率下跌超过此点，企业必须依赖外部融资输血** |",
        f"| **营收断崖容忍极限 ($\\Delta Revenue$)** | **-{results['max_rev_drop_pct']:.2f}%** | > -25.0% 具备抗周期力 | **在变动成本可变的前提下，营收下滑此比例利润归零** |",
        "",
        "#### 2. 高息环境负债展期与利息吞噬测试 (Debt Refinancing Stress)",
        "",
        f"| 负债风险指标 | 测算数值 | 评估标准 | 风险预警解析 |",
        f"|---|---|---|---|",
        f"| **有息总负债 ($Total\\,Debt$)** | {results['total_debt']:.2f} {unit} | - | 存量短期借款、长期借款与公司债 |",
        f"| **现金及等价物 ($Cash$)** | {results['cash_and_equivalents']:.2f} {unit} | - | 随时可动用的流动性储备 |",
        f"| **净负债 ($Net\\,Debt$)** | **{results['net_debt']:.2f} {unit}** | 负值代表净现金 | {'净现金充裕（抗风险极佳）' if results['net_debt'] < 0 else '存在净负债敞口'} |",
        f"| **当前有效隐性借款利率** | {results['current_implied_debt_rate_pct']:.2f}% | - | 当前存量债务利息负担 |",
        f"| **高息展期假设利率 ($r_{{refinance}}$)** | **{results['refinance_rate_pct']:.2f}%** | 当前宏观高息基准 | 存量债务到期重新发债的惩罚性利率 |",
        f"| **年化额外激增利息支出** | **+{results['extra_interest']:.2f} {unit}** | 越小越好 | 展期导致利润表直接新增的失血额 |",
        f"| **新增利息吞噬营业利润比例** | **{results['ebit_consumed_pct']:.2f}%** | < 20% 为安全 | 息税前营业利润被额外利息吃掉的比例 |",
        f"| **利息保障倍数 ($EBIT / Interest$)** | **{results['current_coverage']:.2f}x $\\to$ {results['new_coverage']:.2f}x** | > 3.0x 为安全线 | 展期后息税前利润对利息的覆盖能力 |",
        f"| **致命借款利率 ($r_{{fatal}}$)** | **{results['fatal_interest_rate_pct']:.2f}%** | 远高于市场利率为佳 | **若再融资利率达到该值，全部营业利润被利息吞光** |",
        "",
        "#### 3. 价格战 / 成本通胀极端逆境情景推演 (Stress Scenarios)",
        "",
        "模拟在不同**毛利率受侵蚀幅度**下，公司盈利能力与现金流造血状态的动态演变：",
        "",
        f"| 毛利率被蚕食点数 | 模拟毛利率 | 模拟 EBIT ({unit}) | 模拟 FCF ({unit}) | 状态诊断 |",
        f"|---|---|---|---|---|",
    ]

    for sc in results["scenarios"]:
        lines.append(
            f"| 降价/成本上涨 -{sc['cut_pct']}% | {sc['new_gm_pct']}% | {sc['sim_ebit']:.2f} | {sc['sim_fcf']:.2f} | **{sc['status']}** |"
        )

    lines.extend([
        "",
        "#### 4. 芒格反转法则投资裁决 (Charlie Munger Inversion Verdict)",
        f"- **致命死穴识别**：检查 $r_{{fatal}}$ 是否贴近当前市场利率，以及毛利率缓冲垫 $\\Delta GM_{{Cash}}$ 是否小于 5%。若缓冲垫过薄，企业在价格战或行业寒冬中将迅速丧失生存权；",
        f"- **现金流生存底线**：若遭遇极端黑天鹅，企业营收至多允许下滑 **{results['max_rev_drop_pct']:.2f}%**，超过此幅度即便大幅裁员亦将产生实质性亏损；",
        f"- **防御性评估结论**：{'企业资产负债表极其稳健，拥有深厚毛利防线与净现金护盾，极难被外部风暴杀死。' if (results['net_debt'] <= 0 and results['gm_drop_to_zero_ebit_pct'] > 15.0) else '企业在极端逆境或高息重定价下面临可观的利润侵蚀风险，需高度警惕再融资与行业降价。'}",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Munger Inversion & Checklist Stress Test Calculator."
    )
    parser.add_argument("--company", type=str, default="目标标的", help="Company name or ticker.")
    parser.add_argument("--revenue", type=float, required=True, help="Annual Revenue (TTM).")
    parser.add_argument("--gross-profit", type=float, required=True, help="Annual Gross Profit (TTM).")
    parser.add_argument("--operating-income", type=float, required=True, help="Annual Operating Income / EBIT (TTM).")
    parser.add_argument("--interest-expense", type=float, default=0.0, help="Annual Interest Expense (TTM).")
    parser.add_argument("--total-debt", type=float, default=0.0, help="Total interest-bearing debt.")
    parser.add_argument("--cash", type=float, default=0.0, help="Cash and short-term liquid investments.")
    parser.add_argument("--capex", type=float, default=0.0, help="Annual Maintenance/Total Capex (TTM).")
    parser.add_argument("--fcf", type=float, default=None, help="Annual Free Cash Flow (optional).")
    parser.add_argument("--refinance-rate", type=float, default=0.075, help="Stress refinancing debt rate (default 0.075).")
    parser.add_argument("--unit", type=str, default="亿美元 ($B)", help="Monetary unit (default: 亿美元 ($B)).")
    parser.add_argument("--output", type=str, default="", help="Path to write Markdown output report.")

    args = parser.parse_args()

    results = calculate_inversion_stress(
        revenue=args.revenue,
        gross_profit=args.gross_profit,
        operating_income=args.operating_income,
        interest_expense=args.interest_expense,
        total_debt=args.total_debt,
        cash_and_equivalents=args.cash,
        capex=args.capex,
        current_fcf=args.fcf,
        refinance_rate=args.refinance_rate,
    )

    print("=" * 68)
    print(f"   查理·芒格逆向思维与负面清单压力测试结果 [{args.company}]")
    print("=" * 68)
    print(f"营业收入 (Revenue)              : {results['revenue']:.2f} {args.unit}")
    print(f"当前毛利率 (Gross Margin)        : {results['gross_margin_pct']:.2f}%")
    print(f"当前营业利润率 (EBIT Margin)     : {results['operating_margin_pct']:.2f}%")
    print("-" * 68)
    print(f"毛利率降至 EBIT=0 临界安全垫     : -{results['gm_drop_to_zero_ebit_pct']:.2f}% (毛利跌破 {results['gm_ebit_zero_pct']:.2f}% 出现营业亏损)")
    print(f"现金流断裂临界毛利率            : {results['gm_cash_breakeven_pct']:.2f}% (距当前缓冲垫: -{results['gm_drop_to_cash_drain_pct']:.2f}%)")
    print(f"允许营收断崖式下滑极限           : -{results['max_rev_drop_pct']:.2f}%")
    print("-" * 68)
    print(f"存量总有息负债 / 净负债          : {results['total_debt']:.2f} / {results['net_debt']:.2f} {args.unit}")
    print(f"展期利息侵蚀 (以 {results['refinance_rate_pct']:.1f}% 展期)   : 新增利息 +{results['extra_interest']:.2f} {args.unit} (吃掉 EBIT {results['ebit_consumed_pct']:.1f}%)")
    print(f"致命借款利率 (r_fatal)           : {results['fatal_interest_rate_pct']:.2f}% (利率超此值 EBIT 被利息吞光)")
    print("=" * 68)

    if args.output:
        md_text = format_markdown_report(results, company=args.company, unit=args.unit)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_text, encoding="utf-8")
        print(f"\n[+] 逆向压力测试 Markdown 结果已保存至: {out_path.resolve()}")


if __name__ == "__main__":
    main()
