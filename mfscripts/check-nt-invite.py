"""Simulate results in NT and 2D on 3 JT3 K9876 KQ72 opposite 14-16"""

import collections
import pprint
from typing import Any

from redeal import Deal, Shape, SmartStack, hcp

# Shape for a 1NT opener with no 4cM (2D response to Stayman).
bal_no_4cM = Shape.from_cond(
    lambda s, h, d, c: min(c, d, h, s) > 1  # no singletons or voids
    and s < 4
    and h < 4  # no 4cM
) - Shape(
    "22(27)"
)  # remove specific shape we won't open 1NT on
predeal = {"S": "3 JT3 K9876 KQ72", "N": SmartStack(bal_no_4cM, hcp, [14, 15, 16])}
two_diamond_result = collections.Counter()
go_on_15_result = collections.Counter()
pass_vs_15 = collections.Counter()
go_on_16_result = collections.Counter()
pass_vs_16 = collections.Counter()


def cmp(a: Any, b: Any) -> int:
    """Return 1 if a > b, 0 if a = b, -1 if b > a"""
    return int(a > b) - int(a < b)


def do(deal: Deal) -> None:
    # ensure that I got the shape right
    north = deal.north
    assert (
        len(north.spades) in {2, 3}
        and len(north.hearts) in {2, 3}
        and len(north.diamonds) in range(2, 7)
        and len(north.clubs) in range(2, 7)
        and hcp(north) in {14, 15, 16}
    ), f"OOPS: North not 1NT: {north}, shape={north.shape}, HCP={hcp(north)}"

    scores = {
        contract: deal.dd_score(contract, vul=True)
        for contract in ["2DN", "2NN", "3NN"]
    }
    two_diamond_result[scores["2DN"]] += 1
    nt_score = {
        accept: scores["2NN" if hcp(north) < accept else "3NN"] for accept in {15, 16}
    }
    go_on_15_result[nt_score[15]] += 1
    pass_vs_15[cmp(scores["2DN"], nt_score[15])] += 1
    go_on_16_result[nt_score[16]] += 1
    pass_vs_16[cmp(scores["2DN"], nt_score[16])] += 1


def final(n_deals: int) -> None:
    pprint.pprint(sorted(two_diamond_result.items()))
    pprint.pprint(sorted(go_on_15_result.items()))
    pprint.pprint(sorted(go_on_16_result.items()))
    print(
        f"2D: {sum(two_diamond_result.elements())/n_deals} "
        f"NT (accept 15): {sum(go_on_15_result.elements())/n_deals} "
        f"NT (accept 16): {sum(go_on_16_result.elements())/n_deals}"
    )
    print(
        f"passing better than 2NT: {pass_vs_15} if accept any 15, "
        f"{pass_vs_16} if accept any 16"
    )
