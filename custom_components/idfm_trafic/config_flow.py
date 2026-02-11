"""Configuration flow pour IDFM Trafic."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import CONF_API_KEY, CONF_LINES, CONF_STATIONS, DOMAIN, LINES
from .idfm_api import IDFMApiClient

_LOGGER = logging.getLogger(__name__)


class IDFMTraficConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configuration flow pour IDFM Trafic."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialisation du flow."""
        self._api_key: str | None = None
        self._selected_lines: list[str] = []
        self._selected_stations: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Étape initiale - saisie de l'API key."""
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            
            # Vérifier l'API key
            client = IDFMApiClient(api_key)
            try:
                # Test avec une requête simple (RER A par exemple)
                test_data = await client.async_get_line_traffic("line:IDFM:C01742")
                await client.close()
                
                if test_data is not None:
                    self._api_key = api_key
                    return await self.async_step_select_lines()
                else:
                    errors["base"] = "invalid_api_key"
            except Exception as e:
                _LOGGER.error("Erreur lors de la validation de l'API key: %s", e)
                errors["base"] = "cannot_connect"
                await client.close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
        )

    async def async_step_select_lines(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Sélection des lignes à surveiller."""
        if user_input is not None:
            self._selected_lines = user_input.get(CONF_LINES, [])
            return await self.async_step_select_stations()

        # Créer les options de lignes groupées par type
        metro_lines = {k: v["name"] for k, v in LINES.items() if v["type"] == "metro"}
        rer_lines = {k: v["name"] for k, v in LINES.items() if v["type"] == "rer"}
        tram_lines = {k: v["name"] for k, v in LINES.items() if v["type"] == "tram"}

        return self.async_show_form(
            step_id="select_lines",
            data_schema=vol.Schema({
                vol.Optional(CONF_LINES, default=[]): cv.multi_select(
                    {**metro_lines, **rer_lines, **tram_lines}
                ),
            }),
            description_placeholders={
                "info": "Sélectionnez les lignes pour lesquelles vous voulez les infos trafic"
            },
        )

    async def async_step_select_stations(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Saisie manuelle des stations (ID ou recherche)."""
        if user_input is not None:
            stations_input = user_input.get("stations_input", "")
            
            # Parser les IDs de stations (séparés par des virgules)
            if stations_input:
                self._selected_stations = [
                    s.strip() for s in stations_input.split(",") if s.strip()
                ]
            
            # Créer l'entrée de configuration
            return self.async_create_entry(
                title="IDFM Trafic",
                data={
                    CONF_API_KEY: self._api_key,
                    CONF_LINES: self._selected_lines,
                    CONF_STATIONS: self._selected_stations,
                    "traffic_enabled": True,
                    "departures_enabled": True,
                },
            )

        return self.async_show_form(
            step_id="select_stations",
            data_schema=vol.Schema({
                vol.Optional("stations_input", default=""): str,
            }),
            description_placeholders={
                "info": "Entrez les IDs de stations séparés par des virgules (ex: stop_area:IDFM:71234,stop_area:IDFM:71235). Laissez vide pour ne surveiller que les lignes."
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> IDFMTraficOptionsFlow:
        """Options flow."""
        return IDFMTraficOptionsFlow(config_entry)


class IDFMTraficOptionsFlow(config_entries.OptionsFlow):
    """Options flow pour IDFM Trafic."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialisation de l'options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gestion des options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Options actuelles
        current_lines = self.config_entry.data.get(CONF_LINES, [])
        current_stations = self.config_entry.data.get(CONF_STATIONS, [])

        # Créer les options de lignes
        all_lines = {k: v["name"] for k, v in LINES.items()}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(CONF_LINES, default=current_lines): cv.multi_select(all_lines),
                vol.Optional("stations_input", default=",".join(current_stations)): str,
                vol.Optional("traffic_enabled", default=True): bool,
                vol.Optional("departures_enabled", default=True): bool,
            }),
        )
