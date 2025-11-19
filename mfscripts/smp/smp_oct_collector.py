"""SMP: October weird tests"""

from pathlib import Path

from redeal import Deal, Hand, SmartStack, hcp

from generate_hands import Pass, combine_and_print_hands, generate_pbn_passes
from smp_1d import two_m_response
from smp_definitions import (
    ns_hcp,
    one_diamond_opener,
    one_heart_opener,
    one_spade_opener,
    two_clubs_opener,
    two_diamond_shape,
    two_diamonds_opener,
)

DEBUG = False
MIN_HCP_STRONG = 23


def two_club_accept(deal: Deal) -> bool:
    return two_clubs_opener(deal.south) and ns_hcp(deal) > 20


def two_diamond_accept(deal: Deal) -> bool:
    return two_diamonds_opener(deal.south) and ns_hcp(deal) > 20


def one_major_opener_values(deal: Deal) -> bool:
    return (
        one_spade_opener(deal.south) or one_heart_opener(deal.south)
    ) and 18 <= ns_hcp(deal) <= 28


def reverse_flannery(hand: Hand, min_hcp: int = 0, max_hcp: int = 40) -> bool:
    """Reverse Flannery: 54xx. We play 1D-2M as RF < GF."""
    return hand.spades == 5 and hand.hearts == 4 and min_hcp <= hand.hcp <= max_hcp


def one_diamond_weird(deal: Deal) -> bool:
    return one_diamond_opener(deal.south) and (
        two_m_response(deal.north) or reverse_flannery(deal.north, min_hcp=5)
    )


passes = (
    Pass(
        two_diamond_accept, {"S": SmartStack(two_diamond_shape, hcp, range(11, 16))}, 6
    ),
    Pass(one_major_opener_values, None, 12),
    Pass(one_diamond_weird, None, 6),
)


outputs = generate_pbn_passes(passes)
F = "collector.pbn"
with (Path.cwd() / "pbn" / F).open(encoding="utf-8", mode="w") as f:
    combine_and_print_hands(f, outputs, randomize=True, alternate_after=5)
