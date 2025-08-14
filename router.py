# Deadline-aware / nearest-neighbor hybrid router.
from datetime import datetime, time
from models import Truck, HUB_INDEX
from models import START_TIME


class Router:
    def __init__(self, distance_table, package_table):
        self.D = distance_table
        self.packages = package_table       # HashTable of id -> Package
        self.trucks = [Truck("Truck 1"), Truck("Truck 2"), Truck("Truck 3")]
        self.total_miles = 0.0

    # ------------------------- helpers -----------------------------------
    def _distance(self, i, j):
        return self.D.distance(i, j)

    def _nearest(self, current_idx, candidate_pkgs):
        """Pick the nearest address (break ties by earliest deadline)."""
        best = None
        best_dist = 1e9
        for p in candidate_pkgs:
            if p.address_index < 0:
                continue
            d = self._distance(current_idx, p.address_index)
            if d < best_dist:
                best = p
                best_dist = d
            elif abs(d - best_dist) < 1e-9:
                if p.deadline_dt() < best.deadline_dt():
                    best = p
                    best_dist = d
        return best, best_dist

    def _load_available(self, truck, remaining):
        """Load up to capacity from 'remaining' that are available now (constraints)."""
        truck.packages.clear()
        now = truck.clock

        def available(pkg):
            # Package #9 address corrected at 10:20 (update address index only then)
            if pkg.package_id == 9:
                fix_time = datetime.combine(now.date(), time(10, 20))
                if now < fix_time:
                    return False
                # set correct address index once the time has passed
                if "410 S State St" not in pkg.address:
                    pkg.address = "410 S State St"
                if pkg.address_index < 0:
                    pkg.address_index = self.D.index_of(pkg.address)
            # delayed notes like “Delayed on flight—will not arrive to depot until 9:05 am”
            note = (pkg.note or "").lower()
            if "delayed" in note and "9:05" in note:
                unlock = datetime.combine(now.date(), time(9, 5))
                return now >= unlock
            return True

        # bias by deadline first, then by current proximity
        candidates = [p for p in remaining if available(p)]
        candidates.sort(key=lambda p: (p.deadline_dt(), p.package_id))

        # take first k up to capacity
        chosen = []
        for p in candidates:
            if len(chosen) >= truck.capacity:
                break
            chosen.append(p)
        truck.packages = [p.package_id for p in chosen]
        for p in chosen:
            p.status = "En Route"
            p.truck_id = truck.truck_id
            p.time_loaded = now
        return chosen

    def _deliver_run(self, truck, to_deliver):
        """Perform a nearest-neighbor tour for the loaded packages."""
        current = truck.location
        remaining = to_deliver[:]
        while remaining:
            next_pkg, dist = self._nearest(current, remaining)
            if next_pkg is None:
                break
            # travel to next_pkg
            truck.travel(dist)
            self.total_miles += dist
            current = next_pkg.address_index
            truck.set_location(current)

            # deliver
            next_pkg.status = "Delivered"
            next_pkg.time_delivered = truck.clock
            remaining.remove(next_pkg)

        # return to hub if more work is pending
        if remaining == [] and current != HUB_INDEX:
            back = self._distance(current, HUB_INDEX)
            truck.travel(back)
            self.total_miles += back
            truck.set_location(HUB_INDEX)

    # ------------------------- main entry ---------------------------------
    def plan_and_simulate(self):
        """Greedy loop: always send the earliest-available truck with a fresh load."""
        # Gather all Package objects
        pool = [pkg for _, pkg in self.packages.items()]

        # mark all at hub initially
        for p in pool:
            p.status = "At Hub"
            p.truck_id = None
            # some sheets omit zip inside address; index may be -1; it's OK—will be set later if needed

        # we operate two trucks from 08:00, and start truck 3 when one returns (driver frees up).
        active = [self.trucks[0], self.trucks[1]]
        parked = [self.trucks[2]]

        while True:
            undelivered = [p for p in pool if p.status != "Delivered"]
            if not undelivered:
                break

            # pick the truck with the earliest clock to act next
            truck = min(active + parked, key=lambda t: t.clock)
            # if chosen truck is in parked and others still out, wait until a driver frees up:
            if truck in parked:
                # choose the active truck that will free driver first
                soonest = min(active, key=lambda t: t.clock)
                # advance parked truck's clock to that time and make it active
                truck.clock = soonest.clock
                active.append(truck)
                parked.remove(truck)

            # load what is available right now
            loaded = self._load_available(truck, [p for p in undelivered if p.status != "En Route"])
            if not loaded:
                # Nothing available *right now*. Decide what time to jump to.
                # 1) Hard time gates (9:05 delayed; 10:20 address fix for #9)
                gates = [
                    datetime.combine(truck.clock.date(), time(9, 5)),
                    datetime.combine(truck.clock.date(), time(10, 20)),
                ]
                gate_candidates = [t for t in gates if t > truck.clock]

                # 2) Also consider when other active trucks will free a driver
                other_finish = [t.clock for t in active if t is not truck and t.clock > truck.clock]

                # Merge all possible “future” times and jump to the earliest one
                possible_times = gate_candidates + other_finish

                # >>> Guard: if no future events exist, stop cleanly (prevents min() on empty)
                if not possible_times:
                    # Nothing else to wait for; simulation is done (or another truck will break the loop)
                    break

                truck.clock = min(possible_times)
                continue

            # deliver this run
            self._deliver_run(truck, loaded)

        # total_miles already accumulated per truck
        self.total_miles = sum(t.miles for t in self.trucks)

        # ------------------------- status reporting ---------------------------

    def _base_dt(self) -> datetime:
        """Return a base datetime to use for comparisons/printing."""
        # If START_TIME is a datetime, use it. If it's a time, fuse it with a real date
        # (use the first truck's current day).
        if isinstance(START_TIME, datetime):
            return START_TIME
        elif isinstance(START_TIME, time):
            return datetime.combine(self.trucks[0].clock.date(), START_TIME)
        # Fallback: now (but in practice you won't hit this)
        return self.trucks[0].clock

    def _normalize_when(self, when_dt) -> datetime:
        """Accept datetime, time, or 'HH:MM' and return a datetime."""
        if isinstance(when_dt, datetime):
            return when_dt
        base = self._base_dt()
        if isinstance(when_dt, time):
            return datetime.combine(base.date(), when_dt)
        # allow strings like "09:00"
        try:
            hh, mm = map(int, str(when_dt).strip().split(":"))
            return datetime.combine(base.date(), time(hh, mm))
        except Exception:
            return base

    def _status_at(self, pkg, when_dt):
        """
        Return (status_text, time_text) for the package at 'when_dt'.
        Uses pkg.time_loaded and pkg.time_delivered if present.
        """
        td = getattr(pkg, "time_delivered", None)  # datetime or None
        tl = getattr(pkg, "time_loaded", None)     # datetime or None

        when_dt = self._normalize_when(when_dt)

        if td is not None and td <= when_dt:
            return ("Delivered", td.strftime("%H:%M"))
        if tl is not None and tl <= when_dt:
            return ("En Route", tl.strftime("%H:%M"))
        return ("At Hub", "")

    def print_statuses_at(self, when_dt):
        """
        Print the status of ALL packages at the specified time/datetime, grouped by truck.
        Accepts a datetime, time, or 'HH:MM' string.
        """
        when_dt = self._normalize_when(when_dt)
        print(f"\n=== Package statuses at {when_dt.strftime('%H:%M')} ===")

        all_pkgs = [pkg for _, pkg in self.packages.items()]
        groups = {"Truck 1": [], "Truck 2": [], "Truck 3": [], None: []}

        for p in all_pkgs:
            status, when = self._status_at(p, when_dt)
            groups.setdefault(p.truck_id, []).append((p, status, when))

        def print_group(label):
            rows = groups.get(label, [])
            print(f"\n--- {label or 'Unassigned/At Hub'} ---")
            if not rows:
                print("(no packages)")
                return
            rows.sort(key=lambda r: r[0].package_id)
            for p, status, when in rows:
                time_note = f" at {when}" if when else ""
                addr = f"{p.address}, {p.city} {p.zipcode}"
                print(
                    f"ID {p.package_id:>2} | {addr} | deadline {p.deadline:>5} | "
                    f"{status}{time_note} | weight {p.weight}"
                )

        print_group("Truck 1")
        print_group("Truck 2")
        print_group("Truck 3")
        print_group(None)

        delivered_count = sum(
            1 for p in all_pkgs
            if getattr(p, "time_delivered", None) and p.time_delivered <= when_dt
        )
        print(f"\nDelivered by {when_dt.strftime('%H:%M')}: {delivered_count} / {len(all_pkgs)} packages")
        print(f"Total mileage (all trucks): {sum(t.miles for t in self.trucks):.2f} miles\n")
