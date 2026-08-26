from calculator import get_final_price


def test_discount():
    assert get_final_price(100, 0.10) == 90


def test_no_discount():
    assert get_final_price(100, None) == 100