import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration using YAML (if needed)."""
    _LOGGER.debug("async_setup called with config: %s", config)
    return True  # Allow UI-only configuration

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from the UI."""
    _LOGGER.info("Setting up MQTT Media Player integration for entry: %s", entry.title)
    _LOGGER.debug("Entry data: %s", entry.data)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    )
    _LOGGER.debug("Successfully set up platforms: %s", PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of the integration."""
    _LOGGER.info("Unloading MQTT Media Player integration for entry: %s", entry.title)
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    _LOGGER.debug("Unload result: %s", result)
    return result
