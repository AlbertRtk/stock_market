from simulator import calculate_investment_value, _determine_print_color_from_prices
from extra_print import print_green, print_red
from wallet.wallet import Wallet


def test_calculate_investment_value__max():
    wallet = Wallet(0.01, 3)  # min recomended investment = 300
    wallet.money = 10000
    max_fraction = 5
    expected_result = 2000

    result = calculate_investment_value(wallet, max_fraction)

    assert expected_result == result


def test_calculate_investment_value__low_money():
    wallet = Wallet(0.01, 3)  # min recomended investment = 300
    wallet.money = 100
    max_fraction = 5
    expected_result = 0

    result = calculate_investment_value(wallet, max_fraction)

    assert expected_result == result


def test_calculate_investment_value__min():
    wallet = Wallet(0.01, 3)  # min recomended investment = 300
    wallet.money = 500
    max_fraction = 5
    expected_result = 300

    result = calculate_investment_value(wallet, max_fraction)

    assert expected_result == result


def test_calculate_investment_value__invest_all():
    wallet = Wallet(0.01, 3)  # min recomended investment = 300
    wallet.money = 2000
    wallet.buy('CCC', 20, 50)  # cost = 1010
    max_fraction = 2
    expected_result = 990

    result = calculate_investment_value(wallet, max_fraction)

    assert expected_result == result


def test_calculate_investment_value__no_money():
    wallet = Wallet(0.01, 3)  # min recomended investment = 300
    wallet.money = 1010
    wallet.buy('CCC', 20, 50)  # cost = 1010
    max_fraction = 2
    expected_result = 0

    result = calculate_investment_value(wallet, max_fraction)

    assert expected_result == result


def test__determine_print_color_from_prices__green():
    result = _determine_print_color_from_prices(12.3, 9)
    assert print_green == result


def test__determine_print_color_from_prices__red():
    result = _determine_print_color_from_prices(0.5, 0.9)
    assert print_red == result


def test__determine_print_color_from_prices__red_eq():
    result = _determine_print_color_from_prices(3, 3)
    assert print_red == result
