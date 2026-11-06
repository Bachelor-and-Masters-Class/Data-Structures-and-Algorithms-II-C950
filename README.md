# Package Delivery Router

**WGU C950 · Data Structures and Algorithms II**

Plans delivery routes for 40 packages across Salt Lake City with 3 trucks and 2 drivers. The total has to stay under 140 miles. **Result: all 40 delivered in 134.3 miles.**

## The rules it has to follow

- Some packages have hard deadlines.
- Some can only go on a specific truck.
- Some must be delivered together.
- One has a wrong address that isn't fixed until 10:20 a.m.
- Some don't arrive at the depot until later in the morning.

## How it works

- **Custom hash table:** packages are stored in a hash table built from scratch, without Python's built-in dictionary. Lookups are fast (O(1) on average).
- **Routing:** each truck drives to the closest undelivered package on board, delivers it, and repeats (nearest neighbor). That's not perfect, but it's fast and well under the mileage limit.
- **Time simulation:** tracks when each package is loaded and delivered, so you can check any package's status at any time of day.
- **Menu:** shows total miles, every package's status at a chosen time, or one package by ID.

## Run it

```
python main.py
```

Needs `WGUPS_Distance_Table.csv` and `WGUPS_Package_File.csv` in `data/`.

## Files

- `main.py`, `ui.py`: menu and status display
- `hash_table.py`: the custom hash table
- `router.py`: routing, truck loading and time simulation
- `distance.py`: distance lookups between addresses
- `models.py`: package and truck objects
- `data_loader.py`: reads the CSV files
- `data/`: package and distance data

**Built with:** Python
