# MQTT Media Player Integration - Agent Guide

## Project Overview
This is a Home Assistant custom integration that provides MQTT-based media player entities using a modern coordinator-based architecture. Media players are discovered via MQTT discovery or manually configured through the UI, with complete configuration validation during setup.

## Project Structure
```
custom_components/mqtt_media_player/
├── __init__.py           # Integration setup with coordinator lifecycle
├── config_flow.py        # Discovery & validation config flow
├── const.py             # Constants, schemas, and validation
├── coordinator.py        # MQTT data coordination (NEW)
├── manifest.json        # Integration metadata with MQTT discovery
├── media_player.py      # CoordinatorEntity-based implementation
└── strings.json         # UI translation strings (NEW)
```

## Architecture Overview

### Modern Coordinator Pattern
- **Push-based**: Pure MQTT event-driven updates (no polling)
- **Centralized**: Single coordinator manages all MQTT communication
- **Immediate**: Entities created with complete configuration from day one
- **Validated**: Full config validation during setup, not runtime

### Data Flow
```
MQTT Discovery/Manual → Config Flow Validation → Complete Config Entry → Coordinator + Entity Ready
```

## Key Files

### `coordinator.py` (NEW)
- `MQTTMediaPlayerCoordinator` extends `DataUpdateCoordinator`
- Handles all MQTT subscriptions and message processing
- Push-based updates via `async_set_updated_data()`
- Automatic subscription cleanup on removal
- Comprehensive debug logging for all MQTT operations

### `config_flow.py` (REWRITTEN)
- **MQTT Discovery**: Automatic device discovery via `async_step_mqtt`
- **Manual Setup**: Fallback for devices not yet configured
- **Device Selection**: User-friendly device selection UI
- **Config Validation**: Fetches and validates complete MQTT config during setup
- **Error Handling**: Proper error messages and user feedback

### `media_player.py` (REWRITTEN)
- **CoordinatorEntity**: Inherits from `CoordinatorEntity` instead of `MediaPlayerEntity`
- **Immediate Config**: All configuration available from `config_entry.data`
- **Dynamic Features**: `supported_features` based on available command topics
- **Push Updates**: Updates via `_handle_coordinator_update()`
- **Proper Device Info**: Uses `DeviceInfo` type with proper device registration

### `const.py` (ENHANCED)
- **Validation Schemas**: Voluptuous schemas for config validation
- **Topic Patterns**: Discovery and configuration topic patterns
- **Default Values**: Centralized default device information
- **Constants**: All integration constants and configuration keys

### `manifest.json` (UPDATED)
- **MQTT Discovery**: Added `"mqtt": ["homeassistant/media_player/+/config"]`
- **Version**: Updated to 1.0.0
- **Dependencies**: Proper dependency declarations

## Configuration Format

### MQTT Discovery Support
The integration automatically discovers devices publishing to:
`homeassistant/media_player/+/config`

### Configuration Schema
```json
{
  "name": "Device Name",
  "unique_id": "device_unique_id",
  "device": {
    "identifiers": ["device_id"],
    "manufacturer": "Device Manufacturer",
    "model": "Device Model",
    "sw_version": "1.0.0"
  },
  "availability_topic": "device/available",
  "availability": {
    "payload_available": "online",
    "payload_not_available": "offline"
  },
  "state_topic": "device/state",
  "title_topic": "device/title",
  "artist_topic": "device/artist",
  "album_topic": "device/album",
  "duration_topic": "device/duration",
  "position_topic": "device/position",
  "volume_topic": "device/volume",
  "albumart_topic": "device/albumart",
  "mediatype_topic": "device/mediatype",
  "play_topic": "device/play",
  "pause_topic": "device/pause",
  "stop_topic": "device/stop",
  "next_topic": "device/next",
  "previous_topic": "device/previous",
  "volumeset_topic": "device/volumeset",
  "playmedia_topic": "device/playmedia",
  "seek_topic": "device/seek",
  "browse_media_topic": "device/browse"
}
```

## Major Improvements Implemented

### 1. Architecture Transformation
- **Before**: Runtime configuration → Entity waits for MQTT config → Errors
- **After**: Config flow validation → Complete config entry → Entity ready immediately

### 2. Discovery & Validation
- **MQTT Auto-Discovery**: Finds devices automatically via manifest-based discovery
- **Manual Configuration**: Fallback option with real-time validation
- **Config Fetching**: Pulls complete MQTT config during setup process
- **Duplicate Prevention**: Proper unique ID handling prevents duplicate setups

### 3. Performance & Reliability
- **No More Runtime Errors**: Eliminated `NoEntitySpecifiedError` and empty state periods
- **Push-Based Updates**: Pure MQTT event-driven architecture
- **Centralized Management**: Single coordinator handles all MQTT communication
- **Immediate Features**: Dynamic feature detection available from entity creation

### 4. User Experience
- **Guided Setup**: Discovery → Selection → Validation → Ready
- **Error Prevention**: Validation during setup prevents runtime issues
- **Clear Feedback**: Comprehensive error messages and user guidance
- **Flexible Options**: Both auto-discovery and manual configuration

## Debug Logging

Enable debug logging in `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.mqtt_media_player: debug
```

### Comprehensive Logging Coverage
- **Integration Lifecycle**: Setup, coordinator initialization, entity creation
- **MQTT Operations**: Topic subscriptions, message handling, connection status
- **Config Flow**: Discovery process, validation steps, error handling
- **Data Processing**: Album art handling (base64 vs URL), state updates
- **Feature Detection**: Dynamic feature calculation, command availability

## Development Patterns

### Home Assistant Best Practices
- **DataUpdateCoordinator**: Proper coordinator pattern for data management
- **Config Flow**: Manifest-based discovery with validation
- **Entity Standards**: `CoordinatorEntity` with proper device registration
- **Type Safety**: Proper type annotations and `DeviceInfo` usage
- **Error Handling**: Specific exceptions with meaningful messages

### MQTT Integration Patterns
- **Discovery Protocol**: Follows Home Assistant MQTT discovery standards
- **Topic Management**: Centralized subscription handling with cleanup
- **Message Processing**: Callback-based message handling with state updates
- **Configuration Validation**: Schema-based validation during setup

### Code Quality Standards
- **Comprehensive Logging**: Debug logging throughout all operations
- **Error Prevention**: Validation at config time, not runtime
- **Resource Management**: Proper cleanup of subscriptions and coordinators
- **Documentation**: Clear docstrings and type hints

## Testing & Validation

### Testing Approach
1. **Install Integration**: Through HACS or manual installation
2. **Test Discovery**: Publish MQTT config and verify auto-discovery
3. **Test Manual Setup**: Configure via UI with device name
4. **Test Operations**: Verify all media player commands work
5. **Test Error Handling**: Validate error messages and recovery

### Common Commands for Testing
```bash
# Test discovery
mosquitto_pub -t "homeassistant/media_player/test_player/config" -m '{"name": "Test Player", "state_topic": "test/state"}'

# Test state updates
mosquitto_pub -t "test/state" -m "playing"
mosquitto_pub -t "test/title" -m "Test Track"

# Test album art (both formats)
mosquitto_pub -t "test/albumart" -m "https://example.com/cover.jpg"
mosquitto_pub -t "test/albumart" -m "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
```

## Resolved Issues

### Critical Issues Fixed
1. **Entity Registration Errors**: Fixed `NoEntitySpecifiedError` with proper device setup
2. **Runtime Configuration**: Eliminated waiting for MQTT config after entity creation
3. **Topic Subscription**: Fixed "0 topics subscribed" with correct key mappings
4. **Deprecated Patterns**: Removed deprecated options flow manual assignment

### Code Quality Improvements
1. **Type Safety**: Proper type annotations and imports
2. **Linting**: Fixed all bare except clauses and unused imports
3. **Architecture**: Modern coordinator pattern following HA best practices
4. **Error Handling**: Comprehensive error handling with user feedback

## Future Enhancements

### Potential Improvements
- **Config Migration**: Version-based config entry migration for schema changes
- **Advanced Discovery**: Support for additional MQTT discovery patterns
- **Caching**: Album art caching for improved performance
- **Multi-Entity**: Support for multiple entities per device
- **Subentries**: Support for complex device hierarchies

### Extensibility
- **Plugin Architecture**: Easy to add new media player features
- **Custom Schemas**: Extensible validation for custom device types
- **Advanced Logging**: Structured logging for better debugging
- **Testing Framework**: Comprehensive test suite for integration validation

The integration now follows all Home Assistant best practices and provides a robust, discoverable, and user-friendly MQTT media player experience.
