import asyncio
from treadmill_control import TreadmillControl, parse_treadmill_data
from video_playback import play_video
import queue
import time
from datetime import datetime
import xml.etree.ElementTree as ET

async def exercise_routine(initial_speed, routine, video_path):
    treadmill = TreadmillControl()  # Set testing=True here for test mode
    await treadmill.connect()
    await treadmill.request_control()
    await asyncio.sleep(10)
    await treadmill.set_incline(1.0)

    speed_ratio_queue = queue.Queue()
    speed_ratio_queue.put(1.0)
    speed_queue = queue.Queue()
    speed_queue.put(initial_speed)
    distance_queue = queue.Queue()
    distance_queue.put(0.0)

    start_time = time.time()
    workout_data = []

    def callback(sender, data):
        speed, distance, incline = parse_treadmill_data(data)
        print(f"Speed: {speed:.2f} km/h, Distance: {distance:.2f} km, Incline: {incline:.2f} %")
        speed_ratio = speed / initial_speed if initial_speed > 0 else 1.0
        speed_ratio_queue.put(speed_ratio)
        speed_queue.put(speed)
        distance_queue.put(distance)

        workout_data.append({
            "timestamp": datetime.utcnow(),
            "speed": speed,
            "distance": distance,
            "incline": incline
        })

    # Start monitoring treadmill data first
    await treadmill.start_monitoring(callback)

    # THEN start video playback (after treadmill is ready)
    video_task = asyncio.create_task(
        play_video(video_path, speed_ratio_queue, speed_queue, distance_queue, start_time)
    )

    for duration, speed_increment in routine:
        await treadmill.set_speed(speed_increment)
        await asyncio.sleep(duration * 60)

    await treadmill.stop_monitoring()
    await treadmill.disconnect()
    await video_task

    generate_tcx_file(workout_data)

def generate_tcx_file(workout_data):
    import xml.etree.ElementTree as ET
    import os

    root = ET.Element("TrainingCenterDatabase", xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
    activities = ET.SubElement(root, "Activities")
    activity = ET.SubElement(activities, "Activity", Sport="Running")
    ET.SubElement(activity, "Id").text = workout_data[0]["timestamp"].isoformat()

    lap = ET.SubElement(activity, "Lap", StartTime=workout_data[0]["timestamp"].isoformat())
    ET.SubElement(lap, "TotalTimeSeconds").text = str(
        (workout_data[-1]["timestamp"] - workout_data[0]["timestamp"]).total_seconds()
    )
    ET.SubElement(lap, "DistanceMeters").text = str(workout_data[-1]["distance"] * 1000)
    ET.SubElement(lap, "Calories").text = "0"
    ET.SubElement(lap, "Intensity").text = "Active"
    ET.SubElement(lap, "TriggerMethod").text = "Manual"

    track = ET.SubElement(lap, "Track")
    for data in workout_data:
        trackpoint = ET.SubElement(track, "Trackpoint")
        ET.SubElement(trackpoint, "Time").text = data["timestamp"].isoformat()
        ET.SubElement(trackpoint, "DistanceMeters").text = str(data["distance"] * 1000)
        extensions = ET.SubElement(trackpoint, "Extensions")
        tpx = ET.SubElement(extensions, "TPX", xmlns="http://www.garmin.com/xmlschemas/ActivityExtension/v2")
        ET.SubElement(tpx, "Speed").text = str(data["speed"] / 3.6)

    os.makedirs("TCX", exist_ok=True)
    filename = f"TCX/workout_{workout_data[0]['timestamp'].strftime('%Y-%m-%d')}.tcx"
    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"Workout data saved to {filename}")

if __name__ == "__main__":
    initial_speed = 8.0
    routine = [
        (5, 8.0),
        (5, 8.5),
        (4, 9.0),
        (4, 9.5),
        (3, 10.0),
        (3, 10.5),
        (2, 11.0),
        (2, 11.5),
        (1, 12.0),
        (1, 12.5)
    ]
    video_path = 'path_to_your_video.mp4'
    asyncio.run(exercise_routine(initial_speed, routine, video_path))
