from calculator import get_final_price


def main():
    price = 100
    discount = None

    result = get_final_price(price, discount)

    print(result)


if __name__ == "__main__":
    main()