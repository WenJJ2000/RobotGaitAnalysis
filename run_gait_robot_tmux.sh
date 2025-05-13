#!/bin/bash

SESSION_NAME="robotSession"

# Kill any existing session
tmux kill-session -t $SESSION_NAME 2>/dev/null

# Start new session and run test_cam.py in first window
tmux new-session -d -s $SESSION_NAME \
    "source /home/jj/RobotGaitAnalysis/venv/bin/activate && echo 'Running test_cam.py' && python3 /home/jj/RobotGaitAnalysis/main.py || read"

# Create a second window and run camera_servo.py
tmux new-window -t $SESSION_NAME:1 -n 'servo' \
    "source /home/jj/RobotGaitAnalysis/env/bin/activate && echo 'Running camera_servo.py' && python3 /home/jj/RobotGaitAnalysis/arducam/camera_servo.py || read"

# Attach to session
tmux attach-session -t $SESSION_NAME
