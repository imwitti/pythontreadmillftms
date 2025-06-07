import cv2
import asyncio
import queue
import time

async def play_video(video_path, speed_ratio_queue, speed_queue, distance_queue, start_time):
    cap = cv2.VideoCapture(video_path)
    last_known_speed = 0.0  # Initialize last known speed
    last_known_distance = 0.0  # Initialize last known distance

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if not speed_ratio_queue.empty():
            speed_ratio = speed_ratio_queue.get()
        if not speed_queue.empty():
            last_known_speed = speed_queue.get()  # Update last known speed
        if not distance_queue.empty():
            last_known_distance = distance_queue.get()  # Update last known distance

        # Display the last known speed as HUD (top left)
        hud_speed_text = f"{last_known_speed:.1f} km/h"
        cv2.putText(frame, hud_speed_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display the distance completed as HUD (top right)
        hud_distance_text = f"{last_known_distance:.2f} km"
        cv2.putText(frame, hud_distance_text, (frame.shape[1] - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display the elapsed time as HUD (bottom left)
        elapsed_time = time.time() - start_time
        hud_time_text = f"Time: {int(elapsed_time // 60)}:{int(elapsed_time % 60):02d}"
        cv2.putText(frame, hud_time_text, (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow('Video', frame)
        if cv2.waitKey(int(1000 / (30 * speed_ratio))) & 0xFF == ord('q'):
            break
        await asyncio.sleep(0)  # Yield control to the event loop
    cap.release()
    cv2.destroyAllWindows()
