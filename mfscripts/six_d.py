"""Given a pair of sample hands, does it make 6D or 3NT?"""

from redeal import Deal

predeal = {"W": "4 AJT864 A53 QJ9", "E": "AQ762 7 KQJ94 A4"}
TABLE = {"6d": 0, "3nt": 0}


def do(deal: Deal) -> None:
    """Count if slam or 3NT makes."""
    TABLE["6d"] += deal.dd_score("6DE") > 0
    TABLE["3nt"] += deal.dd_score("3NE") > 0


def final(n_tries: int) -> None:
    """Print results."""
    print(TABLE)
    print(f"Tries: {n_tries}")
