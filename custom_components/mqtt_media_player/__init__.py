"""MQTT Media Player integration."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import MQTTMediaPlayerCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration using YAML (if needed)."""
    _LOGGER.debug("async_setup called with config: %s", config)
    return True  # Allow UI-only configuration


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MQTT Media Player from config entry."""
    _LOGGER.info("Setting up MQTT Media Player integration for entry: %s", entry.title)
    _LOGGER.debug("Entry data: %s", entry.data)

    # Initialize coordinator
    coordinator = MQTTMediaPlayerCoordinator(hass, entry)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Set up coordinator MQTT subscriptions
    await coordinator.async_added_to_hass()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.debug("Successfully set up MQTT Media Player integration")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of the integration."""
    _LOGGER.info("Unloading MQTT Media Player integration for entry: %s", entry.title)

    # Unload platforms
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Clean up coordinator
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        coordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_will_remove_from_hass()
        del hass.data[DOMAIN][entry.entry_id]

        # Remove domain data if empty
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]

    _LOGGER.debug("Unload result: %s", result)
    return result
