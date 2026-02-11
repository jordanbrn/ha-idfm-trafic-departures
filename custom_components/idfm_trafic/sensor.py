"""Sensors pour l'intégration IDFM Trafic."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, LINES
from .idfm_api import IDFMApiClient, IDFMTrafficParser

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configuration des sensors depuis une config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    
    entities = []
    
    # Récupérer les lignes configurées
    lines = entry.data.get("lines", [])
    stations = entry.data.get("stations", [])
    
    traffic_enabled = entry.data.get("traffic_enabled", True)
    departures_enabled = entry.data.get("departures_enabled", True)
    
    # Créer les sensors de trafic par ligne
    if traffic_enabled:
        for line_id in lines:
            entities.append(
                IDFMLineTrafficSensor(coordinator, client, line_id, entry.entry_id)
            )
    
    # Créer les sensors de départs par station
    if departures_enabled:
        for station_id in stations:
            entities.append(
                IDFMStationDeparturesSensor(coordinator, client, station_id, entry.entry_id)
            )
    
    async_add_entities(entities)


class IDFMLineTrafficSensor(CoordinatorEntity, SensorEntity):
    """Sensor pour les infos trafic d'une ligne."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: IDFMApiClient,
        line_id: str,
        entry_id: str,
    ) -> None:
        """Initialisation du sensor."""
        super().__init__(coordinator)
        self._client = client
        self._line_id = line_id
        self._entry_id = entry_id
        self._attr_has_entity_name = True
        
        # Récupérer les infos de la ligne
        line_info = LINES.get(line_id, {})
        self._line_name = line_info.get("name", line_id)
        self._line_color = line_info.get("color", "#000000")
        
        self._attr_name = f"{self._line_name} Trafic"
        self._attr_unique_id = f"{entry_id}_{line_id}_traffic"
        
        self._traffic_data = None

    @property
    def native_value(self) -> str:
        """Valeur du sensor (statut)."""
        if self._traffic_data:
            return self._traffic_data.get("status", "unknown")
        return "unknown"

    @property
    def icon(self) -> str:
        """Icône du sensor."""
        if self._traffic_data:
            status = self._traffic_data.get("status", "unknown")
            if status == "normal":
                return "mdi:check-circle"
            elif status == "perturbation":
                return "mdi:alert-circle"
            elif status == "information":
                return "mdi:information"
        return "mdi:train"

    @property
    def icon_color(self) -> str:
        """Couleur de l'icône selon la sévérité."""
        if self._traffic_data:
            severity = self._traffic_data.get("severity", "information")
            if severity == "blocking":
                return "#FF0000"  # Rouge
            elif severity == "perturbation":
                return "#FF8C00"  # Orange
            elif severity == "information":
                return "#FFA500"  # Orange clair
        return "#00FF00"  # Vert (normal)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Attributs supplémentaires."""
        if not self._traffic_data:
            return {}
        
        severity = self._traffic_data.get("severity", "information")
        
        # Déterminer la couleur selon la sévérité
        if severity == "blocking":
            status_color = "#FF0000"  # Rouge
        elif severity == "perturbation":
            status_color = "#FF8C00"  # Orange
        elif severity == "information":
            status_color = "#FFA500"  # Orange clair
        else:
            status_color = "#00FF00"  # Vert (normal)
        
        return {
            "line_id": self._line_id,
            "line_name": self._line_name,
            "line_color": self._line_color,
            "severity": severity,
            "status_color": status_color,
            "messages": self._traffic_data.get("messages", []),
            "updated_at": self._traffic_data.get("updated_at"),
            "message_count": len(self._traffic_data.get("messages", [])),
        }

    async def async_added_to_hass(self) -> None:
        """Quand l'entité est ajoutée à Home Assistant."""
        await super().async_added_to_hass()
        # Forcer une première mise à jour
        await self._async_update_data()

    async def async_update(self) -> None:
        """Mise à jour via le coordinateur."""
        await self._async_update_data()

    async def _async_update_data(self) -> None:
        """Récupérer les données de l'API."""
        try:
            data = await self._client.async_get_line_traffic(self._line_id)
            if data:
                self._traffic_data = IDFMTrafficParser.parse_line_reports(data)
                _LOGGER.debug("Traffic data updated for %s: %s", self._line_name, self._traffic_data.get("status"))
        except Exception as e:
            _LOGGER.error("Error updating traffic for %s: %s", self._line_name, e)


class IDFMStationDeparturesSensor(CoordinatorEntity, SensorEntity):
    """Sensor pour les prochains départs d'une station."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: IDFMApiClient,
        station_id: str,
        entry_id: str,
    ) -> None:
        """Initialisation du sensor."""
        super().__init__(coordinator)
        self._client = client
        self._station_id = station_id
        self._entry_id = entry_id
        self._attr_has_entity_name = True
        
        # Le nom de la station sera récupéré depuis l'API
        self._station_name = station_id.split(":")[-1]  # Fallback
        
        self._attr_name = f"{self._station_name} Départs"
        self._attr_unique_id = f"{entry_id}_{station_id}_departures"
        
        self._departures = []

    @property
    def native_value(self) -> int:
        """Valeur du sensor (nombre de départs)."""
        return len(self._departures)

    @property
    def icon(self) -> str:
        """Icône du sensor."""
        return "mdi:clock-outline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Attributs supplémentaires."""
        attributes = {
            "station_id": self._station_id,
            "station_name": self._station_name,
            "departures": self._departures,
        }
        
        # Ajouter les 5 prochains départs comme attributs individuels
        for i, departure in enumerate(self._departures[:5], 1):
            attributes[f"departure_{i}"] = {
                "line": departure.get("line"),
                "direction": departure.get("direction"),
                "time": departure.get("time_remaining"),
                "platform": departure.get("platform"),
            }
        
        # Prochain départ
        if self._departures:
            next_dep = self._departures[0]
            attributes["next_departure"] = {
                "line": next_dep.get("line"),
                "direction": next_dep.get("direction"),
                "time": next_dep.get("time_remaining"),
            }
        
        return attributes

    async def async_added_to_hass(self) -> None:
        """Quand l'entité est ajoutée à Home Assistant."""
        await super().async_added_to_hass()
        # Forcer une première mise à jour
        await self._async_update_data()

    async def async_update(self) -> None:
        """Mise à jour via le coordinateur."""
        await self._async_update_data()

    async def _async_update_data(self) -> None:
        """Récupérer les données de l'API."""
        try:
            data = await self._client.async_get_station_departures(self._station_id, count=10)
            if data:
                self._departures = IDFMTrafficParser.parse_departures(data)
                _LOGGER.debug("Departures updated for %s: %d trains", self._station_name, len(self._departures))
        except Exception as e:
            _LOGGER.error("Error updating departures for %s: %s", self._station_name, e)


class IDFMStationTrafficSensor(CoordinatorEntity, SensorEntity):
    """Sensor pour les infos trafic affectant une station."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: IDFMApiClient,
        station_id: str,
        entry_id: str,
    ) -> None:
        """Initialisation du sensor."""
        super().__init__(coordinator)
        self._client = client
        self._station_id = station_id
        self._entry_id = entry_id
        self._attr_has_entity_name = True
        
        self._station_name = station_id.split(":")[-1]
        
        self._attr_name = f"{self._station_name} Trafic"
        self._attr_unique_id = f"{entry_id}_{station_id}_traffic"
        
        self._traffic_data = None

    @property
    def native_value(self) -> str:
        """Valeur du sensor (statut)."""
        if self._traffic_data:
            return self._traffic_data.get("status", "unknown")
        return "unknown"

    @property
    def icon(self) -> str:
        """Icône du sensor."""
        if self._traffic_data:
            status = self._traffic_data.get("status", "unknown")
            if status == "normal":
                return "mdi:check-circle"
            elif status == "perturbation":
                return "mdi:alert-circle"
        return "mdi:train-variant"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Attributs supplémentaires."""
        if not self._traffic_data:
            return {}
        
        return {
            "station_id": self._station_id,
            "station_name": self._station_name,
            "severity": self._traffic_data.get("severity", "information"),
            "messages": self._traffic_data.get("messages", []),
            "updated_at": self._traffic_data.get("updated_at"),
        }

    async def async_update(self) -> None:
        """Mise à jour des données."""
        data = await self._client.async_get_station_traffic(self._station_id)
        if data:
            self._traffic_data = IDFMTrafficParser.parse_line_reports(data)
