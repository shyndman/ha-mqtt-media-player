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
| availability             | Availability                                             |                     |           |
|   topic                  | Availability topic                                       | myplayer/available  |           |
|   payload_available      | Availability payload when available                      |                     | online    |
|   payload_unavailable    | Availability payload when unavailable                    |                     | offline   |
| name                     | The name of the Media Player                             |                     | MyPlayer  |
| state_state_topic        | Media Player state (off, idle, paused, stopped, playing) | myplayer/state      |           |
| state_title_topic        | Track Title                                              | myplayer/title      |           |
| state_artist_topic       | Track Artist                                             | myplayer/artist     |           |
| state_album_topic        | Track Album                                              | myplayer/album      |           |
| state_duration_topic     | Track Duration (int)                                     | myplayer/duration   |           |
| state_position_topic     | Track Position (int)                                     | myplayer/position   |           |
| state_albumart_topic     | Album Art (base64 or URL)                               | myplayer/albumart   |           |
| state_mediatype_topic    | Media Type (music, video)                                | myplayer/mediatype  |           |
| state_volume_topic       | Current system volume                                    | myplayer/volume     |           |
| command_volume_topic     | Set System volume                                        | myplayer/volumeset  |           |
| command_play_topic       | Play media                                               | myplayer/play       | Play      |
| command_pause_topic      | Pause media                                              | myplayer/pause      | Pause     |
| *command_playpause_topic | PlayPause media                                          | myplayer/playpause  | PlayPause |
| command_next_topic       | Go to next track                                         | myplayer/next       | Next      |
| command_previous_topic   | Go to previous track                                     | myplayer/previous   | Previous  |
| command_playmedia_topic  | Support TTS, playing media, etc...                       | myplayer/playmedia  |           |


## Example MQTT configuration
A MQTT configuration should be sent to `homeassistant/media_player/myplayer/config`.
```json
{
  "availability": {
    "topic": "myplayer/available",
    "payload_available": "ON",
    "payload_not_available": "OFF"
  },
  "name": "My Custom Player",
  "state_state_topic": "myplayer/state",
  "state_title_topic": "myplayer/title",
  "state_artist_topic": "myplayer/artist",
  "state_album_topic": "myplayer/album",
  "state_duration_topic": "myplayer/duration",
  "state_position_topic": "myplayer/position",
  "state_volume_topic": "myplayer/volume",
  "state_albumart_topic": "myplayer/albumart",
  "state_mediatype_topic": "myplayer/mediatype",
  "command_volume_topic": "myplayer/set_volume",
  "command_play_topic": "myplayer/play",
  "command_play_payload": "play",
  "command_pause_topic": "myplayer/pause",
  "command_pause_payload": "pause",
  "command_playpause_topic": "myplayer/playpause",
  "command_playpause_payload": "playpause",
  "command_next_topic": "myplayer/next",
  "command_next_payload": "next",
  "command_previous_topic": "myplayer/previous",
  "command_previous_payload": "previous",
  "command_playmedia_topic": "myplayer/playmedia"
}
```

## Features

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
