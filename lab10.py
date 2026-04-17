import asyncio
import shelve
from bleak import BleakScanner
from time import strftime, gmtime, sleep

async def scan_for_devices():
    print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Device Name: {device.name}, Address: {device.address}")
    return devices

#I'm not much of a Bluetooth guy, so the only device I picked up is a neighbor's LED controller. Hope they don't mind.
KNOWN_DEVICES = {
    "BJ_LED_M": "02:24:05:14:5B:4E",
    "JBL Tune 520BT-LE-2": "63971F11-682D-CF9F-6927-B40D1461895F"
}

async def check_for_known_devices():
    devices = await BleakScanner.discover()
    nearby_known_devices = {}

    for device in devices:
        if device.address in KNOWN_DEVICES.values():
            # Find matching name
            for name, addr in KNOWN_DEVICES.items():
                if addr == device.address:
                    print(f"{name} is nearby!")
                    nearby_known_devices[name] = addr

    return nearby_known_devices

import shelve

def log_devices(devices):
    with shelve.open( "device_log" ) as db:
        for name, address in devices.items():
            key = name + '_' + address
            formatted_time = strftime( "%Y-%m-%d %H:%M:%S", gmtime())
            if key in db:
                time_list = db[key]
                time_list.append(formatted_time)
                db[key] = time_list
            else:
                db[key] = [formatted_time]
    print( "Logged devices in the shelf database." )

async def scan():
    nearby_devices = await check_for_known_devices()
    if nearby_devices:
        log_devices( nearby_devices )
    else:
        print( "No known devices nearby." )

async def clear_logs_one_hour():
    while True:
        await asyncio.sleep(3600)
        with shelve.open("device_log") as db:
            db.clear()
        print("Cleared the device log.")

def main():
    # asyncio.run( scan_for_devices() )
    while True:
        print("Scanning...")
        asyncio.run( scan() )
        print("sleeping till next loop...")
        sleep(15)
        # This is the verifying portion
        print("Verifying log...")
        with shelve.open( "device_log" ) as db:
            for name, address in db.items():
                print( f"{name}: {address}" )

if __name__ == '__main__':
    main()
    clear_logs_one_hour() #Kind of a hackjob but I think it'll work.
