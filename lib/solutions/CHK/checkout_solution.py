from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    unit_price: int


@dataclass
class MultiOffer:
    sku: str
    quantity: int
    total_price: int


@dataclass
class FreeOffer:
    sku: str
    quantity: int
    target_sku: str
    target_quantity: int


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
FREE_OFFERS = [
    FreeOffer(sku="E", quantity=2, target_sku="B", target_quantity=1),
]


# noinspection PyUnusedLocal
# skus = unicode string
def checkout(skus: str) -> int:
    basket = Counter(skus)

    for offer in FREE_OFFERS:
        quantity = basket.get(offer.sku)
        if quantity is None or quantity < offer.quantity:
            continue

        target_quantity = basket.get(offer.target_sku)
        if target_quantity is None or target_quantity < offer.target_quantity:
            continue

        times_offer_can_be_applied = quantity // offer.quantity
        target_items_allowed_free = times_offer_can_be_applied * offer.target_quantity
        updated_target_quantity = target_quantity - target_items_allowed_free
        basket[offer.target_sku] = max(updated_target_quantity, 0)

    prices = defaultdict(int)

    for sku, basket_quantity in basket.items():
        current_quantity = basket_quantity
        item = PRICE_TABLE.get(sku)
        if item is None:
            return -1

        multi_offers = [v for v in MULTI_OFFERS if v.sku == sku]
        if not multi_offers:
            prices[sku] = current_quantity * item.unit_price
            continue

        multi_offers = sorted(multi_offers, key=lambda o: o.quantity, reverse=True)
        for offer in multi_offers:
            times_offer_applied, remaining_quantity = divmod(current_quantity, offer.quantity)
            price_with_offer = times_offer_applied * offer.total_price
            prices[sku] += price_with_offer

            current_quantity = remaining_quantity

        prices[sku] += current_quantity * item.unit_price

    return sum(prices.values())
