from typing import Dict, List, Tuple

TAX_BRACKETS: List[Tuple[float, float, float]] = [
    (36000, 0.03, 0),
    (144000, 0.10, 2520),
    (300000, 0.20, 16920),
    (420000, 0.25, 31920),
    (660000, 0.30, 52920),
    (960000, 0.35, 85920),
    (float('inf'), 0.45, 181920),
]

BASIC_DEDUCTION_PER_MONTH = 5000


def calculate_tax(
    monthly_income: float,
    cumulative_income: float,
    cumulative_tax_free_deduction: float,
    cumulative_special_deduction: float,
    months_count: int,
    cumulative_prepaid_tax: float = 0.0,
    cumulative_special_additional_deduction: float = 0.0,
    cumulative_other_deduction: float = 0.0,
) -> Dict[str, float]:
    """
    基于累计预扣法计算当月应缴个人所得税。

    Args:
        monthly_income: 当月收入（元）
        cumulative_income: 截至上月的累计收入（元）
        cumulative_tax_free_deduction: 累计免税扣除（元）
        cumulative_special_deduction: 累计专项扣除（元，如五险一金等）
        months_count: 当年截至本月的任职月份数（包含本月）
        cumulative_prepaid_tax: 累计已预缴税额（元，截至上月）
        cumulative_special_additional_deduction: 累计专项附加扣除（元，如子女教育、赡养老人等）
        cumulative_other_deduction: 累计依法确定的其他扣除（元）

    Returns:
        包含计算结果的字典：
        - monthly_tax: 当月应缴个税
        - cumulative_tax: 累计应缴个税
        - cumulative_taxable_income: 累计应纳税所得额
        - tax_rate: 适用税率
        - quick_deduction: 速算扣除数
    """
    if months_count <= 0:
        raise ValueError("months_count 必须大于 0")

    total_cumulative_income = cumulative_income + monthly_income
    total_basic_deduction = BASIC_DEDUCTION_PER_MONTH * months_count

    cumulative_taxable_income = (
        total_cumulative_income
        - cumulative_tax_free_deduction
        - total_basic_deduction
        - cumulative_special_deduction
        - cumulative_special_additional_deduction
        - cumulative_other_deduction
    )

    cumulative_taxable_income = max(0.0, cumulative_taxable_income)

    tax_rate, quick_deduction = _get_tax_rate(cumulative_taxable_income)

    cumulative_tax = cumulative_taxable_income * tax_rate - quick_deduction
    cumulative_tax = max(0.0, cumulative_tax)

    monthly_tax = cumulative_tax - cumulative_prepaid_tax
    monthly_tax = max(0.0, round(monthly_tax, 2))

    return {
        "monthly_tax": monthly_tax,
        "cumulative_tax": round(cumulative_tax, 2),
        "cumulative_taxable_income": round(cumulative_taxable_income, 2),
        "tax_rate": tax_rate,
        "quick_deduction": quick_deduction,
    }


def _get_tax_rate(cumulative_taxable_income: float) -> Tuple[float, float]:
    """根据累计应纳税所得额获取适用税率和速算扣除数。"""
    for upper_bound, rate, quick_deduction in TAX_BRACKETS:
        if cumulative_taxable_income <= upper_bound:
            return rate, quick_deduction
    return TAX_BRACKETS[-1][1], TAX_BRACKETS[-1][2]
