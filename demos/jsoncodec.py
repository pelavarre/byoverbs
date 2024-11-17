import ast
import json


def loads(quoted) -> object | None:
    try:
        obj_else = json.loads(quoted, object_hook=object_hook)
    except Exception:
        obj_else = ast.literal_eval(quoted)
        return obj_else
    return obj_else


def dumps(obj_else) -> str:
    try:
        quoted = json.dumps(obj_else, cls=JSONEncoder)
        return quoted
    except Exception:
        quoted = repr(obj_else)
        return quoted


class JSONEncoder(json.JSONEncoder):
    """Quote the conventionally unquotable Python Object's as Python Repr's"""

    def default(self, o):
        if isinstance(o, tuple):
            quoted = repr(o)
            return quoted
        try:
            quoted = json.JSONEncoder.default(self, o=o)
            return quoted
        except Exception:
            quoted = repr(o)
            return quoted


def object_hook(obj_else) -> object | None:
    """Unquote the Str's that are Python Repr's as Python Object's"""

    if not isinstance(obj_else, str):
        return obj_else

    try:
        obj_else = ast.literal_eval(obj_else)
        return obj_else
    except Exception:
        return obj_else


int_by_tuple = dict()
int_by_tuple[1, 2] = 12

tests: list[object]
tests = list()

tests.append(b"")
tests.append(b"123")
tests.append(set())
tests.append(set("abc"))  # works, but disorders output
tests.append(int_by_tuple)
tests.append(tuple())  # round-trips wrong, as list()
tests.append(tuple("xyz"))  # round-trips wrong, as list("xyz")

for test in tests:
    print()
    quoted = dumps(test)
    print(repr(quoted))
    obj = loads(quoted)
    print(type(obj).__name__, repr(obj), str(obj))


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/jsoncodec.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
