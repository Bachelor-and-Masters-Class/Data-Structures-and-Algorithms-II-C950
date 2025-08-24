# distance.py
import re

class DistanceTable:
    def __init__(self):
        self.addresses = []
        self.matrix = []

    def load_from_csv_lower(self, addresses, lower_triangle_rows):
        self.addresses = addresses[:]
        n = len(self.addresses)
        self.matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1):
                cell = lower_triangle_rows[i][j]
                val = float(cell) if cell != "" else 0.0
                self.matrix[i][j] = val
                self.matrix[j][i] = val

    # ---------- Robust normalization + matching ----------
    # include '#' too (for things like "#104")
    _punct = re.compile(r"[#,.()]")
    _space = re.compile(r"\s{2,}")

    def _norm(self, s: str) -> str:
        if not s:
            return ""

        # drop anything in parentheses (often zip or notes)
        s = s.split("(")[0]
        s = self._punct.sub("", s).strip()

        parts = []
        for w in s.split():
            u = w.upper()

            # compass directions
            if u == "NORTH":  parts.append("N");  continue
            if u == "SOUTH":  parts.append("S");  continue
            if u == "EAST":   parts.append("E");  continue
            if u == "WEST":   parts.append("W");  continue

            # street types
            if u == "STREET":     parts.append("ST");   continue
            if u == "AVENUE":     parts.append("AVE");  continue
            if u == "BOULEVARD":  parts.append("BLVD"); continue
            if u == "ROAD":       parts.append("RD");   continue
            if u == "DRIVE":      parts.append("DR");   continue
            if u == "COURT":      parts.append("CT");   continue
            if u == "PLACE":      parts.append("PL");   continue
            if u == "LANE":       parts.append("LN");   continue
            if u == "PARKWAY":    parts.append("PKWY"); continue
            if u == "SQUARE":     parts.append("SQ");   continue
            if u == "TERRACE":    parts.append("TER");  continue
            if u == "CIRCLE":     parts.append("CIR");  continue
            if u == "HIGHWAY":    parts.append("HWY");  continue

            # special cases for this dataset
            # treat "Sta" and "Station" as the same (or ignore both)
            if u in ("STA", "STATION"):
                # We simply drop it so both forms match:
                # "Valley Central Sta bus Loop" == "Valley Central Station bus Loop"
                continue

            # "BUS" is sometimes present; safe to ignore for matching
            if u == "BUS":
                continue

            parts.append(w)

        s = " ".join(parts)
        s = self._space.sub(" ", s).strip().lower()
        return s

    def index_of(self, address: str) -> int:
        """
        Find an index by comparing normalized forms.
        Accept equality, 'a in b', or 'b in a' as a match.
        """
        needle = self._norm(address)
        for i, lab in enumerate(self.addresses):
            hay = self._norm(lab)
            if needle == hay or needle in hay or hay in needle:
                return i
        return -1

    def distance(self, i: int, j: int) -> float:
        return self.matrix[i][j]
