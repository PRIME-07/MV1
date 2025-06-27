# inspect_acc_shared_memory.py

from pyaccsharedmemory import accSharedMemory
import time

def inspect_acc_data():
    print("🔍 Reading ACC Shared Memory...")
    asm = accSharedMemory()

    while True:
        sm = asm.read_shared_memory()
        if sm is None:
            print("⚠️ ACC not running or shared memory not available. Retrying...")
            time.sleep(1)
            continue

        print("\n====================")
        print("🧠 GraphicsMap Fields:")
        print("====================")
        print(dir(sm.Graphics))

        print("\n====================")
        print("🏎️ PhysicsMap Fields:")
        print("====================")
        print(dir(sm.Physics))

        print("\n====================")
        print("📃 StaticMap Fields:")
        print("====================")
        print(dir(sm.Static))

        break  # exit after one good read

if __name__ == "__main__":
    inspect_acc_data()
