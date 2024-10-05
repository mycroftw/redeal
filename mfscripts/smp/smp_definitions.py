"""utility functions for SMP bidding practise."""

import random
from typing import Callable, Optional, TextIO

from redeal import Deal, Hand, Shape, balanced, hcp

# tester functions.  All take a hand and return True-if-match.
balanced_no_5cM = balanced - Shape("5xxx") - Shape("x5xx")
two_clubs_shape = Shape.from_cond(lambda s, h, d, c: c >= 6 and c > max([s, h, d]))
two_diamond_shape = Shape("3415") + Shape("4315") + Shape("4405") + Shape("4414")


def _non_1c_strength(hand: Hand, nv: bool = False) -> bool:
    """True if an "11-15" opener.  NV, can be 10"""
    min_opener = 10 if nv else 11
    return hcp(hand) in range(min_opener, 16)


def one_club_opener(hand: Hand) -> bool:
    """True if 16+ unBAL or 16-19 or 22+ BAL"""
    return hcp(hand) > 16 and not one_nt_opener(hand) and not two_nt_opener(hand)


def one_diamond_opener(hand: Hand) -> bool:
    """True if 1D opener.  Special catchall: "not anything else"."""
    return _non_1c_strength(hand) and not (
        one_nt_opener(hand)
        or one_heart_opener(hand)
        or one_spade_opener(hand)
        or two_clubs_opener(hand)
        or two_diamonds_opener(hand)
    )


def one_heart_opener(hand: Hand) -> bool:
    """True if 1H opener.  Will bid 1S with equal length, 1D or 2C if longer."""
    hearts = len(hand.hearts)
    return (
        _non_1c_strength(hand)
        and hearts >= 5
        and hearts > len(hand.spades)
        and hearts >= max(minor_lengths(hand))
    )


def one_spade_opener(hand: Hand) -> bool:
    """True if 1S opener.  spades at least tied for longest."""
    spades = len(hand.spades)
    return _non_1c_strength(hand) and spades >= 5 and spades == hand.l1


def one_nt_opener(hand: Hand) -> bool:
    """True if balanced 14-16.  We do not open 5cM 1NT."""
    return hcp(hand) in range(14, 17) and balanced_no_5cM(hand)


def two_clubs_opener(hand: Hand) -> bool:
    """True if 2C opener.  6 clubs, not 6-6."""
    clubs = len(hand.clubs)
    return _non_1c_strength(hand) and clubs >= 6 and clubs > max(hand.shape[:2])


def two_diamonds_opener(hand: Hand) -> bool:
    """True if 2D opener.  4415 minus a card."""
    return _non_1c_strength(hand) and two_diamond_shape(hand)


def two_nt_opener(hand: Hand) -> bool:
    """True if 2NT opener.  20-21 balanced (could be 5cM)"""
    return hcp(hand) in range(20, 22) and balanced(hand)


# One club responses
def one_diamond_response_sc(hand: Hand) -> bool:
    """True if 0-7 HCP (1D response to 1C).  For ease of reading."""
    return hcp(hand) <= 7


def one_heart_response_sc(hand: Hand) -> bool:
    """True if 8-11 HCP (1H response to 1C). For ease of readng."""
    return hcp(hand) in range(8, 12)


def strong_response_sc(hand: Hand) -> bool:
    """True if 12+ HCP (1S+ response to 1C).  For ease of reading."""
    return hcp(hand) >= 12


# convenience functions.
def minor_lengths(hand: Hand) -> tuple[int, int]:
    """minor suit lengths, in (diamonds, clubs) order."""
    return hand.shape[2:]


def major_lengths(hand: Hand) -> tuple[int, int]:
    """major suit lengths, in (spades, hearts) order."""
    return hand.shape[:2]


def _n_card_major(hand: Hand, n: int, plus: bool = True) -> bool:
    """True if hand has an n(+)card major"""
    if plus:
        return max(major_lengths(hand)) >= n
    return max(major_lengths(hand)) == n


def four_card_major(hand: Hand, plus: bool = True) -> bool:
    """True if hand has a 4(+)card major"""
    return _n_card_major(hand, 4, plus)


def five_card_major(hand: Hand, plus: bool = True) -> bool:
    """True if hand has a 5(+)card major"""
    return _n_card_major(hand, 5, plus)


# functions to print hands
def generate_and_print_hands(
    output: TextIO,
    accept_function: Callable,
    predeal: Optional[dir] = None,
    num_hands: int = 100,
    alternate_after: int = 10,
) -> None:
    """Generate and deal hands with constraints.

    reverse the PBN (set dealer N and rotate the hand 180 degrees)
    every alternate_after hands.  To not do this, set alternate_after >= num_hands.
    """
    Deal.set_str_style("pbn")
    dealer = Deal.prepare(predeal)
    vulnerabilities = ["None", "NS", "EW", "Both"]

    for i in range(1, num_hands):
        deal = str(dealer(accept_function))
        dlr = "S"
        if i // alternate_after % 2:
            deal = deal.replace("N", "S", 1)
            dlr = "N"

        output.writelines(
            [
                f'\n[Board "{i}"]',
                f'\n[Dealer "{dlr}"]',
                f'\n[Vulnerable "{random.choice(vulnerabilities)}"]\n',
                deal,
                "\n",
            ]
        )