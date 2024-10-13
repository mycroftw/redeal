"""1NT after a double-negative results."""

from collections import defaultdict
from enum import Enum, auto

from redeal import C, Deal, Shape, SmartStack, Suit, balanced, hcp

DEBUG = False
MIN_NT = 17
MAX_NT = 19
PULL_4432 = True  # will responder GStayman with (443)2?
PAR = False  # compare against par?

# criteria.
predeal = {"S": SmartStack(balanced, hcp, range(MIN_NT, MAX_NT + 1))}
transfer = (  # if shape matches, will transfer.  Uses redeal.Suit order.
    Shape.from_cond(lambda s, h, d, c: s >= 5 and s >= h),
    Shape.from_cond(lambda s, h, d, c: h >= 5 and s < h),
    Shape.from_cond(lambda s, h, d, c: d >= 6 and s < 5 and h < 5 and d >= c),
    Shape.from_cond(lambda s, h, d, c: c >= 6 and s < 5 and h < 5 and d < c),
)
stayman = Shape("xxx1") + Shape("4450")
if PULL_4432:
    stayman += Shape("(443)2")
pull = sum(transfer, stayman)  # here is the complete shape for "N will pull 1NT"

# dict to store results
results_counter = defaultdict(int)


def accept(deal: Deal) -> bool:
    """Redeal accept function: the auction must be 1C (16+)-1S (0-5); 1NT (17-19).

    Note that opener is guaranteed to meet the restrictions via SmartStack,
    so is not checked here.
    """
    return hcp(deal.north) <= 5


def do(deal: Deal) -> None:
    """Score up contract from South into tabulators."""
    contract = _find_contract(deal)
    if DEBUG:
        s = deal.south
        okay = (
            balanced(s) and hcp(s) in range(MIN_NT, MAX_NT + 1) and hcp(deal.north) <= 5
        )
        print(f"{s}\t{hcp(s)}\t{contract}\t{okay}")
    if PAR:
        _do_par(deal, contract)
    else:
        _do_nopar(deal, contract)


def _find_contract(deal: Deal) -> str:
    """Simple use of Stayman and transfers by North."""
    north = deal.north
    south = deal.south
    for suit, transfer_cond in zip(Suit, transfer):
        if transfer_cond(north):
            return f"2{suit.name}S"
    if stayman(north):
        if len(south.hearts) >= 4 and len(south.hearts) >= len(south.spades):
            return "2HS"
        if len(south.spades) >= 4:
            return "2SS"
        return "2DS"
    return "1NTS"


def _do_nopar(deal: Deal, contract: str) -> None:
    """No compare against par: count contract/DD tricks for each hand."""
    tricks = deal.dd_tricks(contract)
    results_counter[(contract, tricks)] += 1


def _do_par(deal: Deal, contract: str) -> None:
    """Compare against par (all four vuls), count score."""
    for i in range(4):
        vuls = (i & 1, i & 2)  # convert int to (bool, bool)
        pars = deal.par("S", *vuls)
        par_score = pars[0].score  # all "par" scores are the same, grab the first
        one_nt_score = deal.dd_score(contract, vuls[0])
        results_counter[i] += one_nt_score - par_score


class Counter(Enum):
    """Different counters used in data reporting"""

    HAND = auto()
    TRICK = auto()
    SCORE_NV = auto()
    SCORE_V = auto()


def final(_: int) -> None:
    """End of simulation: Print results."""
    if PAR:
        _final_par()
    else:
        _final_nopar()


def _final_nopar() -> None:
    """Eval against zero: display each contract/tricks level and score average."""
    # create Contract objects for each declared contract
    nv_contract = {}
    v_contract = {}
    unique_contracts = {contract for contract, _ in results_counter}
    for contract in unique_contracts:
        nv_contract[contract] = C(contract, vul=False)
        v_contract[contract] = C(contract, vul=True)
    counts = {k: 0 for k in Counter}

    print(
        f"\n{MIN_NT}-{MAX_NT} NT, Responder 0-5,"
        f" will{'' if PULL_4432 else ' not'} pull NT with (443)2"
    )
    print("Ctract  Tricks\tCount\tSc. NV\tSc. V\t")
    for (contract, tricks), count in sorted(results_counter.items()):
        nv_score = nv_contract[contract].score(tricks)
        v_score = v_contract[contract].score(tricks)
        print(f"{contract:4}\t{tricks}\t{count}\t{nv_score:+}\t{v_score:+}")
        counts[Counter.HAND] += count
        counts[Counter.TRICK] += count * tricks
        counts[Counter.SCORE_NV] += count * nv_score
        counts[Counter.SCORE_V] += count * v_score
    wt_sum = {k: (v / counts[Counter.HAND]) for k, v in counts.items()}
    print("WtAvg: (if first entry is not 1.0, something is very wrong)")
    print("\t".join(map(str, wt_sum.values())))


def _final_par() -> None:
    """Print out results vs par at each vul pair."""
    print(f"\n{MIN_NT}-{MAX_NT} NT, Responder 0-5, will pull NT")
    print("Vul\tresult vs par")
    print(f"None\t{results_counter[0]}")
    print(f"N-S\t{results_counter[1]}")
    print(f"E-W\t{results_counter[2]}")
    print(f"Both\t{results_counter[3]}")
