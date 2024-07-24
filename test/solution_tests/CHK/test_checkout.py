import pytest

from solutions.CHK.checkout_solution import  MultiOffer, Item, checkout


@pytest.fixture
def offer():
    return MultiOffer(quantity=3, total_price=20)


@pytest.fixture
def item():
    return Item(sku="A", unit_price=10)


class TestCheckout:
    def test_returns_zero_when_basket_empty(self):
        assert checkout("") == 0

    @pytest.mark.parametrize(
        "basket",
        ["X", "AX", "ABCDX"]
    )
    def test_returns_minus_one_when_item_not_found(self, basket):
        assert checkout(basket) == -1

    @pytest.mark.parametrize(
        "basket,expected",
        [
            ("A", 50),
            ("AA", 100),
            ("AB", 80),
        ]
    )
    def test_no_offers(self, basket, expected):
        assert checkout(basket) == expected

    @pytest.mark.parametrize(
        "basket,expected",
        [
            ("A" * 3, 130),
            ("A" * 4, 130 + 50),
            ("A" * 5, 200),
            ("A" * 6, 200 + 50),
            ("A" * 10, 200 * 2),
            ("A" * 11, 200 * 2 + 50),
            ("A" * 13, 200 * 2 + 130),
        ]
    )
    def test_multi_offers(self, basket, expected):
        assert checkout(basket) == expected

    @pytest.mark.parametrize(
        "basket,expected",
        [
            ("EEB", 40 * 2),
            ("EEEEBB", 40 * 4),
            ("EEBB", 40 * 2 + 30)
        ]
    )
    def test_free_offers(self, basket, expected):
        assert checkout(basket) == expected

    @pytest.mark.parametrize(
        "basket,expected",
        [
            ("F", 10),
            ("FF", 10 * 2),
            ("FFF", 10 * 2),
            ("FFFF", 10 * 2 + 10),
        ]
    )
    def test_free_offers_same_item(self, basket, expected):
        assert checkout(basket) == expected

    @pytest.mark.parametrize(
        "basket,expected",
        [
            ("EEBBB", 40 * 2 + 45),
            ("EEEEBBB", 40 * 4 + 30),
        ]
    )
    def test_combined_offers(self, basket, expected):
        assert checkout(basket) == expected
