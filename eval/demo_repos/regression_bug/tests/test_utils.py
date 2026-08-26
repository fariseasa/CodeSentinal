from utils import format_username


def test_format_username():
    assert format_username("  FARIS  ") == "Faris"