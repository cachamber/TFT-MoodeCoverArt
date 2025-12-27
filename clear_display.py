"""Clear Display Utility for TFT-MoodeCoverArt

Simple utility script to clear the ST7789 TFT display and turn off the backlight.
Used when stopping the main display service or for manual display clearing.

This script:
1. Reads display configuration from config.yml
2. Initializes the ST7789 display with proper settings
3. Draws a black screen
4. Turns off the backlight

Usage:
    python3 clear_display.py
    
Or as part of systemd service shutdown:
    ExecStop=/path/to/clear_display.py

Author: Original by rusconi, Enhanced fork by cachamber
"""

import st7789
from PIL import Image, ImageDraw
from os import path
import yaml

# set default config for pirate audio

MODE=0
ROTATION=270
SPI_SPEED=100000000

OVERLAY=2

confile = 'config.yml'

# Read conf.json for user config
if path.exists(confile):
 
    with open(confile) as config_file:
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        displayConf = data.get('display', {})
        OVERLAY = displayConf.get('overlay', OVERLAY)
        MODE = displayConf.get('mode', MODE)
        ROTATION = displayConf.get('rotation', ROTATION)
        SPI_SPEED = displayConf.get('spi_speed_hz', SPI_SPEED)


# Standard SPI connections for ST7789
# Create ST7789 LCD display class.
if MODE == 3:    
    disp = st7789.ST7789(
        port=0,
        cs=st7789.BG_SPI_CS_FRONT,  # GPIO 8, Physical pin 24
        dc=9,
        rst=22,
        backlight=13,
        rotation=ROTATION,
        spi_speed_hz=SPI_SPEED
    )   
else:   
    disp = st7789.ST7789(
        port=0,
        cs=st7789.BG_SPI_CS_FRONT,  # GPIO 8, Physical pin 24 
        dc=9,
        backlight=13,
        rotation=ROTATION,
        spi_speed_hz=SPI_SPEED
    )


disp.begin()
img = Image.new('RGB', (240, 240), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, 240, 240), (0, 0, 0))
disp.display(img)

disp.set_backlight(False)
