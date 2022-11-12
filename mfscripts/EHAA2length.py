from collections import Counter
import pprint

from redeal import Evaluator, hcp, Shape, Simulation, Deal, Hand
from redeal.global_defs import Suit


DEBUG = {
    'hand': False,
    'hcp': True,
    'is_clubs': False,
    'suits': False,
}

IS_CLUBS = True
RANGE_MIN = 6
RANGE_MAX = 12

twobidshape = Shape.from_cond(
    lambda s, h, d, c: s >= 5 or h >= 5 or d >= 5 or (c >= 5 and IS_CLUBS)
)
full_suit_eval = Evaluator(*range(14, 1, -1))


def ehaa_nt(hand: Hand) -> bool:
    is_nt_shape = (Shape('(4333)') + Shape('(4432)')
                   + Shape('(33)(25)') + Shape('(32)(35)'))
    return is_nt_shape(hand) and hcp(hand) in (10, 11, 12)


class EHAA2length(Simulation):

    def __init__(self):
        super().__init__()
        self.bidsuit = []
        self.maxlength = Counter()
        self.points = Counter()

    def accept(self, deal: Deal) -> bool:
        return (
                deal.south.shape in twobidshape
                and hcp(deal.south) in range(RANGE_MIN, RANGE_MAX + 1)
                and not ehaa_nt(deal.south)
        )

    def do(self, deal: Deal) -> None:
        if DEBUG['hand']:
            print(deal.south)

        if DEBUG['is_clubs'] and len(deal.south.clubs) >= 5:
            other_suit = (len(deal.south.diamonds) >= len(deal.south.clubs)
                          or len(deal.south.hearts) >= len(deal.south.clubs)
                          or len(deal.south.spades) >= len(deal.south.clubs))
            print(f'{deal.south}   {other_suit}')

        ml = max(deal.south.shape)
        self.maxlength[ml] += 1
        self.points[deal.south.hcp] += 1
        for suit in Suit:
            if len(deal.south[suit]) == ml:
                self.bidsuit.append(deal.south[suit])
                break  # only store 1 longest suit (highest by fiat) per hand

    def final(self, n_tries: int) -> None:

        print('Lengths:')
        pprint.pprint(dict(self.maxlength), width=1)

        if DEBUG['hcp']:
            print('\nHCP:')
            pprint.pprint(dict(self.points), width=1)

        # sort on secondary key first (strength of suit), then primary (length)
        sorted_bidsuit = sorted(self.bidsuit, key=full_suit_eval, reverse=True)
        sorted_bidsuit = sorted(sorted_bidsuit,
                                key=lambda x: len(x),
                                reverse=True)
        if DEBUG['suits']:
            pprint.pprint([(str(x), len(x), full_suit_eval(x))
                           for x in sorted_bidsuit],
                          width=100,
                          compact=True)

        print(f'\nMedian hand: {sorted_bidsuit[len(self.bidsuit) // 2]}')


simulation = EHAA2length()
