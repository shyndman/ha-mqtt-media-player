"""MQTT Media Player entity implementation."""
import hashlib
import json
import logging
from typing import Any

from homeassistant.components import media_source
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    async_fetch_image,
)
from homeassistant.components.media_player.browse_media import (
    async_process_play_media_url,
)
from homeassistant.components.media_player.const import MediaPlayerEntityFeature
from homeassistant.components.mqtt import async_publish
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util.dt import utcnow

from .const import DOMAIN

# Import coordinator for runtime use
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
    """MQTT Media Player entity using coordinator."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: MQTTMediaPlayerCoordinator, config_entry: ConfigEntry) -> None:
        """Initialize the MQTT Media Player."""
        super().__init__(coordinator)

        self._config_entry = config_entry
        self._mqtt_config = config_entry.data["mqtt_config"]

        # Set up entity attributes from config
        self._attr_unique_id = self._mqtt_config.get("unique_id", config_entry.title)
        self._attr_name = self._mqtt_config.get("name") if self._mqtt_config.get("name") != config_entry.title else None

        # Set up device info
        device_config = self._mqtt_config.get("device", {})
        device_identifiers = {(DOMAIN, self._attr_unique_id)}

        # If device has custom identifiers, use them
        if "identifiers" in device_config:
            device_identifiers = {(DOMAIN, identifier) for identifier in device_config["identifiers"]}

        self._attr_device_info = DeviceInfo(
            identifiers=device_identifiers,  # type: ignore
            name=config_entry.title,
            manufacturer=device_config.get("manufacturer", "MQTT Media Player"),
            model=device_config.get("model", "MQTT Media Player"),
            sw_version=device_config.get("sw_version", "1.0.0"),
        )

        _LOGGER.debug("Initialized MQTT Media Player: %s", self._attr_unique_id)

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Return supported features based on available command topics."""
        features = MediaPlayerEntityFeature(0)

        # Check command topics from config
        if self._mqtt_config.get("play_topic"):
            features |= MediaPlayerEntityFeature.PLAY

        if self._mqtt_config.get("pause_topic"):
            features |= MediaPlayerEntityFeature.PAUSE

        if self._mqtt_config.get("stop_topic"):
            features |= MediaPlayerEntityFeature.STOP

        if self._mqtt_config.get("volumeset_topic"):
            features |= MediaPlayerEntityFeature.VOLUME_SET
            features |= MediaPlayerEntityFeature.VOLUME_STEP

        if self._mqtt_config.get("next_topic"):
            features |= MediaPlayerEntityFeature.NEXT_TRACK

        if self._mqtt_config.get("previous_topic"):
            features |= MediaPlayerEntityFeature.PREVIOUS_TRACK

        if self._mqtt_config.get("playmedia_topic"):
            features |= MediaPlayerEntityFeature.PLAY_MEDIA

        if self._mqtt_config.get("seek_topic"):
            features |= MediaPlayerEntityFeature.SEEK

        if self._mqtt_config.get("browse_media_topic"):
            features |= MediaPlayerEntityFeature.BROWSE_MEDIA

        _LOGGER.debug("Supported features for %s: %s", self._attr_unique_id, features)
        return features

    @property
    def state(self) -> str | None:
        """Return the state of the media player."""
        if self.coordinator.data.get("available") is False:
            return "unavailable"
        return self.coordinator.data.get("state")

    @property
    def volume_level(self) -> float | None:
        """Return volume level of the media player (0..1)."""
        return self.coordinator.data.get("volume")

    @property
    def media_title(self) -> str | None:
        """Return the title of current playing media."""
        return self.coordinator.data.get("title")

    @property
    def media_artist(self) -> str | None:
        """Return the artist of current playing media."""
        return self.coordinator.data.get("artist")

    @property
    def media_album_name(self) -> str | None:
        """Return the album name of current playing media."""
        return self.coordinator.data.get("album")

    @property
    def media_content_type(self) -> str | None:
        """Return the content type of current playing media."""
        return self.coordinator.data.get("mediatype", "music")

    @property
    def media_position(self) -> int | None:
        """Return the current position in seconds."""
        return self.coordinator.data.get("position")

    @property
    def media_position_updated_at(self) -> str | None:
        """Return when the position was last updated."""
        return getattr(self, '_attr_media_position_updated_at', None)

    @property
    def media_duration(self) -> int | None:
        """Return the duration of current playing media in seconds."""
        return self.coordinator.data.get("duration")

    @property
    def media_image_url(self) -> str | None:
        """Return the image URL of current playing media."""
        return self.coordinator.data.get("albumart_url")

    @property
    def media_image_remotely_accessible(self) -> bool:
        """Return True if media image is accessible from outside the local network."""
        # Base64 images are handled locally and don't need proxying
        # URLs from local network (like local media servers) need proxying
        if self.coordinator.data.get("albumart") is not None:
            return True  # Base64 data is always accessible
        return False  # URLs might not be accessible remotely, so proxy them

    @property
    def media_image_hash(self) -> str | None:
        """Return a hash of the media image."""
        albumart = self.coordinator.data.get("albumart")
        albumart_url = self.coordinator.data.get("albumart_url")

        if albumart:
            hash_value = hashlib.md5(albumart).hexdigest()[:5]
            _LOGGER.debug("Generated hash for base64 image: %s", hash_value)
            return hash_value
        elif albumart_url:
            hash_value = hashlib.md5(albumart_url.encode()).hexdigest()[:5]
            _LOGGER.debug("Generated hash for URL image: %s", hash_value)
            return hash_value

        return None

    async def async_get_media_image(self) -> tuple[bytes | None, str | None]:
        """Fetch media image of current playing media."""
        _LOGGER.debug("async_get_media_image called")

        albumart = self.coordinator.data.get("albumart")
        albumart_url = self.coordinator.data.get("albumart_url")

        if albumart:
            _LOGGER.debug("Returning base64 image data (%d bytes)", len(albumart))
            return (albumart, "image/jpeg")
        elif albumart_url:
            # Use Home Assistant's built-in image fetching for URL-based images
            _LOGGER.debug("Fetching image from URL: %s", albumart_url)
            try:
                result = await async_fetch_image(_LOGGER, self.hass, albumart_url)
                if result[0]:
                    _LOGGER.debug("Successfully fetched image from URL (%d bytes, %s)", len(result[0]), result[1])
                else:
                    _LOGGER.debug("No image data returned from URL")
                return result
            except Exception as e:
                _LOGGER.warning("Failed to fetch album art from URL %s: %s", albumart_url, e)

        _LOGGER.debug("No media image available")
        return None, None

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Coordinator update received for %s", self._attr_unique_id)

        # Update position timestamp if position changed
        if self.coordinator.data.get("position") is not None:
            self._attr_media_position_updated_at = utcnow()

        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        """Send play command via MQTT."""
        play_topic = self._mqtt_config.get("play_topic")
        if not play_topic:
            _LOGGER.warning("Play command not available - no play_topic configured")
            return

        play_payload = self._mqtt_config.get("play_payload", "Play")
        await async_publish(self.hass, play_topic, play_payload)

    async def async_media_pause(self) -> None:
        """Send pause command via MQTT."""
        pause_topic = self._mqtt_config.get("pause_topic")
        if not pause_topic:
            _LOGGER.warning("Pause command not available - no pause_topic configured")
            return

        pause_payload = self._mqtt_config.get("pause_payload", "Pause")
        await async_publish(self.hass, pause_topic, pause_payload)

    async def async_media_stop(self) -> None:
        """Send stop command via MQTT."""
        stop_topic = self._mqtt_config.get("stop_topic")
        if not stop_topic:
            _LOGGER.warning("Stop command not available - no stop_topic configured")
            return

        stop_payload = self._mqtt_config.get("stop_payload", "Stop")
        await async_publish(self.hass, stop_topic, stop_payload)

    async def async_media_next_track(self) -> None:
        """Send next track command via MQTT."""
        next_topic = self._mqtt_config.get("next_topic")
        if not next_topic:
            _LOGGER.warning("Next track command not available - no next_topic configured")
            return

        next_payload = self._mqtt_config.get("next_payload", "Next")
        await async_publish(self.hass, next_topic, next_payload)

    async def async_media_previous_track(self) -> None:
        """Send previous track command via MQTT."""
        previous_topic = self._mqtt_config.get("previous_topic")
        if not previous_topic:
            _LOGGER.warning("Previous track command not available - no previous_topic configured")
            return

        previous_payload = self._mqtt_config.get("previous_payload", "Previous")
        await async_publish(self.hass, previous_topic, previous_payload)

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        volumeset_topic = self._mqtt_config.get("volumeset_topic")
        if not volumeset_topic:
            _LOGGER.warning("Volume set command not available - no volumeset_topic configured")
            return

        await async_publish(self.hass, volumeset_topic, round(volume, 2))

    async def async_media_seek(self, position: int) -> None:
        """Send seek command via MQTT."""
        seek_topic = self._mqtt_config.get("seek_topic")
        if not seek_topic:
            _LOGGER.warning("Seek command not available - no seek_topic configured")
            return

        await async_publish(self.hass, seek_topic, position)

    async def async_play_media(self, media_type: str, media_id: str, **kwargs: Any) -> None:
        """Send play media command via MQTT."""
        playmedia_topic = self._mqtt_config.get("playmedia_topic")
        if not playmedia_topic:
            _LOGGER.warning("Play media command not available - no playmedia_topic configured")
            return

        if media_source.is_media_source_id(media_id):
            sourced_media = await media_source.async_resolve_media(self.hass, media_id)
            media_type = sourced_media.mime_type
            media_id = async_process_play_media_url(self.hass, sourced_media.url)

        media_data = {
            "media_type": media_type,
            "media_id": media_id,
        }
        await async_publish(self.hass, playmedia_topic, json.dumps(media_data))

    async def async_browse_media(self, media_content_type: str, media_content_id: str) -> Any:
        """Implement the websocket media browsing helper."""
        if not self._mqtt_config.get("browse_media_topic"):
            _LOGGER.warning("Browse media not available - no browse_media_topic configured")
            return None

        return await media_source.async_browse_media(
            self.hass,
            media_content_id,
            content_filter=lambda item: bool(item.media_content_type),
        )
