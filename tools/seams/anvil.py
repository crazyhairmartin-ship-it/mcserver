"""Minimal Anvil region access (read + write chunks) on top of tools/skyvillage/nbtio.py's tag model.
Chunk NBT is kept as nbtio (type, value) trees so it can be written back unchanged apart from deliberate edits."""
import io, os, struct, time, zlib, gzip, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skyvillage"))
import nbtio  # noqa: E402


def region_path(world, kind, cx, cz):
    return os.path.join(world, kind, f"r.{cx >> 5}.{cz >> 5}.mca")


def _read_tag(raw):
    r = nbtio.R(raw)
    t = r.u("b"); r.s()
    return (t, r.payload(t))


def _write_tag(tag):
    w = nbtio.W(); t, v = tag
    w.p("b", t); w.s(""); w.payload(t, v)
    return bytes(w.out)


class Region:
    def __init__(self, path):
        self.path = path
        self.data = bytearray(open(path, "rb").read()) if os.path.exists(path) else bytearray(8192)
        if len(self.data) < 8192:
            self.data += bytes(8192 - len(self.data))

    def _loc(self, cx, cz):
        i = 4 * ((cx & 31) + (cz & 31) * 32)
        off = struct.unpack(">I", b"\0" + self.data[i:i + 3])[0]
        return i, off, self.data[i + 3]

    def has(self, cx, cz):
        return self._loc(cx, cz)[1] != 0

    def read(self, cx, cz):
        _, off, _ = self._loc(cx, cz)
        if off == 0:
            return None
        p = off * 4096
        length = struct.unpack(">I", self.data[p:p + 4])[0]
        comp = self.data[p + 4]
        body = bytes(self.data[p + 5:p + 4 + length])
        raw = zlib.decompress(body) if comp == 2 else gzip.decompress(body) if comp == 1 else body
        return _read_tag(raw)

    def delete(self, cx, cz):
        i, _, _ = self._loc(cx, cz)
        self.data[i:i + 4] = b"\0\0\0\0"
        self.data[4096 + i:4096 + i + 4] = b"\0\0\0\0"

    def write(self, cx, cz, tag):
        """Appends the chunk at the end of the file (old sectors become dead space; Minecraft doesn't mind)."""
        body = zlib.compress(_write_tag(tag))
        blob = struct.pack(">I", len(body) + 1) + b"\x02" + body
        blob += bytes((-len(blob)) % 4096)
        if len(self.data) % 4096:
            self.data += bytes(4096 - len(self.data) % 4096)
        sector = len(self.data) // 4096
        self.data += blob
        i, _, _ = self._loc(cx, cz)
        self.data[i:i + 4] = struct.pack(">I", sector)[1:] + bytes([len(blob) // 4096])
        self.data[4096 + i:4096 + i + 4] = struct.pack(">I", int(time.time()))

    def save(self):
        with open(self.path, "wb") as f:
            f.write(self.data)


def plain(tag):
    return nbtio.plain(tag)


def heightmap(chunk_plain, name="WORLD_SURFACE"):
    """16x16 heights (absolute y of the first air above the column) from a chunk's packed heightmap, or None."""
    hm = chunk_plain.get("Heightmaps", {}).get(name)
    if hm is None:
        return None
    ymin = chunk_plain.get("yPos", -4) * 16
    bits = 9
    per = 64 // bits
    out = []
    for i in range(256):
        word = hm[i // per] & ((1 << 64) - 1)
        v = (word >> ((i % per) * bits)) & ((1 << bits) - 1)
        out.append(v + ymin)
    return [out[z * 16:(z + 1) * 16] for z in range(16)]   # [z][x]
