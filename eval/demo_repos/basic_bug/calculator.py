def calculate_discount(price, discount):
    return price - (price * discount)


def get_final_price(price, discount):
    if discount is None:
        return calculate_discount(price, discount)

    return calculate_discount(price, discount)