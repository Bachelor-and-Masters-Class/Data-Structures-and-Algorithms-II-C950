
# WGUPS Routing Program (Task 2)

This project implements the WGUPS routing program in Python **without using `dict`**.  
All mappings are implemented via a custom `HashTable` and simple list-based structures.

## How to run
```
python3 main.py
```
The app will prompt for a time (e.g., `09:05`) to show status of any package and total mileage.
Quick demo shortcuts are available in the menu to print statuses for the three required windows.

## Data files
Place the three CSV files in the `data/` folder (names must match):

- `WGUPS_Package_File.csv`
- `WGUPS_Distance_Table.csv`
- `WGUPS_Address_List.csv` (one address per line in the same order as the distance matrix header)

> If you only have the combined distance table with headers, you can export the address column to `WGUPS_Address_List.csv` in the order they appear.

## Design
- `HashTable` (custom, separate chaining using lists) stores **Package** objects keyed by package ID.
- `DistanceTable` holds the symmetric distances and provides O(1) matrix lookup.
- `Router` builds and simulates routes using a **greedy nearest-neighbor with deadline bias**, then simulates truck movement at 18 mph.
- `UI` prints package statuses at any time and total miles.

## Screenshots to capture (for submission)
1. Status of all packages on each truck between **8:35–9:25 AM** (use menu option 2).
2. Status of all packages on each truck between **9:35–10:25 AM** (use menu option 3).
3. Status of all packages on each truck between **12:03–1:12 PM** (use menu option 4).
4. Completion screen showing **total mileage for all trucks** (menu option 1 after simulation).

## Notes
- Package #9 wrong address is auto-corrected at **10:20 AM**.
- Three trucks, capacity 16. Two drivers: Truck 1 and Truck 2 start at 08:00; Truck 3 can begin when a driver is free.
- Delivery/loading time is instantaneous (factored into average speed).
