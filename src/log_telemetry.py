import time
import csv
import os
from pyaccsharedmemory import accSharedMemory

def main():
    asm = accSharedMemory()

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Output filename with session timestamp
    filename = f"data/telemetry_session_{int(time.time())}.csv"

    print(f"📁 Logging to: {filename}")
    print("📡 Waiting for ACC telemetry...")

    # Wait until ACC starts
    while asm.read_shared_memory() is None:
        print("⌛ ACC not running... waiting")
        time.sleep(1)

    print("✅ ACC detected. Starting telemetry logging...\n")

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header row
        headers = [
            "timestamp",
            "lap_number",
            "track",
            "lap_distance",
            "track_position",
            "speed_kmh",
            "gas",
            "brake",
            "steer_angle",
            "gear",
            "rpm",
            "heading",
            "local_velocity_x",
            "local_velocity_y",
            "local_velocity_z",
            "g_force_x",
            "g_force_y",
            "g_force_z"
        ]
        writer.writerow(headers)

        missed_reads = 0
        max_missed = 180  # e.g. exit after ~3 seconds of missing shared memory (at 60Hz)

        while True:
            sm = asm.read_shared_memory()
            if sm is None:
                missed_reads += 1
                if missed_reads >= max_missed:
                    print("\n🛑 ACC closed or shared memory lost. Stopping logger.")
                    break
                time.sleep(1 / 60)
                continue

            missed_reads = 0  # reset counter

            phys = sm.Physics
            gfx = sm.Graphics
            static = sm.Static

            g = phys.g_force
            v = phys.local_velocity

            # Data values
            row = [
                time.time(),
                gfx.completed_lap + 1,
                static.track,
                gfx.distance_traveled,
                gfx.normalized_car_position,
                phys.speed_kmh,
                phys.gas,
                phys.brake,
                phys.steer_angle,
                phys.gear,
                phys.rpm,
                phys.heading,
                v.x, v.y, v.z,
                g.x, g.y, g.z
            ]

            # Write to CSV and print nicely
            writer.writerow(row)
            print(f"Lap {row[1]:>2} | {row[2]} | Speed: {row[5]:.1f} km/h | Throttle: {row[6]:.2f} | Brake: {row[7]:.2f} | Steer: {row[8]:.2f}")

            time.sleep(1 / 60)

if __name__ == "__main__":
    main()
