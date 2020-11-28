from extra_print import print_green, print_red, \
    _determine_print_color_from_prices


def test__determine_print_color_from_prices__green():
    result = _determine_print_color_from_prices(12.3, 9)
    assert print_green == result


def test__determine_print_color_from_prices__red():
    result = _determine_print_color_from_prices(0.5, 0.9)
    assert print_red == result


def test__determine_print_color_from_prices__red_eq():
    result = _determine_print_color_from_prices(3, 3)
    assert print_red == result
