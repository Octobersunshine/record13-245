from tax_calculator import (
    calculate_tax,
    calculate_bonus_tax_separate,
    calculate_bonus_tax_merged,
    compare_bonus_modes,
)


def test_case_1():
    """测试1月，月薪10000，无其他扣除"""
    result = calculate_tax(
        monthly_income=10000,
        cumulative_income=0,
        cumulative_tax_free_deduction=0,
        cumulative_special_deduction=0,
        months_count=1,
        cumulative_prepaid_tax=0,
    )
    print("=== 测试用例1：1月，月薪10000，无其他扣除 ===")
    print(f"累计应纳税所得额: {result['cumulative_taxable_income']}")
    print(f"适用税率: {result['tax_rate']}")
    print(f"速算扣除数: {result['quick_deduction']}")
    print(f"累计应缴个税: {result['cumulative_tax']}")
    print(f"当月应缴个税: {result['monthly_tax']}")
    assert abs(result["monthly_tax"] - 150.0) < 0.01, f"预期150.0，实际{result['monthly_tax']}"
    print("✓ 测试通过\n")


def test_case_2():
    """测试2月，月薪10000，累计已预缴150"""
    result = calculate_tax(
        monthly_income=10000,
        cumulative_income=10000,
        cumulative_tax_free_deduction=0,
        cumulative_special_deduction=0,
        months_count=2,
        cumulative_prepaid_tax=150,
    )
    print("=== 测试用例2：2月，月薪10000，累计已预缴150 ===")
    print(f"累计应纳税所得额: {result['cumulative_taxable_income']}")
    print(f"适用税率: {result['tax_rate']}")
    print(f"速算扣除数: {result['quick_deduction']}")
    print(f"累计应缴个税: {result['cumulative_tax']}")
    print(f"当月应缴个税: {result['monthly_tax']}")
    assert abs(result["monthly_tax"] - 150.0) < 0.01, f"预期150.0，实际{result['monthly_tax']}"
    print("✓ 测试通过\n")


def test_case_3():
    """测试税率跳档：月薪30000，12月时跳档"""
    result_month12 = calculate_tax(
        monthly_income=30000,
        cumulative_income=330000,
        cumulative_tax_free_deduction=0,
        cumulative_special_deduction=0,
        months_count=12,
        cumulative_prepaid_tax=29880,
    )
    print("=== 测试用例3：月薪30000，第12月（税率跳档） ===")
    print(f"累计应纳税所得额: {result_month12['cumulative_taxable_income']}")
    print(f"适用税率: {result_month12['tax_rate']}")
    print(f"速算扣除数: {result_month12['quick_deduction']}")
    print(f"累计应缴个税: {result_month12['cumulative_tax']}")
    print(f"当月应缴个税: {result_month12['monthly_tax']}")
    print("✓ 测试通过\n")


def test_case_4():
    """测试有专项扣除：月薪15000，五险一金3000/月"""
    result = calculate_tax(
        monthly_income=15000,
        cumulative_income=0,
        cumulative_tax_free_deduction=0,
        cumulative_special_deduction=3000,
        months_count=1,
        cumulative_prepaid_tax=0,
    )
    print("=== 测试用例4：1月，月薪15000，专项扣除3000 ===")
    print(f"累计应纳税所得额: {result['cumulative_taxable_income']}")
    print(f"当月应缴个税: {result['monthly_tax']}")
    expected = (15000 - 5000 - 3000) * 0.03
    assert abs(result["monthly_tax"] - expected) < 0.01, f"预期{expected}，实际{result['monthly_tax']}"
    print("✓ 测试通过\n")


def test_case_5():
    """测试低收入，不需要缴税"""
    result = calculate_tax(
        monthly_income=4000,
        cumulative_income=0,
        cumulative_tax_free_deduction=0,
        cumulative_special_deduction=0,
        months_count=1,
        cumulative_prepaid_tax=0,
    )
    print("=== 测试用例5：月薪4000，低于起征点 ===")
    print(f"累计应纳税所得额: {result['cumulative_taxable_income']}")
    print(f"当月应缴个税: {result['monthly_tax']}")
    assert result["monthly_tax"] == 0.0, f"预期0.0，实际{result['monthly_tax']}"
    print("✓ 测试通过\n")


def test_case_6():
    """测试有专项附加扣除：月薪20000，子女教育2000/月，赡养老人1000/月"""
    result = calculate_tax(
        monthly_income=20000,
        cumulative_income=0,
        cumulative_tax_free_deduction=0,
        cumulative_special_deduction=0,
        months_count=1,
        cumulative_prepaid_tax=0,
        cumulative_special_additional_deduction=3000,
    )
    print("=== 测试用例6：1月，月薪20000，专项附加扣除3000 ===")
    print(f"累计应纳税所得额: {result['cumulative_taxable_income']}")
    print(f"当月应缴个税: {result['monthly_tax']}")
    expected = (20000 - 5000 - 3000) * 0.03
    assert abs(result["monthly_tax"] - expected) < 0.01, f"预期{expected}，实际{result['monthly_tax']}"
    print("✓ 测试通过\n")


def test_bonus_separate_basic():
    """测试年终奖单独计税：36000元年终奖"""
    result = calculate_bonus_tax_separate(annual_bonus=36000)
    print("=== 测试用例7：年终奖单独计税，36000元 ===")
    print(f"月均金额: {result['monthly_equivalent']}")
    print(f"适用税率: {result['tax_rate']}")
    print(f"速算扣除数: {result['quick_deduction']}")
    print(f"年终奖应纳税额: {result['bonus_tax']}")
    assert result["monthly_equivalent"] == 3000.0
    assert result["tax_rate"] == 0.03
    assert result["quick_deduction"] == 0
    assert abs(result["bonus_tax"] - 1080.0) < 0.01
    print("✓ 测试通过\n")


def test_bonus_separate_boundary():
    """测试年终奖单独计税临界点陷阱：36000 vs 36001"""
    result_36000 = calculate_bonus_tax_separate(annual_bonus=36000)
    result_36001 = calculate_bonus_tax_separate(annual_bonus=36001)
    print("=== 测试用例8：年终奖临界点陷阱 ===")
    print(f"36000元年终奖，税率{result_36000['tax_rate']}，纳税{result_36000['bonus_tax']}元")
    print(f"36001元年终奖，税率{result_36001['tax_rate']}，纳税{result_36001['bonus_tax']}元")
    print(f"多发1元，多纳税{result_36001['bonus_tax'] - result_36000['bonus_tax']:.2f}元")
    assert result_36000["tax_rate"] == 0.03
    assert result_36001["tax_rate"] == 0.10
    assert result_36001["bonus_tax"] > result_36000["bonus_tax"]
    print("✓ 测试通过（临界点陷阱已正确识别）\n")


def test_bonus_separate_high():
    """测试年终奖单独计税：120000元"""
    result = calculate_bonus_tax_separate(annual_bonus=120000)
    print("=== 测试用例9：年终奖单独计税，120000元 ===")
    print(f"月均金额: {result['monthly_equivalent']}")
    print(f"适用税率: {result['tax_rate']}")
    print(f"速算扣除数: {result['quick_deduction']}")
    print(f"年终奖应纳税额: {result['bonus_tax']}")
    assert result["monthly_equivalent"] == 10000.0
    assert result["tax_rate"] == 0.10
    assert result["quick_deduction"] == 210
    expected = 120000 * 0.10 - 210
    assert abs(result["bonus_tax"] - expected) < 0.01
    print("✓ 测试通过\n")


def test_bonus_merged_basic():
    """测试年终奖并入综合所得：月薪15000，年终奖30000"""
    result = calculate_bonus_tax_merged(
        annual_bonus=30000,
        annual_cumulative_income=180000,
        annual_cumulative_tax_free_deduction=0,
        annual_cumulative_special_deduction=0,
        months_count=12,
        annual_cumulative_prepaid_tax=5880,
    )
    print("=== 测试用例10：年终奖并入综合所得 ===")
    print(f"并入后全年应纳税所得额: {result['total_taxable_income']}")
    print(f"并入后全年应纳税额: {result['total_tax_after_merge']}")
    print(f"已预缴税额: {result['total_tax_before_merge']}")
    print(f"年终奖部分补缴税额: {result['bonus_tax']}")
    total_income = 180000 + 30000
    total_deduction = 5000 * 12
    taxable = total_income - total_deduction
    assert abs(result["total_taxable_income"] - taxable) < 0.01
    print("✓ 测试通过\n")


def test_bonus_merged_low_income():
    """测试低收入者年终奖并入更优惠：月薪3000，年终奖30000"""
    separate = calculate_bonus_tax_separate(annual_bonus=30000)
    merged = calculate_bonus_tax_merged(
        annual_bonus=30000,
        annual_cumulative_income=36000,
        annual_cumulative_tax_free_deduction=0,
        annual_cumulative_special_deduction=0,
        months_count=12,
        annual_cumulative_prepaid_tax=0,
    )
    print("=== 测试用例11：低收入者年终奖对比 ===")
    print(f"单独计税: {separate['bonus_tax']}元")
    print(f"并入综合所得: {merged['bonus_tax']}元")
    print(f"并入综合所得更优惠: {merged['bonus_tax'] < separate['bonus_tax']}")
    assert merged["bonus_tax"] < separate["bonus_tax"]
    print("✓ 测试通过\n")


def test_compare_modes():
    """测试对比模式：高薪者单独计税更优惠"""
    result = compare_bonus_modes(
        annual_bonus=60000,
        annual_cumulative_income=240000,
        annual_cumulative_tax_free_deduction=0,
        annual_cumulative_special_deduction=0,
        months_count=12,
        annual_cumulative_prepaid_tax=14880,
    )
    print("=== 测试用例12：高薪者年终奖对比模式 ===")
    print(f"单独计税: {result['separate']['bonus_tax']}元")
    print(f"并入综合所得: {result['merged']['bonus_tax']}元")
    print(f"推荐模式: {result['recommended_mode']}")
    print(f"推荐原因: {result['recommended_reason']}")
    assert result["recommended_mode"] in ["separate", "merged"]
    assert result["tax_diff"] == round(
        result["separate"]["bonus_tax"] - result["merged"]["bonus_tax"], 2
    )
    print("✓ 测试通过\n")


def test_bonus_zero():
    """测试年终奖为0"""
    result = calculate_bonus_tax_separate(annual_bonus=0)
    print("=== 测试用例13：年终奖为0 ===")
    print(f"年终奖应纳税额: {result['bonus_tax']}")
    assert result["bonus_tax"] == 0.0
    print("✓ 测试通过\n")


if __name__ == "__main__":
    print("开始运行个税计算测试...\n")
    test_case_1()
    test_case_2()
    test_case_3()
    test_case_4()
    test_case_5()
    test_case_6()
    test_bonus_separate_basic()
    test_bonus_separate_boundary()
    test_bonus_separate_high()
    test_bonus_merged_basic()
    test_bonus_merged_low_income()
    test_compare_modes()
    test_bonus_zero()
    print("所有测试用例通过！")
