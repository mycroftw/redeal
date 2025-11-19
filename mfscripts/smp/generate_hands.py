"""functions to print hands"""

import itertools
import random
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, TextIO

from redeal import Deal, SmartStack

VULNERABILITY = ("None", "NS", "EW", "Both")


@dataclass
class Pass:
    """One of potentially multiple "Passes" of generated hands to amalgamate.

    If we want to practise hands, but not "know" what hand partner has, we can
    generate "10 of these, 15 of these, 5 of these" and then combine them into
    one pbn file.

    Consists of an accept function, an optional `SmartStack` used to predeal, and
    the number of hands that meet the criteria to return.

    Needs a better name, given the ambiguity with a bridge Pass call!
    """

    accept_function: Callable[[Deal], bool]
    predeal: Optional[dict[str, SmartStack]]
    num_hands: int = 10


def generate_and_print_pass(
    output: TextIO,
    criteria: Pass,
    alternate_after: int = 5,
) -> None:
    """Generate and deal hands with a single constraint.  Convenience function.

    Reverses the PBN (set dealer N and rotate the hand 180 degrees)
    every `alternate_after` hands.  To not do this, set alternate_after >= num_hands.

    """
    deals = generate_pbn_hands(criteria)
    print_pbn_hands(output, deals, alternate_after)


def generate_and_print_hands(
    output: TextIO,
    accept_function: Callable,
    predeal: Optional[dir] = None,
    num_hands: int = 20,
    alternate_after: int = 5,
) -> None:
    """Generate and deal hands with constraint.

    Old-style input, not using `Pass` dataclass for criteria.
    """
    generate_and_print_pass(
        output,
        Pass(accept_function, predeal, num_hands),
        alternate_after,
    )


def generate_pbn_hands(criteria: Pass) -> list[str]:
    """Generate and deal hands with constraints, return each as just the deal line in PBN.

    This is useful for later manipulation as "dealer" is always South, and nothing else is needed.
    """

    Deal.set_str_style("pbn")
    dealer = Deal.prepare(criteria.predeal)
    output = []

    for _ in range(criteria.num_hands):
        deal = str(dealer(criteria.accept_function))
        output.append(deal)

    return output


def generate_pbn_passes(
    criteria: Iterable[Pass],
) -> list[list[str]]:
    """Generate and deal hands with multiple constraints, output as PBN deals.

    Convenience function for calling `generate_pbn_hands` repeatedly with different
    accept criteria and predeal (a "pass") and returning all results in a format i
    suitable for combining either linearly or randomly with `combine_and_print_hands`.
    """

    output = []
    for criterion in criteria:
        output.append(generate_pbn_hands(criterion))
    return output


def print_pbn_hands(
    output: TextIO,
    deals: list[str],
    alternate_after: int = 5,
) -> None:
    """Print the hands in full pbn format."""

    for i, deal in enumerate(deals):
        dlr = "S"
        if i // alternate_after % 2:
            deal = deal.replace("N", "S", 1)
            dlr = "N"
        output.writelines(
            [
                f'\n[Board "{i + 1}"]',
                f'\n[Dealer "{dlr}"]',
                f'\n[Vulnerable "{random.choice(VULNERABILITY)}"]\n',
                deal,
                "\n",
            ]
        )


def combine_and_print_hands(
    output: TextIO,
    deal_sets: list[list[str]],
    randomize: bool = True,
    alternate_after: int = 5,
) -> None:
    """Combine multiple sets of deals created with generate_pbn_hands and print them.

    This interleaves the hands from each set.
    If randomize is True, then randomize after interleave.
    """

    combined_deals = [
        x
        for x in itertools.chain.from_iterable(itertools.zip_longest(*deal_sets))
        if x is not None
    ]
    if randomize:
        random.shuffle(combined_deals)
    print_pbn_hands(output, combined_deals, alternate_after)
