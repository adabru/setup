#!/usr/bin/env python

import os
import sys
import re

if len(sys.argv) < 2:
    print("""
  usage:
    \033[1mrename.py\033[22m expression replacement [file ...] [f]

  expressions:
    'MemAvailable: *([0-9]+).*SwapFree: *([0-9]+)'
  """)
    sys.exit(0)

regex = re.compile(sys.argv[1], re.S)
repl = sys.argv[2]


def preview():
    for entry in os.scandir('.'):
        if not entry.name.startswith('.') and entry.is_file():
            print(entry.name)
            new_name = regex.sub(repl, entry.name)
            print(new_name)


# preview(files, "")


# def oninput(regex):
#     if input is <enter >:
#         apply()
#         exit()
#     elif input is <esc >:
#         exit()
#     else:
#         preview(files, regex)


# for f in files:
#     print(f + " → " + regex.exec(f))
# print("press <enter> to apply or <esc> to cancel")


# def apply(files, regex):
#     for f in files:
#         os.rename(f, regex.exec(f))


# rename = s = > {
#     [, r, n] = s.split(s[0])
#     r = new RegExp(r)
#     _old = fs.readdirSync('.').filter(f= > r.test(f))
#     _new = _old.map(f= > {
#         m=r.exec(f)
#     return n.replace( /\$([0-9])/g, ([, i]) = > m[i])
#     })
#     for(i in _old) console.log(`${_old[i]}  →  ${_new[i]}`)
#     console.log('Ok? (enter _() if yes)')
#     return () = > _old.forEach((_, i)= > fs.renameSync(_old[i], _new[i]))
# }

def edit_sequence(u, v):
    # dynamic programming with backtracking, start with mapping(u₀=ε, …, uₙ=v) → v₀ = ε
    cost = [i for i in range(len(u) + 1)]
    backtracking = [['_'] + ['D'] * len(u)] + [[]] * len(u)

    # build 'table' up until(u₀=ε, …, uₙ=v) → vₙ = v
    # i\j     ε  u₁ …  uₙ
    # ε[0  1  …  n] = cost, i = 0
    # v₁[1  …] = cost, i = 1
    # …
    # vₘ               _ x = optimum
    #
    # insertion = add from v
    # deletion = add from u
    # substitution = add from both
    #
    for i in range(1, len(v) + 1):
        # previous row
        _cost = cost[:]

        cost[0] = _cost[0] + 1
        backtracking[0] += ['I']
        for j in range(1, len(u) + 1):
            substitutionCost = cost[j] = _cost[j-1] + \
                (0 if u[j-1] == v[i-1] else 1)
            insertionCost = _cost[j] + 1
            deletionCost = cost[j-1] + 1
            print(substitutionCost, insertionCost, deletionCost)
            cost[j] = min(substitutionCost, insertionCost, deletionCost)
            if cost[j] == substitutionCost:
                # differentiate between unchanged and changed substitution
                backtracking[j] += ['0'] if u[j-1] == v[i-1] else ['1']
            elif cost[j] == insertionCost:
                backtracking[j] += ['I']
            else:
                backtracking[j] += ['D']

    print(cost)
    print(backtracking)

    # backtrace and calculate edit-sequence
    j = len(u)
    i = len(v)
    sequence = []
    while backtracking[j][i] != '_':
        sequence.insert(0, backtracking[j][i])
        if backtracking[j][i] in ['0', '1']:
            j -= 1
            i -= 1
        elif backtracking[j][i] == 'I':
            i -= 1
        elif backtracking[j][i] == 'D':
            j -= 1

    return sequence


print(edit_sequence('s', 't'))
