# treadmill_control.py
import asyncio
from bleak import BleakScanner, BleakClient

ftms_service_uuid = "00001826-0000-1000-8000-00805f9b34fb"
control_point_uuid = "00002AD9-0000-1000-8000-00805f9b34fb"
treadmill_data_uuid = "00002ACD-0000-1000-8000-00805f9b34fb"

class TreadmillControl:
    def __init__(self):
        self.client = None

    async def connect(self):
        devices = await BleakScanner.discover(return_adv=True)
        treadmill = None
        for device, adv_data in devices.values():
            if ftms_service_uuid in adv_data.service_uuids:
                treadmill = device
                break
        if treadmill:
            self.client = BleakClient(treadmill.address)
            await self.client.connect()
        else:
            raise Exception("No FTMS treadmill found.")

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

    async def request_control(self):
        await self.client.write_gatt_char(control_point_uuid, bytearray([0x00]))
        await self.wait_for_response()

    async def set_speed(self, speed_kmh):
        speed_mph = round(speed_kmh / 1.59, 2)
        speed_value = int(speed_mph * 100).to_bytes(2, byteorder='little')
        await self.client.write_gatt_char(control_point_uuid, bytearray([0x02]) + speed_value)
        print(f"Set speed to {speed_kmh:.2f} km/h ({speed_mph:.2f} mph)")
        await self.wait_for_response()

    async def set_incline(self, incline):
        incline_value = int(incline * 10).to_bytes(2, byteorder='little', signed=True)
        await self.client.write_gatt_char(control_point_uuid, bytearray([0x03]) + incline_value)
        print(f"Set incline to {incline:.1f} %")
        await self.wait_for_response()

    async def wait_for_response(self):
        def handle_response(sender, data):
            op_code = data[0]
            request_op_code = data[1]
            result_code = data[2]
            if result_code == 0x01:
                print(f"Operation {request_op_code} succeeded")
            else:
                print(f"Operation {request_op_code} failed with result code {result_code}")

        await self.client.start_notify(control_point_uuid, handle_response)
        await asyncio.sleep(1)  # Wait for the response
        await self.client.stop_notify(control_point_uuid)

    async def start_monitoring(self, callback):
        if self.client:
            await self.client.start_notify(treadmill_data_uuid, callback)

    async def stop_monitoring(self):
        if self.client:
            await self.client.stop_notify(treadmill_data_uuid)

def parse_treadmill_data(data):
    flags = data[0]
    speed = int.from_bytes(data[2:4], byteorder='little') / 100.0
    distance = int.from_bytes(data[4:7], byteorder='little') / 100.0
    incline = None
    if flags & 0x08:  # Check if Inclination and Ramp Angle Setting Present bit is set
        incline = int.from_bytes(data[7:9], byteorder='little', signed=True) / 10.0
    return speed, distance, incline
