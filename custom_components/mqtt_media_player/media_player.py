import base64
import hashlib
import json
import logging


from homeassistant.components import media_source
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    async_fetch_image,
)
from homeassistant.components.media_player.browse_media import (
    async_process_play_media_url,
)
from homeassistant.components.media_player.const import MediaPlayerEntityFeature
from homeassistant.components.mqtt import (
    async_publish,
    async_subscribe,
)
from homeassistant.util.dt import utcnow

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup entry point."""
    _LOGGER.info("Setting up MQTT Media Player entity for: %s", config_entry.title)
    _LOGGER.debug("Config entry data: %s", config_entry.data)

    player = MQTTMediaPlayer(hass, config_entry)
    async_add_entities([player])

    # Subscribe to the config topic to get media player configuration dynamically
    CONFIG_TOPIC = f"homeassistant/media_player/{config_entry.title}/config"
    _LOGGER.info("Subscribing to config topic: %s", CONFIG_TOPIC)
    await async_subscribe(hass, CONFIG_TOPIC, player.handle_config)


class MQTTMediaPlayer(MediaPlayerEntity):
    """Representation of a MQTT Media Player."""

    def __init__(self, hass, config_entry):
        """Initialize the MQTT Media Player."""
        _LOGGER.debug(
            "Initializing MQTT Media Player for config entry: %s", config_entry.title
        )
        self._hass = hass
        self._config_entry = config_entry
        self._name = None
        # self._domain = __name__.split(".")[-2]
        self._state = None
        self._volume = 0.0
        self._media_title = None
        self._media_artist = None
        self._media_album = None
        self._album_art = None
        self._album_art_url = None
        self._duration = None
        self._position = None
        self._available = None
        self._media_type = "music"
        self._subscribed = []
        _LOGGER.debug("MQTT Media Player initialized with default values")

    async def handle_config(self, message):
        """Handle incoming configuration from MQTT."""
        config = json.loads(message.payload)
        _LOGGER.info(f"Received configuration: {config}")
        self._name = config.get("name")

        # Set the MQTT topics from the configuration
        self._availability_topics = {
            "availability_topic": config.get("availability_topic"),
            "available": config.get("availability", {}).get(
                "payload_available", "online"
            ),
            "not_available": config.get("availability", {}).get(
                "payload_not_available", "offline"
            ),
        }
        self._state_topics = {
            "state_topic": config.get("state_topic"),
            "title_topic": config.get("title_topic"),
            "artist_topic": config.get("artist_topic"),
            "album_topic": config.get("album_topic"),
            "duration_topic": config.get("duration_topic"),
            "position_topic": config.get("position_topic"),
            "volume_topic": config.get("volume_topic"),
            "albumart_topic": config.get("albumart_topic"),
            "mediatype_topic": config.get("mediatype_topic"),
        }
        self._cmd_topics = {
            "volumeset_topic": config.get("volumeset_topic"),
            "play_topic": config.get("play_topic"),
            "play_payload": config.get("play_payload", "Play"),
            "pause_topic": config.get("pause_topic"),
            "pause_payload": config.get("pause_payload", "Pause"),
            "stop_topic": config.get("stop_topic"),
            "stop_payload": config.get("stop_payload", "Stop"),
            "next_topic": config.get("next_topic"),
            "next_payload": config.get("next_payload", "Next"),
            "previous_topic": config.get("previous_topic"),
            "previous_payload": config.get("previous_payload", "Previous"),
            "playmedia_topic": config.get("playmedia_topic"),
            "seek_topic": config.get("seek_topic"),
        }

        # Unsubscribe from subscribed topics
        for subscription in self._subscribed:
            subscription()
        self._subscribed = []

        # Subscribe to relevant state topics
        _LOGGER.debug("Subscribing to state topics")
        if (check_topic := self._state_topics["state_topic"]) is not None:
            _LOGGER.debug("Subscribing to state topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_state)
            )
        if (check_topic := self._state_topics["title_topic"]) is not None:
            _LOGGER.debug("Subscribing to title topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_title)
            )
        if (check_topic := self._state_topics["artist_topic"]) is not None:
            _LOGGER.debug("Subscribing to artist topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_artist)
            )
        if (check_topic := self._state_topics["album_topic"]) is not None:
            _LOGGER.debug("Subscribing to album topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_album)
            )
        if (check_topic := self._state_topics["duration_topic"]) is not None:
            _LOGGER.debug("Subscribing to duration topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_duration)
            )
        if (check_topic := self._state_topics["position_topic"]) is not None:
            _LOGGER.debug("Subscribing to position topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_position)
            )
        if (check_topic := self._state_topics["volume_topic"]) is not None:
            _LOGGER.debug("Subscribing to volume topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_volume)
            )
        if (check_topic := self._state_topics["albumart_topic"]) is not None:
            _LOGGER.debug("Subscribing to albumart topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_albumart)
            )
        if (check_topic := self._state_topics["mediatype_topic"]) is not None:
            _LOGGER.debug("Subscribing to mediatype topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_mediatype)
            )
        if (check_topic := self._availability_topics["availability_topic"]) is not None:
            _LOGGER.debug("Subscribing to availability topic: %s", check_topic)
            self._subscribed.append(
                await async_subscribe(self._hass, check_topic, self.handle_availability)
            )

        _LOGGER.info("Successfully subscribed to %d MQTT topics", len(self._subscribed))

    @property
    def supported_features(self):
        """Return supported features based on available command topics."""
        features = MediaPlayerEntityFeature(0)
        
        # Always support browse media since it's implemented
        features |= MediaPlayerEntityFeature.BROWSE_MEDIA
        
        # Dynamic features based on available command topics
        if self._cmd_topics.get("play_topic"):
            features |= MediaPlayerEntityFeature.PLAY
            _LOGGER.debug("Added PLAY feature")
            
        if self._cmd_topics.get("pause_topic"):
            features |= MediaPlayerEntityFeature.PAUSE
            _LOGGER.debug("Added PAUSE feature")
            
        if self._cmd_topics.get("stop_topic"):
            features |= MediaPlayerEntityFeature.STOP
            _LOGGER.debug("Added STOP feature")
            
        if self._cmd_topics.get("volumeset_topic"):
            features |= MediaPlayerEntityFeature.VOLUME_SET
            features |= MediaPlayerEntityFeature.VOLUME_STEP
            _LOGGER.debug("Added VOLUME_SET and VOLUME_STEP features")
            
        if self._cmd_topics.get("next_topic"):
            features |= MediaPlayerEntityFeature.NEXT_TRACK
            _LOGGER.debug("Added NEXT_TRACK feature")
            
        if self._cmd_topics.get("previous_topic"):
            features |= MediaPlayerEntityFeature.PREVIOUS_TRACK
            _LOGGER.debug("Added PREVIOUS_TRACK feature")
            
        if self._cmd_topics.get("playmedia_topic"):
            features |= MediaPlayerEntityFeature.PLAY_MEDIA
            _LOGGER.debug("Added PLAY_MEDIA feature")
            
        if self._cmd_topics.get("seek_topic"):
            features |= MediaPlayerEntityFeature.SEEK
            _LOGGER.debug("Added SEEK feature")
            
        _LOGGER.debug("Supported features: %s", features)
        return features

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._config_entry.title

    @property
    def state(self):
        if self._available is False:
            return "unavailable"
        return self._state

    @property
    def volume_level(self):
        return self._volume

    @property
    def media_title(self):
        return self._media_title

    @property
    def media_artist(self):
        return self._media_artist

    @property
    def media_album_name(self):
        return self._media_album

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return self._media_type

    @property
    def media_position(self):
        """Position of player in percentage."""
        return self._position

    @property
    def media_duration(self):
        """Duration of current playing media in percentage."""
        return self._duration

    @property
    def media_image_url(self):
        """URL for media image."""
        if self._album_art_url:
            _LOGGER.debug("Returning media image URL: %s", self._album_art_url)
            return self._album_art_url
        _LOGGER.debug("No media image URL available")
        return None

    @property
    def media_image_remotely_accessible(self):
        """Return True if media image is accessible from outside the local network."""
        # Base64 images are handled locally and don't need proxying
        # URLs from local network (like local media servers) need proxying
        if self._album_art is not None:
            _LOGGER.debug("Media image is base64 data, remotely accessible: True")
            return True  # Base64 data is always accessible
        _LOGGER.debug("Media image is URL, remotely accessible: False (needs proxying)")
        return False  # URLs might not be accessible remotely, so proxy them

    @property
    def media_image_hash(self):
        """Hash value for media image."""
        if self._album_art:
            hash_value = hashlib.md5(self._album_art).hexdigest()[:5]
            _LOGGER.debug("Generated hash for base64 image: %s", hash_value)
            return hash_value
        elif self._album_art_url:
            hash_value = hashlib.md5(self._album_art_url.encode()).hexdigest()[:5]
            _LOGGER.debug("Generated hash for URL image: %s", hash_value)
            return hash_value
        _LOGGER.debug("No media image available for hash generation")
        return None

    async def async_get_media_image(self):
        """Fetch media image of current playing image."""
        _LOGGER.debug("async_get_media_image called")
        if self._album_art:
            _LOGGER.debug("Returning base64 image data (%d bytes)", len(self._album_art))
            return (self._album_art, "image/jpeg")
        elif self._album_art_url:
            # Use Home Assistant's built-in image fetching for URL-based images
            _LOGGER.debug("Fetching image from URL: %s", self._album_art_url)
            try:
                result = await async_fetch_image(_LOGGER, self._hass, self._album_art_url)
                if result[0]:
                    _LOGGER.debug("Successfully fetched image from URL (%d bytes, %s)", len(result[0]), result[1])
                else:
                    _LOGGER.debug("No image data returned from URL")
                return result
            except Exception as e:
                _LOGGER.warning("Failed to fetch album art from URL %s: %s", self._album_art_url, e)
        _LOGGER.debug("No media image available")
        return None, None

    async def handle_availability(self, message):
        """Update the media player availability status."""
        if message.payload == self._availability_topics["available"]:
            self._available = True
        elif message.payload == self._availability_topics["not_available"]:
            self._available = False
        self.async_write_ha_state()

    async def handle_state(self, message):
        """Update the player state based on the MQTT state topic."""
        print("Changed state:", message.payload)
        self._state = message.payload
        self.async_write_ha_state()

    async def handle_title(self, message):
        """Update the media title based on the MQTT title topic."""
        self._media_title = message.payload
        self.async_write_ha_state()

    async def handle_artist(self, message):
        """Update the media artist based on the MQTT artist topic."""
        self._media_artist = message.payload
        self.async_write_ha_state()

    async def handle_album(self, message):
        """Update the media album based on the MQTT album topic."""
        self._media_album = message.payload
        self.async_write_ha_state()

    async def handle_duration(self, message):
        """Update the media duration based on the MQTT duration topic."""
        try:
            self._duration = int(message.payload)
        except (ValueError, TypeError):
            self._duration = None
        self.async_write_ha_state()

    async def handle_position(self, message):
        """Update the media position based on the MQTT position topic."""
        try:
            self._position = int(message.payload)
            self._attr_media_position_updated_at = utcnow()
        except (ValueError, TypeError):
            self._position = None
        self.async_write_ha_state()

    async def handle_volume(self, message):
        """Update the volume based on the MQTT volume topic."""
        self._volume = float(message.payload)
        self.async_write_ha_state()

    async def handle_albumart(self, message):
        """Update the album art based on the MQTT album art topic."""
        payload = message.payload.strip()
        
        # Check if payload is a URL (starts with http:// or https://)
        if payload.startswith(('http://', 'https://')):
            _LOGGER.debug("Album art payload is URL: %s", payload)
            self._album_art_url = payload
            self._album_art = None
        else:
            # Assume it's base64 encoded data
            _LOGGER.debug("Album art payload is base64 data")
            try:
                self._album_art = base64.b64decode(payload.replace("\n", ""))
                self._album_art_url = None
            except Exception as e:
                _LOGGER.warning("Failed to decode base64 album art: %s", e)
                self._album_art = None
                self._album_art_url = None
        
        self.async_write_ha_state()

    async def handle_mediatype(self, message):
        """Update the media media_type based on the MQTT media_type topic."""
        self._media_type = message.payload
        self.async_write_ha_state()

    async def async_media_play(self):
        """Send play command via MQTT."""
        if not self._cmd_topics.get("play_topic"):
            _LOGGER.warning("Play command not available - no play_topic configured")
            return
        await async_publish(
            self._hass, self._cmd_topics["play_topic"], self._cmd_topics["play_payload"]
        )

    async def async_media_pause(self):
        """Send pause command via MQTT."""
        if not self._cmd_topics.get("pause_topic"):
            _LOGGER.warning("Pause command not available - no pause_topic configured")
            return
        await async_publish(
            self._hass,
            self._cmd_topics["pause_topic"],
            self._cmd_topics["pause_payload"],
        )

    async def async_media_stop(self):
        """Send stop command via MQTT."""
        if not self._cmd_topics.get("stop_topic"):
            _LOGGER.warning("Stop command not available - no stop_topic configured")
            return
        await async_publish(
            self._hass,
            self._cmd_topics["stop_topic"],
            self._cmd_topics["stop_payload"],
        )

    async def async_media_next_track(self):
        """Send next track command via MQTT."""
        if not self._cmd_topics.get("next_topic"):
            _LOGGER.warning("Next track command not available - no next_topic configured")
            return
        await async_publish(
            self._hass, self._cmd_topics["next_topic"], self._cmd_topics["next_payload"]
        )

    async def async_media_previous_track(self):
        """Send previous track command via MQTT."""
        if not self._cmd_topics.get("previous_topic"):
            _LOGGER.warning("Previous track command not available - no previous_topic configured")
            return
        await async_publish(
            self._hass,
            self._cmd_topics["previous_topic"],
            self._cmd_topics["previous_payload"],
        )

    async def async_set_volume_level(self, volume):
        """Set the volume level via MQTT."""
        if not self._cmd_topics.get("volumeset_topic"):
            _LOGGER.warning("Volume set command not available - no volumeset_topic configured")
            return
        self._volume = round(float(volume), 2)
        await async_publish(
            self._hass, self._cmd_topics["volumeset_topic"], self._volume
        )

    async def async_media_seek(self, position):
        """Send seek command via MQTT."""
        if not self._cmd_topics.get("seek_topic"):
            _LOGGER.warning("Seek command not available - no seek_topic configured")
            return
        await async_publish(
            self._hass, self._cmd_topics["seek_topic"], position
        )

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Sends media to play."""
        if not self._cmd_topics.get("playmedia_topic"):
            _LOGGER.warning("Play media command not available - no playmedia_topic configured")
            return
        if media_source.is_media_source_id(media_id):
            sourced_media = await media_source.async_resolve_media(self.hass, media_id)
            media_type = sourced_media.mime_type
            media_id = async_process_play_media_url(self.hass, sourced_media.url)
        media = {
            "media_type": media_type,
            "media_id": media_id,
        }
        await async_publish(
            self._hass, self._cmd_topics["playmedia_topic"], json.dumps(media)
        )

    async def async_browse_media(self, media_content_type, media_content_id):
        """Implement the websocket media browsing helper."""
        return await media_source.async_browse_media(
            self.hass,
            media_content_id,
            content_filter=lambda item: bool(item.media_content_type),
        )
