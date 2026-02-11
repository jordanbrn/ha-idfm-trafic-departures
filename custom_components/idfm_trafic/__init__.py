"""
IDFM Trafic - Integration pour Home Assistant
Infos trafic et prochains départs pour Métro, RER, Train et Tram d'Île-de-France
"""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .idfm_api import IDFMApiClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuration de l'intégration IDFM Trafic."""
    hass.data.setdefault(DOMAIN, {})
    
    api_key = entry.data["api_key"]
    client = IDFMApiClient(api_key)
    
    # Coordinateur pour les mises à jour
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=client.async_get_all_data,
        update_interval=timedelta(seconds=60),
    )
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Déchargement de l'intégration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
