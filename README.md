# MQTT Media Player v2.0

**⚠️ Breaking Changes in v2.0** - This version implements the [`ha-mqtt-discoverable`](https://github.com/shyndman/ha-mqtt-discoverable) MediaPlayer specification with automatic feature detection. See [Migration Guide](docs/migration-guide.md) for upgrade instructions.

A Home Assistant custom integration that provides MQTT-based media player entities with full discovery support and comprehensive feature detection.

## Features

- **🔍 MQTT Auto-Discovery** - Automatically discovers spec-compliant devices
- **🎛️ Comprehensive Controls** - Play, pause, stop, seek, volume, mute, shuffle, repeat
- **📱 Advanced Features** - Source selection, sound modes, turn on/off, playlist management
- **🎵 Rich Metadata** - Title, artist, album, duration, position, album art, episode info
- **🔗 Multi-room Support** - Group member tracking for multi-room audio systems
- **⚡ Dynamic Features** - Only shows controls supported by your device
- **📺 Multi-media Support** - Music, video, podcasts, TV shows with appropriate metadata

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=shyndman&repository=ha-mqtt-media-player&category=integration)

### Manual Installation

1. Copy the `custom_components/mqtt_media_player` directory to your Home Assistant `custom_components` folder
2. Restart Home Assistant
3. Add the integration via the UI

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mqtt_media_player)

## Quick Start

### Option 1: MQTT Discovery (Recommended)

For devices implementing the [`ha-mqtt-discoverable`](https://github.com/shyndman/ha-mqtt-discoverable) MediaPlayer specification, discovery is automatic. Just publish your configuration:

```bash
mosquitto_pub -t "homeassistant/media_player/my_player/config" -m '{
  "name": "My Music Player",
  "unique_id": "my_player_001",
  "state_topic": "myplayer/state",
  "media_title_topic": "myplayer/title",
  "media_artist_topic": "myplayer/artist",
  "volume_level_topic": "myplayer/volume",
  "play_topic": "myplayer/play",
  "pause_topic": "myplayer/pause",
  "volume_set_topic": "myplayer/volume_set"
}'
```

The device will automatically appear in Home Assistant with play, pause, and volume controls enabled.

### Option 2: Manual Configuration

Add the integration via Home Assistant UI and enter your device name. The integration will attempt to fetch the configuration from MQTT.

## Device Implementation

### Using ha-mqtt-discoverable Library

The easiest way to create compatible devices is using the [`ha-mqtt-discoverable`](https://github.com/shyndman/ha-mqtt-discoverable) Python library:

```python
from ha_mqtt_discoverable import Settings, DeviceInfo  
from ha_mqtt_discoverable.media_player import MediaPlayer, MediaPlayerInfo

# Configure your media player
player_info = MediaPlayerInfo(
    name="My Player",
    device=DeviceInfo(name="My Device", identifiers="my_device"),
)

settings = Settings(mqtt=mqtt_settings, entity=player_info)
player = MediaPlayer(settings, command_callbacks)

# Update state
player.set_state("playing")
player.set_title("Current Song")
player.set_volume(0.75)
```

### Manual Implementation

If implementing your own device, publish configuration to:
```
homeassistant/media_player/{device_name}/config
```

## Configuration Reference

### Basic Media Player

```json
{
  "name": "Living Room Speaker",
  "unique_id": "living_room_001", 
  "state_topic": "speaker/state",
  "media_title_topic": "speaker/title",
  "media_artist_topic": "speaker/artist",
  "volume_level_topic": "speaker/volume",
  "play_topic": "speaker/play",
  "pause_topic": "speaker/pause",
  "stop_topic": "speaker/stop",
  "volume_set_topic": "speaker/volume_set"
}
```

### Advanced Media Player

```json
{
  "name": "Advanced Player",
  "unique_id": "advanced_001",
  "device": {
    "identifiers": ["advanced_player"],
    "manufacturer": "Example Corp",
    "model": "Player Pro",
    "sw_version": "2.1.0"
  },
  "state_topic": "player/state",
  "media_title_topic": "player/title", 
  "media_artist_topic": "player/artist",
  "media_album_name_topic": "player/album",
  "media_duration_topic": "player/duration",
  "media_position_topic": "player/position",
  "volume_level_topic": "player/volume",
  "media_image_url_topic": "player/albumart",
  "is_volume_muted_topic": "player/muted",
  "shuffle_topic": "player/shuffle",
  "repeat_topic": "player/repeat", 
  "source_topic": "player/source",
  "sound_mode_topic": "player/sound_mode",
  "play_topic": "player/play",
  "pause_topic": "player/pause",
  "stop_topic": "player/stop",
  "next_topic": "player/next",
  "previous_topic": "player/previous",
  "volume_set_topic": "player/volume_set",
  "mute_topic": "player/mute",
  "shuffle_set_topic": "player/shuffle_set",
  "repeat_set_topic": "player/repeat_set",
  "seek_topic": "player/seek",
  "select_source_topic": "player/select_source",
  "select_sound_mode_topic": "player/select_sound_mode"
}
```

## Topic Reference

### State Topics (Published by Device)

| Topic | Description | Data Type | Example |
|-------|-------------|-----------|---------|
| `state_topic` | Player state | string | `playing`, `paused`, `stopped`, `idle`, `off` |
| `media_title_topic` | Current track title | string | `"Bohemian Rhapsody"` |
| `media_artist_topic` | Current artist | string | `"Queen"` |
| `media_album_name_topic` | Current album | string | `"A Night at the Opera"` |
| `media_duration_topic` | Media duration (seconds) | integer | `355` |
| `media_position_topic` | Current position (seconds) | integer | `120` |
| `volume_level_topic` | Volume level (0.0-1.0) | float | `0.75` |
| `media_image_url_topic` | Album art URL or base64 | string | `"https://example.com/art.jpg"` |
| `is_volume_muted_topic` | Mute state | boolean | `true` / `false` |
| `shuffle_topic` | Shuffle state | boolean | `true` / `false` |
| `repeat_topic` | Repeat mode | string | `off`, `all`, `one` |
| `source_topic` | Current input source | string | `"Spotify"` |
| `sound_mode_topic` | Current sound mode | string | `"Music"` |

### Command Topics (Subscribed by Device)

| Topic | Description | Payload |
|-------|-------------|---------|
| `play_topic` | Play command | Any string |
| `pause_topic` | Pause command | Any string |  
| `stop_topic` | Stop command | Any string |
| `next_topic` | Next track | Any string |
| `previous_topic` | Previous track | Any string |
| `volume_set_topic` | Set volume | Float 0.0-1.0 |
| `mute_topic` | Mute/unmute | `ON` / `OFF` |
| `shuffle_set_topic` | Set shuffle | `ON` / `OFF` |
| `repeat_set_topic` | Set repeat mode | `off`, `all`, `one` |
| `seek_topic` | Seek to position | Integer (seconds) |
| `select_source_topic` | Select source | Source name |
| `select_sound_mode_topic` | Select sound mode | Sound mode name |

## Feature Detection

Features are automatically enabled based on which topics are present in your configuration:

- **Play/Pause/Stop Controls** - `play_topic`, `pause_topic`, `stop_topic`
- **Volume Controls** - `volume_set_topic` (enables both set and step)
- **Mute Control** - `mute_topic`
- **Track Navigation** - `next_topic`, `previous_topic`
- **Seek Control** - `seek_topic` 
- **Shuffle/Repeat** - `shuffle_set_topic`, `repeat_set_topic`
- **Source Selection** - `select_source_topic`
- **Sound Modes** - `select_sound_mode_topic`
- **Power Control** - `turn_on_topic`, `turn_off_topic`
- **Media Playback** - `play_media_topic`
- **Advanced Features** - `clear_playlist_topic`, `browse_media_topic`

## Examples & Documentation

- 📖 **[Configuration Examples](docs/configuration-examples.md)** - Complete configuration examples for different use cases
- 🔄 **[Migration Guide](docs/migration-guide.md)** - Upgrade instructions from v1.x to v2.0
- 🔍 **[Discovery Support](docs/discovery-support.md)** - MQTT discovery implementation details

## Debugging

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.mqtt_media_player: debug
```

This provides detailed logs for:
- MQTT discovery and configuration validation
- Topic subscriptions and message handling  
- Feature detection and entity setup
- Command publishing and state updates

## Version 2.0 Changes

v2.0 is a complete rewrite implementing the [`ha-mqtt-discoverable`](https://github.com/shyndman/ha-mqtt-discoverable) MediaPlayer specification:

- ✅ **Full spec compliance** with automatic feature detection
- ✅ **Enhanced MQTT discovery** with validation 
- ✅ **New topic names** following the official specification
- ✅ **Comprehensive features** - mute, shuffle, repeat, sources, etc.
- ✅ **Better reliability** with proper error handling
- ❌ **Breaking changes** - requires configuration migration

See the [Migration Guide](docs/migration-guide.md) for detailed upgrade instructions.

## Related Projects

- **[ha-mqtt-discoverable](https://github.com/shyndman/ha-mqtt-discoverable)** - Python library for implementing spec-compliant MQTT discoverable devices
- **[Home Assistant MQTT Discovery](https://www.home-assistant.io/docs/mqtt/discovery/)** - Official Home Assistant MQTT discovery documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.