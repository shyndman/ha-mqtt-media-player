# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration that provides MQTT-based media player entities. It implements the `ha-mqtt-discoverable` MediaPlayer specification with full MQTT discovery support and comprehensive configuration validation.

## Development Commands

Since this is a Home Assistant custom integration, there are no build/test commands. Development workflow:

1. **Installation**: Copy to `custom_components/mqtt_media_player/` in Home Assistant config directory
2. **Restart**: Restart Home Assistant to load the integration
3. **Setup**: Add via Home Assistant UI (Settings → Devices & Services → Add Integration)
4. **Testing**: Use MQTT commands to test functionality

### Debug Logging

Enable comprehensive debug logging in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.mqtt_media_player: debug
```

## Architecture v2.0

### Core Components

- **ha-mqtt-discoverable Spec Compliance**: Full implementation of the MediaPlayer specification
- **Automatic Feature Detection**: Features determined by presence of command topics in configuration
- **Coordinator Pattern**: `MQTTMediaPlayerCoordinator` manages all MQTT communication
- **Enhanced Discovery**: Supports both MQTT auto-discovery and manual configuration with validation
- **Push-based Updates**: Pure MQTT event-driven, no polling

### Key Files

- `__init__.py` - Integration lifecycle with coordinator setup
- `config_flow.py` - Enhanced discovery & validation with spec compliance checking
- `coordinator.py` - Comprehensive MQTT data coordination with all spec topics
- `media_player.py` - Full spec-compliant media player entity implementation
- `const.py` - Complete validation schemas, feature mapping, and spec constants

### Data Flow

```
MQTT Discovery/Manual → Spec Validation → Feature Detection → Coordinator + Entity Ready
```

## MQTT Integration Details v2.0

### Discovery Protocol

- **Auto-discovery**: Devices publish to `homeassistant/media_player/+/config`
- **Spec Validation**: Strict validation against ha-mqtt-discoverable MediaPlayer spec
- **Feature Detection**: Automatic feature flag generation based on present topics
- **Error Handling**: Clear validation errors and fallback to manual configuration

### Topic Structure

#### State Topics (Published by Device)
- `media_title_topic`, `media_artist_topic`, `media_album_name_topic`
- `media_duration_topic`, `media_position_topic`, `volume_level_topic`
- `media_image_url_topic`, `shuffle_topic`, `repeat_topic`
- `source_topic`, `sound_mode_topic`, `app_name_topic`
- Plus many more per ha-mqtt-discoverable spec

#### Command Topics (Subscribed by Device)  
- `play_topic`, `pause_topic`, `stop_topic`, `next_topic`, `previous_topic`
- `volume_set_topic`, `mute_topic`, `seek_topic`
- `shuffle_set_topic`, `repeat_set_topic`, `turn_on_topic`, `turn_off_topic`
- `select_source_topic`, `select_sound_mode_topic`, `play_media_topic`
- `clear_playlist_topic`, `browse_media_topic`

### Feature Detection Logic

Features are automatically enabled based on topic presence:
- `play_topic` present → `supports_play: true`
- `volume_set_topic` present → `supports_volume_set: true` AND `supports_volume_step: true` 
- No explicit feature flags required in configuration

### Configuration Schema

Uses voluptuous validation with:
- All topics optional
- Automatic feature flag generation
- Device info validation
- Availability payload configuration
- Strict schema validation with helpful error messages

## Testing MQTT Functionality

### Basic Configuration Example
```bash
# Publish discovery message
mosquitto_pub -t "homeassistant/media_player/test_player/config" -m '{
  "name": "Test Player",
  "unique_id": "test_player_001",
  "state_topic": "test/state",
  "media_title_topic": "test/title",
  "play_topic": "test/play",
  "pause_topic": "test/pause",
  "volume_set_topic": "test/volume_set"
}'

# Test state updates  
mosquitto_pub -t "test/state" -m "playing"
mosquitto_pub -t "test/title" -m "Test Track"
mosquitto_pub -t "test/volume" -m "0.75"

# Test commands (HA will publish to these)
mosquitto_sub -t "test/play"
mosquitto_sub -t "test/volume_set"
```

### Advanced Configuration Testing
```bash
# Full-featured player
mosquitto_pub -t "homeassistant/media_player/advanced_player/config" -m '{
  "name": "Advanced Player",
  "state_topic": "advanced/state",
  "media_title_topic": "advanced/title",
  "media_artist_topic": "advanced/artist",
  "volume_level_topic": "advanced/volume",
  "shuffle_topic": "advanced/shuffle_state",
  "repeat_topic": "advanced/repeat_state",
  "play_topic": "advanced/play",
  "pause_topic": "advanced/pause",
  "volume_set_topic": "advanced/volume_set",
  "shuffle_set_topic": "advanced/shuffle_set",
  "repeat_set_topic": "advanced/repeat_set"
}'
```

## Code Patterns v2.0

### Home Assistant Best Practices

- **ha-mqtt-discoverable Compliance**: Full implementation of MediaPlayer specification
- **DataUpdateCoordinator**: Centralized MQTT data management with comprehensive state handling
- **CoordinatorEntity**: Modern entity pattern with automatic updates
- **Config Flow Discovery**: Enhanced discovery with validation and error handling
- **Feature Detection**: Dynamic feature flags based on configuration topology
- **Proper Device Registration**: Complete DeviceInfo implementation with configuration URLs

### MQTT Patterns

- **Spec-Compliant Topics**: All topic names follow ha-mqtt-discoverable MediaPlayer spec
- **Automatic Validation**: Configuration validated against spec during discovery and setup
- **Comprehensive State Handling**: Support for all media player properties per spec
- **Feature-Based Subscriptions**: Only subscribe to topics for supported features
- **Error Resilience**: Proper validation, error handling, and graceful degradation

### Validation and Error Handling

- **Schema Validation**: Complete voluptuous schemas for all configuration
- **Feature Consistency**: Automatic feature flag generation ensures consistency
- **Discovery Validation**: Strict validation during MQTT discovery with clear error messages
- **Graceful Fallbacks**: Manual configuration fallback when discovery fails or configurations are invalid

## Important Notes v2.0

- **Breaking Changes**: v2.0 is a complete rewrite with breaking changes from v1.x
- **No Legacy Support**: Clean implementation without backward compatibility
- **Migration Required**: Users must migrate configurations to new topic names
- **Spec Compliance**: Strict adherence to ha-mqtt-discoverable MediaPlayer specification
- **Feature Auto-Detection**: No manual feature flag configuration required
- **Enhanced Discovery**: Both automatic discovery and manual configuration supported
- **Comprehensive Validation**: All configurations validated against spec during setup

## Related Projects

- **Device Implementation**: [ha-mqtt-discoverable](https://github.com/shyndman/ha-mqtt-discoverable) - Python library for implementing spec-compliant MQTT discoverable devices
- **Integration Pairing**: This integration is designed to work seamlessly with devices implemented using the ha-mqtt-discoverable library

The integration now provides a complete, spec-compliant MQTT media player experience with automatic discovery, comprehensive feature support, and robust error handling.