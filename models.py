from datetime import datetime, time, timedelta

# Scenario constants
START_TIME: time = time(8, 0)
SPEED_MPH: float = 18.0
HUB_INDEX: int = 0
MAX_CAPACITY: int = 16


class Package:
    def __init__(self, package_id, address, city, zipcode, deadline, weight, note):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.zipcode = zipcode
        self.deadline = (deadline or "").strip()
        self.weight = weight
        self.note = note
        self.address_index = -1

        # runtime fields
        self.status = "At Hub"
        self.time_loaded = None          # <— router uses this
        self.time_delivered = None
        self.truck_id = None

    def _normalize_deadline(self) -> str:
        d = (self.deadline or "").strip()
        if not d or d.upper() == "EOD":
            return "EOD"
        d = d.replace(".", "")
        while "  " in d:
            d = d.replace("  ", " ")
        return d

    def deadline_dt(self) -> datetime:
        d = self._normalize_deadline()
        if d == "EOD":
            return datetime.combine(datetime.today().date(), time(23, 59))
        patterns = ["%H:%M", "%I:%M %p", "%I:%M%p", "%H:%M:%S", "%I %p"]
        for fmt in patterns:
            try:
                t = datetime.strptime(d, fmt).time()
                return datetime.combine(datetime.today().date(), t)
            except ValueError:
                pass
        digits = "".join(ch for ch in d if ch.isdigit())
        if len(digits) in (3, 4):
            hh = int(digits[:-2]); mm = int(digits[-2:])
            if 0 <= hh < 24 and 0 <= mm < 60:
                return datetime.combine(datetime.today().date(), time(hh, mm))
        return datetime.combine(datetime.today().date(), time(23, 59))

    def __repr__(self):
        return f"Package({self.package_id}, '{self.address}', '{self.deadline}', idx={self.address_index})"


class Truck:
    """Minimal truck model used by router."""
    def __init__(self, truck_id: str):
        self.truck_id = truck_id
        self.capacity = MAX_CAPACITY
        self.location = HUB_INDEX
        self.location_index = HUB_INDEX
        self.clock = datetime.combine(datetime.today().date(), START_TIME)
        self.miles = 0.0
        self.packages = []    # package IDs on the truck
        self.history = []

    def set_location(self, idx: int):
        self.location = idx
        self.location_index = idx

    def travel(self, miles: float):
        hours = miles / SPEED_MPH if SPEED_MPH > 0 else 0.0
        self.clock += timedelta(hours=hours)
        self.miles += miles
