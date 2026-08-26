from app import get_user_response


def test_user_response():

    response = get_user_response(42)

    assert response["id"] == 42
    assert response["name"] == "Faris"
    assert response["status"] == "success"