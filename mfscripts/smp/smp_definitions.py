"""utility functions for SMP bidding practise."""

from redeal import Deal, Hand, Shape, balanced

# useful shapes
balanced_no_5cM = balanced - Shape("5xxx") - Shape("x5xx")
marmic = Shape("(4441)")
two_clubs_shape = Shape.from_cond(lambda s, h, d, c: c >= 6 and c > max([s, h, d]))
two_diamond_shape = Shape("3415") + Shape("4315") + Shape("4405") + Shape("4414")


# tester functions.  All take a hand and return True-if-match.
def _opener_not_1c(hand: Hand, nv: bool = False) -> bool:
    """True if an "11-15" opener.  NV, can be 10"""
    min_opener = 10 if nv else 11
    return hand.hcp in range(min_opener, 16)


def one_club_opener(hand: Hand) -> bool:
    """True if 16+ unBAL or 16-19 or 22+ BAL"""
    return hand.hcp > 16 and not one_nt_opener(hand) and not two_nt_opener(hand)


def one_diamond_opener(hand: Hand) -> bool:
    """True if 1D opener.  Special catchall: "not anything else"."""
    return _opener_not_1c(hand) and not (
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
        _opener_not_1c(hand)
        and hearts >= 5
        and hearts > len(hand.spades)
        and hearts >= max(minor_lengths(hand))
    )


def one_spade_opener(hand: Hand) -> bool:
    """True if 1S opener.  spades at least tied for longest."""
    spades = len(hand.spades)
    return _opener_not_1c(hand) and spades >= 5 and spades == hand.l1


def one_nt_opener(hand: Hand) -> bool:
    """True if balanced 14-16.  We 100% open 5cM 1NT."""
    return hand.hcp in range(14, 17) and balanced(hand)


def two_clubs_opener(hand: Hand) -> bool:
    """True if 2C opener.  6 clubs, not 6-6."""
    return _opener_not_1c(hand) and two_clubs_shape(hand)


def two_diamonds_opener(hand: Hand) -> bool:
    """True if 2D opener.  4415 minus a card."""
    return _opener_not_1c(hand) and two_diamond_shape(hand)


def two_nt_opener(hand: Hand) -> bool:
    """True if 2NT opener.  20-21 balanced (could be 5cM)"""
    return hand.hcp in range(20, 22) and balanced(hand)


# One club responses
def one_diamond_response_sc(hand: Hand) -> bool:
    """True if 0-7 HCP (1D response to 1C).  For ease of reading."""
    return hand.hcp <= 7


def one_heart_response_sc(hand: Hand) -> bool:
    """True if 8-11 HCP (1H response to 1C). For ease of reading."""
    return hand.hcp in range(8, 12)


def strong_response_sc(hand: Hand) -> bool:
    """True if 12+ HCP (1S+ response to 1C).  For ease of reading."""
    return hand.hcp >= 12


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


def ns_hcp(deal: Deal) -> int:
    """Return NS HCP total"""
    return deal.north.hcp + deal.south.hcp
