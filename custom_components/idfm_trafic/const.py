"""Constantes pour l'intégration IDFM Trafic."""

DOMAIN = "idfm_trafic"
NAME = "IDFM Trafic"

# API IDFM
API_BASE_URL = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia"

# Types de transport
TRANSPORT_TYPES = {
    "metro": "Métro",
    "rer": "RER",
    "train": "Train",
    "tram": "Tramway",
}

# Lignes principales (exemples - à compléter)
LINES = {
    # Métros
    "line:IDFM:C01371": {"name": "Métro 1", "type": "metro", "color": "#FFCD00"},
    "line:IDFM:C01372": {"name": "Métro 2", "type": "metro", "color": "#0064B0"},
    "line:IDFM:C01373": {"name": "Métro 3", "type": "metro", "color": "#9F9825"},
    "line:IDFM:C01374": {"name": "Métro 4", "type": "metro", "color": "#C04191"},
    "line:IDFM:C01375": {"name": "Métro 5", "type": "metro", "color": "#F28E42"},
    "line:IDFM:C01376": {"name": "Métro 6", "type": "metro", "color": "#83C491"},
    "line:IDFM:C01377": {"name": "Métro 7", "type": "metro", "color": "#F3A4BA"},
    "line:IDFM:C01378": {"name": "Métro 8", "type": "metro", "color": "#CEADD2"},
    "line:IDFM:C01379": {"name": "Métro 9", "type": "metro", "color": "#D5C900"},
    "line:IDFM:C01380": {"name": "Métro 10", "type": "metro", "color": "#E3B32A"},
    "line:IDFM:C01381": {"name": "Métro 11", "type": "metro", "color": "#8D5E2A"},
    "line:IDFM:C01382": {"name": "Métro 12", "type": "metro", "color": "#00814F"},
    "line:IDFM:C01383": {"name": "Métro 13", "type": "metro", "color": "#98D4E2"},
    "line:IDFM:C01384": {"name": "Métro 14", "type": "metro", "color": "#662483"},
    # RER
    "line:IDFM:C01742": {"name": "RER A", "type": "rer", "color": "#E3051C"},
    "line:IDFM:C01743": {"name": "RER B", "type": "rer", "color": "#5291CE"},
    "line:IDFM:C01727": {"name": "RER C", "type": "rer", "color": "#F99D1D"},
    "line:IDFM:C01728": {"name": "RER D", "type": "rer", "color": "#00A88F"},
    "line:IDFM:C01729": {"name": "RER E", "type": "rer", "color": "#E4B4D1"},
    # Tramways (exemples)
    "line:IDFM:C01389": {"name": "Tramway T1", "type": "tram", "color": "#0064B0"},
    "line:IDFM:C01390": {"name": "Tramway T2", "type": "tram", "color": "#C04191"},
    "line:IDFM:C01391": {"name": "Tramway T3a", "type": "tram", "color": "#F28E42"},
    "line:IDFM:C01679": {"name": "Tramway T3b", "type": "tram", "color": "#00814F"},
}

# Configuration
CONF_API_KEY = "api_key"
CONF_LINES = "lines"
CONF_STATIONS = "stations"
CONF_TRAFFIC_ENABLED = "traffic_enabled"
CONF_DEPARTURES_ENABLED = "departures_enabled"
