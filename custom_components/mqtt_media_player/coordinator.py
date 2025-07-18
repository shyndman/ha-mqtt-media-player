"""MQTT Media Player Data Update Coordinator."""
import logging
import math

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.mqtt import async_subscribe
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MQTTMediaPlayerCoordinator(DataUpdateCoordinator):
    """Coordinate MQTT data for media player entities."""

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

        # Initialize data structure
        self.data = {
            "state": None,
            "title": None,
            "artist": None,
            "album": None,
            "duration": None,
            "position": None,
            "volume": None,
            "albumart": None,
            "albumart_url": None,
            "mediatype": "music",
            "available": None,
        }

        _LOGGER.debug("Initialized coordinator for: %s", self.mqtt_config.get("name"))

    async def _async_update_data(self):
        """Fetch data from MQTT - not used since we're push-based."""
        return self.data

    async def async_added_to_hass(self):
        """Subscribe to MQTT topics when coordinator is added."""
        _LOGGER.debug("Setting up MQTT subscriptions")

        # Subscribe to state topics
        state_topics = {
            "state_topic": self._handle_state,
            "title_topic": self._handle_title,
            "artist_topic": self._handle_artist,
            "album_topic": self._handle_album,
            "duration_topic": self._handle_duration,
            "position_topic": self._handle_position,
            "volume_topic": self._handle_volume,
            "albumart_topic": self._handle_albumart,
            "mediatype_topic": self._handle_mediatype,
        }

        for topic_key, handler in state_topics.items():
            topic = self.mqtt_config.get(topic_key)
            if topic:
                _LOGGER.debug("Subscribing to %s: %s", topic_key, topic)
                subscription = await async_subscribe(
                    self.hass, topic, handler, qos=0
                )
                self._subscriptions.append(subscription)

        # Subscribe to availability topic
        availability_topic = self.mqtt_config.get("availability_topic")
        if availability_topic:
            _LOGGER.debug("Subscribing to availability topic: %s", availability_topic)
            subscription = await async_subscribe(
                self.hass, availability_topic, self._handle_availability, qos=0
            )
            self._subscriptions.append(subscription)

        _LOGGER.info("Successfully subscribed to %d MQTT topics", len(self._subscriptions))

    async def async_will_remove_from_hass(self):
        """Clean up MQTT subscriptions."""
        _LOGGER.debug("Cleaning up MQTT subscriptions")
        for subscription in self._subscriptions:
            subscription()
        self._subscriptions.clear()

    @callback
    def _handle_state(self, message):
        """Handle state updates."""
        _LOGGER.debug("State update: %s", message.payload)
        self.data["state"] = message.payload
        self.async_set_updated_data(self.data)

    @callback
    def _handle_title(self, message):
        """Handle title updates."""
        _LOGGER.debug("Title update: %s", message.payload)
        self.data["title"] = message.payload
        self.async_set_updated_data(self.data)

    @callback
    def _handle_artist(self, message):
        """Handle artist updates."""
        _LOGGER.debug("Artist update: %s", message.payload)
        self.data["artist"] = message.payload
        self.async_set_updated_data(self.data)

    @callback
    def _handle_album(self, message):
        """Handle album updates."""
        _LOGGER.debug("Album update: %s", message.payload)
        self.data["album"] = message.payload
        self.async_set_updated_data(self.data)

    @callback
    def _handle_duration(self, message):
        """Handle duration updates."""
        try:
            duration = float(message.payload)
            duration_int = math.ceil(duration)
            _LOGGER.debug("Duration update: %s (rounded from %s)", duration_int, duration)
            self.data["duration"] = duration_int
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid duration value: %s", message.payload)
            self.data["duration"] = None
        self.async_set_updated_data(self.data)

    @callback
    def _handle_position(self, message):
        """Handle position updates."""
        try:
            position = float(message.payload)
            position_int = math.ceil(position)
            _LOGGER.debug("Position update: %s (rounded from %s)", position_int, position)
            self.data["position"] = position_int
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid position value: %s", message.payload)
            self.data["position"] = None
        self.async_set_updated_data(self.data)

    @callback
    def _handle_volume(self, message):
        """Handle volume updates."""
        try:
            volume = float(message.payload)
            _LOGGER.debug("Volume update: %s", volume)
            self.data["volume"] = volume
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid volume value: %s", message.payload)
            self.data["volume"] = None
        self.async_set_updated_data(self.data)

    @callback
    def _handle_albumart(self, message):
        """Handle album art updates."""
        import base64

        payload = message.payload.strip()

        # Check if payload is a URL (starts with http:// or https://)
        if payload.startswith(('http://', 'https://')):
            _LOGGER.debug("Album art payload is URL: %s", payload)
            self.data["albumart_url"] = payload
            self.data["albumart"] = None
        else:
            # Assume it's base64 encoded data
            _LOGGER.debug("Album art payload is base64 data")
            try:
                albumart_data = base64.b64decode(payload.replace("\n", ""))
                self.data["albumart"] = albumart_data
                self.data["albumart_url"] = None
            except Exception as e:
                _LOGGER.warning("Failed to decode base64 album art: %s", e)
                self.data["albumart"] = None
                self.data["albumart_url"] = None

        self.async_set_updated_data(self.data)

    @callback
    def _handle_mediatype(self, message):
        """Handle media type updates."""
        _LOGGER.debug("Media type update: %s", message.payload)
        self.data["mediatype"] = message.payload
        self.async_set_updated_data(self.data)

    @callback
    def _handle_availability(self, message):
        """Handle availability updates."""
        availability_config = self.mqtt_config.get("availability", {})
        available_payload = availability_config.get("payload_available", "online")
        not_available_payload = availability_config.get("payload_not_available", "offline")

        if message.payload == available_payload:
            _LOGGER.debug("Device available")
            self.data["available"] = True
        elif message.payload == not_available_payload:
            _LOGGER.debug("Device not available")
            self.data["available"] = False
        else:
            _LOGGER.debug("Unknown availability payload: %s", message.payload)

        self.async_set_updated_data(self.data)
