"""Client API pour IDFM (Île-de-France Mobilités)."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

import aiohttp

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class IDFMApiClient:
    """Client pour l'API IDFM."""

    def __init__(self, api_key: str) -> None:
        """Initialisation du client API."""
        self.api_key = api_key
        self.session: aiohttp.ClientSession | None = None
        self._headers = {
            "apiKey": api_key,
            "Accept": "application/json",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtenir ou créer une session aiohttp."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _request(self, endpoint: str) -> dict[str, Any] | None:
        """Effectuer une requête à l'API."""
        url = f"{API_BASE_URL}/{endpoint}"
        
        try:
            session = await self._get_session()
            async with session.get(url, headers=self._headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error("Erreur API IDFM: status %s pour %s", response.status, url)
                    return None
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout lors de la requête à %s", url)
            return None
        except Exception as e:
            _LOGGER.error("Erreur lors de la requête à %s: %s", url, e)
            return None

    async def async_get_line_traffic(self, line_id: str) -> dict[str, Any] | None:
        """
        Récupérer les infos trafic d'une ligne.
        
        Args:
            line_id: ID de la ligne (ex: "line:IDFM:C01742" pour RER A)
        
        Returns:
            Informations de trafic de la ligne
        """
        endpoint = f"line_reports/lines/{line_id}/line_reports?"
        return await self._request(endpoint)

    async def async_get_station_departures(
        self, 
        stop_area_id: str, 
        count: int = 5
    ) -> dict[str, Any] | None:
        """
        Récupérer les prochains départs d'une station.
        
        Args:
            stop_area_id: ID de la station (ex: "stop_area:IDFM:...")
            count: Nombre de départs à récupérer
        
        Returns:
            Prochains départs de la station
        """
        endpoint = f"departures/{stop_area_id}?count={count}"
        return await self._request(endpoint)

    async def async_get_station_traffic(self, stop_area_id: str) -> dict[str, Any] | None:
        """
        Récupérer les infos trafic affectant une station.
        
        Args:
            stop_area_id: ID de la station
        
        Returns:
            Informations de trafic de la station
        """
        # L'API IDFM peut retourner les perturbations par station
        endpoint = f"traffic_reports/{stop_area_id}"
        return await self._request(endpoint)

    async def async_search_stations(self, query: str) -> list[dict[str, Any]]:
        """
        Rechercher des stations par nom.
        
        Args:
            query: Nom de la station à rechercher
        
        Returns:
            Liste des stations correspondantes
        """
        endpoint = f"coverage/fr-idf/places?q={query}&type[]=stop_area"
        result = await self._request(endpoint)
        
        if result and "places" in result:
            return result["places"]
        return []

    async def async_get_all_data(self) -> dict[str, Any]:
        """
        Méthode pour le coordinateur - récupère toutes les données nécessaires.
        À personnaliser selon la configuration de l'utilisateur.
        """
        # Cette méthode sera appelée par le coordinateur
        # Pour l'instant, retourne un dict vide
        return {}

    async def close(self) -> None:
        """Fermer la session aiohttp."""
        if self.session and not self.session.closed:
            await self.session.close()


class IDFMTrafficParser:
    """Parser pour les données de trafic IDFM."""

    @staticmethod
    def parse_line_reports(data: dict[str, Any]) -> dict[str, Any]:
        """
        Parser les rapports de trafic d'une ligne.
        
        Returns:
            {
                "status": "normal" | "perturbation" | "travaux",
                "severity": "information" | "perturbation" | "blocking",
                "messages": [{"title": "...", "message": "..."}],
                "updated_at": datetime
            }
        """
        if not data or "line_reports" not in data:
            return {
                "status": "unknown",
                "severity": "information",
                "messages": [],
                "updated_at": datetime.now(),
            }

        line_reports = data.get("line_reports", [])
        
        if not line_reports:
            return {
                "status": "normal",
                "severity": "information",
                "messages": [],
                "updated_at": datetime.now(),
            }

        # Analyser les perturbations
        messages = []
        max_severity = "information"
        
        for report in line_reports:
            pt_objects = report.get("pt_objects", [])
            
            for pt_obj in pt_objects:
                line_reports_list = pt_obj.get("line_reports", [])
                
                for line_report in line_reports_list:
                    severity = line_report.get("severity", {}).get("name", "information")
                    
                    # Déterminer la sévérité maximale
                    if severity == "blocking":
                        max_severity = "blocking"
                    elif severity == "perturbation" and max_severity != "blocking":
                        max_severity = "perturbation"
                    
                    # Extraire les messages
                    message_obj = line_report.get("message", {})
                    if message_obj:
                        messages.append({
                            "title": message_obj.get("title", ""),
                            "message": message_obj.get("text", ""),
                            "severity": severity,
                        })

        # Déterminer le statut global
        if max_severity == "blocking":
            status = "perturbation"
        elif max_severity == "perturbation":
            status = "perturbation"
        else:
            status = "normal" if not messages else "information"

        return {
            "status": status,
            "severity": max_severity,
            "messages": messages,
            "updated_at": datetime.now(),
        }

    @staticmethod
    def parse_departures(data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Parser les prochains départs.
        
        Returns:
            [
                {
                    "line": "RER A",
                    "direction": "Cergy",
                    "departure_time": datetime,
                    "time_remaining": "3 min",
                    "platform": "1",
                }
            ]
        """
        if not data or "departures" not in data:
            return []

        departures = []
        
        for departure in data.get("departures", []):
            stop_date_time = departure.get("stop_date_time", {})
            display_info = departure.get("display_informations", {})
            
            # Heure de départ
            departure_dt_str = stop_date_time.get("departure_date_time")
            if departure_dt_str:
                departure_dt = datetime.strptime(departure_dt_str, "%Y%m%dT%H%M%S")
            else:
                continue
            
            # Temps restant
            now = datetime.now()
            time_diff = (departure_dt - now).total_seconds()
            
            if time_diff < 60:
                time_remaining = "À l'approche"
            else:
                minutes = int(time_diff / 60)
                time_remaining = f"{minutes} min"
            
            departures.append({
                "line": display_info.get("label", ""),
                "line_code": display_info.get("code", ""),
                "direction": display_info.get("direction", ""),
                "departure_time": departure_dt,
                "time_remaining": time_remaining,
                "platform": stop_date_time.get("departure_platform", ""),
                "headsign": display_info.get("headsign", ""),
                "network": display_info.get("network", ""),
            })

        return sorted(departures, key=lambda x: x["departure_time"])
