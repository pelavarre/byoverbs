_ = """

00 01 02
10 11 12
20 21 22

"""


rows = list()
rows.append("a b c".split())
rows.append("d e f".split())
rows.append("g h i".split())


p0 = ((0, 2), (1, 2), (2, 2))
p1 = ((0, 1), (1, 1), (2, 1))
p2 = ((0, 0), (1, 0), (2, 0))
left = (p0, p1, p2)


p0 = ((2, 0), (2, 1), (2, 2))
p1 = ((1, 0), (1, 1), (1, 2))
p2 = ((0, 0), (0, 1), (0, 2))
hflip = (p0, p1, p2)


def shuffle(rows, picks_list):

    flats = list(b for a in rows for b in a)

    assert sorted(flats) == sorted(set(flats)), flats

    shuffled = list()
    for picks in picks_list:
        picked = list()
        for pick in picks:
            y = pick[0]
            x = pick[-1]
            picked.append(rows[y][x])
        shuffled.append(picked)

    shuffled = tuple(tuple(_) for _ in shuffled)

    return shuffled


def func(step):
    print()
    for y in range(3):
        print(" ".join(step[y]))


step = tuple(tuple(_) for _ in rows)

step = shuffle(step, picks_list=hflip)

for _ in range(4):
    func(step)
    step = shuffle(step, picks_list=left)
