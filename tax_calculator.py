from enum import Enum
from typing import Dict, List, Optional, Tuple


class BonusTaxMode(str, Enum):
    SEPARATE = "separate"
    MERGED = "merged"


TAX_BRACKETS: List[Tuple[float, float, float]] = [
    (36000, 0.03, 0),
    (144000, 0.10, 2520),
    (300000, 0.20, 16920),
    (420000, 0.25, 31920),
    (660000, 0.30, 52920),
    (960000, 0.35, 85920),
    (float('inf'), 0.45, 181920),
]

MONTHLY_TAX_BRACKETS: List[Tuple[float, float, float]] = [
    (3000, 0.03, 0),
    (12000, 0.10, 210),
    (25000, 0.20, 1410),
    (35000, 0.25, 2660),
    (55000, 0.30, 4410),
    (80000, 0.35, 7160),
    (float('inf'), 0.45, 15160),
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


def reverse_calculate_tax(
    after_tax_income: float,
    cumulative_income: float,
    cumulative_tax_free_deduction: float,
    cumulative_special_deduction: float,
    months_count: int,
    cumulative_prepaid_tax: float = 0.0,
    cumulative_special_additional_deduction: float = 0.0,
    cumulative_other_deduction: float = 0.0,
) -> Dict[str, float]:
    """
    已知税后工资，反算税前工资（基于累计预扣法）。

    核心思路：对每个税率档，假设累计应纳税所得额落入该档，
    利用代数关系反推月收入，再验证假设是否成立。

    代数推导：
      税后 = 税前 - 月个税
      月个税 = 累计应纳税所得额 × 税率 - 速扣 - 已预缴
      累计应纳税所得额 = (累计收入 + 税前) - 各项扣除
      令 T = 累计应纳税所得额, x = 税前, a = 累计收入 - 各项扣除(不含当月)
      则 T = a + x
      税后 = x - (T × r - q - p) = x - ((a+x)×r - q - p)
      税后 = x - a×r - x×r + q + p = x(1-r) - a×r + q + p
      x = (税后 + a×r - q - p) / (1 - r)

    Args:
        after_tax_income: 期望的税后工资（元）
        cumulative_income: 截至上月的累计收入（元）
        cumulative_tax_free_deduction: 累计免税扣除（元）
        cumulative_special_deduction: 累计专项扣除（元）
        months_count: 当年截至本月的任职月份数
        cumulative_prepaid_tax: 累计已预缴税额（元）
        cumulative_special_additional_deduction: 累计专项附加扣除（元）
        cumulative_other_deduction: 累计其他扣除（元）

    Returns:
        包含计算结果的字典：
        - pre_tax_income: 税前工资（元）
        - monthly_tax: 当月应缴个税
        - after_tax_income: 验证用税后工资（应与输入一致）
        - cumulative_taxable_income: 累计应纳税所得额
        - tax_rate: 适用税率
        - quick_deduction: 速算扣除数
    """
    if months_count <= 0:
        raise ValueError("months_count 必须大于 0")

    if after_tax_income < 0:
        raise ValueError("税后工资不能为负数")

    total_basic_deduction = BASIC_DEDUCTION_PER_MONTH * months_count

    fixed_deductions = (
        cumulative_income
        - cumulative_tax_free_deduction
        - total_basic_deduction
        - cumulative_special_deduction
        - cumulative_special_additional_deduction
        - cumulative_other_deduction
    )

    if after_tax_income == 0:
        return {
            "pre_tax_income": 0.0,
            "monthly_tax": 0.0,
            "after_tax_income": 0.0,
            "cumulative_taxable_income": 0.0,
            "tax_rate": 0.0,
            "quick_deduction": 0.0,
        }

    candidate = _reverse_for_zero_tax(after_tax_income, fixed_deductions)
    if candidate is not None:
        return {
            "pre_tax_income": round(candidate, 2),
            "monthly_tax": 0.0,
            "after_tax_income": round(candidate, 2),
            "cumulative_taxable_income": 0.0,
            "tax_rate": 0.0,
            "quick_deduction": 0.0,
        }

    for upper_bound, rate, quick_deduction in TAX_BRACKETS:
        if rate == 0:
            continue

        denominator = 1.0 - rate
        if denominator <= 0:
            continue

        numerator = after_tax_income + fixed_deductions * rate - quick_deduction - cumulative_prepaid_tax
        pre_tax = numerator / denominator

        cumulative_taxable = fixed_deductions + pre_tax

        lower = 0.0
        for ub_prev, _, _ in TAX_BRACKETS:
            if ub_prev < upper_bound:
                lower = ub_prev
            else:
                break

        if lower < cumulative_taxable <= upper_bound and pre_tax > 0:
            cumulative_tax = cumulative_taxable * rate - quick_deduction
            cumulative_tax = max(0.0, cumulative_tax)
            monthly_tax = cumulative_tax - cumulative_prepaid_tax
            monthly_tax = max(0.0, monthly_tax)
            verified_after_tax = pre_tax - monthly_tax

            return {
                "pre_tax_income": round(pre_tax, 2),
                "monthly_tax": round(monthly_tax, 2),
                "after_tax_income": round(verified_after_tax, 2),
                "cumulative_taxable_income": round(cumulative_taxable, 2),
                "tax_rate": rate,
                "quick_deduction": quick_deduction,
            }

    raise ValueError("无法反算税前工资，请检查输入参数")


def _reverse_for_zero_tax(after_tax_income: float, fixed_deductions: float) -> Optional[float]:
    """检查是否存在税率为0的解（即税前工资不足以产生应纳税所得额）。"""
    if fixed_deductions >= 0:
        pre_tax = after_tax_income
        if fixed_deductions + pre_tax <= 0:
            return pre_tax
    else:
        max_non_taxable = -fixed_deductions
        if after_tax_income <= max_non_taxable:
            return after_tax_income
    return None


def _get_tax_rate(cumulative_taxable_income: float) -> Tuple[float, float]:
    """根据累计应纳税所得额获取适用税率和速算扣除数。"""
    for upper_bound, rate, quick_deduction in TAX_BRACKETS:
        if cumulative_taxable_income <= upper_bound:
            return rate, quick_deduction
    return TAX_BRACKETS[-1][1], TAX_BRACKETS[-1][2]


def _get_monthly_tax_rate(monthly_amount: float) -> Tuple[float, float]:
    """根据月均金额获取适用税率和速算扣除数（用于年终奖单独计税）。"""
    for upper_bound, rate, quick_deduction in MONTHLY_TAX_BRACKETS:
        if monthly_amount <= upper_bound:
            return rate, quick_deduction
    return MONTHLY_TAX_BRACKETS[-1][1], MONTHLY_TAX_BRACKETS[-1][2]


def calculate_bonus_tax_separate(annual_bonus: float) -> Dict[str, float]:
    """
    年终奖单独计税：将年终奖除以12确定适用税率和速算扣除数，
    再用全年一次性奖金收入乘以税率减去速算扣除数计算应纳税额。

    Args:
        annual_bonus: 年终奖金额（元）

    Returns:
        包含计算结果的字典：
        - bonus_tax: 年终奖应纳税额
        - tax_rate: 适用税率
        - quick_deduction: 速算扣除数
        - monthly_equivalent: 月均金额（年终奖/12）
    """
    if annual_bonus < 0:
        raise ValueError("年终奖金额不能为负数")

    if annual_bonus == 0:
        return {
            "bonus_tax": 0.0,
            "tax_rate": 0.0,
            "quick_deduction": 0.0,
            "monthly_equivalent": 0.0,
        }

    monthly_equivalent = annual_bonus / 12
    tax_rate, quick_deduction = _get_monthly_tax_rate(monthly_equivalent)
    bonus_tax = annual_bonus * tax_rate - quick_deduction
    bonus_tax = max(0.0, round(bonus_tax, 2))

    return {
        "bonus_tax": bonus_tax,
        "tax_rate": tax_rate,
        "quick_deduction": quick_deduction,
        "monthly_equivalent": round(monthly_equivalent, 2),
    }


def calculate_bonus_tax_merged(
    annual_bonus: float,
    annual_cumulative_income: float,
    annual_cumulative_tax_free_deduction: float,
    annual_cumulative_special_deduction: float,
    months_count: int,
    annual_cumulative_prepaid_tax: float = 0.0,
    annual_cumulative_special_additional_deduction: float = 0.0,
    annual_cumulative_other_deduction: float = 0.0,
) -> Dict[str, float]:
    """
    年终奖并入综合所得计税：将年终奖并入当年综合所得，
    按累计预扣法重新计算全年应纳税额，减去已预缴税额得到补缴（或退还）金额。

    Args:
        annual_bonus: 年终奖金额（元）
        annual_cumulative_income: 截至发放年终奖前的累计收入（元）
        annual_cumulative_tax_free_deduction: 累计免税扣除（元）
        annual_cumulative_special_deduction: 累计专项扣除（元）
        months_count: 当年任职月份数
        annual_cumulative_prepaid_tax: 累计已预缴税额（元）
        annual_cumulative_special_additional_deduction: 累计专项附加扣除（元）
        annual_cumulative_other_deduction: 累计其他扣除（元）

    Returns:
        包含计算结果的字典：
        - bonus_tax: 年终奖部分导致的补缴税额
        - total_tax_after_merge: 并入后的全年应纳税额
        - total_tax_before_merge: 并入前的已缴税额（即 annual_cumulative_prepaid_tax）
        - total_taxable_income: 并入后的全年应纳税所得额
        - tax_rate: 适用税率
        - quick_deduction: 速算扣除数
    """
    total_income = annual_cumulative_income + annual_bonus
    total_basic_deduction = BASIC_DEDUCTION_PER_MONTH * months_count

    total_taxable_income = (
        total_income
        - annual_cumulative_tax_free_deduction
        - total_basic_deduction
        - annual_cumulative_special_deduction
        - annual_cumulative_special_additional_deduction
        - annual_cumulative_other_deduction
    )
    total_taxable_income = max(0.0, total_taxable_income)

    tax_rate, quick_deduction = _get_tax_rate(total_taxable_income)

    total_tax_after_merge = total_taxable_income * tax_rate - quick_deduction
    total_tax_after_merge = max(0.0, total_tax_after_merge)

    bonus_tax = total_tax_after_merge - annual_cumulative_prepaid_tax
    bonus_tax = max(0.0, round(bonus_tax, 2))

    return {
        "bonus_tax": bonus_tax,
        "total_tax_after_merge": round(total_tax_after_merge, 2),
        "total_tax_before_merge": round(annual_cumulative_prepaid_tax, 2),
        "total_taxable_income": round(total_taxable_income, 2),
        "tax_rate": tax_rate,
        "quick_deduction": quick_deduction,
    }


def compare_bonus_modes(
    annual_bonus: float,
    annual_cumulative_income: float,
    annual_cumulative_tax_free_deduction: float,
    annual_cumulative_special_deduction: float,
    months_count: int,
    annual_cumulative_prepaid_tax: float = 0.0,
    annual_cumulative_special_additional_deduction: float = 0.0,
    annual_cumulative_other_deduction: float = 0.0,
) -> Dict:
    """
    对比年终奖两种计税模式，推荐较优方案。

    Args: 同 calculate_bonus_tax_merged

    Returns:
        包含两种模式计算结果和推荐方案的字典
    """
    separate_result = calculate_bonus_tax_separate(annual_bonus)

    merged_result = calculate_bonus_tax_merged(
        annual_bonus=annual_bonus,
        annual_cumulative_income=annual_cumulative_income,
        annual_cumulative_tax_free_deduction=annual_cumulative_tax_free_deduction,
        annual_cumulative_special_deduction=annual_cumulative_special_deduction,
        months_count=months_count,
        annual_cumulative_prepaid_tax=annual_cumulative_prepaid_tax,
        annual_cumulative_special_additional_deduction=annual_cumulative_special_additional_deduction,
        annual_cumulative_other_deduction=annual_cumulative_other_deduction,
    )

    separate_tax = separate_result["bonus_tax"]
    merged_tax = merged_result["bonus_tax"]
    tax_diff = round(separate_tax - merged_tax, 2)

    if separate_tax < merged_tax:
        recommended_mode = BonusTaxMode.SEPARATE
    elif merged_tax < separate_tax:
        recommended_mode = BonusTaxMode.MERGED
    else:
        recommended_mode = BonusTaxMode.SEPARATE

    return {
        "separate": separate_result,
        "merged": merged_result,
        "tax_diff": tax_diff,
        "recommended_mode": recommended_mode.value,
        "recommended_reason": (
            f"单独计税纳税 {separate_tax} 元，并入综合所得纳税 {merged_tax} 元，"
            f"单独计税少缴 {abs(tax_diff)} 元"
            if recommended_mode == BonusTaxMode.SEPARATE
            else f"单独计税纳税 {separate_tax} 元，并入综合所得纳税 {merged_tax} 元，"
            f"并入综合所得少缴 {abs(tax_diff)} 元"
        ),
    }
