"""Minimal NBT reader/writer (gzip structure files). Tags kept as (type, value) so files round-trip exactly."""
import gzip, struct

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BARR, STR, LIST, COMP, IARR, LARR = range(13)


class R:
    def __init__(self, b):
        self.b, self.i = b, 0

    def take(self, n):
        v = self.b[self.i:self.i + n]
        self.i += n
        return v

    def u(self, fmt):
        n = struct.calcsize(fmt)
        return struct.unpack(">" + fmt, self.take(n))[0]

    def s(self):
        return self.take(self.u("H")).decode("utf8")

    def payload(self, t):
        if t == BYTE: return self.u("b")
        if t == SHORT: return self.u("h")
        if t == INT: return self.u("i")
        if t == LONG: return self.u("q")
        if t == FLOAT: return self.u("f")
        if t == DOUBLE: return self.u("d")
        if t == BARR: return list(self.take(self.u("i")))
        if t == STR: return self.s()
        if t == LIST:
            et = self.u("b"); n = self.u("i")
            return (et, [self.payload(et) for _ in range(n)])
        if t == COMP:
            d = {}
            while True:
                tt = self.u("b")
                if tt == END: return d
                k = self.s()
                d[k] = (tt, self.payload(tt))
        if t == IARR: return [self.u("i") for _ in range(self.u("i"))]
        if t == LARR: return [self.u("q") for _ in range(self.u("i"))]
        raise ValueError(t)


def load(path):
    r = R(gzip.open(path).read())
    t = r.u("b"); r.s()
    return (t, r.payload(t))


class W:
    def __init__(self):
        self.out = bytearray()

    def p(self, fmt, v):
        self.out += struct.pack(">" + fmt, v)

    def s(self, v):
        b = v.encode("utf8"); self.p("H", len(b)); self.out += b

    def payload(self, t, v):
        if t == BYTE: self.p("b", v)
        elif t == SHORT: self.p("h", v)
        elif t == INT: self.p("i", v)
        elif t == LONG: self.p("q", v)
        elif t == FLOAT: self.p("f", v)
        elif t == DOUBLE: self.p("d", v)
        elif t == BARR: self.p("i", len(v)); self.out += bytes(x & 0xff for x in v)
        elif t == STR: self.s(v)
        elif t == LIST:
            et, items = v; self.p("b", et); self.p("i", len(items))
            for it in items: self.payload(et, it)
        elif t == COMP:
            for k, (tt, vv) in v.items():
                self.p("b", tt); self.s(k); self.payload(tt, vv)
            self.p("b", END)
        elif t == IARR:
            self.p("i", len(v)); [self.p("i", x) for x in v]
        elif t == LARR:
            self.p("i", len(v)); [self.p("q", x) for x in v]


def save(path, tag):
    w = W(); t, v = tag
    w.p("b", t); w.s(""); w.payload(t, v)
    with gzip.open(path, "wb") as f:
        f.write(bytes(w.out))


def plain(tag):
    """(type, value) tree -> plain python, for printing."""
    t, v = tag
    if t == COMP: return {k: plain(x) for k, x in v.items()}
    if t == LIST: return [plain((v[0], x)) for x in v[1]]
    return v
