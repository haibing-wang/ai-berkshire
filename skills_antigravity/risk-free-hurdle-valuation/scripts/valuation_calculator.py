"""
无风险机会成本与企业增速门槛测算器 (Duan Yongping & Buffett Opportunity Cost Framework)
"""

import argparse
from typing import Dict, Any


def calculate_hurdle(
    market_cap: float,
    risk_free_rate: float,
    current_earnings: float,
    years: int = 10,
    compounding_frequency: int = 1,
) -> Dict[str, Any]:
    """
    计算国债终值机会成本及股票为跑赢国债所需的年复合利润增速 (CAGR)。

    :param market_cap: 当前市值 (如 50000 亿美元)
    :param risk_free_rate: 10年期国债年化利率 (如 0.052 代表 5.2%)
    :param current_earnings: 当前基准年净利润/自由现金流 (如 1000 亿美元)
    :param years: 测算周期 (默认 10 年)
    :param compounding_frequency: 计息频率 (1 为年度复利，2 为半年付息一次再投资)
    :return: 包含测算指标的字典
    """
    # 1. 计算国债终值 (FV)
    if compounding_frequency == 1:
        treasury_future_value = market_cap * ((1 + risk_free_rate) ** years)
    else:
        treasury_future_value = market_cap * (
            (1 + risk_free_rate / compounding_frequency) ** (years * compounding_frequency)
        )

    # 2. 计算国债产生的无风险利息差额（企业必须赚得的利润底线）
    hurdle_profit = treasury_future_value - market_cap

    # 3. 求解等比数列求和以得到年复合增速 g:
    # Sum_{t=1}^{n} E0 * (1 + g)^t = hurdle_profit
    def cumulative_profit(g: float) -> float:
        if abs(g) < 1e-9:
            return current_earnings * years
        return current_earnings * (1 + g) * (((1 + g) ** years) - 1) / g

    # 二分法数值求解
    low, high = -0.5, 2.0
    for _ in range(100):
        mid = (low + high) / 2
        val = cumulative_profit(mid)
        if abs(val - hurdle_profit) < 1e-4:
            break
        if val < hurdle_profit:
            low = mid
        else:
            high = mid
    required_cagr = mid

    # 第 10 年预期的单年利润
    terminal_year_earnings = current_earnings * ((1 + required_cagr) ** years)

    return {
        "market_cap": market_cap,
        "risk_free_rate_pct": risk_free_rate * 100,
        "years": years,
        "treasury_future_value": round(treasury_future_value, 2),
        "hurdle_profit": round(hurdle_profit, 2),
        "current_earnings": current_earnings,
        "required_cagr_pct": round(required_cagr * 100, 2),
        "terminal_year_earnings": round(terminal_year_earnings, 2),
    }


if __name__ == "__main__":
    # 以推文中的苹果公司数据为例：
    # 市值 50,000 亿，国债利率 5.2%，基准利润 1,000 亿，周期 10 年
    results = calculate_hurdle(
        market_cap=50000.0,
        risk_free_rate=0.052,
        current_earnings=1000.0,
        years=10,
        compounding_frequency=1,
    )

    print("=" * 60)
    print("      无风险机会成本与企业增速门槛测算结果")
    print("=" * 60)
    print(f"当前市值 (初始投入 P0)       : {results['market_cap']:.2f} 亿美元")
    print(f"基准无风险利率 (r)           : {results['risk_free_rate_pct']:.2f}%")
    print(f"投资测算周期 (n)             : {results['years']} 年")
    print("-" * 60)
    print(f"10年后国债期末本息和 (FV)    : {results['treasury_future_value']:.2f} 亿美元")
    print(f"需赚取的累计利润门槛 (Delta) : {results['hurdle_profit']:.2f} 亿美元")
    print(f"当前年度基准净利润 (E0)      : {results['current_earnings']:.2f} 亿美元")
    print(f"推演隐含利润年复合增速 (g)   : {results['required_cagr_pct']:.2f}%")
    print(f"第 10 年所需年度净利润       : {results['terminal_year_earnings']:.2f} 亿美元")
    print("=" * 60)