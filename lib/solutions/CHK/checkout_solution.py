from collections import Counter
from typing import List, Optional


class Offer:
    pass


class MultiOffer(Offer):
    def __init__(self, sku: str, quantity: int, total_price: int):
        self.sku = sku
        self.quantity = quantity
        self.total_price = total_price


class OtherItemOffer(Offer):
    def __init__(self, sku: str, quantity: int, other_sku: str, other_quantity: int):
        self.sku = sku
        self.quantity = quantity
        self.other_sku = other_sku
        self.other_quantity = other_quantity


class Item:
    def __init__(self, sku: str, unit_price: int):
        self.sku = sku
        self.unit_price = unit_price

    def calculate_price(self, quantity: int) -> int:

        times_offer_applied, remaining_quantity = divmod(quantity, self.offer.quantity)
        price_with_offer = times_offer_applied * self.offer.total_price
        return price_with_offer + remaining_quantity * self.unit_price


class Basket:
    def __init__(self, skus: List[str]):
        self.skus = Counter(skus)


PRICE_TABLE = {
    "A": Item(sku="A", unit_price=50),
    "B": Item(sku="B", unit_price=30),
    "C": Item(sku="C", unit_price=20),
    "D": Item(sku="D", unit_price=15),
    "E": Item(sku="E", unit_price=40),
}
MULTI_OFFERS = [
    MultiOffer(sku="A", quantity=3, total_price=130),
    MultiOffer(sku="A", quantity=5, total_price=200),
    MultiOffer(sku="B", quantity=2, total_price=45),
]
OTHER_ITEM_OFFERS = [
    OtherItemOffer(sku="E", quantity=2, other_sku="B", other_quantity=1),
]


# noinspection PyUnusedLocal
# skus = unicode string
def checkout(skus: str) -> int:
    # assuming skus looks like ABCD
    basket = Counter(skus)
    for offer in OTHER_ITEM_OFFERS:
        quantity_in_basket = basket.get(offer.sku)
        other_quantity_in_basket = basket.get(offer.other_sku)
        if (
                quantity_in_basket is None or
                quantity_in_basket < offer.quantity or
                other_quantity_in_basket is None or
                other_quantity_in_basket < offer.other_quantity
        ):
            continue
        basket[offer.other_sku] -= offer.other_quantity

    prices = {}
    for offer in MULTI_OFFERS:
        quantity_in_basket = basket.get(offer.sku)
        item = PRICE_TABLE.get(offer.sku)
        if quantity_in_basket is None or item is None or quantity_in_basket < offer.quantity:
            continue

        times_offer_applied, remaining_quantity = divmod(quantity_in_basket, offer.quantity)
        price_with_offer = times_offer_applied * offer.total_price
        prices[offer.sku] = price_with_offer + remaining_quantity * item.unit_price

    total_price = 0
    for sku, quantity in basket.items():
        item = PRICE_TABLE.get(sku)
        if item is None:
            return -1

        total_price += item.calculate_price(quantity)

    return total_price
