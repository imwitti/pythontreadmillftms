import struct
from datetime import datetime

class FitEncoder:
    def __init__(self):
        self.records = []

    def write_file_header(self):
        header = struct.pack('<2BHI4s', 14, 16, 0, 0, b'.FIT')
        self.records.append(header)

    def write_session_message(self, start_time, end_time):
        start_time = int((start_time - datetime(1989, 12, 31)).total_seconds())
        end_time = int((end_time - datetime(1989, 12, 31)).total_seconds())
        session_message = struct.pack('<4s2I', b'SESS', start_time, end_time)
        self.records.append(session_message)

    def write_lap_message(self, start_time, end_time):
        start_time = int((start_time - datetime(1989, 12, 31)).total_seconds())
        end_time = int((end_time - datetime(1989, 12, 31)).total_seconds())
        lap_message = struct.pack('<4s2I', b'LAP', start_time, end_time)
        self.records.append(lap_message)

    def write_record_message(self, timestamp, speed, distance, incline):
        timestamp = int((timestamp - datetime(1989, 12, 31)).total_seconds())
        record_message = struct.pack('<4sI3f', b'REC', timestamp, speed, distance, incline)
        self.records.append(record_message)

    def write_file(self, filename):
        with open(filename, 'wb') as f:
            for record in self.records:
                f.write(record)
