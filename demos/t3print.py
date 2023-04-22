chars = """

Tic-tac-toe - turn left, turn right, spin around y-axis, flip over x-axis


== base ==

a b c
d e f
g h i

== turn left three times, and spin each of these around its y-axis ==

a b c   c b a
d e f   f e d
g h i   i h g

c f i   i f c
b e h   h e b
a d g   g d a

i h g   g h i
f e d   d e f
c b a   a b c

g d a   a d g
h e b   b e h
i f c   c f i


== flip the base over x-axis, and then turn right three times ==
== each such result already appears above, as the spin after turning left twice ==

g h i
d e f
a b c

a d g
b e h
c f i

c b a
f e d
i h g

i f c
h e b
g d a

== numbered ==

0 1 2
3 4 5
6 7 8


"""


from_chars = "abcdefghi"


to_strs = list()
to_strs.append("\x1B[36m" "." "\x1B[0m")  # Cyan
to_strs.append("\x1B[32m" "." "\x1B[0m")  # Green
to_strs.append("\x1B[33m" "." "\x1B[0m")  # Yello
to_strs.append("\x1B[35m" "." "\x1B[0m")  # Magenta (often rendered as Pink)
to_strs.append("\x1B[31m" "." "\x1B[0m")  # Red
to_strs.append("\x1B[34m" "." "\x1B[0m")  # Blue
to_strs.append("\x1B[30m" "." "\x1B[0m")  # Black
to_strs.append("\x1B[37m" "." "\x1B[0m")  # White (often rendered as Grey)
to_strs.append("\N{Middle Dot}")

to_strs = list(_.replace(".", "\N{Black Large Circle}") for _ in to_strs)


lines = chars.splitlines()

dent = 4 * " "
for line in lines:
    if not all((len(_) == 1) for _ in line.split()):
        print(dent + line)
    else:
        alt_line = line
        for f, t in zip(from_chars, to_strs):
            alt_line = alt_line.replace(f, t)
        print(dent + alt_line)


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/t3print.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
