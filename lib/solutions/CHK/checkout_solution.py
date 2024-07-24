from collections import Counter, defaultdict
from dataclasses import dataclass
import re


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
    "F": Item(sku="F", unit_price=10),
}
MULTI_OFFERS = [
    MultiOffer(sku="A", quantity=3, total_price=130),
    MultiOffer(sku="A", quantity=5, total_price=200),
    MultiOffer(sku="B", quantity=2, total_price=45),
]
FREE_OFFERS = [
    FreeOffer(sku="E", quantity=2, target_sku="B", target_quantity=1),
    FreeOffer(sku="F", quantity=2, target_sku="F", target_quantity=1),
]

RAW_PRICE_TABLE = """\
+------+-------+------------------------+
| Item | Price | Special offers         |
+------+-------+------------------------+
| A    | 50    | 3A for 130, 5A for 200 |
| B    | 30    | 2B for 45              |
| C    | 20    |                        |
| D    | 15    |                        |
| E    | 40    | 2E get one B free      |
| F    | 10    | 2F get one F free      |
| G    | 20    |                        |
| H    | 10    | 5H for 45, 10H for 80  |
| I    | 35    |                        |
| J    | 60    |                        |
| K    | 80    | 2K for 150             |
| L    | 90    |                        |
| M    | 15    |                        |
| N    | 40    | 3N get one M free      |
| O    | 10    |                        |
| P    | 50    | 5P for 200             |
| Q    | 30    | 3Q for 80              |
| R    | 50    | 3R get one Q free      |
| S    | 30    |                        |
| T    | 20    |                        |
| U    | 40    | 3U get one U free      |
| V    | 50    | 2V for 90, 3V for 130  |
| W    | 20    |                        |
| X    | 90    |                        |
| Y    | 10    |                        |
| Z    | 50    |                        |
+------+-------+------------------------+\
"""

MULTI_OFFER_RE = re.compile(r"(?P<quantity>\d+)(?P<sku>[A-Za-z]) for (?P<total_price>\d+)")
FREE_OFFER_RE = re.compile(r"(?P<quantity>\d+)(?P<sku>[A-Za-z]) get one (?P<target_sku>[A-Za-z]) free")
PRICE_TABLE = {}
MULTI_OFFERS = []
FREE_OFFERS = []

for row in RAW_PRICE_TABLE.splitlines():
    if row.startswith("+") or "Special offers" in row or not row.strip():
        continue

    _, sku, raw_price, raw_offers, _ = [col.strip() for col in row.split("|")]
    PRICE_TABLE[sku] = Item(sku=sku, unit_price=int(raw_price))

    offers = (o.strip() for o in raw_offers.split(","))
    offers = (o for o in offers if o)
    for offer in offers:
        multi_match = MULTI_OFFER_RE.match(offer)
        if multi_match:
            MULTI_OFFERS.append(
                MultiOffer(
                    sku=multi_match["sku"], quantity=int(multi_match["quantity"]),
                    total_price=int(multi_match["total_price"])
                )
            )
            continue

        free_match = FREE_OFFER_RE.match(offer)
        if free_match:
            FREE_OFFERS.append(
                FreeOffer(
                    sku=free_match["sku"], quantity=int(free_match["quantity"]),
                    target_sku=free_match["target_sku"], target_quantity=1
                )
            )
            continue

        raise RuntimeError(offer)


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

        if offer.sku == offer.target_sku:
            times_offer_can_be_applied = quantity // (offer.quantity + offer.target_quantity)
        else:
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
