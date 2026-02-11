# IDFM Trafic - Intégration Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Intégration Home Assistant pour les **infos trafic** et **prochains départs** des transports en commun d'Île-de-France (Métro, RER, Train, Tramway).

Utilise l'API officielle [PRIM (Île-de-France Mobilités)](https://prim.iledefrance-mobilites.fr/).

## ✨ Fonctionnalités

- 🚇 **Infos trafic en temps réel** par ligne (Métro, RER, Train, Tram)
- 🚉 **Prochains départs** par station avec directions
- 📊 **Attributs détaillés** : messages de perturbations, sévérité, temps d'attente
- 🎨 **Configuration UI** simple et intuitive
- 🔄 **Mise à jour automatique** toutes les minutes

## 📦 Installation

### Via HACS (recommandé)

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur "Integrations"
3. Cliquez sur le menu ⋮ en haut à droite
4. Sélectionnez "Custom repositories"
5. Ajoutez l'URL : `https://github.com/jordanbrn/ha-idfm-trafic-departures`
6. Catégorie : `Integration`
7. Cliquez sur "Add"
8. Recherchez "IDFM Trafic" et installez
9. Redémarrez Home Assistant

### Installation manuelle

1. Copiez le dossier `custom_components/idfm_trafic` dans votre dossier `config/custom_components/`
2. Redémarrez Home Assistant

## 🔧 Configuration

### 1. Obtenir une clé API IDFM

1. Créez un compte sur [PRIM](https://prim.iledefrance-mobilites.fr/)
2. Créez une application
3. Copiez votre clé API

### 2. Ajouter l'intégration

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur **+ Ajouter une intégration**
3. Recherchez **IDFM Trafic**
4. Entrez votre clé API : `7cx7PoingnrOU3gS0ZxQ7BqCCTcgg7bL`
5. Sélectionnez les lignes à surveiller
6. (Optionnel) Ajoutez des IDs de stations pour les départs

## 📍 Trouver les IDs de stations

Les IDs de stations suivent le format : `stop_area:IDFM:XXXXX`

**Méthode 1 : Via l'API**

```bash
curl -H "apiKey: VOTRE_CLE" \
  "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/coverage/fr-idf/places?q=Chatelet&type[]=stop_area"
```

**Méthode 2 : Exemples de stations principales**

| Station               | ID                     |
| --------------------- | ---------------------- |
| Châtelet - Les Halles | `stop_area:IDFM:71570` |
| Gare du Nord          | `stop_area:IDFM:71249` |
| Gare de Lyon          | `stop_area:IDFM:71505` |
| Saint-Lazare          | `stop_area:IDFM:71364` |
| La Défense            | `stop_area:IDFM:71386` |

## 📊 Utilisation

### Sensors créés

Pour chaque **ligne** sélectionnée :

- `sensor.rer_a_trafic` : État du trafic (normal / perturbation / information)

Pour chaque **station** configurée :

- `sensor.chatelet_departs` : Nombre de prochains départs

### Attributs disponibles

**Sensor de trafic :**

```yaml
line_id: "line:IDFM:C01742"
line_name: "RER A"
line_color: "#E3051C"
severity: "perturbation"
messages:
  - title: "Trafic perturbé"
    message: "Incident technique à Auber"
    severity: "perturbation"
message_count: 1
updated_at: "2026-02-11T14:30:00"
```

**Sensor de départs :**

```yaml
station_id: "stop_area:IDFM:71570"
station_name: "Châtelet"
departures:
  - line: "RER A"
    direction: "Cergy"
    time_remaining: "3 min"
    platform: "1"
    departure_time: "2026-02-11T14:33:00"
next_departure:
  line: "RER A"
  direction: "Cergy"
  time: "3 min"
departure_1:
  line: "RER A"
  direction: "Cergy"
  time: "3 min"
  platform: "1"
```

## 🎨 Exemples de cartes Lovelace

### Carte Trafic Simple

```yaml
type: entities
title: État du Trafic
entities:
  - entity: sensor.rer_a_trafic
  - entity: sensor.rer_e_trafic
  - entity: sensor.metro_1_trafic
  - entity: sensor.metro_9_trafic
```

### Carte Trafic Détaillée avec Markdown

```yaml
type: markdown
content: |
  ## 🚇 Trafic RER A

  **État:** {{ states('sensor.rer_a_trafic') | upper }}

  {% if state_attr('sensor.rer_a_trafic', 'messages') %}
  ### ⚠️ Perturbations
  {% for msg in state_attr('sensor.rer_a_trafic', 'messages') %}
  **{{ msg.title }}**
  {{ msg.message }}
  {% endfor %}
  {% else %}
  ✅ Trafic normal
  {% endif %}
```

### Carte Prochains Départs

```yaml
type: markdown
content: |
  ## 🚉 Prochains départs - Châtelet

  {% for i in range(1, 6) %}
  {% set dep = 'departure_' ~ i %}
  {% if state_attr('sensor.chatelet_departs', dep) %}
  **{{ state_attr('sensor.chatelet_departs', dep).line }}** 
  → {{ state_attr('sensor.chatelet_departs', dep).direction }}
  ⏱️ {{ state_attr('sensor.chatelet_departs', dep).time }}
  {% endif %}
  {% endfor %}
```

### Carte avec Conditional (Alertes uniquement)

```yaml
type: conditional
conditions:
  - entity: sensor.rer_a_trafic
    state_not: "normal"
card:
  type: markdown
  content: |
    ## 🚨 Alerte Trafic RER A

    {% for msg in state_attr('sensor.rer_a_trafic', 'messages') %}
    **{{ msg.title }}**
    {{ msg.message }}
    ---
    {% endfor %}
```

### Carte Custom Button (nécessite button-card)

```yaml
type: custom:button-card
entity: sensor.rer_a_trafic
name: RER A
show_state: true
styles:
  card:
    - background: |
        [[[
          if (entity.state === 'normal') return 'green';
          if (entity.state === 'perturbation') return 'red';
          return 'orange';
        ]]]
  name:
    - color: white
  state:
    - color: white
```

## 🛠️ Automatisations

### Notification en cas de perturbation

```yaml
automation:
  - alias: "Alerte Trafic RER A"
    trigger:
      - platform: state
        entity_id: sensor.rer_a_trafic
        to: "perturbation"
    action:
      - service: notify.mobile_app
        data:
          title: "🚨 Trafic RER A perturbé"
          message: >
            {{ state_attr('sensor.rer_a_trafic', 'messages')[0].message }}
```

### Rappel avant le départ

```yaml
automation:
  - alias: "Prochain train dans 5 min"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('sensor.chatelet_departs', 'next_departure').time == '5 min' }}
    action:
      - service: notify.mobile_app
        data:
          title: "🚇 Ton train arrive"
          message: >
            {{ state_attr('sensor.chatelet_departs', 'next_departure').line }} 
            direction {{ state_attr('sensor.chatelet_departs', 'next_departure').direction }} 
            dans 5 minutes
```

## 🔍 IDs des lignes

### Métros

- Métro 1 : `line:IDFM:C01371`
- Métro 2 : `line:IDFM:C01372`
- Métro 3 : `line:IDFM:C01373`
- Métro 4 : `line:IDFM:C01374`
- Métro 5 : `line:IDFM:C01375`
- Métro 6 : `line:IDFM:C01376`
- Métro 7 : `line:IDFM:C01377`
- Métro 8 : `line:IDFM:C01378`
- Métro 9 : `line:IDFM:C01379`
- Métro 10 : `line:IDFM:C01380`
- Métro 11 : `line:IDFM:C01381`
- Métro 12 : `line:IDFM:C01382`
- Métro 13 : `line:IDFM:C01383`
- Métro 14 : `line:IDFM:C01384`

### RER

- RER A : `line:IDFM:C01742`
- RER B : `line:IDFM:C01743`
- RER C : `line:IDFM:C01727`
- RER D : `line:IDFM:C01728`
- RER E : `line:IDFM:C01729`

### Tramways

- Tramway T1 : `line:IDFM:C01389`
- Tramway T2 : `line:IDFM:C01390`
- Tramway T3a : `line:IDFM:C01391`
- Tramway T3b : `line:IDFM:C01679`

## 📝 Configuration YAML (legacy)

Si vous préférez la configuration YAML :

```yaml
# configuration.yaml
idfm_trafic:
  api_key: "7cx7PoingnrOU3gS0ZxQ7BqCCTcgg7bL"
  lines:
    - line:IDFM:C01742 # RER A
    - line:IDFM:C01729 # RER E
    - line:IDFM:C01371 # Métro 1
  stations:
    - stop_area:IDFM:71570 # Châtelet
```

## 🐛 Dépannage

### Les sensors ne se créent pas

1. Vérifiez que votre clé API est valide
2. Consultez les logs : **Configuration** → **Logs**
3. Vérifiez que les IDs de lignes/stations sont corrects

### Les données ne se mettent pas à jour

1. L'intervalle de mise à jour est de 60 secondes
2. Vérifiez votre connexion Internet
3. L'API IDFM peut être temporairement indisponible

### Activer les logs de debug

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.idfm_trafic: debug
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

- Signaler des bugs
- Proposer des améliorations
- Ajouter des lignes manquantes

## 📄 Licence

MIT License

## 🙏 Remerciements

- [Île-de-France Mobilités](https://www.iledefrance-mobilites.fr/) pour l'API PRIM
- La communauté Home Assistant

---

**Développé avec ❤️ pour les voyageurs franciliens**
