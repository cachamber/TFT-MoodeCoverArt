"""TFT-MoodeCoverArt Display Application

Displays album artwork and metadata from Moode Audio Player on ST7789 TFT displays.
Supports Pimoroni Pirate Audio boards and compatible 240x240 TFT screens.

Features:
- Cover art display with metadata overlay
- Smooth continuous text scrolling
- Configurable display options via config.yml
- Support for multiple audio sources (Library, Radio, Bluetooth, Airplay, Spotify)
- Optimized rendering with caching and change detection

Author: Original by rusconi, Enhanced fork by cachamber
Version: 0.0.9
License: See LICENSE file
"""

from PIL import Image, ImageDraw, ImageColor, ImageFont, ImageStat
import subprocess
import time
import musicpd
import os
import os.path
from os import path
import RPi.GPIO as GPIO
from mediafile import MediaFile
from io import BytesIO
from numpy import mean 
import st7789
from PIL import ImageFilter
import yaml
import urllib.parse

# set default config for pirate audio

__version__ = "0.1.0"

# get the path of the script
script_path = os.path.dirname(os.path.abspath( __file__ ))
# set script path as current directory - 
os.chdir(script_path)

MODE=0
OVERLAY=2
TIMEBAR=1
BLANK=0
SHADE=0
PPBUTTON=0
PAUSEBLANK=0
SCROLLSPEED=2
ROTATION=0
SPI_SPEED=100000000

confile = 'config.yml'

# Read config.yml for user config
if path.exists(confile):
 
    with open(confile) as config_file:
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        displayConf = data.get('display', {})
        OVERLAY = displayConf.get('overlay', OVERLAY)
        MODE = displayConf.get('mode', MODE)
        TIMEBAR = displayConf.get('timebar', TIMEBAR)
        BLANK = displayConf.get('blank', BLANK)
        SHADE = displayConf.get('shadow', SHADE)
        PPBUTTON = displayConf.get('ppbutton', PPBUTTON)
        PAUSEBLANK = displayConf.get('pauseblank', PAUSEBLANK)
        SCROLLSPEED = displayConf.get('scrollspeed', SCROLLSPEED)
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



# Initialize display.
disp.begin()


WIDTH = 240
HEIGHT = 240
font_s = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',20)
font_m = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',24)
font_l = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',30)


img = Image.new('RGB', (240, 240), color=(0, 0, 0, 25))

if PPBUTTON == 1:
    # reversed play and pause icons
    pause_icons = Image.open(script_path + '/images/controls-play.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
    pause_icons_dark = Image.open(script_path + '/images/controls-play-dark.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
    play_icons = Image.open(script_path + '/images/controls-pause.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
    play_icons_dark = Image.open(script_path + '/images/controls-pause-dark.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
else:
    # original play and pause icons
    play_icons = Image.open(script_path + '/images/controls-play.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
    play_icons_dark = Image.open(script_path + '/images/controls-play-dark.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
    pause_icons = Image.open(script_path + '/images/controls-pause.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
    pause_icons_dark = Image.open(script_path + '/images/controls-pause-dark.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")

vol_icons = Image.open(script_path + '/images/controls-vol.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
vol_icons_dark = Image.open(script_path + '/images/controls-vol-dark.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")

bt_back = Image.open(script_path + '/images/bta.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
ap_back = Image.open(script_path + '/images/airplay.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
jp_back = Image.open(script_path + '/images/jack.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
sp_back = Image.open(script_path + '/images/spotify.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")
sq_back = Image.open(script_path + '/images/squeeze.png').resize((240,240), resample=Image.Resampling.LANCZOS).convert("RGBA")


def isServiceActive(service):
    """Check if a systemd service is active.
    
    Polls systemctl up to 30 times with 1 second intervals to determine if the
    specified service is active. This provides a startup delay for services that
    need time to initialize.
    
    Args:
        service (str): Name of the systemd service to check (e.g., 'mpd')
    
    Returns:
        bool: True if service is active, False if not active after 30 attempts
    
    Example:
        >>> if isServiceActive('mpd'):
        ...     print("MPD is running")
    """
    waiting = True
    count = 0
    active = False

    while (waiting == True):

        process = subprocess.run(['systemctl','is-active',service], check=False, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        stat = output[:6]

        if stat == 'active':
            waiting = False
            active = True

        if count > 29:
            waiting = False

        count += 1
        time.sleep(1)

    return active


def getMoodeMetadata(filename):
    """Parse Moode Audio metadata from currentsong.txt file.
    
    Reads the Moode Audio metadata file and extracts playback information including
    artist, album, title, cover URL, and audio source type. Handles special cases
    for radio streams, Bluetooth, Airplay, Spotify, and other input sources.
    
    Args:
        filename (str): Path to the currentsong.txt metadata file
                       (typically /var/local/www/currentsong.txt)
    
    Returns:
        dict: Dictionary containing metadata with keys:
            - 'artist': Artist name
            - 'album': Album name
            - 'title': Track title
            - 'file': File path or stream URL
            - 'coverurl': URL/path to cover art
            - 'source': Audio source type ('library', 'radio', 'bluetooth',
                       'airplay', 'spotify', 'squeeze', 'input')
    
    Note:
        For radio streams with combined artist/title (format "Artist - Title"),
        the function automatically splits them into separate fields.
    """
    # Initalise dictionary
    metaDict = {}
    
    if path.exists(filename):
        # add each line fo a list removing newline
        nowplayingmeta = [line.rstrip('\n') for line in open(filename)]
        i = 0
        while i < len(nowplayingmeta):
            # traverse list converting to a dictionary
            (key, value) = nowplayingmeta[i].split('=', 1)
            metaDict[key] = value
            i += 1
        
        metaDict['coverurl'] = urllib.parse.unquote(metaDict['coverurl'])
        
        metaDict['source'] = 'library'
        if 'file' in metaDict:
            if (metaDict['file'].find('http://', 0) > -1) or (metaDict['file'].find('https://', 0) > -1):
                # set radio stream to true
                metaDict['source'] = 'radio'
                # if radio station has arist and title in one line separated by a hyphen, split into correct keys
                if metaDict['title'].find(' - ', 0) > -1:
                    (art,tit) = metaDict['title'].split(' - ', 1)
                    metaDict['artist'] = art
                    metaDict['title'] = tit
            elif metaDict['file'].find('Bluetooth Active', 0) > -1:
                metaDict['source'] = 'bluetooth'
            elif metaDict['file'].find('Airplay Active', 0) > -1:
                metaDict['source'] = 'airplay'
            elif metaDict['file'].find('Spotify Active', 0) > -1:
                metaDict['source'] = 'spotify'
            elif metaDict['file'].find('Squeezelite Active', 0) > -1:
                metaDict['source'] = 'squeeze'
            elif metaDict['file'].find('Input Active', 0) > -1:
                metaDict['source'] = 'input' 
            

    # return metadata
    return metaDict

def get_cover(metaDict):
    """Retrieve cover art image based on metadata.
    
    Searches for and returns album artwork from multiple sources in order of priority:
    1. Radio station logos (for radio streams)
    2. Source-specific backgrounds (Bluetooth, Airplay, Spotify, etc.)
    3. Embedded artwork in audio files
    4. Folder images (Cover.jpg, Folder.jpg, etc.)
    5. Default cover image as fallback
    
    Args:
        metaDict (dict): Metadata dictionary from getMoodeMetadata() containing
                        'source', 'file', and 'coverurl' keys
    
    Returns:
        PIL.Image: Cover art image object (240x240 or will be resized later)
    
    Note:
        For library files, checks for embedded art first, then searches for
        common cover image filenames in the same directory as the audio file.
        Supported cover image formats: jpg, jpeg, png, tif, tiff (case-insensitive).
    """
    cover = None
    cover = Image.open(script_path + '/images/default-cover-v6.jpg')
    covers = ['Cover.jpg', 'cover.jpg', 'Cover.jpeg', 'cover.jpeg', 'Cover.png', 'cover.png', 'Cover.tif', 'cover.tif', 'Cover.tiff', 'cover.tiff',
		'Folder.jpg', 'folder.jpg', 'Folder.jpeg', 'folder.jpeg', 'Folder.png', 'folder.png', 'Folder.tif', 'folder.tif', 'Folder.tiff', 'folder.tiff']
    if metaDict['source'] == 'radio':
        if 'coverurl' in metaDict:
            rc = '/var/local/www/' + metaDict['coverurl']
            if path.exists(rc):
                if rc != '/var/local/www/images/default-cover-v6.svg':
                    cover = Image.open(rc)

    elif metaDict['source'] == 'airplay':
        cover = ap_back
    elif metaDict['source'] == 'bluetooth':
        cover = bt_back
    elif metaDict['source'] == 'input':
        cover = jp_back
    elif metaDict['source'] == 'spotify':
        cover = sp_back
    elif metaDict['source'] == 'squeeze':
        cover = sq_back
    else:
        if 'file' in metaDict:
            if len(metaDict['file']) > 0:

                fp = '/var/lib/mpd/music/' + metaDict['file']   
                mf = MediaFile(fp)     
                if mf.art:
                    cover = Image.open(BytesIO(mf.art))
                    return cover
                else:
                    for it in covers:
                        cp = os.path.dirname(fp) + '/' + it
                        
                        if path.exists(cp):
                            cover = Image.open(cp)
                            return cover
    return cover


def main():
    """Main display loop for TFT-MoodeCoverArt.
    
    Initializes the display and runs the main event loop that:
    - Monitors MPD service status
    - Reads metadata from Moode Audio
    - Retrieves and caches cover art
    - Renders text with smooth scrolling
    - Displays playback overlays and controls
    - Manages backlight based on playback state
    
    The function implements optimizations including:
    - Cover art caching to avoid redundant resizing
    - Change detection to minimize CPU usage
    - Smooth 20fps rendering for text scrolling
    - Display blanking timeout based on config
    
    Raises:
        KeyboardInterrupt: Caught to gracefully shut down display
    
    Note:
        If MPD service is not active after 30 seconds, displays an error
        message and stops. The loop runs continuously until interrupted.
    """
    disp.set_backlight(True)
    
    filename = '/var/local/www/currentsong.txt'

    c = 0
    ss = 0
    x1 = 20.0
    x2 = 20.0
    x3 = 20.0
    title_top = 105
    volume_top = 184
    time_top = 222
    act_mpd = isServiceActive('mpd')
    SHADE = displayConf['shadow']
    
    # Cache variables for optimization
    prev_cover_path = None
    cached_cover = None
    cached_resized_cover = None
    prev_state = {}
    needs_redraw = True
    
    # Scrolling text tracking
    has_scrolling_text = False

    if act_mpd == True:
        print("mpd is active")
        while True:
            client = musicpd.MPDClient()   # create client object
            try:     
                client.connect()           # use MPD_HOST/MPD_PORT
            except:
                pass
            else:                  
                moode_meta = getMoodeMetadata(filename)
                mpd_status = client.status()
                
                # Check if anything has changed to avoid unnecessary redrawing
                current_state = {
                    'file': moode_meta.get('file', ''),
                    'state': mpd_status.get('state', ''),
                    'volume': mpd_status.get('volume', ''),
                    'elapsed': mpd_status.get('elapsed', '')
                }
                
                needs_redraw = (current_state != prev_state) or has_scrolling_text
                
                if not needs_redraw:
                    prev_state = current_state.copy()
                    time.sleep(0.05)
                    continue
                
                # Get cover with caching
                cover_path = moode_meta.get('coverurl', '') + moode_meta.get('file', '')
                if cover_path != prev_cover_path:
                    cover = get_cover(moode_meta)
                    cached_cover = cover
                    cached_resized_cover = cover.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
                    prev_cover_path = cover_path
                    # Reset text positions when track changes
                    x1 = x2 = x3 = 20.0
                    has_scrolling_text = False
                else:
                    cover = cached_cover
                
                prev_state = current_state.copy()
                
                mn = 50
                if OVERLAY == 3:
                    img.paste(cached_resized_cover.convert('RGB'))
                else:
                    img.paste(cached_resized_cover.filter(ImageFilter.GaussianBlur).convert('RGB'))
                
                # Create draw object for this frame
                draw = ImageDraw.Draw(img, 'RGBA')
                
                if 'state' in mpd_status:
                    if ((mpd_status['state'] == 'stop') and (BLANK != 0)) or ((mpd_status['state'] == 'pause') and (BLANK != 0) and (PAUSEBLANK != 0)):
                        if ss < BLANK:
                            ss = ss + 1
                        else:
                            disp.set_backlight(False)
                    else:
                        ss = 0
                        disp.set_backlight(True)
                
                
                im_stat = ImageStat.Stat(cover) 
                im_mean = im_stat.mean
                mn = mean(im_mean)
                
                #txt_col = (255-int(im_mean[0]), 255-int(im_mean[1]), 255-int(im_mean[2]))
                txt_col = (255,255,255)
                str_col = (15,15,15)
                bar_col = (255, 255, 255, 255)
                dark = False
                if mn > 175:
                    txt_col = (55,55,55)
                    str_col = (200,200,200)
                    dark=True
                    bar_col = (100,100,100,225)
                if mn < 80:
                    txt_col = (200,200,200)
                    str_col = (55,55,55)
                
                if (moode_meta['source'] == 'library') or (moode_meta['source'] == 'radio'):

                    if (OVERLAY > 0) and (OVERLAY < 3):
                        if 'state' in mpd_status:
                            if OVERLAY == 2:
                                if mpd_status['state'] != 'play':
                                    if dark is False:
                                        img.paste(pause_icons, (0,0), pause_icons)
                                    else:
                                        img.paste(pause_icons_dark, (0,0), pause_icons_dark)
                                else:
                                    if dark is False:
                                        img.paste(play_icons, (0,0), play_icons)
                                    else:
                                        img.paste(play_icons_dark, (0,0), play_icons_dark)
                            elif OVERLAY == 1:
                                if dark is False:
                                    img.paste(vol_icons, (0,0), vol_icons)
                                else:
                                    img.paste(vol_icons_dark, (0,0), vol_icons_dark)
                            
                        else:
                            img.paste(play_icons, (0,0), play_icons)
    
                        if 'volume' in mpd_status:
                            vol = int(mpd_status['volume'])
                            vol_x = int((vol/100)*(WIDTH - 33))
                            draw.rectangle((5, volume_top, WIDTH-34, volume_top+8), (255,255,255,145))
                            draw.rectangle((5, volume_top, vol_x, volume_top+8), bar_col)
                    
                    if OVERLAY < 3:    
                        if TIMEBAR == 1:
                            if 'elapsed' in  mpd_status:
                                el_time = int(float(mpd_status['elapsed']))
                                if 'duration' in mpd_status:
                                    du_time = int(float(mpd_status['duration']))
                                    dur_x = int((el_time/du_time)*(WIDTH-10))
                                    draw.rectangle((5, time_top, WIDTH-5, time_top + 12), (255,255,255,145))
                                    draw.rectangle((5, time_top, dur_x, time_top + 12), bar_col)
        
                        
                        top = 7
                        if 'artist' in moode_meta:
                            bbox = draw.textbbox((0, 0), moode_meta['artist'], font_m)
                            w1 = bbox[2] - bbox[0]
                            
                            if w1 <= WIDTH:
                                # Center text if it fits
                                x1 = (WIDTH - w1)//2
                                if SHADE != 0:
                                    draw.text((x1+SHADE, top+SHADE), moode_meta['artist'], font=font_m, fill=str_col)
                                draw.text((x1, top), moode_meta['artist'], font=font_m, fill=txt_col)
                            else:
                                # Continuous scrolling with gap
                                has_scrolling_text = True
                                x1 = x1 - (SCROLLSPEED * 0.5)
                                gap = 60  # Gap between repeated text
                                if x1 < -(w1 + gap):
                                    x1 = 0
                                
                                # Draw text twice for seamless loop
                                if SHADE != 0:
                                    draw.text((int(x1)+SHADE, top+SHADE), moode_meta['artist'], font=font_m, fill=str_col)
                                    draw.text((int(x1+w1+gap)+SHADE, top+SHADE), moode_meta['artist'], font=font_m, fill=str_col)
                                draw.text((int(x1), top), moode_meta['artist'], font=font_m, fill=txt_col)
                                draw.text((int(x1+w1+gap), top), moode_meta['artist'], font=font_m, fill=txt_col)
                        
                        top = 35
                        
                        if 'album' in moode_meta:
                            bbox = draw.textbbox((0, 0), moode_meta['album'], font_s)
                            w2 = bbox[2] - bbox[0]
                            
                            if w2 <= WIDTH:
                                # Center text if it fits
                                x2 = (WIDTH - w2)//2
                                if SHADE != 0:
                                    draw.text((x2+SHADE, top+SHADE), moode_meta['album'], font=font_s, fill=str_col)
                                draw.text((x2, top), moode_meta['album'], font=font_s, fill=txt_col)
                            else:
                                # Continuous scrolling with gap
                                has_scrolling_text = True
                                x2 = x2 - (SCROLLSPEED * 0.5)
                                gap = 60
                                if x2 < -(w2 + gap):
                                    x2 = 0
                                
                                # Draw text twice for seamless loop
                                if SHADE != 0:
                                    draw.text((int(x2)+SHADE, top+SHADE), moode_meta['album'], font=font_s, fill=str_col)
                                    draw.text((int(x2+w2+gap)+SHADE, top+SHADE), moode_meta['album'], font=font_s, fill=str_col)
                                draw.text((int(x2), top), moode_meta['album'], font=font_s, fill=txt_col)
                                draw.text((int(x2+w2+gap), top), moode_meta['album'], font=font_s, fill=txt_col)

                        
                        if 'title' in moode_meta:
                            bbox = draw.textbbox((0, 0), moode_meta['title'], font_l)
                            w3 = bbox[2] - bbox[0]
                            
                            if w3 <= WIDTH:
                                # Center text if it fits
                                x3 = (WIDTH - w3)//2
                                if SHADE != 0:
                                    draw.text((x3+SHADE, title_top+SHADE), moode_meta['title'], font=font_l, fill=str_col)
                                draw.text((x3, title_top), moode_meta['title'], font=font_l, fill=txt_col)
                            else:
                                # Continuous scrolling with gap
                                has_scrolling_text = True
                                x3 = x3 - (SCROLLSPEED * 0.5)
                                gap = 60
                                if x3 < -(w3 + gap):
                                    x3 = 0
                                
                                # Draw text twice for seamless loop
                                if SHADE != 0:
                                    draw.text((int(x3)+SHADE, title_top+SHADE), moode_meta['title'], font=font_l, fill=str_col)
                                    draw.text((int(x3+w3+gap)+SHADE, title_top+SHADE), moode_meta['title'], font=font_l, fill=str_col)
                                draw.text((int(x3), title_top), moode_meta['title'], font=font_l, fill=txt_col)
                                draw.text((int(x3+w3+gap), title_top), moode_meta['title'], font=font_l, fill=txt_col)


                else:
                    if 'file' in moode_meta:
                        txt = moode_meta['file'].replace(' ', '\n')
                        bbox = draw.multiline_textbbox((0, 0), txt, font_l, spacing=6)
                        w3 = bbox[2] - bbox[0]
                        h3 = bbox[3] - bbox[1]
                        x3 = (WIDTH - w3)//2
                        y3 = (HEIGHT - h3)//2
                        if SHADE != 0:
                            draw.text((x3+SHADE, y3+SHADE), txt, font=font_l, fill=str_col)
                        draw.text((x3, y3), txt, font=font_l, fill=txt_col, spacing=6, align="center")
            
            
            disp.display(img)

            if c == 0:
                img.save(script_path+'/dump.jpg')
                c += 1

            time.sleep(0.05)

        client.disconnect()
    else:
        draw = ImageDraw.Draw(img)
        draw.rectangle((0,0,240,240), fill=(0,0,0))
        txt = 'MPD not Active!\nEnsure MPD is running\nThen restart script'
        bbox = draw.multiline_textbbox((0, 0), txt, font=font_m, spacing=4)
        mlw = bbox[2] - bbox[0]
        draw.multiline_text(((WIDTH-mlw)//2, 20), txt, fill=(255,255,255), font=font_m, spacing=4, align="center")
        disp.display(img)
        



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        disp.reset()
        disp.set_backlight(False)
        pass
