def lay_from_odds(odds: str) -> float:
    d = int(odds[1:]) / 100
    d = np.sqrt(d)
    if odds[0] == "+":
        return 1.0 / d
    return d

def prob_from_odds(odds: str) -> float:
    """Assumes even-money"""
    d = int(odds[1:]) / 100
    if odds[0] == "+":
        return 1 / (1 + d)
    return d / (1 + d)

def win_multiplier(odds: str) -> float:
    d = int(odds[1:]) / 100
    if odds[0] == "+":
        return d
    return 1 / d
