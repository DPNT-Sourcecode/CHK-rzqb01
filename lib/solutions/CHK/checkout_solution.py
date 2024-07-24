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


@dataclass(frozen=True)
class GroupOffer:
    skus: frozenset[str]
    quantity: int
    total_price: int


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
RAW_PRICE_TABLE = """\
+------+-------+---------------------------------+
| Item | Price | Special offers                  |
+------+-------+---------------------------------+
| A    | 50    | 3A for 130, 5A for 200          |
| B    | 30    | 2B for 45                       |
| C    | 20    |                                 |
| D    | 15    |                                 |
| E    | 40    | 2E get one B free               |
| F    | 10    | 2F get one F free               |
| G    | 20    |                                 |
| H    | 10    | 5H for 45, 10H for 80           |
| I    | 35    |                                 |
| J    | 60    |                                 |
| K    | 70    | 2K for 120                      |
| L    | 90    |                                 |
| M    | 15    |                                 |
| N    | 40    | 3N get one M free               |
| O    | 10    |                                 |
| P    | 50    | 5P for 200                      |
| Q    | 30    | 3Q for 80                       |
| R    | 50    | 3R get one Q free               |
| S    | 20    | buy any 3 of (S,T,X,Y,Z) for 45 |
| T    | 20    | buy any 3 of (S,T,X,Y,Z) for 45 |
| U    | 40    | 3U get one U free               |
| V    | 50    | 2V for 90, 3V for 130           |
| W    | 20    |                                 |
| X    | 17    | buy any 3 of (S,T,X,Y,Z) for 45 |
| Y    | 20    | buy any 3 of (S,T,X,Y,Z) for 45 |
| Z    | 21    | buy any 3 of (S,T,X,Y,Z) for 45 |
+------+-------+---------------------------------+\
"""

MULTI_OFFER_RE = re.compile(r"^(?P<quantity>\d+)(?P<sku>[A-Za-z]) for (?P<total_price>\d+)$")
FREE_OFFER_RE = re.compile(
    r"^(?P<quantity>\d+)(?P<sku>[A-Za-z]) get one (?P<target_sku>[A-Za-z]) free$"
)
GROUP_OFFER_RE = re.compile(
    r"^buy any (?P<quantity>\d+) of \((?P<skus>[A-Z,]+)\) for (?P<total_price>\d+)$"
)

PRICE_TABLE = {}
MULTI_OFFERS = []
FREE_OFFERS = []
GROUP_OFFERS = set()

for row in RAW_PRICE_TABLE.splitlines():
    if row.startswith("+") or "Special offers" in row or not row.strip():
        continue

    _, sku, raw_price, raw_offers, _ = [col.strip() for col in row.split("|")]
    PRICE_TABLE[sku] = Item(sku=sku, unit_price=int(raw_price))

    if "buy any" in raw_offers:
        offers = [raw_offers.strip()]
    else:
        offers = [o.strip() for o in raw_offers.split(",")]
    offers = [o for o in offers if o]
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

        group_match = GROUP_OFFER_RE.match(offer)
        if group_match:
            GROUP_OFFERS.add(
                GroupOffer(
                    skus=frozenset(group_match["skus"].split(",")),
                    quantity=int(group_match["quantity"]),
                    total_price=int(group_match["total_price"])
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

    checkout_price = 0

    for offer in GROUP_OFFERS:
        quantities = {sku: basket.get(sku) for sku in offer.skus if basket.get(sku) is not None}
        total_quantity = sum(quantities.values())
        if total_quantity < offer.quantity:
            continue

        times_offer_applied = total_quantity // offer.quantity
        checkout_price += times_offer_applied * offer.total_price

        # import code; code.interact(local=locals())

        quantity_to_remove = times_offer_applied * offer.quantity
        for sku in offer.skus:
            if sku not in basket:
                continue

            quantity = basket[sku]
            quantity_removed = min(quantity_to_remove, quantity)
            basket[sku] -= quantity_removed
            quantity_to_remove -= quantity_removed

            if quantity_to_remove == 0:
                break

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

    checkout_price += sum(prices.values())

    return checkout_price


