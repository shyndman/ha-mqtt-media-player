"""Constants for MQTT Media Player integration v2.0 - ha-mqtt-discoverable spec compliant."""

import voluptuous as vol

DOMAIN = "mqtt_media_player"
COMPONENT = "media_player"

# MQTT topic patterns
CONFIG_TOPIC_PATTERN = "homeassistant/media_player/{}/config"
DISCOVERY_TOPIC = "homeassistant/media_player/+/config"

# Default device info
DEFAULT_MANUFACTURER = "MQTT Media Player"
DEFAULT_MODEL = "MQTT Media Player"
DEFAULT_SW_VERSION = "2.0.0"

# State topics - published by device
STATE_TOPICS = {
    "state_topic": "state",
    "media_title_topic": "title",
    "media_artist_topic": "artist",
    "media_album_name_topic": "album",
    "media_album_artist_topic": "album_artist",
    "media_track_topic": "track",
    "media_duration_topic": "duration",
    "media_position_topic": "position",
    "media_content_type_topic": "content_type",
    "media_image_url_topic": "image_url",
    "media_episode_topic": "episode",
    "media_season_topic": "season",
    "media_series_title_topic": "series_title",
    "media_channel_topic": "channel",
    "media_playlist_topic": "playlist",
    "volume_level_topic": "volume_level",
    "is_volume_muted_topic": "is_volume_muted",
    "shuffle_topic": "shuffle",
    "repeat_topic": "repeat",
    "source_topic": "source",
    "source_list_topic": "source_list",
    "sound_mode_topic": "sound_mode",
    "sound_mode_list_topic": "sound_mode_list",
    "app_id_topic": "app_id",
    "app_name_topic": "app_name",
    "group_members_topic": "group_members",
    "availability_topic": "availability",
}

# Command topics and their corresponding feature flags
# Format: topic_key -> (feature_flag, command_name)
COMMAND_TOPICS = {
    "play_topic": ("supports_play", "play"),
    "pause_topic": ("supports_pause", "pause"),
    "stop_topic": ("supports_stop", "stop"),
    "next_topic": ("supports_next_track", "next"),
    "previous_topic": ("supports_previous_track", "previous"),
    "volume_set_topic": ("supports_volume_set", "volume_set"),
    "mute_topic": ("supports_volume_mute", "mute"),
    "shuffle_set_topic": ("supports_shuffle_set", "shuffle_set"),
    "repeat_set_topic": ("supports_repeat_set", "repeat_set"),
    "seek_topic": ("supports_seek", "seek"),
    "turn_on_topic": ("supports_turn_on", "turn_on"),
    "turn_off_topic": ("supports_turn_off", "turn_off"),
    "select_source_topic": ("supports_select_source", "select_source"),
    "select_sound_mode_topic": ("supports_select_sound_mode", "select_sound_mode"),
    "play_media_topic": ("supports_play_media", "play_media"),
    "clear_playlist_topic": ("supports_clear_playlist", "clear_playlist"),
    "browse_media_topic": ("supports_browse_media", "browse_media"),
}

# Additional feature mappings that don't have direct command topics
IMPLICIT_FEATURES = {
    "supports_volume_step": "volume_set_topic",  # Volume step is available if volume_set is available
}

# Configuration validation schemas
DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional("identifiers"): [str],
        vol.Optional("manufacturer", default=DEFAULT_MANUFACTURER): str,
        vol.Optional("model", default=DEFAULT_MODEL): str,
        vol.Optional("name"): str,
        vol.Optional("sw_version", default=DEFAULT_SW_VERSION): str,
        vol.Optional("configuration_url"): str,
    }
)

AVAILABILITY_SCHEMA = vol.Schema(
    {
        vol.Optional("payload_available", default="online"): str,
        vol.Optional("payload_not_available", default="offline"): str,
    }
)


def _create_mqtt_config_schema():
    """Create the MQTT configuration schema."""
    schema_dict = {
        # Core configuration
        vol.Optional("name"): str,
        vol.Optional("unique_id"): str,
        vol.Optional("device"): DEVICE_SCHEMA,
        vol.Optional("availability"): AVAILABILITY_SCHEMA,
        # Component identifier - must match our constant
        vol.Optional("component", default=COMPONENT): vol.In([COMPONENT]),
    }

    # Add all state topics as optional
    for topic_key in STATE_TOPICS:
        schema_dict[vol.Optional(topic_key)] = str

    # Add all command topics as optional
    for topic_key in COMMAND_TOPICS:
        schema_dict[vol.Optional(topic_key)] = str

    return vol.Schema(schema_dict, extra=vol.PREVENT_EXTRA)


MQTT_CONFIG_SCHEMA = _create_mqtt_config_schema()


def get_supported_features(config: dict) -> dict:
    """Determine supported features based on present topics."""
    features = {}

    # Check command topics for direct feature mapping
    for topic_key, (feature_flag, _) in COMMAND_TOPICS.items():
        features[feature_flag] = topic_key in config and config[topic_key] is not None

    # Check implicit features
    for feature_flag, required_topic in IMPLICIT_FEATURES.items():
        features[feature_flag] = (
            required_topic in config and config[required_topic] is not None
        )

    return features


def validate_configuration(config: dict) -> dict:
    """Validate and enrich configuration with feature flags."""
    # First validate against schema
    validated_config = MQTT_CONFIG_SCHEMA(config)

    # Add supported features based on present topics
    supported_features = get_supported_features(validated_config)
    validated_config.update(supported_features)

    return validated_config


# Valid states per spec
VALID_STATES = ["playing", "paused", "stopped", "idle", "off"]

# Valid repeat modes per spec
VALID_REPEAT_MODES = ["off", "all", "one"]

# Default payloads for boolean commands
BOOLEAN_COMMAND_PAYLOADS = {
    "ON": True,
    "OFF": False,
    "on": True,
    "off": False,
    "true": True,
    "false": False,
    "1": True,
    "0": False,
}

# Media content types
MEDIA_CONTENT_TYPES = [
    "music",
    "video",
    "podcast",
    "audiobook",
    "tvshow",
    "movie",
    "playlist",
    "image",
    "url",
    "game",
]
