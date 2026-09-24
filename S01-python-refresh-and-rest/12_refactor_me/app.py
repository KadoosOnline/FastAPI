"""REFACTOR ME: working code, written the way we must never write it again.

This file runs and prints a correct report. That is exactly the danger:
"it works" is not the same as "it is good". Your job (exercise 12 in
exercises.md) is to rewrite it with everything we refreshed today, WITHOUT
changing the printed output.

What is wrong here, in no particular order:
* no type hints at all -- nobody knows what `c` or `data` contains
* magic dictionaries with string keys ('t', 'p', 'st') instead of a model
* one giant function that loads, validates, calculates and prints
* a global variable that is changed from inside a function
* errors signalled with `return -1` and a printed message
* a bare `except:` that also catches Ctrl-C and real bugs
* a mutable default argument (`log=[]`)
* float money
* copy-pasted code for the two currencies

Keep this original next to your version and compare the outputs.
"""

TOTAL = 0

data = [
    {'t': 'Python', 'p': '2500000', 'cap': 20, 'st': [1, 2, 3]},
    {'t': 'FastAPI', 'p': '4800000', 'cap': 2, 'st': [1, 2]},
    {'t': 'Broken', 'p': 'free', 'cap': 10, 'st': []},
    {'t': 'SQL', 'p': '2900000', 'cap': 0, 'st': []},
]


def process(d, log=[]):
    global TOTAL
    res = []
    for c in d:
        try:
            p = float(c['p'])
        except:
            print('bad price for', c['t'])
            log.append(c['t'])
            continue
        if c['cap'] == 0:
            print('bad capacity for', c['t'])
            log.append(c['t'])
            continue
        r = p * len(c['st'])
        TOTAL = TOTAL + r
        full = 'yes' if len(c['st']) >= c['cap'] else 'no'
        res.append(
            c['t']
            + ' | '
            + str(len(c['st']))
            + '/'
            + str(c['cap'])
            + ' | full: '
            + full
            + ' | '
            + str(int(r))
            + ' IRT'
        )
        res.append(
            c['t']
            + ' | '
            + str(len(c['st']))
            + '/'
            + str(c['cap'])
            + ' | full: '
            + full
            + ' | '
            + str(round(r / 600000, 2))
            + ' USD'
        )
    return res


def check(x):
    if x < 0:
        return -1
    return x


for line in process(data):
    print(line)
print('total:', int(TOTAL))
print('check:', check(TOTAL))
