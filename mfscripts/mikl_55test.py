"""Testing GF with AKxxx xxxxx xx x after 1H opener."""

from collections import Counter

from redeal import Deal, Evaluator, Shape, SmartStack, balanced

DEBUG = False  # make false when works
USE_MIN = False  # if True, limit to minimum hand
MAX_RANGE = 14 if USE_MIN else 21

one_heart_shape = Shape.from_cond(
    lambda s, h, d, c: s <= 4 and h >= 5 and d <= h and c <= h
)
predeal = {
    "S": "AK872 T7432 85 9",
    "N": SmartStack(one_heart_shape, Evaluator(4, 3, 2, 1), range(12, MAX_RANGE + 1)),
}
_score = 0  # running total of results in 4HN
_count = Counter()  # times each DD tricks
_result = Counter()  # times "down, game, slam"
_hands = 0


def accept(deal: Deal) -> bool:
    """Accept hands that open 1H.  Smartstack handles everything but NTs."""
    north = deal.north
    nt_opener = balanced(north) and north.hcp in (15, 16, 17, 20, 21)
    return not nt_opener


def do(deal: Deal) -> None:
    """Count tricks in a heart contract."""
    global _hands, _score

    _hands += 1
    tricks = deal.dd_tricks("4HN")
    _count[tricks] += 1
    down_game_slam = 0 + (tricks >= 12) - (tricks < 10)
    _result[down_game_slam] += 1
    score = deal.dd_score("4HN", True)
    _score += score
    if DEBUG:
        print(deal, tricks, score)


def final(n_hands: int) -> None:
    """print the results"""
    print(
        f"{n_hands} generated, {_hands} accepted:\n"
        f"Range of opener: 12-{MAX_RANGE} inclusive\n"
        f"Tricks: {sorted(_count.items())},\n"
        f"Average score in 4HN: {_score/_hands},\n"
        f"down:game:slam: {sorted(_result.items())}"
    )
