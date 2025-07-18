"""Constants for MQTT Media Player integration."""
import voluptuous as vol

DOMAIN = "mqtt_media_player"

# MQTT topic patterns
CONFIG_TOPIC_PATTERN = "homeassistant/media_player/{}/config"
DISCOVERY_TOPIC = "homeassistant/media_player/+/config"

# Default device info
DEFAULT_MANUFACTURER = "MQTT Media Player"
DEFAULT_MODEL = "MQTT Media Player"
DEFAULT_SW_VERSION = "1.0.0"

# Configuration validation schemas
DEVICE_SCHEMA = vol.Schema({
    vol.Optional("identifiers"): [str],
    vol.Optional("manufacturer", default=DEFAULT_MANUFACTURER): str,
    vol.Optional("model", default=DEFAULT_MODEL): str,
    vol.Optional("name"): str,
    vol.Optional("sw_version", default=DEFAULT_SW_VERSION): str,
})

AVAILABILITY_SCHEMA = vol.Schema({
    vol.Optional("payload_available", default="online"): str,
    vol.Optional("payload_not_available", default="offline"): str,
})

MQTT_CONFIG_SCHEMA = vol.Schema({
    vol.Optional("name"): str,
    vol.Optional("unique_id"): str,
    vol.Optional("device"): DEVICE_SCHEMA,
    vol.Optional("availability"): AVAILABILITY_SCHEMA,
    vol.Optional("availability_topic"): str,
    
    # State topics
    vol.Optional("state_topic"): str,
    vol.Optional("title_topic"): str,
    vol.Optional("artist_topic"): str,
    vol.Optional("album_topic"): str,
    vol.Optional("duration_topic"): str,
    vol.Optional("position_topic"): str,
    vol.Optional("volume_topic"): str,
    vol.Optional("albumart_topic"): str,
    vol.Optional("mediatype_topic"): str,
    
    # Command topics
    vol.Optional("play_topic"): str,
    vol.Optional("play_payload", default="Play"): str,
    vol.Optional("pause_topic"): str,
    vol.Optional("pause_payload", default="Pause"): str,
    vol.Optional("stop_topic"): str,
    vol.Optional("stop_payload", default="Stop"): str,
    vol.Optional("next_topic"): str,
    vol.Optional("next_payload", default="Next"): str,
    vol.Optional("previous_topic"): str,
    vol.Optional("previous_payload", default="Previous"): str,
    vol.Optional("volumeset_topic"): str,
    vol.Optional("playmedia_topic"): str,
    vol.Optional("seek_topic"): str,
    vol.Optional("browse_media_topic"): str,
})
