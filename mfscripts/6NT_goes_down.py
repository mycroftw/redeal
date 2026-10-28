"""From BBO: how often (and how) 6NT goes down on 18-opposite-7solid."""

import collections
import itertools
import pprint
from enum import StrEnum, IntEnum

from redeal import Deal, Evaluator, Shape, SmartStack, hcp


class Debug(IntEnum):
    NONE = 0
    DOWN = 1
    ALL = 2


DEBUG = Debug.NONE


class Types(StrEnum):
    MAKING = "6NT making"
    OFF_AA = "off two Aces"
    OFF_AK = "off suited AK"
    OTHER = "other reason"


# Auction went 1C-1H; 2NT
two_nt_rebid = Shape.from_cond(
    lambda s, h, d, c: min(c, d, h, s) > 1  # no singletons or voids
    and max(c, d) <= 6
    and h < 4  # no raise
    and s < 5
    and (c > d or c == d == 3)
)
predeal = {"N": "65 AKQJT42 Q95 8", "S": SmartStack(two_nt_rebid, hcp, (18, 19))}
aces = Evaluator(1)
hands = collections.defaultdict(list)


def do(deal: Deal) -> None:

    south = deal.south
    s, h, d, c = (
        len(south.spades),
        len(south.hearts),
        len(south.diamonds),
        len(south.clubs),
    )
    assert (
        s in {2, 3, 4}
        and h in {2, 3}
        and d in range(2, 6)
        and c in range(2, 7)
        and (d < c or d == c == 3)
        and south.hcp in {18, 19}
    ), (
        f"OOPS: South not 2NT rebid: {south}, shape={south.shape}, "
        f"eval={s, h, d, c},  hcp={hcp(south)}"
    )

    result = deal.dd_score("6NS", vul=True)
    if result < 0:  # contract does not make
        if any(
            suit.controls == 0 for suit in {south.spades, south.diamonds, south.clubs}
        ):
            type_ = Types.OFF_AK
        elif aces(south) < 2:
            type_ = Types.OFF_AA
        else:
            type_ = Types.OTHER
    else:  # making
        type_ = Types.MAKING
    hands[type_].append(str(south))


def final(n_hands: int) -> None:

    if len(list(itertools.chain(*hands.values()))) != n_hands:
        print(
            f"WARNING: not all hands counted! "
            f"{n_hands} != {len(list(itertools.chain(*hands.values())))}"
        )
    if DEBUG > Debug.NONE:
        making = hands.pop(Types.MAKING)
        for k, v in sorted(hands.items()):
            print(k)
            pprint.pprint(v)
        if DEBUG == Debug.ALL:
            print(Types.MAKING)
            pprint.pprint(making)
    print(", ".join(f"{k}: {len(v)}" for k, v in sorted(hands.items())))
