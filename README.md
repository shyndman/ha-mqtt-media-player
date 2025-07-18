# MQTT Media Player

Easiest way to add a custom MQTT Media Player

## Installation
Easiest install is via [HACS](https://hacs.xyz/):

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bkbilly&repository=mqtt_media_player&category=integration)

Add the name of your media player, eg: `myplayer`.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mqtt_media_player)


## Options

| Variables                | Description                                              | Topic               | Payload   |
|--------------------------|----------------------------------------------------------|---------------------|-----------|
| availability_topic       | Availability topic                                       | myplayer/available  |           |
| availability             | Availability payloads                                    |                     |           |
|   payload_available      | Availability payload when available                      |                     | online    |
|   payload_not_available  | Availability payload when unavailable                    |                     | offline   |
| name                     | The name of the Media Player                             |                     | MyPlayer  |
| device                   | Device information (optional)                            |                     |           |
| state_topic              | Media Player state (off, idle, paused, stopped, playing) | myplayer/state      |           |
| title_topic              | Track Title                                              | myplayer/title      |           |
| artist_topic             | Track Artist                                             | myplayer/artist     |           |
| album_topic              | Track Album                                              | myplayer/album      |           |
| duration_topic           | Track Duration (int)                                     | myplayer/duration   |           |
| position_topic           | Track Position (int)                                     | myplayer/position   |           |
| albumart_topic           | Album Art (base64 or URL)                               | myplayer/albumart   |           |
| mediatype_topic          | Media Type (music, video)                                | myplayer/mediatype  |           |
| volume_topic             | Current system volume                                    | myplayer/volume     |           |
| volumeset_topic          | Set System volume                                        | myplayer/volumeset  |           |
| play_topic               | Play media                                               | myplayer/play       | Play      |
| pause_topic              | Pause media                                              | myplayer/pause      | Pause     |
| stop_topic               | Stop media                                               | myplayer/stop       | Stop      |
| next_topic               | Go to next track                                         | myplayer/next       | Next      |
| previous_topic           | Go to previous track                                     | myplayer/previous   | Previous  |
| playmedia_topic          | Support TTS, playing media, etc...                       | myplayer/playmedia  |           |
| seek_topic               | Seek to position                                         | myplayer/seek       |           |
| browse_media_topic       | Enable media browsing functionality                      | myplayer/browse     |           |


## Example MQTT configuration
A MQTT configuration should be sent to `homeassistant/media_player/myplayer/config`.
```json
{
  "availability_topic": "myplayer/available",
  "availability": {
    "payload_available": "ON",
    "payload_not_available": "OFF"
  },
  "name": "My Custom Player",
  "device": {
    "identifiers": ["webos_youtube_app"],
    "name": "webOS YouTube App",
    "model": "YouTube TV App",
    "manufacturer": "webOS",
    "sw_version": "0.3.8"
  },
  "state_topic": "myplayer/state",
  "title_topic": "myplayer/title",
  "artist_topic": "myplayer/artist",
  "album_topic": "myplayer/album",
  "duration_topic": "myplayer/duration",
  "position_topic": "myplayer/position",
  "volume_topic": "myplayer/volume",
  "albumart_topic": "myplayer/albumart",
  "mediatype_topic": "myplayer/mediatype",
  "volumeset_topic": "myplayer/set_volume",
  "play_topic": "myplayer/play",
  "play_payload": "play",
  "pause_topic": "myplayer/pause",
  "pause_payload": "pause",
  "stop_topic": "myplayer/stop",
  "stop_payload": "stop",
  "next_topic": "myplayer/next",
  "next_payload": "next",
  "previous_topic": "myplayer/previous",
  "previous_payload": "previous",
  "playmedia_topic": "myplayer/playmedia",
  "seek_topic": "myplayer/seek",
  "browse_media_topic": "myplayer/browse"
}
```

## Features

### Dynamic Feature Support
The integration dynamically advertises supported features based on the configured command topics:

- **PLAY** - Available when `play_topic` is configured
- **PAUSE** - Available when `pause_topic` is configured  
- **STOP** - Available when `stop_topic` is configured
- **SEEK** - Available when `seek_topic` is configured
- **VOLUME_SET/VOLUME_STEP** - Available when `volumeset_topic` is configured
- **NEXT_TRACK** - Available when `next_topic` is configured
- **PREVIOUS_TRACK** - Available when `previous_topic` is configured
- **PLAY_MEDIA** - Available when `playmedia_topic` is configured
- **BROWSE_MEDIA** - Available when `browse_media_topic` is configured

This ensures Home Assistant only shows media controls that are actually functional for your media player.

### Album Art Support
The integration supports two formats for album art via the `state_albumart_topic`:

1. **Base64 encoded images**: Send base64 encoded image data directly
2. **Image URLs**: Send HTTP/HTTPS URLs to images (e.g., `https://example.com/albumart.jpg`)

The integration automatically detects the format and handles image proxying through Home Assistant for remote access when needed.

**Example album art payloads:**
```bash
# Base64 encoded image (existing format)
mosquitto_pub -t "myplayer/albumart" -m "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

# Image URL (new format)
mosquitto_pub -t "myplayer/albumart" -m "https://example.com/album-cover.jpg"
```

### Debug Logging
Comprehensive debug logging is available throughout the integration. Set your Home Assistant logging level to `debug` for the component to see detailed information about:

- Integration setup process
- MQTT topic subscriptions  
- Configuration handling
- Album art processing (base64 vs URL)
- Image fetching and proxying

To enable debug logging, add this to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.mqtt_media_player: debug
```
```
