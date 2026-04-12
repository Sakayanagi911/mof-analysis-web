import pytest
from services.whitebox_model import calculate_wug, calculate_wuv, predict_working_capacity

def test_calculate_wug_basic():
    """
    Test calculate_wug returns a float and is rounded to 3 decimals.
    """
    result = calculate_wug(5.0, 3500.0, 1800.0, 0.75, 1.25, 15.0, 10.0)
    assert isinstance(result, float)
    # Check if rounded to 3 decimals (multiplying by 1000 should result in an integer-like float)
    assert round(result * 1000) == result * 1000

def test_calculate_wuv_basic():
    """
    Test calculate_wuv returns a float and is rounded to 3 decimals.
    """
    result = calculate_wuv(5.0, 3500.0, 1800.0, 0.75, 1.25, 15.0, 10.0)
    assert isinstance(result, float)
    assert round(result * 1000) == result * 1000

def test_calculate_functions_zero_input():
    """
    Verify that the polynomial equations handle zero inputs without crashing.
    """
    wug = calculate_wug(0, 0, 0, 0, 0, 0, 0)
    wuv = calculate_wuv(0, 0, 0, 0, 0, 0, 0)
    assert isinstance(wug, float)
    assert isinstance(wuv, float)

def test_predict_working_capacity_output_format():
    """
    Test predict_working_capacity returns the correct dictionary structure.
    """
    result = predict_working_capacity(5.0, 3500.0, 1800.0, 0.75, 1.25, 15.0, 10.0)
    assert isinstance(result, dict)
    assert "gravimetric_wc" in result
    assert "volumetric_wc" in result
    assert "is_feasible" in result
    assert isinstance(result["is_feasible"], bool)

def test_predict_working_capacity_logic_consistency():
    """
    Ensure the is_feasible flag is correctly calculated based on WUG and WUV thresholds.
    Thresholds: WUG >= 5.5 AND WUV >= 40.0
    """
    # High values
    res_high = predict_working_capacity(100.0, 5000.0, 3000.0, 0.9, 3.0, 30.0, 25.0)
    expected_high = (res_high["gravimetric_wc"] >= 5.5) and (res_high["volumetric_wc"] >= 40.0)
    assert res_high["is_feasible"] == expected_high

    # Low values
    res_low = predict_working_capacity(1.0, 10.0, 10.0, 0.1, 0.1, 1.0, 1.0)
    assert res_low["is_feasible"] is False
    assert res_low["gravimetric_wc"] < 5.5 or res_low["volumetric_wc"] < 40.0

def test_predict_working_capacity_partial_feasibility():
    """
    Test that it returns False if only one of the criteria is met.
    (This depends on the actual polynomial output for specific inputs).
    """
    # We find a case where one might be high but other is low if possible,
    # but the logic check (A and B) is what matters most.

    # Mocking or specifically calculated values are usually better here,
    # but since these are pure functions, we check the conditional logic.
    params = [
        (5.0, 2000.0, 1000.0, 0.5, 0.8, 10.0, 5.0),
        (20.0, 1000.0, 2500.0, 0.3, 0.5, 5.0, 2.0),
        (70.0, 4000.0, 500.0, 0.8, 2.0, 20.0, 18.0)
    ]

    for p in params:
        res = predict_working_capacity(*p)
        if res["gravimetric_wc"] >= 5.5 and res["volumetric_wc"] >= 40.0:
            assert res["is_feasible"] is True
        else:
            assert res["is_feasible"] is False
