STYPE = 0
PTYPE = 1
ATYPE = 2
OTYPE = 3


def _strip(s: str) -> str:
    if s == "/":
        return s
    if s.startswith("/"):
        s = s[1:]
    if s.endswith("/"):
        s = s[:-1]
    return s


def _split(s: str) -> list[str]:
    s = _strip(s)
    return ["/"] if s == "/" else s.split("/")


def _is_match(segs: list[str], obj: dict, idx: int) -> bool:
    seg = segs[idx]
    if obj["type"] == STYPE:
        return obj["val"] == seg
    if seg == "/":
        return obj["type"] > PTYPE
    return obj["type"] != STYPE and seg.endswith(obj["end"])


def match_it(s: str, all_patterns: list[list[dict]]) -> list[dict]:
    segs = _split(s)
    seg_len = len(segs)

    for pattern in all_patterns:
        plen = len(pattern)
        last = pattern[-1]["type"] if pattern else None

        if (
            plen == seg_len
            or (plen < seg_len and last == ATYPE)
            or (plen > seg_len and last == OTYPE)
        ):
            if all(_is_match(segs, obj, idx) for idx, obj in enumerate(pattern)):
                return pattern

    return []


def parse_it(s: str) -> list[dict]:
    if s == "/":
        return [{"old": s, "type": STYPE, "val": s, "end": ""}]

    path = _strip(s)
    i = 0
    length = len(path)
    out = []

    while i < length:
        c = path[i]

        if c == ":":
            j = i + 1
            t = PTYPE
            x = 0
            sfx = ""

            while i < length and path[i] != "/":
                if path[i] == "?":
                    x = i
                    t = OTYPE
                elif path[i] == "." and not sfx:
                    sfx = path[i:]
                    x = i
                i += 1

            out.append(
                {"old": s, "type": t, "val": path[j:x] if x else path[j:i], "end": sfx}
            )

        elif c == "*":
            out.append({"old": s, "type": ATYPE, "val": path[i:], "end": ""})
            break

        else:
            j = i
            while i < length and path[i] != "/":
                i += 1
            out.append({"old": s, "type": STYPE, "val": path[j:i], "end": ""})

        if i < length and path[i] == "/":
            i += 1

    return out


def exec_it(s: str, pattern: list[dict]) -> dict[str, str]:
    segs = _split(s)
    result = {}

    for i, p in enumerate(pattern):
        if i >= len(segs):
            break
        seg = segs[i]
        if seg == "/":
            continue
        if p["type"] | 2 == OTYPE:
            result[p["val"]] = seg.removesuffix(p["end"])

    return result
