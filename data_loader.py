# CSV loaders (no dict() used for primary storage)
import csv
from models import Package


def load_distance_table(distance_file: str):
    """
    Return (addresses, lower_triangle):
      - addresses: list[str]
      - lower_triangle: list[list[str|float]] where row i has entries for j<=i
    Detects numeric block automatically.
    """
    rows = []
    with open(distance_file, newline="", encoding="utf-8") as f:
        for r in csv.reader(f):
            rows.append(r)

    # Heuristic: first row with many non-empty cells is the header line,
    # addresses start on the next row in column A.
    header_row = None
    for i, r in enumerate(rows):
        non_empty = sum(1 for c in r if c.strip())
        if non_empty >= 5:
            header_row = i
            break
    if header_row is None:
        raise RuntimeError("Could not locate header row in WGUPS_Distance_Table.csv")

    addresses = []
    start = header_row + 1
    for r in rows[start:]:
        first = r[0].strip() if r and len(r) > 0 else ""
        if first == "":
            break
        addresses.append(first)

    n = len(addresses)
    tri = [["" for _ in range(n)] for _ in range(n)]
    for i in range(n):
        sr = rows[start + i] if start + i < len(rows) else []
        for j in range(i + 1):
            col = 1 + j
            if col < len(sr):
                cell = sr[col].strip()
                if cell != "":
                    try:
                        tri[i][j] = float(cell)
                    except:
                        tri[i][j] = ""
    return addresses, tri


def load_packages(packages_file: str):
    """
    Robustly read the package file.
    We start when the first cell parses as int (Package ID).
    Columns:
      0 ID, 1 Address, 2 City, 3 State, 4 Zip, 5 Deadline, 6 Weight, 7 Notes
    """
    packages = []
    with open(packages_file, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        for row in rd:
            if not row or len(row) < 6:
                continue
            try:
                pid = int(row[0].strip())
            except:
                continue
            address = row[1].strip() if len(row) > 1 else ""
            city = row[2].strip() if len(row) > 2 else ""
            zipcode = row[4].strip() if len(row) > 4 else ""
            deadline = row[5].strip() if len(row) > 5 and row[5].strip() else "EOD"
            weight = row[6].strip() if len(row) > 6 else ""
            note = row[7].strip() if len(row) > 7 else ""
            packages.append(Package(pid, address, city, zipcode, deadline, weight, note))

    if not packages:
        raise RuntimeError("No package rows found in WGUPS_Package_File.csv")
    return packages
