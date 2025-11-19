"""Generate all "weird" hands for SMP."""

from pathlib import Path

from redeal import Deal

from generate_hands import Pass, combine_and_print_hands, generate_pbn_passes
from smp_1d import two_m_response
from smp_definitions import (
    ns_hcp,
    one_club_opener,
    one_diamond_opener,
    one_diamond_response_sc,
    strong_response_sc,
    two_clubs_opener,
    two_diamonds_opener,
)

# TWEAK HERE
ALLOW_STRONG = True  # allow slammish hands not in the weird categories
REQUIRE_STRONG = False  # only accept slammish hands in the weird categories
MIN_HCP_STRONG = 29
DEBUG = True


def slammish(deal: Deal) -> bool:
    """Is slammish if HCP(NS) >= MIN_HCP_STRONG."""
    return ns_hcp(deal) >= MIN_HCP_STRONG


def slammish_if_required(deal: Deal) -> bool:
    """if REQUIRE_STRONG, only true if slammish.  Always True otherwise."""
    return not REQUIRE_STRONG or slammish(deal)


def accept_1c_1d(deal: Deal) -> bool:
    """1C-1D, or 1C-12+"""
    return (
        one_club_opener(deal.south)
        and (one_diamond_response_sc(deal.north) or strong_response_sc(deal.north))
        and slammish_if_required(deal)
    )


def accept_1d_2m(deal: Deal) -> bool:
    """1D-2m response hands."""
    return (
        one_diamond_opener(deal.south)
        and two_m_response(deal.north)
        and slammish_if_required(deal)
    )


def accept_2m(deal: Deal) -> bool:
    """2C or 2D openers"""
    return (
        two_clubs_opener(deal.south) or two_diamonds_opener(deal.south)
    ) and slammish_if_required(deal)


criteria = [
    Pass(accept_1c_1d, None),
    Pass(accept_1d_2m, None),
    Pass(accept_2m, None),
]
if ALLOW_STRONG:
    criteria.append(Pass(slammish, None))

outputs = generate_pbn_passes(criteria)
F = "SMP_weird.pbn"
with (Path.cwd() / "pbn" / F).open(encoding="utf=8", mode="w") as f:
    combine_and_print_hands(f, outputs, randomize=True, alternate_after=5)
