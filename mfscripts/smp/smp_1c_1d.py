"""SMP 1C-1D hand generators."""

import sys
from pathlib import Path

from redeal import Deal, Hand, balanced, hcp

from generate_hands import generate_and_print_hands
from smp_definitions import four_card_major, one_club_opener

# TWEAK HERE
REBID_1M = True  # if the hands should be 1C-1D; 1M, or 1C-1D; any
DEBUG = True


def strong_one_diamond_response(hand: Hand) -> bool:
    """5-7 HCP."""

    return 5 <= hcp(hand) <= 7


def one_major_rebid(hand: Hand) -> bool:
    """True if opener would rebid 1M after 1C-1D.

    Per the book: always with 4+M, unless GF or suit-set.

    Going to ignore suit-set, and consider GF as "22+"
    """
    gf = hcp(hand) >= 22

    return not gf and not balanced(hand) and four_card_major(hand)


def accept(deal: Deal) -> bool:
    """Accept if 1C-1D (; 1M)."""
    # if not one_club_opener(deal.south) or not one_diamond_response_sc(deal.north):
    if not one_club_opener(deal.south) or not strong_one_diamond_response(deal.north):
        return False
    if not REBID_1M:
        return True

    if one_major_rebid(deal.south):
        if DEBUG:
            sys.stderr.write(f"Bingo! {deal.south}\n")
        return True
    if DEBUG:
        sys.stderr.write(f"Aw, no 1M rebid. {deal.south}\n")
    return False


F = f"1C-1D{"-1M" if REBID_1M else ""}.pbn"
with Path(Path.cwd() / F).open(encoding="utf=8", mode="w") as f:
    generate_and_print_hands(f, accept)
