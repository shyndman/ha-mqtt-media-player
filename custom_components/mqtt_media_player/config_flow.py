import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from homeassistant.const import CONF_NAME
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class MqttMediaPlayerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        _LOGGER.debug(
            "Config flow async_step_user called with user_input: %s", user_input
        )
        errors = {}
        if user_input is not None:
            _LOGGER.info("Creating config entry with title: %s", user_input[CONF_NAME])
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        _LOGGER.debug("Showing user form for initial setup")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        _LOGGER.debug(
            "Options flow async_step_init called with user_input: %s", user_input
        )
        if user_input is not None:
            _LOGGER.info(
                "Creating options entry for config: %s", self.config_entry.title
            )
            return self.async_create_entry(title="", data=user_input)

        _LOGGER.debug("Showing options form")
        return self.async_show_form(step_id="init", data_schema=vol.Schema({}))
