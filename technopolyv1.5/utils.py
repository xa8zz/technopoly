"""
utils.py

Contains simple helper functions (clamp, formatting, random generator, etc.)
"""

import random

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def format_money(val: float) -> str:
    if val>=1_000_000_000:
        return f"${val/1_000_000_000:.2f}B"
    elif val>=1_000_000:
        return f"${val/1_000_000:.2f}M"
    elif val>=1_000:
        return f"${val/1_000:.2f}K"
    else:
        return f"${val:.2f}"

def random_company_name(prefixes, suffixes, used_names):
    while True:
        pre = random.choice(prefixes)
        suf = random.choice(suffixes)
        name= f"{pre}{suf}"
        if name not in used_names:
            used_names.add(name)
            return name

_product_fallback_counter = 1


def random_product_name(used_names):
    """
    Generate a pseudo-random product name that is unique within ``used_names``.

    The original implementation only combined items from ``prefix_samples`` and
    ``suffix_samples``. Once every combination had been used the function would
    loop forever, consuming CPU and freezing the UI.  This situation can happen
    after 20-30 turns as the AI keeps launching new products.  To avoid that we
    keep the original behaviour for as long as unused combinations exist but we
    fall back to a deterministic, incrementing name when they are exhausted.
    """

    global _product_fallback_counter

    prefix_samples = [
        "Sky", "Neo", "Prime", "Nova", "Aero", "Delta", "Zeta", "Omega",
        "Quantum", "Hyper", "Green", "Cyber", "Mono", "Alpha", "Aqua",
    ]
    suffix_samples = [
        "Flow", "Boost", "Hub", "Core", "Link", "Edge", "Sphere",
        "Guard", "Gate", "Layer", "Matrix", "Flash", "Pulse", "Logic",
        "Sense",
    ]

    max_unique_combinations = len(prefix_samples) * len(suffix_samples)
    max_attempts = max_unique_combinations * 5  # allow extra attempts for randomness

    for _ in range(max_attempts):
        candidate = random.choice(prefix_samples) + random.choice(suffix_samples)
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate

    # Fall back to an incrementing name once the curated pool is exhausted.
    while True:
        candidate = f"Product{_product_fallback_counter}"
        _product_fallback_counter += 1
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
