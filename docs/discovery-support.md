# MQTT Discovery Support

This document evaluates the current discovery implementation and outlines the strategy for v2.0 spec compliance.

## Current Discovery Implementation (v1.x)

### What We Have
The current implementation **does support** MQTT discovery:

1. **Manifest Declaration**: `"mqtt": ["homeassistant/media_player/+/config"]` enables automatic discovery
2. **Discovery Handler**: `async_step_mqtt()` processes discovery messages  
3. **Config Flow Integration**: Discovery triggers automatic setup flow
4. **Manual Fallback**: Users can also manually configure devices

### Discovery Flow
1. **Device publishes config** → `homeassistant/media_player/{device_name}/config`
2. **Home Assistant receives** → Triggers `async_step_mqtt()`
3. **Parse configuration** → Extracts device info and config
4. **User confirmation** → `async_step_discovered_device()`
5. **Create entity** → Device appears in Home Assistant

### Current Limitations
- **Topic validation**: May not properly validate new spec topics
- **Feature flag parsing**: Doesn't understand `supports_*` flags  
- **Schema compliance**: Uses v1.x schema validation
- **Error handling**: May fail on spec-compliant configurations

## Discovery Strategy for v2.0

### Option A: Enhanced Discovery (Recommended)
**Status**: ✅ **SELECTED**

**Rationale**: 
- Discovery is a key feature of the MQTT integration ecosystem
- Current implementation provides a solid foundation
- Users expect discovery to "just work" with spec-compliant devices

**Implementation Plan**:
1. **Update discovery parsing** to handle new spec topics
2. **Add feature flag validation** during discovery
3. **Enhance error handling** for invalid configurations
4. **Maintain backward compatibility** during transition (v1.x configs still work via manual setup)

### Option B: Manual Configuration Only
**Status**: ❌ **NOT SELECTED** 

**Rationale**: Discovery is too valuable to remove entirely.

### Option C: Basic Discovery + Manual Fallback  
**Status**: ❌ **NOT SELECTED**

**Rationale**: This is essentially what Option A provides.

## Discovery Implementation Details

### Discovery Topic Structure
**Current**: `homeassistant/media_player/{device_name}/config`
**New**: Same (no change needed)

### Configuration Message Parsing

#### v1.x Discovery Message
```json
{
  "name": "My Player",
  "state_topic": "player/state",
  "title_topic": "player/title",
  "play_topic": "player/play"
}
```

#### v2.0 Discovery Message  
```json
{
  "name": "My Player",
  "state_topic": "player/state",
  "media_title_topic": "player/title",
  "play_topic": "player/play",
  "supports_play": true,
  "supports_pause": false,
  "supports_stop": false
}
```

### Discovery Validation Strategy

#### Strict Validation (Recommended)
- **Require feature flags** in discovery messages
- **Reject invalid configurations** with clear error messages
- **Force spec compliance** from day one

#### Lenient Validation (Alternative)
- **Accept missing feature flags** and infer from topics
- **Warn about deprecated topics** but still process
- **Gradual migration path** for existing devices

**Decision**: **Strict Validation** - Clean break approach aligns with no-legacy-support strategy.

## Updated Discovery Implementation Plan

### 1. Update Discovery Message Parsing
- **Parse feature flags** from discovery messages
- **Validate topic/feature consistency**
- **Handle new topic names** per spec
- **Reject configurations** missing required feature flags

### 2. Enhanced Error Handling
- **Clear error messages** for spec violations
- **Debugging information** for configuration issues  
- **Validation feedback** during discovery process

### 3. Discovery Flow Updates
- **Feature flag validation** in `async_step_mqtt()`
- **New schema validation** against v2.0 spec
- **Enhanced logging** for discovery debugging

### 4. User Experience
- **Automatic setup** for spec-compliant devices
- **Clear error messages** for invalid configurations
- **Manual fallback** for complex configurations

## Discovery Code Changes Required

### `config_flow.py`
```python
async def async_step_mqtt(self, discovery_info: dict):
    """Handle MQTT discovery with v2.0 spec validation."""
    # Parse discovery message
    config_data = json.loads(discovery_info["payload"])
    
    # Validate against v2.0 schema (with feature flags)
    validated_config = MQTT_CONFIG_SCHEMA_V2(config_data)
    
    # Feature flag validation
    self._validate_feature_consistency(validated_config)
    
    # Continue with discovery flow...
```

### `const.py`
```python
# New schema with feature flags required
MQTT_CONFIG_SCHEMA_V2 = vol.Schema({
    vol.Required("supports_play"): bool,
    vol.Required("supports_pause"): bool,
    # ... other required feature flags
    
    # Topics only allowed if feature is supported
    vol.Optional("play_topic"): str,
    vol.Optional("pause_topic"): str,
    # ... conditional topics
}, extra=vol.PREVENT_EXTRA)
```

## Testing Discovery

### Test Discovery Message
```bash
# Publish spec-compliant discovery message
mosquitto_pub -t "homeassistant/media_player/test_device/config" -m '{
  "name": "Test Player",
  "unique_id": "test_player_001",
  "state_topic": "test/state",
  "media_title_topic": "test/title",
  "play_topic": "test/play",
  "pause_topic": "test/pause",
  "supports_play": true,
  "supports_pause": true,
  "supports_stop": false
}'
```

### Expected Behavior
1. **Discovery triggers** → Integration detects device
2. **Validation passes** → Configuration is spec-compliant
3. **User confirmation** → Device appears in discovery UI
4. **Entity creation** → Media player entity appears in HA
5. **Feature detection** → Only play/pause controls visible

### Error Cases
```bash
# Missing feature flags (should fail)
mosquitto_pub -t "homeassistant/media_player/invalid_device/config" -m '{
  "name": "Invalid Player",
  "state_topic": "invalid/state",
  "play_topic": "invalid/play"
}'
```

Expected: Discovery fails with clear error message about missing feature flags.

## Discovery Benefits

### For Users
- **Automatic setup** - Devices appear without manual configuration
- **Zero configuration** - No need to manually map topics
- **Plug and play** - Works with any spec-compliant device

### For Device Developers  
- **Standard protocol** - Follow ha-mqtt-discoverable spec
- **Automatic integration** - No custom HA integration needed
- **Feature declaration** - Clearly specify supported capabilities

### For Integration Maintenance
- **Standardized configurations** - All devices follow same format
- **Reduced support burden** - Clear spec compliance requirements
- **Future-proof** - Aligned with MQTT discovery ecosystem

## Conclusion

Enhanced discovery support in v2.0 will:
- ✅ **Maintain discovery functionality** - Key feature preserved
- ✅ **Enforce spec compliance** - Only accept valid configurations  
- ✅ **Provide clear feedback** - Helpful error messages
- ✅ **Support ecosystem** - Works with ha-mqtt-discoverable devices
- ✅ **Simplify development** - Standard discovery protocol

The discovery implementation will be updated to strictly validate v2.0 spec compliance while maintaining the user-friendly automatic setup experience.