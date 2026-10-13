"""Minimal NBT reading and writing (Minecraft's binary format), keeping every tag's type so a file can be rewritten
exactly. Values are (type, value) pairs; compounds are dicts of name -> (type, value), lists are (element type, [values])."""
import struct

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTES, STRING, LIST, COMPOUND, INTS, LONGS = range(13)


def _read(f, t):
    if t == BYTE:
        return struct.unpack('>b', f.read(1))[0]
    if t == SHORT:
        return struct.unpack('>h', f.read(2))[0]
    if t == INT:
        return struct.unpack('>i', f.read(4))[0]
    if t == LONG:
        return struct.unpack('>q', f.read(8))[0]
    if t == FLOAT:
        return struct.unpack('>f', f.read(4))[0]
    if t == DOUBLE:
        return struct.unpack('>d', f.read(8))[0]
    if t == BYTES:
        n = struct.unpack('>i', f.read(4))[0]
        return f.read(n)
    if t == STRING:
        n = struct.unpack('>H', f.read(2))[0]
        return f.read(n).decode('utf-8', 'surrogatepass')
    if t == LIST:
        et = f.read(1)[0]
        n = struct.unpack('>i', f.read(4))[0]
        return (et, [_read(f, et) for _ in range(n)])
    if t == COMPOUND:
        d = {}
        while True:
            tt = f.read(1)[0]
            if tt == END:
                return d
            name = _read(f, STRING)
            d[name] = (tt, _read(f, tt))
    if t == INTS:
        n = struct.unpack('>i', f.read(4))[0]
        return list(struct.unpack(f'>{n}i', f.read(4 * n)))
    if t == LONGS:
        n = struct.unpack('>i', f.read(4))[0]
        return list(struct.unpack(f'>{n}q', f.read(8 * n)))
    raise ValueError(f'bad tag {t}')


def _write(out, t, v):
    if t == BYTE:
        out += struct.pack('>b', v)
    elif t == SHORT:
        out += struct.pack('>h', v)
    elif t == INT:
        out += struct.pack('>i', v)
    elif t == LONG:
        out += struct.pack('>q', v)
    elif t == FLOAT:
        out += struct.pack('>f', v)
    elif t == DOUBLE:
        out += struct.pack('>d', v)
    elif t == BYTES:
        out += struct.pack('>i', len(v)) + v
    elif t == STRING:
        b = v.encode('utf-8', 'surrogatepass')
        out += struct.pack('>H', len(b)) + b
    elif t == LIST:
        et, items = v
        out += bytes([et]) + struct.pack('>i', len(items))
        for item in items:
            _write(out, et, item)
    elif t == COMPOUND:
        for name, (tt, val) in v.items():
            out += bytes([tt])
            _write(out, STRING, name)
            _write(out, tt, val)
        out += bytes([END])
    elif t == INTS:
        out += struct.pack(f'>i{len(v)}i', len(v), *v)
    elif t == LONGS:
        out += struct.pack(f'>i{len(v)}q', len(v), *v)


def loads(data):
    """Root compound of an uncompressed NBT blob."""
    import io
    f = io.BytesIO(data)
    t = f.read(1)[0]
    _read(f, STRING)
    return _read(f, t)


def dumps(root):
    out = bytearray([COMPOUND])
    _write(out, STRING, '')
    _write(out, COMPOUND, root)
    return bytes(out)
