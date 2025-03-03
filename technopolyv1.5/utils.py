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

def random_product_name(used_names):
    # for convenience, returns random nonsense name
    # can be replaced with your logic
    prefix_samples = ["Sky","Neo","Prime","Nova","Aero","Delta","Zeta","Omega","Quantum","Hyper",
                      "Green","Cyber","Mono","Alpha","Aqua"]
    suffix_samples = ["Flow","Boost","Hub","Core","Link","Edge","Sphere","Guard","Gate","Layer",
                      "Matrix","Flash","Pulse","Logic","Sense"]
    while True:
        pr = random.choice(prefix_samples)
        sf = random.choice(suffix_samples)
        n = pr+sf
        if n not in used_names:
            used_names.add(n)
            return n
