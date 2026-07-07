import random
import requests
import json
import time
import threading

DEVICE_MODELS = {
    "Samsung": ["SM-G991B", "SM-G998B", "SM-A536B", "SM-F926B"],
    "Xiaomi": ["23049PCD8G", "Xiaomi 14", "Xiaomi 15", "Poco X6 Pro"],
    "OnePlus": ["OnePlus 13", "OnePlus 12", "OnePlus 11"],
    "Google": ["Pixel 8 Pro", "Pixel 7a", "Pixel 6"]
}

MCC_CODES = {
    "DE": {"Telekom": 26201, "Vodafone": 26202, "O2": 26203}
}

def generate_device_id():
    return str(random.randint(1000000000000000000, 9999999999999999999))

def generate_odin():
    return hex(random.randint(0, 0xFFFFFFFF))[2:].upper().zfill(8)

def generate_device():
    brand = random.choice(list(DEVICE_MODELS.keys()))
    model = random.choice(DEVICE_MODELS[brand])
    mcc = random.choice(list(MCC_CODES["DE"].values()))
    return {
        "id": generate_device_id(),
        "model": model,
        "mcc": mcc,
        "odin": generate_odin(),
        "android": random.choice(["A12", "A13", "A14", "A15"])
    }

def bulk_report(target_user, device_count=10):
    devices = [generate_device() for _ in range(device_count)]
    
    with open("devices.txt", "w") as f:
        f.write("device_id | model | android | mcc | odin\n")
        f.write("-" * 60 + "\n")
        for d in devices:
            f.write(f"{d['id']} | {d['model']} | {d['android']} | {d['mcc']} | {d['odin']}\n")
    
    print(f"[+] Generated {len(devices)} devices")
    print("[+] Saved to devices.txt")
    
    for i, d in enumerate(devices[:10], 1):
        print(f"[{i:02d}] id:{d['id']} | model:{d['model']} | {d['android']} | mcc:{d['mcc']} | odin:{d['odin']}")
    
    return devices

if __name__ == "__main__":
    bulk_report("example_user", 10)
    print("\n[Program finished]")
