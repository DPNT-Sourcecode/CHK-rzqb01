from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    unit_price: int


@dataclass
def MultiOffer:
    sku: str
    quantity: int
    total_price: int


@dataclass
def FreeOffer:
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
MULTI_OFFERS = {
    "A": MultiOffer(sku="A", quantity=3, total_price=130),
    "A": MultiOffer(sku="A", quantity=5, total_price=200),
    "B": MultiOffer(sku="B", quantity=2, total_price=45),
}
FREE_OFFERS = {
    "E": OtherItemOffer(sku="E", quantity=2, target_sku="B", target_quantity=1),
}


# noinspection PyUnusedLocal
# skus = unicode string
def checkout(skus: str) -> int:
    basket = Counter(skus)

    for sku, offer in FREE_OFFERS.items():
        quantity = basket.get(sku)
        if quantity is None or quantity < offer.quantity:
            continue

        target_quantity = basket.get(offer.target_sku)
        if target_quantity is None or target_quantity < offer.target_quantity:
            continue

        basket[offer.target_sku] -= offer.target_quantity

    prices = defaultdict(int)

    for sku, basket_quantity in basket.items():
        current_quantity = basket_quantity
        item = PRICE_TABLE.get(sku)
        if item is None:
            return -1

        multi_offers = [v for v in MULTI_OFFERS.values() if v.sku == sku]
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
