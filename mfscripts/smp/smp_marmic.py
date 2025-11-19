"""SMP: Strong hands and 4441s"""

from pathlib import Path

from redeal import Deal, SmartStack, hcp

from generate_hands import Pass, combine_and_print_hands, generate_pbn_passes
from smp_definitions import (
    marmic,
    ns_hcp,
    one_club_opener,
    one_diamond_response_sc,
    strong_response_sc,
    two_diamond_shape,
    two_diamonds_opener,
)

# TWEAK HERE
DEBUG = False
MIN_HCP_STRONG = 23


def two_diamond_accept(deal: Deal) -> bool:
    """Accept if slammish and 2D opener"""
    if two_diamonds_opener(deal.south) and ns_hcp(deal) > MIN_HCP_STRONG:
        if DEBUG:
            print(deal)
        return True
    return False


def one_club_marmic(deal: Deal) -> bool:
    """Accept if 1C -> GF and marmic"""
    if (
        one_club_opener(deal.south)
        and marmic(deal.south)
        and not one_diamond_response_sc(deal.north)
    ):
        if DEBUG:
            print(deal)
        return True
    return False


def one_club_strong_resp(deal: Deal) -> bool:
    """Accept if 1C and resp >= 12"""
    if one_club_opener(deal.south) and strong_response_sc(deal.north):
        if DEBUG:
            print(deal)
        return True
    return False


def one_club_strong_marmic(deal: Deal) -> bool:
    """Accept if 1C and responder is 4441 >= 12"""
    if one_club_strong_resp(deal) and marmic(deal.north):
        if DEBUG:
            print(deal)
        return True
    return False


passes = (
    Pass(two_diamond_accept, {"S": SmartStack(two_diamond_shape, hcp, range(11, 16))}),
    Pass(one_club_marmic, {"S": SmartStack(marmic, hcp, range(16, 34))}),
    Pass(one_club_strong_resp, None),
    Pass(one_club_strong_marmic, {"N": SmartStack(marmic, hcp, range(12, 25))}),
)

outputs = generate_pbn_passes(passes)

F = "marmic.pbn"
with (Path.cwd() / "pbn" / F).open(encoding="utf-8", mode="w") as f:
    combine_and_print_hands(f, outputs, randomize=True, alternate_after=5)
