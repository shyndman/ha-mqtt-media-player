# Migration Guide: v1.x to v2.0

This guide helps you migrate from MQTT Media Player v1.x to v2.0, which implements full compliance with the `ha-mqtt-discoverable` MediaPlayer specification.

## Breaking Changes Summary

⚠️ **Version 2.0 is a complete rewrite with breaking changes**

- **All MQTT topic names have changed** to match the official spec
- **Feature flags are now required** to enable functionality
- **Configuration structure has been reorganized**
- **Minimum Home Assistant version is now 2024.1+**
- **No backward compatibility** with v1.x configurations

## Topic Name Changes

### State Topics (Data Published by Your Device)

| v1.x Topic Key | v2.0 Topic Key | Purpose |
|---------------|----------------|---------|
| `title_topic` | `media_title_topic` | Current media title |
| `artist_topic` | `media_artist_topic` | Current media artist |
| `album_topic` | `media_album_name_topic` | Current album name |
| `albumart_topic` | `media_image_url_topic` | Album art URL or base64 |
| `duration_topic` | `media_duration_topic` | Media duration in seconds |
| `position_topic` | `media_position_topic` | Playback position in seconds |
| `volume_topic` | `volume_level_topic` | Volume level (0.0-1.0) |
| `mediatype_topic` | `media_content_type_topic` | Content type (music, video, etc.) |
| `state_topic` | `state_topic` | *(No change)* Player state |
| `availability_topic` | `availability_topic` | *(No change)* Online/offline status |

### Command Topics (Commands Sent to Your Device)

| v1.x Topic Key | v2.0 Topic Key | Purpose |
|---------------|----------------|---------|
| `play_topic` | `play_topic` | *(No change)* Play command |
| `pause_topic` | `pause_topic` | *(No change)* Pause command |
| `stop_topic` | `stop_topic` | *(No change)* Stop command |
| `next_topic` | `next_topic` | *(No change)* Next track |
| `previous_topic` | `previous_topic` | *(No change)* Previous track |
| `volumeset_topic` | `volume_set_topic` | Set volume level |
| `playmedia_topic` | `play_media_topic` | Play specific media |
| `seek_topic` | `seek_topic` | *(No change)* Seek to position |
| `browse_media_topic` | `browse_media_topic` | *(No change)* Browse media |

### New Command Topics (v2.0 Only)

| Topic Key | Purpose |
|-----------|---------|
| `mute_topic` | Mute/unmute volume |
| `shuffle_topic` | Enable/disable shuffle |
| `repeat_topic` | Set repeat mode (off, all, one) |
| `turn_on_topic` | Turn device on |
| `turn_off_topic` | Turn device off |
| `source_topic` | Select input source |
| `sound_mode_topic` | Select sound mode |
| `clear_playlist_topic` | Clear current playlist |

## Feature Detection (Automatic)

v2.0 automatically detects supported features based on which topics are present in your configuration. You don't need to add explicit feature flags - they are determined automatically:

### How It Works
- **Topic Present** = Feature Supported
- **Topic Absent** = Feature Not Supported

### Examples
```json
{
  "play_topic": "player/play"
}
```
→ Automatically enables `supports_play` feature

```json
{
  "play_topic": "player/play",
  "pause_topic": "player/pause", 
  "volume_set_topic": "player/volume_set"
}
```
→ Automatically enables `supports_play`, `supports_pause`, `supports_volume_set`, and `supports_volume_step` features

## Configuration Migration Examples

### Basic Music Player

**v1.x Configuration:**
```json
{
  "name": "My Music Player",
  "state_topic": "music/state",
  "title_topic": "music/title",
  "artist_topic": "music/artist",
  "album_topic": "music/album",
  "duration_topic": "music/duration",
  "position_topic": "music/position",
  "volume_topic": "music/volume",
  "albumart_topic": "music/albumart",
  "play_topic": "music/play",
  "pause_topic": "music/pause",
  "stop_topic": "music/stop",
  "volumeset_topic": "music/volumeset"
}
```

**v2.0 Configuration:**
```json
{
  "name": "My Music Player",
  "state_topic": "music/state",
  "media_title_topic": "music/title",
  "media_artist_topic": "music/artist",
  "media_album_name_topic": "music/album",
  "media_duration_topic": "music/duration",
  "media_position_topic": "music/position",
  "volume_level_topic": "music/volume",
  "media_image_url_topic": "music/albumart",
  "play_topic": "music/play",
  "pause_topic": "music/pause",
  "stop_topic": "music/stop",
  "volume_set_topic": "music/volumeset"
}
```

**Features Automatically Detected:**
- `supports_play: true` (because `play_topic` is present)
- `supports_pause: true` (because `pause_topic` is present)  
- `supports_stop: true` (because `stop_topic` is present)
- `supports_volume_set: true` (because `volume_set_topic` is present)
- `supports_volume_step: true` (automatically enabled when `volume_set_topic` is present)

### Advanced Media Player with All Features

**v2.0 Configuration:**
```json
{
  "name": "Advanced Media Player",
  "unique_id": "advanced_player_001",
  "device": {
    "identifiers": ["advanced_player"],
    "manufacturer": "Example Corp",
    "model": "MediaPro 3000",
    "sw_version": "2.1.0"
  },
  "availability_topic": "player/available",
  "availability": {
    "payload_available": "online",
    "payload_not_available": "offline"
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
  "turn_on_topic": "player/turn_on",
  "turn_off_topic": "player/turn_off",
  "select_source_topic": "player/select_source",
  "select_sound_mode_topic": "player/select_sound_mode",
  "play_media_topic": "player/play_media",
  "clear_playlist_topic": "player/clear_playlist",
  "browse_media_topic": "player/browse"
}
```

**All Features Automatically Detected** based on the presence of their respective command topics.

## Step-by-Step Migration Process

### 1. Backup Your Current Configuration
Save your current MQTT configuration messages before updating.

### 2. Update the Integration
- Remove the old integration from HACS or custom_components
- Install MQTT Media Player v2.0
- Restart Home Assistant

### 3. Update Your Device Configuration
- Update all topic names according to the mapping table above
- Remove any explicit feature flags (they're now automatic)
- Update your device code to publish to the new topic names

### 4. Republish Configuration
Send the updated configuration to the MQTT config topic:
```bash
mosquitto_pub -t "homeassistant/media_player/your_device/config" -m "$(cat your_new_config.json)"
```

### 5. Test Functionality
- Verify the device appears in Home Assistant
- Test all media player controls
- Check that only enabled features are visible in the UI

### 6. Update Automations
Update any automations that reference the old entity attributes or service calls.

## Troubleshooting

### Device Not Appearing
- **Verify topic names**: Confirm you're using the new topic names
- **Check configuration format**: Ensure JSON is valid
- **Check logs**: Enable debug logging for `custom_components.mqtt_media_player`

### Missing Controls
- **Add command topics**: Controls only appear if the corresponding command topic is present
- **Check topic names**: Ensure you're using the correct v2.0 topic names

### Configuration Validation Errors
- **Topic names**: Must use new spec-compliant topic names
- **Unique ID**: Required when device information is provided

## Command Payload Changes

### Boolean Commands
v2.0 uses standardized boolean payloads:
- **Mute**: `"ON"` = mute, `"OFF"` = unmute
- **Shuffle**: `"ON"` = enabled, `"OFF"` = disabled

### Repeat Mode
- `"off"` = no repeat
- `"all"` = repeat all
- `"one"` = repeat current track

### Volume Commands
- **Volume Set**: Float value 0.0-1.0 (same as v1.x)
- **Volume Step**: Use volume up/down buttons in UI

## Getting Help

If you encounter issues during migration:

1. **Check the logs**: Enable debug logging in Home Assistant
2. **Validate your config**: Ensure all required fields are present
3. **Test incrementally**: Start with basic features, then add advanced ones
4. **Review examples**: See `configuration-examples.md` for complete examples

## Benefits of v2.0

- **Full spec compliance** with ha-mqtt-discoverable
- **Enhanced features**: Mute, shuffle, repeat, source selection
- **Better reliability**: Cleaner codebase with proper validation
- **Improved UI**: Only relevant controls are shown
- **Future-proof**: Aligned with Home Assistant standards

The migration requires updating your device configuration, but provides a much more robust and feature-complete media player integration.