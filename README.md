# TFT-MoodeCoverArt

Cover art display for Moode Audio on Raspberry Pi with ST7789 TFT displays.

Based on the look of the pirate audio plugin for mopidy, this project displays album artwork and metadata from your Moode Audio player on a small TFT screen.

![Sample Image](/pics/display.jpg)

## Features

### Display
- Cover art display for library tracks and radio stations
- Embedded album art with fallback to folder images (Cover.jpg, Folder.jpg, etc.)
- Radio station logos from Moode
- Configurable overlays with time bar, volume bar, and playback controls
- Auto-adjusting text colors for light and dark artwork
- Smooth continuous marquee text scrolling for long titles
- Support for multiple input sources: Library, Radio, Bluetooth, Airplay, Spotify, Squeezelite

### Configuration Options
All settings are configurable via `config.yml`:
- Display overlays (full, volume only, or artwork only)
- Time bar display
- Screen blanking timeout
- Pause screen blanking
- Text shadow effects
- Display rotation (0, 90, 180, 270 degrees)
- Text scroll speed
- SPI bus speed
- Play/pause button display preference

### Technical Features
- Optimized rendering with cover art caching
- Change detection to minimize CPU usage
- Smooth 20fps scrolling for long text
- Virtual environment support for isolated dependencies
- Systemd service integration for auto-start
- Safe configuration defaults with graceful fallbacks

## Requirements

- Raspberry Pi with Moode Audio installed
- Pimoroni Pirate Audio board or compatible ST7789 240x240 TFT display
- Python 3.7 or higher
- SPI enabled on Raspberry Pi

## Installation

### 1. Enable SPI

See [Configuring SPI](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-spi)

### 2. Clone the Repository

```bash
cd /home/pi
git clone https://github.com/cachamber/TFT-MoodeCoverArt.git
cd TFT-MoodeCoverArt
```

### 3. Run Installation Script

The installation script will:
- Create a Python virtual environment
- Install all required dependencies
- Generate a systemd service file
- Optionally install and enable the service

```bash
./install_service.sh
```

Follow the prompts to install as a service and reboot.

### 4. Manual Installation (Alternative)

If you prefer manual installation:

```bash
# Create virtual environment
python3 -m venv tftmoodecoverart

# Activate virtual environment
source tftmoodecoverart/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test the script
python3 tft_moode_coverart.py
```

Press Ctrl+C to quit.

## Configuration

Edit `config.yml` to customize your display:

```yaml
display:
  overlay: 2           # 0=no overlay, 1=volume only, 2=full overlay, 3=artwork only
  timebar: 1           # 0=hidden, 1=show progress bar
  mode: 0              # 0=pirate audio with cs pin, 3=boards without cs pin
  rotation: 270        # Display rotation: 0, 90, 180, or 270 degrees
  blank: 60            # Backlight timeout in seconds (0=never)
  pauseblank: 0        # Blank on pause: 0=stay on, 1=blank
  shadow: 3            # Text shadow offset in pixels (0=no shadow)
  ppbutton: 1          # Play/pause button display preference
  scrollspeed: 2       # Text scroll speed (1=slow, 2=medium, 3+=fast)
  spi_speed_hz: 100000000  # SPI bus speed (4-100 MHz)
```

## Usage

### Manual Start
```bash
cd /home/pi/TFT-MoodeCoverArt
source tftmoodecoverart/bin/activate
python3 tft_moode_coverart.py
```

### Service Control
If installed as a service:
```bash
# Start
sudo systemctl start tft-moodecoverart

# Stop
sudo systemctl stop tft-moodecoverart

# Status
sudo systemctl status tft-moodecoverart

# Restart after config changes
sudo systemctl restart tft-moodecoverart
```

### Remove Service
```bash
cd /home/pi/TFT-MoodeCoverArt
./remove_service.sh
```

## Hardware Compatibility

### Tested Boards
- Pimoroni Pirate Audio boards (all variants)
- Generic ST7789 240x240 displays

### Audio Configuration
If your Pirate Audio board doesn't output audio:
- In Moode Audio Config, select "Pimoroni pHAT DAC" or "HiFiBerry DAC"
- See the [Pirate Audio setup guide](https://github.com/pimoroni/pirate-audio) for GPIO pin 25 configuration

## Troubleshooting

### Display Not Working
- Verify SPI is enabled: `ls /dev/spi*`
- Check config.yml settings for your board type
- Try lowering `spi_speed_hz` to 80000000 or 60000000

### No Metadata
- Ensure "Metadata file" is enabled in Moode System Configuration
- Check that `/var/local/www/currentsong.txt` exists and updates

### Service Won't Start
- Check service status: `sudo systemctl status tft-moodecoverart`
- View logs: `sudo journalctl -u tft-moodecoverart -f`
- Ensure MPD is running: `systemctl status mpd`

## Limitations

- Metadata display only works for Radio Stations and Library playback
- For Airplay, Spotify, Bluetooth, Squeezelite, and DAC Input, only source-specific backgrounds are shown
- No online artwork search
- Overlay colors may be difficult to read with certain artwork

## Dependencies

See `requirements.txt` for full list:
- pillow (image processing)
- python-musicpd (MPD client)
- RPi.GPIO (GPIO control)
- st7789 (display driver)
- PyYAML (config parsing)
- numpy (calculations)
- mediafile (audio metadata)

## License

See LICENSE file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Contributing

This is a community-maintained fork. Contributions welcome!