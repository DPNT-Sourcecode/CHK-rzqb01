import pytest

from solutions.CHK.checkout_solution import  Offer, Item, checkout


@pytest.fixture
def offer():
    return Offer(quantity=3, total_price=20)


@pytest.fixture
def item():
    return Item(sku="A", unit_price=10)


@pytest.fixture
def item_with_offer(item, offer):
    item.offer = offer
    return item


class TestItemPrice:
    @pytest.mark.parametrize(
        "quantity,expected",
        [
            (0, 0),
            (1, 10),
            (10, 100)
        ]
    )
    def test_without_offer(self, item, quantity, expected):
        assert item.calculate_price(quantity) == expected

    @pytest.mark.parametrize(
        "quantity,expected",
        [
            (0, 0),
            (1, 10),
            (2, 20),
            (3, 20),
            (4, 30),
            (6, 40),
            (9, 60),
            (100, (99/3) * 20 + 10)
        ]
    )
    def test_with_offer(self, item_with_offer, quantity, expected):
        assert item_with_offer.calculate_price(quantity) == expected


class TestCheckout:
    def test_returns_zero_when_basket_empty(self):
        assert checkout("") == 0

    @pytest.mark.parametrize(
        "basket",
        ["X", "AX", "ABCDX"]
    )
    def test_returns_minus_one_when_item_not_found(self, basket):
        assert checkout(basket) == -1

    def test_checkout_returns_total_value(self):
        price_a = 130
        price_b = 45 + 30
        price_c = 20 * 2
        price_d = 15
        assert checkout("AAABBBCCD") == price_a + price_b + price_c + price_d
