# Configuration Examples

This document provides comprehensive configuration examples for MQTT Media Player v2.0, which implements the `ha-mqtt-discoverable` MediaPlayer specification.

## Basic Music Player

A simple music player with play/pause/stop controls and basic metadata display.

### MQTT Configuration Message
Publish to: `homeassistant/media_player/music_player/config`

```json
{
  "name": "Music Player",
  "unique_id": "music_player_001",
  "device": {
    "identifiers": ["music_player"],
    "manufacturer": "Example Corp",
    "model": "MusicBox 1000",
    "sw_version": "1.0.0"
  },
  "availability_topic": "music/available",
  "availability": {
    "payload_available": "online",
    "payload_not_available": "offline"
  },
  "state_topic": "music/state",
  "media_title_topic": "music/title",
  "media_artist_topic": "music/artist",
  "media_album_name_topic": "music/album",
  "media_duration_topic": "music/duration",
  "media_position_topic": "music/position",
  "media_image_url_topic": "music/albumart",
  "play_topic": "music/play",
  "pause_topic": "music/pause",
  "stop_topic": "music/stop",
  "supports_play": true,
  "supports_pause": true,
  "supports_stop": true
}
```

### Device MQTT Publishing Examples
```bash
# Set player state
mosquitto_pub -t "music/state" -m "playing"

# Update media information
mosquitto_pub -t "music/title" -m "Bohemian Rhapsody"
mosquitto_pub -t "music/artist" -m "Queen"
mosquitto_pub -t "music/album" -m "A Night at the Opera"
mosquitto_pub -t "music/duration" -m "355"
mosquitto_pub -t "music/position" -m "120"

# Set album art (URL)
mosquitto_pub -t "music/albumart" -m "https://example.com/album-cover.jpg"

# Set availability
mosquitto_pub -t "music/available" -m "online"
```

## Volume-Controlled Media Player

Music player with volume control, mute, and volume stepping.

### MQTT Configuration Message
```json
{
  "name": "Volume Player",
  "unique_id": "volume_player_001",
  "state_topic": "volume_player/state",
  "media_title_topic": "volume_player/title",
  "media_artist_topic": "volume_player/artist",
  "volume_level_topic": "volume_player/volume",
  "is_volume_muted_topic": "volume_player/muted",
  "play_topic": "volume_player/play",
  "pause_topic": "volume_player/pause",
  "stop_topic": "volume_player/stop",
  "volume_set_topic": "volume_player/volume_set",
  "mute_topic": "volume_player/mute",
  "supports_play": true,
  "supports_pause": true,
  "supports_stop": true,
  "supports_volume_set": true,
  "supports_volume_step": true,
  "supports_volume_mute": true
}
```

### Device Command Handling Examples
```bash
# Device subscribes to these command topics:
# volume_player/play
# volume_player/pause  
# volume_player/stop
# volume_player/volume_set  (receives 0.0-1.0 values)
# volume_player/mute        (receives "ON" or "OFF")

# Device publishes volume state:
mosquitto_pub -t "volume_player/volume" -m "0.75"
mosquitto_pub -t "volume_player/muted" -m "false"
```

## Advanced Media Player with Full Features

Complete media player with all supported features enabled.

### MQTT Configuration Message
```json
{
  "name": "Advanced Media Player",
  "unique_id": "advanced_player_001",
  "device": {
    "identifiers": ["advanced_player"],
    "manufacturer": "Audio Systems Inc",
    "model": "ProPlayer 5000",
    "sw_version": "2.1.0",
    "configuration_url": "http://192.168.1.100"
  },
  "availability_topic": "advanced/available",
  "availability": {
    "payload_available": "online",
    "payload_not_available": "offline"
  },
  "state_topic": "advanced/state",
  "media_title_topic": "advanced/title",
  "media_artist_topic": "advanced/artist",
  "media_album_name_topic": "advanced/album",
  "media_album_artist_topic": "advanced/album_artist",
  "media_track_topic": "advanced/track",
  "media_duration_topic": "advanced/duration",
  "media_position_topic": "advanced/position",
  "volume_level_topic": "advanced/volume",
  "media_image_url_topic": "advanced/albumart",
  "is_volume_muted_topic": "advanced/muted",
  "shuffle_topic": "advanced/shuffle",
  "repeat_topic": "advanced/repeat",
  "source_topic": "advanced/source",
  "source_list_topic": "advanced/source_list",
  "sound_mode_topic": "advanced/sound_mode",
  "sound_mode_list_topic": "advanced/sound_mode_list",
  "app_name_topic": "advanced/app_name",
  "play_topic": "advanced/play",
  "pause_topic": "advanced/pause",
  "stop_topic": "advanced/stop",
  "next_topic": "advanced/next",
  "previous_topic": "advanced/previous",
  "volume_set_topic": "advanced/volume_set",
  "mute_topic": "advanced/mute",
  "shuffle_set_topic": "advanced/shuffle_set",
  "repeat_set_topic": "advanced/repeat_set",
  "seek_topic": "advanced/seek",
  "turn_on_topic": "advanced/turn_on",
  "turn_off_topic": "advanced/turn_off",
  "select_source_topic": "advanced/select_source",
  "select_sound_mode_topic": "advanced/select_sound_mode",
  "play_media_topic": "advanced/play_media",
  "clear_playlist_topic": "advanced/clear_playlist",
  "browse_media_topic": "advanced/browse",
  "supports_play": true,
  "supports_pause": true,
  "supports_stop": true,
  "supports_seek": true,
  "supports_volume_set": true,
  "supports_volume_step": true,
  "supports_volume_mute": true,
  "supports_next_track": true,
  "supports_previous_track": true,
  "supports_shuffle_set": true,
  "supports_repeat_set": true,
  "supports_turn_on": true,
  "supports_turn_off": true,
  "supports_play_media": true,
  "supports_select_source": true,
  "supports_select_sound_mode": true,
  "supports_clear_playlist": true,
  "supports_browse_media": true
}
```

### Full State Publishing Examples
```bash
# Basic state
mosquitto_pub -t "advanced/state" -m "playing"
mosquitto_pub -t "advanced/available" -m "online"

# Media information
mosquitto_pub -t "advanced/title" -m "Hotel California"
mosquitto_pub -t "advanced/artist" -m "Eagles"
mosquitto_pub -t "advanced/album" -m "Hotel California"
mosquitto_pub -t "advanced/album_artist" -m "Eagles"
mosquitto_pub -t "advanced/track" -m "1"
mosquitto_pub -t "advanced/duration" -m "391"
mosquitto_pub -t "advanced/position" -m "45"

# Audio state
mosquitto_pub -t "advanced/volume" -m "0.65"
mosquitto_pub -t "advanced/muted" -m "false"

# Playback mode
mosquitto_pub -t "advanced/shuffle" -m "false"
mosquitto_pub -t "advanced/repeat" -m "off"

# Sources and sound modes
mosquitto_pub -t "advanced/source" -m "Spotify"
mosquitto_pub -t "advanced/source_list" -m '["Spotify", "Local Music", "Radio", "Bluetooth"]'
mosquitto_pub -t "advanced/sound_mode" -m "Music"
mosquitto_pub -t "advanced/sound_mode_list" -m '["Music", "Movie", "News", "Night"]'

# App information
mosquitto_pub -t "advanced/app_name" -m "Spotify"
```

## Video Player Configuration

Media player optimized for video content.

### MQTT Configuration Message
```json
{
  "name": "Video Player",
  "unique_id": "video_player_001",
  "state_topic": "video/state",
  "media_title_topic": "video/title",
  "media_series_title_topic": "video/series",
  "media_season_topic": "video/season",
  "media_episode_topic": "video/episode",
  "media_duration_topic": "video/duration",
  "media_position_topic": "video/position",
  "media_image_url_topic": "video/poster",
  "media_content_type_topic": "video/content_type",
  "volume_level_topic": "video/volume",
  "play_topic": "video/play",
  "pause_topic": "video/pause",
  "stop_topic": "video/stop",
  "seek_topic": "video/seek",
  "volume_set_topic": "video/volume_set",
  "mute_topic": "video/mute",
  "turn_on_topic": "video/power_on",
  "turn_off_topic": "video/power_off",
  "supports_play": true,
  "supports_pause": true,
  "supports_stop": true,
  "supports_seek": true,
  "supports_volume_set": true,
  "supports_volume_mute": true,
  "supports_turn_on": true,
  "supports_turn_off": true
}
```

### Video State Examples
```bash
# Video content information
mosquitto_pub -t "video/title" -m "The Office - The Pilot"
mosquitto_pub -t "video/series" -m "The Office"
mosquitto_pub -t "video/season" -m "1"
mosquitto_pub -t "video/episode" -m "1"
mosquitto_pub -t "video/content_type" -m "tvshow"
mosquitto_pub -t "video/duration" -m "1380"
mosquitto_pub -t "video/position" -m "245"
```

## Multi-Room Audio Player

Player that supports grouping with other players.

### MQTT Configuration Message
```json
{
  "name": "Living Room Speaker",
  "unique_id": "living_room_speaker_001",
  "device": {
    "identifiers": ["multiroom_system", "living_room"],
    "manufacturer": "MultiRoom Audio",
    "model": "Room Speaker v3",
    "sw_version": "3.2.1"
  },
  "state_topic": "multiroom/living_room/state",
  "media_title_topic": "multiroom/living_room/title",
  "media_artist_topic": "multiroom/living_room/artist",
  "volume_level_topic": "multiroom/living_room/volume",
  "group_members_topic": "multiroom/living_room/group_members",
  "play_topic": "multiroom/living_room/play",
  "pause_topic": "multiroom/living_room/pause",
  "volume_set_topic": "multiroom/living_room/volume_set",
  "supports_play": true,
  "supports_pause": true,
  "supports_volume_set": true
}
```

### Group State Examples
```bash
# Individual player state
mosquitto_pub -t "multiroom/living_room/state" -m "playing"
mosquitto_pub -t "multiroom/living_room/volume" -m "0.8"

# Group information (JSON array of entity IDs)
mosquitto_pub -t "multiroom/living_room/group_members" -m '["media_player.living_room_speaker", "media_player.kitchen_speaker", "media_player.bedroom_speaker"]'
```

## Testing Your Configuration

### 1. Publish Configuration
```bash
# Replace 'your_device' with your actual device name
mosquitto_pub -t "homeassistant/media_player/your_device/config" -m "$(cat your_config.json)"
```

### 2. Test State Updates
```bash
# Test basic playback
mosquitto_pub -t "your_device/state" -m "playing"
mosquitto_pub -t "your_device/title" -m "Test Track"

# Test volume
mosquitto_pub -t "your_device/volume" -m "0.5"
```

### 3. Test Commands
Commands will be sent by Home Assistant to your command topics. Subscribe to test:
```bash
# Subscribe to command topics to see HA commands
mosquitto_sub -t "your_device/play"
mosquitto_sub -t "your_device/volume_set"
mosquitto_sub -t "your_device/mute"
```

## Feature Flag Reference

Enable only the features your device actually supports:

### Playback Control
- `supports_play` - Play button and service
- `supports_pause` - Pause button and service  
- `supports_stop` - Stop button and service

### Track Navigation
- `supports_next_track` - Next track button
- `supports_previous_track` - Previous track button
- `supports_seek` - Seek bar for position control

### Volume Control
- `supports_volume_set` - Volume slider
- `supports_volume_step` - Volume up/down buttons
- `supports_volume_mute` - Mute button

### Playback Modes
- `supports_shuffle_set` - Shuffle toggle
- `supports_repeat_set` - Repeat mode cycling

### Power Control
- `supports_turn_on` - Turn on button/service
- `supports_turn_off` - Turn off button/service

### Media Selection
- `supports_play_media` - Play media service for URLs/IDs
- `supports_browse_media` - Media browser integration
- `supports_clear_playlist` - Clear playlist button

### Audio Configuration
- `supports_select_source` - Input source selection
- `supports_select_sound_mode` - Sound mode/EQ selection

## Common Patterns

### Base64 Album Art
```bash
# For base64 encoded images
mosquitto_pub -t "player/albumart" -m "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA..."
```

### JSON Array Topics
```bash
# For source lists, sound mode lists, group members
mosquitto_pub -t "player/source_list" -m '["Input 1", "Input 2", "Bluetooth", "WiFi"]'
```

### Boolean State Topics
```bash
# Use lowercase true/false for boolean states
mosquitto_pub -t "player/shuffle" -m "true"
mosquitto_pub -t "player/muted" -m "false"
```

### Repeat Mode Values
```bash
mosquitto_pub -t "player/repeat" -m "off"    # No repeat
mosquitto_pub -t "player/repeat" -m "all"    # Repeat all
mosquitto_pub -t "player/repeat" -m "one"    # Repeat current
```

Remember: Only include topics and features that your device actually supports. The integration will dynamically show/hide controls based on your feature flags.