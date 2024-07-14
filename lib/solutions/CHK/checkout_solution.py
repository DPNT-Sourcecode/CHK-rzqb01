from typing import Optional, List
from collections import Counter

class Offer:
    def __init__(self, quantity: int, total_price: int):
        self.quantity = quantity
        self.total_price = total_price


class Item:
    def __init__(self, sku: str, unit_price: int, offers: Optional[List[Offer]] = None):
        self.sku = sku
        self.unit_price = unit_price
        self.offers = offers if offers is not None else []

    def calculate_price(self, quantity: int) -> int:
        if self.offer is None:
            return quantity * self.unit_price

        times_offer_applied, remaining_quantity = divmod(quantity, self.offer.quantity)
        price_with_offer = times_offer_applied * self.offer.total_price
        return price_with_offer + remaining_quantity * self.unit_price


PRICE_TABLE = {
    "A": Item(sku="A", unit_price=50, offers=Offer(quantity=3, total_price=130)),
    "B": Item(sku="B", unit_price=30, offers=Offer(quantity=2, total_price=45)),
    "C": Item(sku="C", unit_price=20),
    "D": Item(sku="D", unit_price=15),
}


# noinspection PyUnusedLocal
# skus = unicode string
def checkout(skus: str) -> int:
    # assuming skus looks like ABCD
    total_price = 0
    basket = Counter(skus)
    for sku, quantity in basket.items():
        item = PRICE_TABLE.get(sku)
        if item is None:
            return -1

        total_price += item.calculate_price(quantity)

    return total_price
