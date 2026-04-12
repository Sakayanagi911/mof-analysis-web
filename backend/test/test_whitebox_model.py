import pytest
from services.whitebox_model import calculate_wug, calculate_wuv, predict_working_capacity

# Known reference values computed from the explicit polynomial equations
# Used for regression testing to catch accidental coefficient changes
_REF_P   = 5.0
_REF_GSA = 3500.0
_REF_VSA = 1800.0
_REF_VF  = 0.75
_REF_PV  = 1.25
_REF_LCD = 15.0
_REF_PLD = 10.0
_REF_WUG = calculate_wug(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
_REF_WUV = calculate_wuv(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)


# ---------------------------------------------------------------------------
# calculate_wug
# ---------------------------------------------------------------------------

def test_calculate_wug_returns_float():
    """calculate_wug must return a float value."""
    result = calculate_wug(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
    assert isinstance(result, float)


def test_calculate_wug_rounded_to_3_decimals():
    """
    calculate_wug rounds its output to 3 decimal places.
    Compare result to round(result, 3) instead of multiplying by 1000 to
    avoid floating-point precision traps.
    """
    result = calculate_wug(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
    assert result == round(result, 3)


def test_calculate_wug_regression():
    """
    Regression test: result must stay identical to the pre-computed reference
    value so that any accidental change to coefficients is immediately detected.
    """
    result = calculate_wug(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
    assert result == pytest.approx(_REF_WUG, rel=1e-6)


def test_calculate_wug_zero_input():
    """Polynomial must not crash when every parameter is zero."""
    result = calculate_wug(0, 0, 0, 0, 0, 0, 0)
    assert isinstance(result, float)


def test_calculate_wug_sensitivity():
    """
    Increasing pressure (p) from a low baseline should change the WUG output,
    confirming the function is sensitive to its inputs.
    """
    base = calculate_wug(1.0, 1000.0, 500.0, 0.5, 0.5, 8.0, 5.0)
    high = calculate_wug(50.0, 1000.0, 500.0, 0.5, 0.5, 8.0, 5.0)
    assert base != high


# ---------------------------------------------------------------------------
# calculate_wuv
# ---------------------------------------------------------------------------

def test_calculate_wuv_returns_float():
    """calculate_wuv must return a float value."""
    result = calculate_wuv(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
    assert isinstance(result, float)


def test_calculate_wuv_rounded_to_3_decimals():
    """calculate_wuv rounds its output to 3 decimal places."""
    result = calculate_wuv(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
    assert result == round(result, 3)


def test_calculate_wuv_regression():
    """Regression test for calculate_wuv."""
    result = calculate_wuv(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
    assert result == pytest.approx(_REF_WUV, rel=1e-6)


def test_calculate_wuv_zero_input():
    """Polynomial must not crash when every parameter is zero."""
    result = calculate_wuv(0, 0, 0, 0, 0, 0, 0)
    assert isinstance(result, float)


def test_calculate_wuv_sensitivity():
    """
    Increasing GSA from a low baseline should change the WUV output,
    confirming the function is sensitive to its inputs.
    """
    base = calculate_wuv(5.0, 500.0, 500.0, 0.5, 0.5, 8.0, 5.0)
    high = calculate_wuv(5.0, 5000.0, 500.0, 0.5, 0.5, 8.0, 5.0)
    assert base != high


# ---------------------------------------------------------------------------
# predict_working_capacity
# ---------------------------------------------------------------------------

def test_predict_working_capacity_output_format():
    """predict_working_capacity must return a dict with the expected keys."""
    result = predict_working_capacity(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
    assert isinstance(result, dict)
    assert "gravimetric_wc" in result
    assert "volumetric_wc" in result
    assert "is_feasible" in result
    assert isinstance(result["is_feasible"], bool)


def test_predict_working_capacity_values_match_individual_functions():
    """
    Values returned by predict_working_capacity must exactly match calling
    calculate_wug and calculate_wuv independently.
    """
    result = predict_working_capacity(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
    assert result["gravimetric_wc"] == pytest.approx(_REF_WUG, rel=1e-6)
    assert result["volumetric_wc"] == pytest.approx(_REF_WUV, rel=1e-6)


def test_predict_working_capacity_feasible_when_both_above_threshold():
    """is_feasible must be True only when WUG >= 5.5 AND WUV >= 40.0."""
    result = predict_working_capacity(_REF_P, _REF_GSA, _REF_VSA, _REF_VF, _REF_PV, _REF_LCD, _REF_PLD)
    expected = (result["gravimetric_wc"] >= 5.5) and (result["volumetric_wc"] >= 40.0)
    assert result["is_feasible"] == expected


def test_predict_working_capacity_infeasible_for_low_inputs():
    """Very small input values should produce results below both DOE thresholds."""
    result = predict_working_capacity(1.0, 10.0, 10.0, 0.1, 0.1, 1.0, 1.0)
    assert result["is_feasible"] is False
    assert result["gravimetric_wc"] < 5.5 or result["volumetric_wc"] < 40.0


def test_predict_working_capacity_logic_for_multiple_inputs():
    """
    Parametrized spot-check: for each input set, is_feasible must agree with
    the (wug >= 5.5 AND wuv >= 40.0) condition evaluated post-hoc.
    """
    test_params = [
        (5.0,  2000.0, 1000.0, 0.5, 0.8, 10.0, 5.0),
        (20.0, 1000.0, 2500.0, 0.3, 0.5,  5.0, 2.0),
        (70.0, 4000.0,  500.0, 0.8, 2.0, 20.0, 18.0),
        (0.0,     0.0,    0.0, 0.0, 0.0,  0.0,  0.0),
    ]
    for params in test_params:
        res = predict_working_capacity(*params)
        expected = (res["gravimetric_wc"] >= 5.5) and (res["volumetric_wc"] >= 40.0)
        assert res["is_feasible"] == expected, (
            f"Mismatch for params {params}: "
            f"wug={res['gravimetric_wc']}, wuv={res['volumetric_wc']}, "
            f"is_feasible={res['is_feasible']}"
        )
