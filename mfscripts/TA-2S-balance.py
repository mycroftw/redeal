"""Simming a balancing decision."""

import pprint
from collections import Counter

from redeal import (
    A,
    Deal,
    Evaluator,
    H,
    Hand,
    Seat,
    Shape,
    SmartStack,
    balanced,
    hcp,
)
from redeal.redeal import Contract, ScoredContract

weak_2_spades_shape = Shape("6xxx") - Shape(
    "64xx"
)  # more extreme are removed in accept
top_3 = Evaluator(1, 1, 1)  # how many of "top 3" in a suit
top_5 = Evaluator(1, 1, 1, 1, 1)
predeal = {
    "S": H("4 JT8542 AK5 AK3"),
    "W": SmartStack(weak_2_spades_shape, hcp, range(6, 11)),
}
contract_counter = Counter()


def two_spades_preempt(hand: Hand) -> bool:
    """Clean up the smartstack to get "traditional" weak 2.

    This is a first seat, RED on WHITE, weak 2S.  Let's assume it's normal.
    """
    if hand.l1 + hand.l2 > 10:  # 65 or better, reject
        return False
    if top_3(hand.spades) < 2 and top_5(hand.spades) < 3:  # "Disciplined" weak 2
        return False
    outside_aces = (A in hand.hearts) + (A in hand.diamonds) + (A in hand.clubs)
    void = int(hand.l4 == 0)  # can't have 2 voids, would be 6-7.
    return outside_aces + void <= 1  # we're good unless two outside 1st round controls


def two_passes(deal: Deal) -> bool:
    """Auction goes 2S-p-p assuming standard but conservative, LOTT-based evaluation."""
    if (
        deal.north.hcp >= 13
        and max(len(deal.north.hearts), len(deal.north.diamonds), len(deal.north.clubs))
        >= 5
    ):
        return False
    if deal.north.hcp >= 15 and balanced(deal.north) and top_3(deal.north) >= 1:
        # don't worry about short spades (Qx), as East won't raise (10 card suit???)
        return False
    if len(deal.east.spades) > 3:  # yes, I know RvW, but let's pretend LOTT
        return False
    if len(deal.east.spades) == 2 and deal.east.pt > 3:  # crude Game Try+ mechanic
        return False
    return True


def accept(deal: Deal) -> bool:
    return two_spades_preempt(deal.west) and two_passes(deal)


def do(deal: Deal) -> None:
    """Analyze.  What is the best contract, and will it get found after 3H or double?"""
    pars = deal.par("W", False, True)
    # deal with 2Sx
    two_s_doubled = ScoredContract(
        Contract.from_str("2SX", True), Seat.W, deal.dd_tricks("2SxW")
    )
    # print(f"{str(pars[0])}, {str(two_s_doubled)}")
    c = pars[0] if pars[0].score >= two_s_doubled.score else two_s_doubled
    contract = "_".join([str(c.contract), str(c.declarer)])
    contract_counter[contract] += 1


def final(_: int) -> None:
    pprint.pprint(contract_counter)
