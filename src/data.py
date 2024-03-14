import utils

DATA = [
    ([9], 2), # ice-cream
    ([9, 24], 2), # ice-cream?
    ([20, 18, 9], 5), # what is ice-cream
    ([20, 18, 9, 24], 5), # what is ice-cream?
    ([20, 18, 9, 9, 1], 55),  # when was world war 2
    ([20, 18, 9, 9, 1, 24], 55),  # when was world war 2?
    ([9, 9, 9], 14), # Apache Attack Helicopter
    ([9, 9, 9, 24], 14), # Apache Attack Helicopter?
    ([20, 18, 9, 9, 9], 55), # What is Apache Attack Helicopter
    ([20, 18, 9, 9, 9, 24], 55), # What is Apache Attack Helicopter?
    ([9, 9], 6), # Tathya Garg
    ([9, 9, 24], 6), # Tathya Garg?
    ([20, 18, 9, 9], 35), # Who is Tathya Garg
    ([20, 18, 9, 9, 24], 35), # Who is Tathya Garg?
    ([20, 9], 3), # What ice-cream
    ([20, 9, 24], 3), # What ice-cream?
    ([20, 9, 18], 3), # What ice-cream is
    ([20, 9, 18, 24], 3), # What ice-cream is?
    ([6, 9], 6),  # Swiss ice-cream
    ([6, 9, 24], 6),  # Swiss ice-cream?
    ([20, 18, 6, 9], 35),  # What is Swiss ice-cream
    ([20, 18, 6, 9, 24], 35),  # What is Swiss ice-cream?
    ([20, 6, 9], 15), # What Swiss ice-cream
    ([20, 6, 9, 24], 15), # What Swiss ice-cream?
    ([20, 6, 9, 18], 15), # What Swiss ice-cream is
    ([20, 6, 9, 18, 24], 15), # What Swiss ice-cream is?
]

DATA = list(map(
    lambda items: (utils.pad(items[0]),items[1]), 
    DATA
))

