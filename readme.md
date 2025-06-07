🏃‍♂️ PillarsApp: Interactive Treadmill Training Companion
PillarsApp is a Python-based treadmill training assistant that synchronizes workout routines with video playback, music, and real-time treadmill control via Bluetooth FTMS. Designed for immersive and structured indoor running sessions, it supports custom routines, ZWO workout files, and virtual competitors.

🚀 Features
🎥 Video Playback with HUD: Displays speed, distance, and elapsed time overlaid on training videos.
🎵 Music Integration: Plays random music tracks from a folder during workouts.
🏋️ Routine Execution: Supports JSON and ZWO-based workout routines with adjustable speed.
📡 Bluetooth FTMS Control: Connects to compatible treadmills to control speed and incline.
👻 Virtual Competitors: Simulates ghost runners with different pacing strategies.
📁 Workout Export: Generates .tcx files for post-workout analysis.
📦 Installation
Make sure you have Python 3.8+ installed. Then install the required packages:


📂 Project Structure
PillarsApp/
├── RoutineSender.py           # Main entry point
├── RunRoutine.py              # Executes routines and manages treadmill
├── treadmill_control.py       # Bluetooth FTMS treadmill interface
├── video_playback.py          # HUD-enhanced video playback
├── zwo_parser.py              # Parses ZWO workout files
├── virtual_competitors.py     # Generates ghost runners
├── routines.json              # Sample JSON routines
├── user_config.json           # User preferences (e.g., 5K PB)
├── music/                     # Folder for MP3 files
├── videos/                    # Folder for MP4 training videos
├── routines/                  # Folder for ZWO workout files
└── TCX/                       # Output folder for workout exports
🧠 How It Works
User selects a routine and video.
Initial speed is calculated based on user’s 5K time.
Routine is adjusted and sent to the treadmill.
Video and music play while treadmill speed and incline are controlled.
Workout data is logged and exported as a .tcx file.
🛠️ Configuration
Edit user_config.json to set your personal best 5K time:


🧪 Testing Mode
The treadmill interface supports a simulated mode for development without hardware. Set testing=True in TreadmillControl.