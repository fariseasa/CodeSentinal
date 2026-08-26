from parser import get_first_item


def test_first_item():
    assert get_first_item(["apple", "banana"]) == "apple"


def test_empty_list():
    assert get_first_item([]) is None