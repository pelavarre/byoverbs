import collections


cc = list()

for o0 in range(9):
    for o1 in range(8):
        for o2 in range(7):
            for o3 in range(6):
                c = 9 * [" "]

                for o in (o0, o1, o2, o3):
                    p = o
                    while c[p] == "o":
                        p = p + 1

                    c[p] = "o"

                for q in range(9):
                    if c[q] == " ":
                        c[q] = "x"

                c = tuple(c)
                cc.append(c)


print()
print(len(cc))
cc = sorted(set(cc))
print(len(cc))


def func(c):
    print()
    print(" ".join(c[:3]))
    print(" ".join(c[3:-3]))
    print(" ".join(c[-3:]))


_ = """
import datetime as dt
t0 = dt.datetime.now()
t1 = dt.datetime.now()
print(t1 - t0)
"""


#
#
#


wins = list()

wins.append((0, 1, 2))
wins.append((3, 4, 5))
wins.append((6, 7, 8))

wins.append((0, 3, 6))
wins.append((1, 4, 7))
wins.append((2, 5, 8))

wins.append((0, 4, 8))
wins.append((2, 4, 6))


c_by_nxo = collections.defaultdict(list)

for c in cc:
    scores = collections.defaultdict(int)
    for w in wins:
        p = tuple(c[_] for _ in w)
        if len(set(p)) == 1:
            assert p[0] != " "
            scores[p[0]] += 1

    summed = sum(scores.values())
    if len(scores.keys()) == 0:
        k = " "
        c_by_nxo[k].append(c)

    elif len(scores.keys()) == 1:
        k = sorted(scores.keys())[-1]
        assert k in "xo", (k,)

        c_by_nxo[k].append(c)

    else:
        kk = sorted(scores.keys())
        vv = sorted(scores.values())

        assert kk == ["o", "x"]
        assert vv == [1, 1]

        c_by_nxo["."].append(c)


print()
print(len(c_by_nxo["x"]))
print(len(c_by_nxo["o"]))
print(len(c_by_nxo["."]))
print(len(c_by_nxo[" "]))
assert 126 == sum(int(_) for _ in "62 12 36 16".split())

print()
print(len(list(_ for _ in c_by_nxo["x"] if _[5] == "x")))
print(len(list(_ for _ in c_by_nxo["o"] if _[5] == "x")))
print(len(list(_ for _ in c_by_nxo[" "] if _[5] == "x")))
print(len(list(_ for _ in c_by_nxo["."] if _[5] == "x")))
print(len(list(_ for _ in c_by_nxo["x"] if _[5] == "o")))
print(len(list(_ for _ in c_by_nxo["o"] if _[5] == "o")))
print(len(list(_ for _ in c_by_nxo[" "] if _[5] == "o")))
print(len(list(_ for _ in c_by_nxo["."] if _[5] == "o")))
assert 126 == sum(int(_) for _ in "31 10 9 20 31 2 7 16".split())


def corners(c):
    four = (c[0], c[2], c[6], c[8])
    return four


print()
print(len(list(_ for _ in c_by_nxo["x"] if _[5] == "x" and "x" in corners(_))))
print(len(list(_ for _ in c_by_nxo["o"] if _[5] == "x" and "x" in corners(_))))
print(len(list(_ for _ in c_by_nxo[" "] if _[5] == "x" and "x" in corners(_))))
print(len(list(_ for _ in c_by_nxo["."] if _[5] == "x" and "x" in corners(_))))

print()
print(len(list(_ for _ in c_by_nxo["x"] if "x" not in corners(_))))
print(len(list(_ for _ in c_by_nxo["o"] if "x" not in corners(_))))
print(len(list(_ for _ in c_by_nxo[" "] if "x" not in corners(_))))
print(len(list(_ for _ in c_by_nxo["."] if "x" not in corners(_))))

for c in c_by_nxo["x"]:
    if "x" not in corners(c):
        func(c)


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/t3maths.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
