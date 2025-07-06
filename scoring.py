# maps item_id → points
POINTS = {
    6729: 100,     # dragon full helm
    11832: 250,    # bandos chestplate
    # … add more …
}

def score(item_id: int, qty: int) -> int:
    base = POINTS.get(item_id, 0)
    return base * qty
