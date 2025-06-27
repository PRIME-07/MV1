import time
import csv
import os
import mss
import mss.tools
from PIL import Image
from pyaccsharedmemory import accSharedMemory
import pygetwindow as gw
import winsound

def get_acc_window_bbox():
    windows = gw.getWindowsWithTitle("AC2")
    for win in windows:
        if win.visible and win.width > 0 and win.height > 0:
            return {
                "left": win.left,
                "top": win.top,
                "width": win.width,
                "height": win.height
            }
    return None

def countdown_with_beep():
    print("⏳ Starting telemetry + screenshot logging in...")
    for i in range(10, 0, -1):
        print(f"   {i}...")
        if i <= 3:
            winsound.Beep(1000, 500)
        time.sleep(1)
    print("🎬 GO!\n")

def main():
    asm = accSharedMemory()
    sct = mss.mss()

    print("🔍 Waiting for ACC to start...")
    while asm.read_shared_memory() is None:
        time.sleep(1)

    acc_bbox = None
    while acc_bbox is None:
        acc_bbox = get_acc_window_bbox()
        if acc_bbox is None:
            print("📛 ACC window not found. Make sure it's running and visible.")
            time.sleep(2)

    countdown_with_beep()

    os.makedirs("data", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)

    session_time = int(time.time())
    csv_filename = f"data/telemetry_session_{session_time}.csv"

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "lap_number", "track", "lap_distance", "track_position",
            "speed_kmh", "gas", "brake", "steer_angle", "gear", "rpm", "heading",
            "local_velocity_x", "local_velocity_y", "local_velocity_z",
            "g_force_x", "g_force_y", "g_force_z",
            "screenshot_path"
        ])

        print(f"📁 Logging to {csv_filename}")
        print(f"🖼️ Capturing from: {acc_bbox}")

        missed_reads = 0
        frame_count = 0
        frame_interval = 1 / 30  # 30 FPS

        while True:
            start_time = time.time()
            sm = asm.read_shared_memory()
            if sm is None:
                missed_reads += 1
                if missed_reads >= 90:
                    print("🛑 Lost connection to ACC. Exiting...")
                    break
                time.sleep(frame_interval)
                continue

            missed_reads = 0
            phys = sm.Physics
            gfx = sm.Graphics
            static = sm.Static

            g = phys.g_force
            v = phys.local_velocity

            timestamp = time.time()
            lap_number = gfx.completed_lap + 1
            track_name = static.track
            lap_distance = gfx.distance_traveled
            track_position = gfx.normalized_car_position

            screenshot_name = f"{session_time}_{frame_count:06d}.jpg"
            screenshot_path = os.path.join("screenshots", screenshot_name)

            try:
                img = sct.grab(acc_bbox)
                Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX").save(screenshot_path)
            except Exception as e:
                print(f"⚠️ Screenshot failed at frame {frame_count}: {e}")
                screenshot_path = ""

            writer.writerow([
                timestamp,
                lap_number,
                track_name,
                lap_distance,
                track_position,
                phys.speed_kmh,
                phys.gas,
                phys.brake,
                phys.steer_angle,
                phys.gear,
                phys.rpm,
                phys.heading,
                v.x, v.y, v.z,
                g.x, g.y, g.z,
                screenshot_path
            ])

            print(f"[Lap {lap_number}] Speed: {phys.speed_kmh:.1f} km/h | Frame {frame_count}")
            frame_count += 1

            elapsed = time.time() - start_time
            sleep_duration = max(0, frame_interval - elapsed)
            time.sleep(sleep_duration)

if __name__ == "__main__":
    main()
