# Student ID: <012494418>  ← replace with YOUR WGU ID
# Entry point & simple console UI.

import os
from hash_table import HashTable
from data_loader import load_distance_table, load_packages
from distance import DistanceTable
from router import Router
from models import START_TIME

DATA_DIR = "data"


def ensure_data_files():
    """Verify the two CSVs exist under ./data/ and return their paths."""
    dt = os.path.join(DATA_DIR, "WGUPS_Distance_Table.csv")
    pf = os.path.join(DATA_DIR, "WGUPS_Package_File.csv")
    for path in (dt, pf):
        if not os.path.exists(path):
            raise SystemExit(f"Missing required data file: {path}")
    return dt, pf


def build_package_table(packages, distance_table):
    """
    Build a hash table keyed by package_id → Package object.
    We also attach address indices for fast distance lookup.
    """
    ht = HashTable()
    for p in packages:
        p.address_index = distance_table.index_of(p.address)
        ht.insert(p.package_id, p)
    return ht


def main():
    print("WGUPS Routing Program — Python (no dict version)")

    # ---- Load data ----------------------------------------------------------
    dt_path, pf_path = ensure_data_files()
    addresses, lower_triangle = load_distance_table(dt_path)

    D = DistanceTable()
    D.load_from_csv_lower(addresses, lower_triangle)

    packages = load_packages(pf_path)
    package_table = build_package_table(packages, D)

    # ---- Plan & simulate ----------------------------------------------------
    router = Router(D, package_table)
    print("Planning and simulating routes...")
    router.plan_and_simulate()
    print(f"Total mileage (all trucks): {router.total_miles:.2f} miles")

    # ---- Quick menu for screenshots required by rubric ---------------------
    while True:
        print("\nMenu:")
        print("1) Total mileage + delivered count")
        print("2) Show statuses at 09:00 (8:35–9:25 window)")
        print("3) Show statuses at 10:05 (9:35–10:25 window)")
        print("4) Show statuses at 12:30 (12:03–1:12 window)")
        print("5) Custom time (HH:MM 24-hr)")
        print("6) Lookup package by ID")
        print("0) Exit")
        choice = input("> ").strip()

        if choice == "0":
            break
        elif choice == "1":
            delivered = sum(
                1 for _, p in package_table.items()
                if getattr(p, "time_delivered", None) is not None
            )
            print(f"Delivered: {delivered}/40; Total miles: {router.total_miles:.2f}")

        elif choice in {"2", "3", "4", "5"}:
            if choice == "2":
                when = START_TIME.replace(hour=9, minute=0)
            elif choice == "3":
                when = START_TIME.replace(hour=10, minute=5)
            elif choice == "4":
                when = START_TIME.replace(hour=12, minute=30)
            else:
                t_str = input("Enter time (HH:MM): ").strip()
                try:
                    hh, mm = map(int, t_str.split(":"))
                    when = START_TIME.replace(hour=hh, minute=mm)
                except Exception:
                    print("Invalid time. Use HH:MM, e.g., 09:15")
                    continue

            # Use the router's status snapshot helper (prints grouped by truck)
            router.print_statuses_at(when)

        elif choice == "6":
            try:
                q = int(input("Package ID: ").strip())
            except Exception:
                print("Invalid.")
                continue

            pkg = package_table.get(q)
            if not pkg:
                print("Not found.")
                continue

            td = pkg.time_delivered.strftime("%H:%M") if pkg.time_delivered else "-"
            tl = getattr(pkg, "time_loaded", None)
            tl = tl.strftime("%H:%M") if tl else "-"

            print(f"""
ID: {pkg.package_id}
Address: {pkg.address}, {pkg.city} {pkg.zipcode}
Deadline: {pkg.deadline}
Weight: {pkg.weight}
Loaded Time: {tl}
Delivered Time: {td}
Status now: {pkg.status}
Truck: {pkg.truck_id or '-'}
""")
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
