"""MQTT Media Player Data Update Coordinator v2.0 - ha-mqtt-discoverable spec compliant."""

import json
import logging
import math

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.mqtt import async_subscribe
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    VALID_STATES,
    VALID_REPEAT_MODES,
    get_supported_features,
)

_LOGGER = logging.getLogger(__name__)


class MQTTMediaPlayerCoordinator(DataUpdateCoordinator):
    """Coordinate MQTT data for media player entities using v2.0 spec."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
        )
        self.config_entry = config_entry
        self.mqtt_config = config_entry.data["mqtt_config"]
        self._subscriptions = []

        # Get supported features based on configuration
        self.supported_features = get_supported_features(self.mqtt_config)

        # Initialize data structure with all possible fields
        self.data = {
            # Core state
            "state": None,
            "available": None,
            # Media information
            "media_title": None,
            "media_artist": None,
            "media_album_name": None,
            "media_album_artist": None,
            "media_track": None,
            "media_duration": None,
            "media_position": None,
            "media_content_type": None,
            "media_image_url": None,
            "media_episode": None,
            "media_season": None,
            "media_series_title": None,
            "media_channel": None,
            "media_playlist": None,
            # Audio properties
            "volume_level": None,
            "is_volume_muted": None,
            # Playback properties
            "shuffle": None,
            "repeat": None,
            # Source/Input properties
            "source": None,
            "source_list": None,
            "sound_mode": None,
            "sound_mode_list": None,
            # App information
            "app_id": None,
            "app_name": None,
            # Group properties
            "group_members": None,
        }

        _LOGGER.debug(
            "Initialized coordinator for: %s with features: %s",
            self.mqtt_config.get("name"),
            self.supported_features,
        )

    async def _async_update_data(self):
        """Fetch data from MQTT - not used since we're push-based."""
        return self.data

    async def async_added_to_hass(self):
        """Subscribe to MQTT topics when coordinator is added."""
        _LOGGER.debug("Setting up MQTT subscriptions")

        # Subscribe to state topics based on configuration
        topic_handlers = {
            "state_topic": self._handle_state,
            "media_title_topic": self._handle_media_title,
            "media_artist_topic": self._handle_media_artist,
            "media_album_name_topic": self._handle_media_album_name,
            "media_album_artist_topic": self._handle_media_album_artist,
            "media_track_topic": self._handle_media_track,
            "media_duration_topic": self._handle_media_duration,
            "media_position_topic": self._handle_media_position,
            "media_content_type_topic": self._handle_media_content_type,
            "media_image_url_topic": self._handle_media_image_url,
            "media_episode_topic": self._handle_media_episode,
            "media_season_topic": self._handle_media_season,
            "media_series_title_topic": self._handle_media_series_title,
            "media_channel_topic": self._handle_media_channel,
            "media_playlist_topic": self._handle_media_playlist,
            "volume_level_topic": self._handle_volume_level,
            "is_volume_muted_topic": self._handle_is_volume_muted,
            "shuffle_topic": self._handle_shuffle,
            "repeat_topic": self._handle_repeat,
            "source_topic": self._handle_source,
            "source_list_topic": self._handle_source_list,
            "sound_mode_topic": self._handle_sound_mode,
            "sound_mode_list_topic": self._handle_sound_mode_list,
            "app_id_topic": self._handle_app_id,
            "app_name_topic": self._handle_app_name,
            "group_members_topic": self._handle_group_members,
            "availability_topic": self._handle_availability,
        }

        for topic_key, handler in topic_handlers.items():
            topic = self.mqtt_config.get(topic_key)
            if topic:
                _LOGGER.debug("Subscribing to %s: %s", topic_key, topic)
                subscription = await async_subscribe(self.hass, topic, handler, qos=0)
                self._subscriptions.append(subscription)

        _LOGGER.info(
            "Successfully subscribed to %d MQTT topics", len(self._subscriptions)
        )

    async def async_will_remove_from_hass(self):
        """Clean up MQTT subscriptions."""
        _LOGGER.debug("Cleaning up MQTT subscriptions")
        for subscription in self._subscriptions:
            subscription()
        self._subscriptions.clear()

    # State handlers
    @callback
    def _handle_state(self, message):
        """Handle state updates."""
        state = message.payload.strip()
        if state in VALID_STATES:
            _LOGGER.debug("State update: %s", state)
            self.data["state"] = state
        else:
            _LOGGER.warning(
                "Invalid state received: %s (valid: %s)", state, VALID_STATES
            )
            return
        self.async_set_updated_data(self.data)

    @callback
    def _handle_availability(self, message):
        """Handle availability updates."""
        payload = message.payload.strip()
        availability_config = self.mqtt_config.get("availability", {})
        payload_available = availability_config.get("payload_available", "online")

        available = payload == payload_available
        _LOGGER.debug("Availability update: %s -> %s", payload, available)
        self.data["available"] = available
        self.async_set_updated_data(self.data)

    # Media information handlers
    @callback
    def _handle_media_title(self, message):
        """Handle media title updates."""
        title = message.payload.strip() or None
        _LOGGER.debug("Media title update: %s", title)
        self.data["media_title"] = title
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_artist(self, message):
        """Handle media artist updates."""
        artist = message.payload.strip() or None
        _LOGGER.debug("Media artist update: %s", artist)
        self.data["media_artist"] = artist
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_album_name(self, message):
        """Handle media album name updates."""
        album = message.payload.strip() or None
        _LOGGER.debug("Media album name update: %s", album)
        self.data["media_album_name"] = album
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_album_artist(self, message):
        """Handle media album artist updates."""
        album_artist = message.payload.strip() or None
        _LOGGER.debug("Media album artist update: %s", album_artist)
        self.data["media_album_artist"] = album_artist
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_track(self, message):
        """Handle media track number updates."""
        try:
            track = int(message.payload.strip()) if message.payload.strip() else None
            _LOGGER.debug("Media track update: %s", track)
            self.data["media_track"] = track
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid track number: %s", message.payload)
            self.data["media_track"] = None
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_duration(self, message):
        """Handle media duration updates."""
        try:
            duration = float(message.payload.strip())
            duration_int = math.ceil(duration) if duration > 0 else None
            _LOGGER.debug("Media duration update: %s (from %s)", duration_int, duration)
            self.data["media_duration"] = duration_int
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid duration value: %s", message.payload)
            self.data["media_duration"] = None
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_position(self, message):
        """Handle media position updates."""
        try:
            position = float(message.payload.strip())
            position_int = math.ceil(position) if position >= 0 else None
            _LOGGER.debug("Media position update: %s (from %s)", position_int, position)
            self.data["media_position"] = position_int
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid position value: %s", message.payload)
            self.data["media_position"] = None
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_content_type(self, message):
        """Handle media content type updates."""
        content_type = message.payload.strip() or "music"
        _LOGGER.debug("Media content type update: %s", content_type)
        self.data["media_content_type"] = content_type
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_image_url(self, message):
        """Handle media image URL updates."""
        image_url = message.payload.strip() or None
        _LOGGER.debug("Media image URL update: %s", image_url)
        self.data["media_image_url"] = image_url
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_episode(self, message):
        """Handle media episode updates."""
        episode = message.payload.strip() or None
        _LOGGER.debug("Media episode update: %s", episode)
        self.data["media_episode"] = episode
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_season(self, message):
        """Handle media season updates."""
        season = message.payload.strip() or None
        _LOGGER.debug("Media season update: %s", season)
        self.data["media_season"] = season
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_series_title(self, message):
        """Handle media series title updates."""
        series_title = message.payload.strip() or None
        _LOGGER.debug("Media series title update: %s", series_title)
        self.data["media_series_title"] = series_title
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_channel(self, message):
        """Handle media channel updates."""
        channel = message.payload.strip() or None
        _LOGGER.debug("Media channel update: %s", channel)
        self.data["media_channel"] = channel
        self.async_set_updated_data(self.data)

    @callback
    def _handle_media_playlist(self, message):
        """Handle media playlist updates."""
        playlist = message.payload.strip() or None
        _LOGGER.debug("Media playlist update: %s", playlist)
        self.data["media_playlist"] = playlist
        self.async_set_updated_data(self.data)

    # Audio property handlers
    @callback
    def _handle_volume_level(self, message):
        """Handle volume level updates."""
        try:
            volume = float(message.payload.strip())
            if 0.0 <= volume <= 1.0:
                _LOGGER.debug("Volume level update: %s", volume)
                self.data["volume_level"] = volume
            else:
                _LOGGER.warning("Volume level out of range (0.0-1.0): %s", volume)
                return
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid volume level: %s", message.payload)
            return
        self.async_set_updated_data(self.data)

    @callback
    def _handle_is_volume_muted(self, message):
        """Handle volume mute state updates."""
        payload = message.payload.strip().lower()
        muted = payload in ("true", "1", "on", "yes")
        _LOGGER.debug("Volume muted update: %s -> %s", payload, muted)
        self.data["is_volume_muted"] = muted
        self.async_set_updated_data(self.data)

    # Playback property handlers
    @callback
    def _handle_shuffle(self, message):
        """Handle shuffle state updates."""
        payload = message.payload.strip().lower()
        shuffle = payload in ("true", "1", "on", "yes")
        _LOGGER.debug("Shuffle update: %s -> %s", payload, shuffle)
        self.data["shuffle"] = shuffle
        self.async_set_updated_data(self.data)

    @callback
    def _handle_repeat(self, message):
        """Handle repeat mode updates."""
        repeat_mode = message.payload.strip().lower()
        if repeat_mode in VALID_REPEAT_MODES:
            _LOGGER.debug("Repeat mode update: %s", repeat_mode)
            self.data["repeat"] = repeat_mode
        else:
            _LOGGER.warning(
                "Invalid repeat mode: %s (valid: %s)", repeat_mode, VALID_REPEAT_MODES
            )
            return
        self.async_set_updated_data(self.data)

    # Source/Input property handlers
    @callback
    def _handle_source(self, message):
        """Handle source updates."""
        source = message.payload.strip() or None
        _LOGGER.debug("Source update: %s", source)
        self.data["source"] = source
        self.async_set_updated_data(self.data)

    @callback
    def _handle_source_list(self, message):
        """Handle source list updates."""
        try:
            source_list = json.loads(message.payload.strip())
            if isinstance(source_list, list):
                _LOGGER.debug("Source list update: %s", source_list)
                self.data["source_list"] = source_list
            else:
                _LOGGER.warning("Source list must be a JSON array: %s", message.payload)
                return
        except (json.JSONDecodeError, ValueError):
            _LOGGER.warning("Invalid JSON for source list: %s", message.payload)
            return
        self.async_set_updated_data(self.data)

    @callback
    def _handle_sound_mode(self, message):
        """Handle sound mode updates."""
        sound_mode = message.payload.strip() or None
        _LOGGER.debug("Sound mode update: %s", sound_mode)
        self.data["sound_mode"] = sound_mode
        self.async_set_updated_data(self.data)

    @callback
    def _handle_sound_mode_list(self, message):
        """Handle sound mode list updates."""
        try:
            sound_mode_list = json.loads(message.payload.strip())
            if isinstance(sound_mode_list, list):
                _LOGGER.debug("Sound mode list update: %s", sound_mode_list)
                self.data["sound_mode_list"] = sound_mode_list
            else:
                _LOGGER.warning(
                    "Sound mode list must be a JSON array: %s", message.payload
                )
                return
        except (json.JSONDecodeError, ValueError):
            _LOGGER.warning("Invalid JSON for sound mode list: %s", message.payload)
            return
        self.async_set_updated_data(self.data)

    # App information handlers
    @callback
    def _handle_app_id(self, message):
        """Handle app ID updates."""
        app_id = message.payload.strip() or None
        _LOGGER.debug("App ID update: %s", app_id)
        self.data["app_id"] = app_id
        self.async_set_updated_data(self.data)

    @callback
    def _handle_app_name(self, message):
        """Handle app name updates."""
        app_name = message.payload.strip() or None
        _LOGGER.debug("App name update: %s", app_name)
        self.data["app_name"] = app_name
        self.async_set_updated_data(self.data)

    # Group property handlers
    @callback
    def _handle_group_members(self, message):
        """Handle group members updates."""
        try:
            group_members = json.loads(message.payload.strip())
            if isinstance(group_members, list):
                _LOGGER.debug("Group members update: %s", group_members)
                self.data["group_members"] = group_members
            else:
                _LOGGER.warning(
                    "Group members must be a JSON array: %s", message.payload
                )
                return
        except (json.JSONDecodeError, ValueError):
            _LOGGER.warning("Invalid JSON for group members: %s", message.payload)
            return
        self.async_set_updated_data(self.data)
