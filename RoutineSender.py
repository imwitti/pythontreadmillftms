# Set correct event loop policy for Bleak on Windows BEFORE any imports
import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json
import os
import random
import pygame
from RunRoutine import exercise_routine
from zwo_parser import load_all_zwo_routines

def load_routines(file_path):
    try:
        with open(file_path, 'r') as file:
            routines = json.load(file)
        print("Routines loaded successfully.")
        return routines
    except Exception as e:
        print(f"Error loading routines: {e}")
        return {}

def adjust_routine(initial_speed, routine):
    return [(duration, initial_speed + speed_increment) for duration, speed_increment in routine]

async def send_routines(routine, initial_speed, video_path, music_folder):
    adjusted_routine = adjust_routine(initial_speed, routine)
    print(f"Starting routine with initial speed: {initial_speed}")
    play_music(music_folder)
    await exercise_routine(initial_speed, adjusted_routine, video_path)
    print(f"Completed routine with initial speed: {initial_speed}")

def load_user_config(config_path='user_config.json'):
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading user config: {e}")
        return {}

def list_videos(video_folder):
    videos = []
    for file in os.listdir(video_folder):
        if file.lower().endswith('.mp4'):
            name, speed, distance = parse_video_title(file)
            videos.append((file, name, float(speed), float(distance)))
    return videos

def parse_video_title(title):
    base_name = os.path.splitext(title)[0]
    parts = base_name.split('_')
    race_name = parts[0].lower()
    video_speed = parts[1]
    distance = parts[2]
    return race_name, video_speed, distance

def display_videos(videos):
    print("Available videos:")
    for i, (file, name, speed, distance) in enumerate(videos, start=1):
        print(f"{i}. {name.capitalize()} - Speed: {speed} km/h, Distance: {distance} km")

def display_routines(routines):
    print("Available routines:")
    for i, name in enumerate(routines.keys(), start=1):
        print(f"{i}. {name}")

def play_music(music_folder):
    pygame.mixer.init()
    music_files = [file for file in os.listdir(music_folder) if file.lower().endswith('.mp3')]
    if music_files:
        selected_music = random.choice(music_files)
        pygame.mixer.music.load(os.path.join(music_folder, selected_music))
        pygame.mixer.music.play()
        print(f"Playing music: {selected_music}")
    else:
        print("No music files found in the folder.")

if __name__ == "__main__":
    # Load user config and calculate initial speed for ZWO routines
    user_config = load_user_config()
    pb_minutes = user_config.get("best_5k_time_minutes", 25.0)
    zwo_initial_speed = (5 * 60) / pb_minutes
    print(f"Using initial speed for ZWO routines based on 5K PB: {zwo_initial_speed:.2f} km/h")

    # Load routines
    json_routines = load_routines('routines.json')
    zwo_routines = load_all_zwo_routines('routines', zwo_initial_speed)

    # Merge routines
    routines = {**json_routines, **zwo_routines}

    display_routines(routines)
    routine_selection = int(input("Enter the number of the routine you want to run: "))
    selected_routine_name = list(routines.keys())[routine_selection - 1]

    video_folder = 'videos'
    videos = list_videos(video_folder)
    display_videos(videos)
    video_selection = int(input("Enter the number of the video you want to use: "))
    selected_video = videos[video_selection - 1]
    video_path = os.path.join(video_folder, selected_video[0])

    music_folder = 'music'
    if selected_routine_name in zwo_routines:
        initial_speed = zwo_initial_speed
    else:
        initial_speed = float(input("Enter the initial speed for this routine: "))

    if selected_routine_name in routines:
        selected_routine = routines[selected_routine_name]
        asyncio.run(send_routines(selected_routine, initial_speed, video_path, music_folder))
    else:
        print("Invalid routine name.")
