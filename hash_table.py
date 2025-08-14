# One open-addressing hash table that supports:
#  - generic insert/get/items for Package objects (used by Router)
#  - rubric-specific insert_by_id(...) and lookup_by_id(...)

class HashTable:
    def __init__(self, capacity: int = 256):
        self.capacity = capacity
        self.size = 0
        self.slots = [None] * capacity  # each slot: None or (key, value)

    # base hashing/probing
    def _hash(self, key: int) -> int:
        return key % self.capacity

    def _probe(self, start):
        i = start
        while True:
            yield i
            i = (i + 1) % self.capacity

    # -------- generic API (for Package objects) ----------------------------
    def insert(self, key: int, value):
        idx = self._hash(key)
        for i in self._probe(idx):
            if self.slots[i] is None:
                self.slots[i] = (key, value)
                self.size += 1
                return
            if self.slots[i][0] == key:
                self.slots[i] = (key, value)
                return

    def get(self, key: int):
        idx = self._hash(key)
        for i in self._probe(idx):
            slot = self.slots[i]
            if slot is None:
                return None
            if slot[0] == key:
                return slot[1]

    def items(self):
        for slot in self.slots:
            if slot is not None:
                yield slot

    # -------- rubric-specific helpers (A & B) ------------------------------
    def insert_by_id(
            self,
            package_id: int,
            address: str,
            deadline: str,
            city: str,
            zipcode: str,
            weight: str,
            status: str,
            delivered_time=None,
    ):
        payload = {
            "address": address,
            "deadline": deadline,
            "city": city,
            "zipcode": zipcode,
            "weight": weight,
            "status": status,
            "delivered_time": delivered_time,
        }
        self.insert(package_id, payload)

    def lookup_by_id(self, package_id: int):
        v = self.get(package_id)
        if v is None:
            return None
        # If a Package instance was stored, convert to rubric view
        if hasattr(v, "address"):
            return {
                "address": v.address,
                "deadline": v.deadline,
                "city": v.city,
                "zipcode": v.zipcode,
                "weight": v.weight,
                "status": v.status,
                "delivered_time": v.time_delivered,
            }
        # Already a rubric payload
        return {
            "address": v["address"],
            "deadline": v["deadline"],
            "city": v["city"],
            "zipcode": v["zipcode"],
            "weight": v["weight"],
            "status": v["status"],
            "delivered_time": v["delivered_time"],
        }
