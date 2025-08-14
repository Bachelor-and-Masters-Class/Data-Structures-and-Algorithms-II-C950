def print_truck_snapshot(trucks, tlabel):
    print(f"\n== Truck snapshot at {tlabel} ==")
    for tr in trucks:
        print(f"{tr.truck_id}: miles={tr.miles:.2f}, time={tr.clock.strftime('%H:%M')}, at={tr.location_index}")
