"""MQTT Media Player entity implementation v2.0 - ha-mqtt-discoverable spec compliant."""

import hashlib
import logging
from typing import Any

from homeassistant.components import media_source
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    RepeatMode,
    async_fetch_image,
)
from homeassistant.components.mqtt import async_publish
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
)
from .coordinator import MQTTMediaPlayerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MQTT Media Player from config entry."""
    _LOGGER.debug("Setting up media player for config entry: %s", config_entry.title)

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create media player entity
    entity = MQTTMediaPlayer(coordinator, config_entry)
    async_add_entities([entity])

    _LOGGER.debug("Media player entity created for: %s", config_entry.title)


class MQTTMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """MQTT Media Player entity using coordinator and v2.0 spec."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self, coordinator: MQTTMediaPlayerCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the MQTT Media Player."""
        super().__init__(coordinator)

        self._config_entry = config_entry
        self._mqtt_config = config_entry.data["mqtt_config"]

        # Set up entity attributes from config
        self._attr_unique_id = self._mqtt_config.get("unique_id", config_entry.title)
        self._attr_name = (
            self._mqtt_config.get("name")
            if self._mqtt_config.get("name") != config_entry.title
            else None
        )

        # Set up device info
        device_config = self._mqtt_config.get("device", {})
        device_identifiers = {(DOMAIN, self._attr_unique_id)}

        # If device has custom identifiers, use them
        if "identifiers" in device_config:
            device_identifiers = {
                (DOMAIN, identifier) for identifier in device_config["identifiers"]
            }

        self._attr_device_info = DeviceInfo(
            identifiers=device_identifiers,
            name=config_entry.title,
            manufacturer=device_config.get("manufacturer", "MQTT Media Player"),
            model=device_config.get("model", "MQTT Media Player"),
            sw_version=device_config.get("sw_version", "2.0.0"),
            configuration_url=device_config.get("configuration_url"),
        )

        _LOGGER.debug("Initialized MQTT Media Player: %s", self._attr_unique_id)

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Return supported features based on available command topics."""
        features = MediaPlayerEntityFeature(0)

        # Map feature flags from coordinator to MediaPlayerEntityFeature
        feature_mapping = {
            "supports_play": MediaPlayerEntityFeature.PLAY,
            "supports_pause": MediaPlayerEntityFeature.PAUSE,
            "supports_stop": MediaPlayerEntityFeature.STOP,
            "supports_seek": MediaPlayerEntityFeature.SEEK,
            "supports_volume_set": MediaPlayerEntityFeature.VOLUME_SET,
            "supports_volume_step": MediaPlayerEntityFeature.VOLUME_STEP,
            "supports_volume_mute": MediaPlayerEntityFeature.VOLUME_MUTE,
            "supports_next_track": MediaPlayerEntityFeature.NEXT_TRACK,
            "supports_previous_track": MediaPlayerEntityFeature.PREVIOUS_TRACK,
            "supports_shuffle_set": MediaPlayerEntityFeature.SHUFFLE_SET,
            "supports_repeat_set": MediaPlayerEntityFeature.REPEAT_SET,
            "supports_turn_on": MediaPlayerEntityFeature.TURN_ON,
            "supports_turn_off": MediaPlayerEntityFeature.TURN_OFF,
            "supports_play_media": MediaPlayerEntityFeature.PLAY_MEDIA,
            "supports_select_source": MediaPlayerEntityFeature.SELECT_SOURCE,
            "supports_select_sound_mode": MediaPlayerEntityFeature.SELECT_SOUND_MODE,
            "supports_clear_playlist": MediaPlayerEntityFeature.CLEAR_PLAYLIST,
            "supports_browse_media": MediaPlayerEntityFeature.BROWSE_MEDIA,
        }

        for feature_flag, feature_enum in feature_mapping.items():
            if self.coordinator.supported_features.get(feature_flag, False):
                features |= feature_enum

        _LOGGER.debug("Supported features for %s: %s", self._attr_unique_id, features)
        return features

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the media player."""
        if self.coordinator.data.get("available") is False:
            return MediaPlayerState.OFF

        state = self.coordinator.data.get("state")
        if state in ["playing", "paused", "stopped", "idle", "off"]:
            return MediaPlayerState(state)

        return None

    @property
    def volume_level(self) -> float | None:
        """Return volume level of the media player (0..1)."""
        return self.coordinator.data.get("volume_level")

    @property
    def is_volume_muted(self) -> bool | None:
        """Return whether the media player is muted."""
        return self.coordinator.data.get("is_volume_muted")

    @property
    def media_content_id(self) -> str | None:
        """Return the content ID of current playing media."""
        # Use title as content ID if available
        return self.coordinator.data.get("media_title")

    @property
    def media_content_type(self) -> str | None:
        """Return the content type of current playing media."""
        return self.coordinator.data.get("media_content_type", "music")

    @property
    def media_title(self) -> str | None:
        """Return the title of current playing media."""
        return self.coordinator.data.get("media_title")

    @property
    def media_artist(self) -> str | None:
        """Return the artist of current playing media."""
        return self.coordinator.data.get("media_artist")

    @property
    def media_album_name(self) -> str | None:
        """Return the album name of current playing media."""
        return self.coordinator.data.get("media_album_name")

    @property
    def media_album_artist(self) -> str | None:
        """Return the album artist of current playing media."""
        return self.coordinator.data.get("media_album_artist")

    @property
    def media_track(self) -> int | None:
        """Return the track number of current playing media."""
        return self.coordinator.data.get("media_track")

    @property
    def media_duration(self) -> int | None:
        """Return the duration of current playing media in seconds."""
        return self.coordinator.data.get("media_duration")

    @property
    def media_position(self) -> int | None:
        """Return the current position in seconds."""
        return self.coordinator.data.get("media_position")

    @property
    def media_position_updated_at(self) -> str | None:
        """Return when the position was last updated."""
        return getattr(self, "_attr_media_position_updated_at", None)

    @property
    def media_image_url(self) -> str | None:
        """Return the image URL of current playing media."""
        return self.coordinator.data.get("media_image_url")

    @property
    def media_image_remotely_accessible(self) -> bool:
        """Return True if media image is accessible from outside the local network."""
        # For URLs, let Home Assistant handle proxying
        image_url = self.coordinator.data.get("media_image_url")
        return not (image_url and image_url.startswith(("http://", "https://")))

    @property
    def media_image_hash(self) -> str | None:
        """Return a hash of the media image."""
        image_url = self.coordinator.data.get("media_image_url")
        if image_url:
            return hashlib.md5(image_url.encode()).hexdigest()[:8]  # noqa: S324
        return None

    @property
    def media_episode(self) -> str | None:
        """Return the episode of current playing media."""
        return self.coordinator.data.get("media_episode")

    @property
    def media_season(self) -> str | None:
        """Return the season of current playing media."""
        return self.coordinator.data.get("media_season")

    @property
    def media_series_title(self) -> str | None:
        """Return the series title of current playing media."""
        return self.coordinator.data.get("media_series_title")

    @property
    def media_channel(self) -> str | None:
        """Return the channel currently playing."""
        return self.coordinator.data.get("media_channel")

    @property
    def media_playlist(self) -> str | None:
        """Return the current playlist title."""
        return self.coordinator.data.get("media_playlist")

    @property
    def app_id(self) -> str | None:
        """Return the ID of the current running app."""
        return self.coordinator.data.get("app_id")

    @property
    def app_name(self) -> str | None:
        """Return the name of the current running app."""
        return self.coordinator.data.get("app_name")

    @property
    def shuffle(self) -> bool | None:
        """Return whether shuffle is enabled."""
        return self.coordinator.data.get("shuffle")

    @property
    def repeat(self) -> RepeatMode | None:
        """Return current repeat mode."""
        repeat_mode = self.coordinator.data.get("repeat")
        if repeat_mode == "off":
            return RepeatMode.OFF
        if repeat_mode == "all":
            return RepeatMode.ALL
        if repeat_mode == "one":
            return RepeatMode.ONE
        return None

    @property
    def source(self) -> str | None:
        """Return the currently selected input source."""
        return self.coordinator.data.get("source")

    @property
    def source_list(self) -> list[str] | None:
        """Return list of available input sources."""
        return self.coordinator.data.get("source_list")

    @property
    def sound_mode(self) -> str | None:
        """Return the current sound mode."""
        return self.coordinator.data.get("sound_mode")

    @property
    def sound_mode_list(self) -> list[str] | None:
        """Return list of available sound modes."""
        return self.coordinator.data.get("sound_mode_list")

    @property
    def group_members(self) -> list[str] | None:
        """Return list of group member entity IDs."""
        return self.coordinator.data.get("group_members")

    async def async_get_media_image(self) -> tuple[bytes | None, str | None]:
        """Fetch media image of current playing media."""
        image_url = self.coordinator.data.get("media_image_url")
        if not image_url:
            return None, None

        # Handle base64 encoded images
        if image_url.startswith("data:image/"):
            try:
                # Extract base64 data
                header, data = image_url.split(",", 1)
                import base64  # noqa: PLC0415

                image_data = base64.b64decode(data)

                # Extract content type
                content_type = header.split(";")[0].split(":")[-1]

            except Exception:
                _LOGGER.exception("Failed to decode base64 image")
                return None, None
            else:
                return image_data, content_type

        # Handle HTTP/HTTPS URLs
        if image_url.startswith(("http://", "https://")):
            try:
                return await async_fetch_image(self.hass, image_url)
            except Exception:
                _LOGGER.exception("Failed to fetch image from URL %s", image_url)
                return None, None

        return None, None

    # Command methods
    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        await self._publish_command("turn_on_topic", "ON")

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        await self._publish_command("turn_off_topic", "OFF")

    async def async_play_media(
        self, media_type: str, media_id: str, **_kwargs: Any
    ) -> None:
        """Play a piece of media."""
        if media_source.is_media_source_id(media_id):
            media_type = "url"
            play_item = await media_source.async_resolve_media(
                self.hass, media_id, self.entity_id
            )
            media_id = play_item.url

        if media_type in ["url", "music", "video"]:
            await self._publish_command("play_media_topic", media_id)
        else:
            _LOGGER.warning("Unsupported media type: %s", media_type)

    async def async_media_play(self) -> None:
        """Send play command."""
        await self._publish_command("play_topic", "Play")

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self._publish_command("pause_topic", "Pause")

    async def async_media_stop(self) -> None:
        """Send stop command."""
        await self._publish_command("stop_topic", "Stop")

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self._publish_command("next_topic", "Next")

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self._publish_command("previous_topic", "Previous")

    async def async_media_seek(self, position: float) -> None:
        """Send seek command."""
        await self._publish_command("seek_topic", str(int(position)))

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        await self._publish_command("volume_set_topic", str(volume))

    async def async_mute_volume(self, mute: bool) -> None:  # noqa: FBT001
        """Mute/unmute volume."""
        payload = "ON" if mute else "OFF"
        await self._publish_command("mute_topic", payload)

    async def async_set_shuffle(self, shuffle: bool) -> None:  # noqa: FBT001
        """Enable/disable shuffle mode."""
        payload = "ON" if shuffle else "OFF"
        await self._publish_command("shuffle_set_topic", payload)

    async def async_set_repeat(self, repeat: RepeatMode) -> None:
        """Set repeat mode."""
        repeat_map = {
            RepeatMode.OFF: "off",
            RepeatMode.ALL: "all",
            RepeatMode.ONE: "one",
        }
        payload = repeat_map.get(repeat, "off")
        await self._publish_command("repeat_set_topic", payload)

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        await self._publish_command("select_source_topic", source)

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Select sound mode."""
        await self._publish_command("select_sound_mode_topic", sound_mode)

    async def async_clear_playlist(self) -> None:
        """Clear players playlist."""
        await self._publish_command("clear_playlist_topic", "Clear")

    async def async_browse_media(
        self,
        media_content_type: str | None = None,  # noqa: ARG002
        media_content_id: str | None = None,  # noqa: ARG002
    ) -> None:
        """Implement the websocket media browsing helper."""
        # This would need to be implemented based on the device's browse capabilities
        # For now, return None to indicate browsing is not supported
        return

    async def _publish_command(self, topic_key: str, payload: str) -> None:
        """Publish a command to the device."""
        topic = self._mqtt_config.get(topic_key)
        if not topic:
            _LOGGER.warning("Command topic %s not configured", topic_key)
            return

        _LOGGER.debug("Publishing command to %s: %s", topic, payload)
        try:
            await async_publish(
                self.hass,
                topic,
                payload,
                qos=0,
                retain=False,
            )
        except Exception:
            _LOGGER.exception("Failed to publish command to %s", topic)
