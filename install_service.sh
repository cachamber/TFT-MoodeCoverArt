#!/bin/bash

echo -e "Install TFT-MoodeCoverArt Service. \n"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo -e "\nSetting up Python virtual environment...\n"

# Create virtual environment if it doesn't exist
if [ ! -d "tftmoodecoverart" ]; then
    python3 -m venv tftmoodecoverart
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment and install requirements
echo -e "\nInstalling Python dependencies...\n"
source tftmoodecoverart/bin/activate

if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "\nDependencies installed successfully.\n"
else
    echo "Warning: requirements.txt not found. Skipping dependency installation."
fi

deactivate

# Create service file with correct paths
echo -e "Generating service file with correct paths...\n"
cat > tft-moodecoverart.service << EOF
[Unit]
Description=TFT-MoodeCoverArt Display
Requires=mpd.socket mpd.service
After=mpd.socket mpd.service
 
[Service]
Type=simple
ExecStart=$SCRIPT_DIR/tftmoodecoverart/bin/python3 $SCRIPT_DIR/tft_moode_coverart.py
WorkingDirectory=$SCRIPT_DIR
ExecStop=$SCRIPT_DIR/clear_display.py
Restart=on-abort
 
[Install]
WantedBy=multi-user.target
EOF

echo "Service file generated."

while true
do
    read -p "Do you wish to install TFT-MoodeCoverArt as a service? " yn
                sudo chmod 644 /lib/systemd/system/tft-moodecoverart.service
                sudo systemctl daemon-reload
                sudo systemctl enable tft-moodecoverart.service
				echo -e "\nTFT-MoodeCoverArt installed as a service.\n"
                echo -e "Please reboot the Raspberry Pi.\n"
                break;;
        [Nn]* ) echo -e "Service not installed \n"; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true
do
    read -p "Do you wish to reboot now?" yn
    case $yn in
        [Yy]* ) echo -e "Rebooting \n"
                sudo reboot
                break;;
        [Nn]* ) echo -e "Not rebooting \n"
                break;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo "TFT-MoodeCoverArt install complete"
