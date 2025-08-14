# Symmetric distance matrix with O(1) index lookup

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

    def index_of(self, address: str) -> int:
        """Match by substring so '410 S State St' matches '410 S State St (84111)'."""
        base = address.strip().lower().split("(")[0].strip()
        for i, lab in enumerate(self.addresses):
            if base in lab.lower():
                return i
        return -1

    def distance(self, i: int, j: int) -> float:
        return self.matrix[i][j]
