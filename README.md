**Overview**

This repository contains my completed submission for the WGU course **C950 – Data Structures and Algorithms II**: the WGUPS Routing Program.

The project implements a package delivery routing system for the Western Governors University Parcel Service (WGUPS). The program loads a set of 40 packages and a distance matrix of delivery addresses, assigns packages to trucks under a set of real-world constraints, and determines an efficient delivery route while keeping total mileage under the required threshold.

The core of the assignment is the design and implementation of a **custom hash table built from scratch** (no Python dictionaries) for package storage and lookup, paired with a **greedy nearest-neighbor algorithm** for route optimization.

**Scenario**

WGUPS must deliver 40 packages across Salt Lake City using three trucks and two available drivers. Delivery planning is complicated by a set of constraints attached to individual packages:

-Specific packages must be delivered by a hard deadline

-Certain packages are restricted to a specific truck

-Some packages must be delivered together on the same truck

-One package has an incorrect address that is not corrected until 10:20 a.m.

-Several packages do not arrive at the depot until later in the morning

The program must satisfy every constraint while keeping combined mileage for all trucks under 140 miles.

**Project Objectives**

-Implement a self-adjusting hash table with insertion and lookup functionality

-Load and parse package and distance data from CSV source files

-Apply a greedy nearest-neighbor algorithm to determine delivery order

-Enforce all delivery, truck, grouping, and timing constraints

-Track and report package status at any point in the delivery day

-Provide a command-line interface for querying delivery status and total mileage

**Technical Implementation**

**Custom Hash Table (`hash_table.py`)**
A chaining hash table implemented without built-in dictionary types. Supports insert and lookup operations keyed by package ID, with each bucket holding the full package record: address, city, ZIP, deadline, weight, delivery status, and timestamps.

**Distance Table (`distance.py`)**
Loads the lower-triangular distance matrix from CSV and resolves address strings to matrix indices, providing symmetric distance lookups between any two delivery points.

**Routing Engine (`router.py`)**
Implements the greedy nearest-neighbor selection logic, truck loading strategy, constraint enforcement, and time simulation. Tracks cumulative mileage and stamps each package with its loaded and delivered times.

**Data Models (`models.py`)**
Defines the Package and Truck objects, delivery status states, and the simulation start time.

**Data Loader (`data_loader.py`)**
Parses `WGUPS_Distance_Table.csv` and `WGUPS_Package_File.csv` into application objects.

**User Interface (`main.py`, `ui.py`)**
A console menu that allows the user to view total mileage and delivered counts, inspect the status of all packages at any given time, and look up individual packages by ID.

**Algorithm and Complexity**

The routing solution uses a greedy nearest-neighbor approach: from the current location, the truck selects the nearest undelivered package on board, delivers it, and repeats until the truck is empty.

-Hash table insert and lookup: O(1) average case

-Nearest-neighbor route construction: O(n²) worst case per truck

-Space complexity: O(n) relative to the number of packages

This approach was selected for its balance of implementation clarity and performance. It produces a near-optimal route in a fraction of the time required by an exhaustive search, and comfortably satisfies the mileage requirement for this dataset.

**Skills Demonstrated**

-Custom data structure design and implementation

-Hash table construction with collision handling

-Greedy algorithm design and application

-Algorithmic complexity analysis (Big-O)

-Constraint-based problem solving

-CSV parsing and data modeling

-Time simulation and state tracking

-Command-line interface development

**How to Run**

```
python main.py
```

The program expects `WGUPS_Distance_Table.csv` and `WGUPS_Package_File.csv` to be present in the `data/` directory.

**Repository Contents**

-`main.py` – Program entry point and console menu

-`hash_table.py` – Custom hash table implementation

-`router.py` – Routing algorithm, truck loading, and delivery simulation

-`distance.py` – Distance matrix handling and address resolution

-`models.py` – Package and truck data models

-`data_loader.py` – CSV parsing and object construction

-`ui.py` – Status display and reporting helpers

-`data/` – Source CSV files for packages and distances
