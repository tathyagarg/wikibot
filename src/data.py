# This needs to be removed, changed with a file in /data
# Update config.toml to hold the path to that
# Add a function

import random

DATA = []
for _ in range(1000):
    n = sorted([random.randint(1, 10) for _ in range(10)])
    x = ((sum(n)**2)*10//2500)

    DATA.append((n, x))

