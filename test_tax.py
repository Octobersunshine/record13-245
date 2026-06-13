from tax_calculator import calculate_tax


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


if __name__ == "__main__":
    print("开始运行个税计算测试...\n")
    test_case_1()
    test_case_2()
    test_case_3()
    test_case_4()
    test_case_5()
    test_case_6()
    print("所有测试用例通过！")
