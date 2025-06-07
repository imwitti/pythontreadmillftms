import asyncio
from bleak import BleakScanner

FTMS_SERVICE_UUID = "00001826-0000-1000-8000-00805f9b34fb"  # Standard FTMS service UUID

async def main():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover(timeout=10)

    found = False
    for d in devices:
        if d.metadata and 'uuids' in d.metadata:
            if FTMS_SERVICE_UUID.lower() in [u.lower() for u in d.metadata['uuids']]:
                print(f"✅ FTMS device found: {d.name} ({d.address})")
                found = True
            else:
                print(f"🔎 Not FTMS: {d.name} ({d.address})")
        else:
            print(f"🔍 Unknown/No UUIDs: {d.name} ({d.address})")

    if not found:
        print("⚠️ No FTMS devices found.")

asyncio.run(main())
