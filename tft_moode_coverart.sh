#!/bin/bash
# TFT-MoodeCoverArt Control Script
# Provides simple start/stop functionality for the display service

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_BIN="${SCRIPT_DIR}/tftmoodecoverart/bin/python3"
MAIN_SCRIPT="${SCRIPT_DIR}/tft_moode_coverart.py"
CLEAR_SCRIPT="${SCRIPT_DIR}/clear_display.py"

# Check if virtual environment exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Virtual environment not found. Please run ./install_service.sh first."
    exit 1
fi

while getopts ":sq" opt; do
  case ${opt} in
    s ) # Start the display
      echo "Stopping any existing display process..."
      sudo pkill -f tft_moode_coverart.py
      
      echo "Clearing display..."
      sudo "$PYTHON_BIN" "$CLEAR_SCRIPT"
      
      echo "Starting TFT-MoodeCoverArt..."
      sudo "$PYTHON_BIN" "$MAIN_SCRIPT" &
      
      echo "Display started."
      ;;
    q ) # Quit/stop the display
      echo "Stopping display..."
      sudo pkill -f tft_moode_coverart.py
      
      echo "Clearing display..."
      sudo "$PYTHON_BIN" "$CLEAR_SCRIPT"
      
      echo "Display stopped."
      ;;
    \? ) echo "Usage: $0 [-s] [-q]"
         echo "  -s  Start the display"
         echo "  -q  Quit/stop the display"
      ;;
  esac
done