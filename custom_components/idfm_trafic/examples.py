"""Exemple de configuration pour l'intégration IDFM Trafic."""

# Exemple de configuration YAML complète avec tous les RER et quelques métros

EXAMPLE_CONFIG = """
# Configuration via l'interface utilisateur (recommandé)
# Allez dans Configuration > Intégrations > Ajouter une intégration > IDFM Trafic

# Configuration YAML alternative (legacy)
idfm_trafic:
  api_key: "7cx7PoingnrOU3gS0ZxQ7BqCCTcgg7bL"
  
  # Lignes à surveiller (infos trafic)
  lines:
    # RER
    - line:IDFM:C01742  # RER A
    - line:IDFM:C01743  # RER B
    - line:IDFM:C01727  # RER C
    - line:IDFM:C01728  # RER D
    - line:IDFM:C01729  # RER E
    
    # Métros
    - line:IDFM:C01371  # Métro 1
    - line:IDFM:C01374  # Métro 4
    - line:IDFM:C01379  # Métro 9
    - line:IDFM:C01384  # Métro 14
  
  # Stations pour les prochains départs
  stations:
    - stop_area:IDFM:71570  # Châtelet - Les Halles
    - stop_area:IDFM:71249  # Gare du Nord
    - stop_area:IDFM:71505  # Gare de Lyon
  
  # Options
  traffic_enabled: true
  departures_enabled: true
"""

# Exemples de cartes Lovelace

LOVELACE_TRAFFIC_CARD = """
# Carte simple avec état du trafic
type: entities
title: 🚇 État du Trafic IDF
entities:
  - entity: sensor.rer_a_trafic
    name: RER A
    icon: mdi:train
  - entity: sensor.rer_b_trafic
    name: RER B
    icon: mdi:train
  - entity: sensor.rer_e_trafic
    name: RER E
    icon: mdi:train
  - entity: sensor.metro_1_trafic
    name: Métro 1
    icon: mdi:subway
  - entity: sensor.metro_9_trafic
    name: Métro 9
    icon: mdi:subway
"""

LOVELACE_DEPARTURES_CARD = """
# Carte des prochains départs avec Markdown
type: markdown
title: 🚉 Prochains Départs - Châtelet
content: |
  {% set departures = state_attr('sensor.chatelet_departs', 'departures') %}
  {% if departures %}
  | Ligne | Direction | Départ | Quai |
  |-------|-----------|--------|------|
  {% for dep in departures[:5] %}
  | **{{ dep.line }}** | {{ dep.direction }} | {{ dep.time_remaining }} | {{ dep.platform }} |
  {% endfor %}
  {% else %}
  Aucun départ disponible
  {% endif %}
  
  *Mise à jour : {{ as_timestamp(states.sensor.chatelet_departs.last_changed) | timestamp_custom('%H:%M') }}*
"""

LOVELACE_TRAFFIC_ALERTS = """
# Carte conditionnelle - Affiche seulement les perturbations
type: vertical-stack
cards:
  - type: conditional
    conditions:
      - entity: sensor.rer_a_trafic
        state_not: "normal"
    card:
      type: markdown
      content: |
        ## 🚨 RER A - Perturbation
        
        {% for msg in state_attr('sensor.rer_a_trafic', 'messages') %}
        ### {{ msg.title }}
        {{ msg.message }}
        
        ---
        {% endfor %}
  
  - type: conditional
    conditions:
      - entity: sensor.rer_b_trafic
        state_not: "normal"
    card:
      type: markdown
      content: |
        ## 🚨 RER B - Perturbation
        
        {% for msg in state_attr('sensor.rer_b_trafic', 'messages') %}
        ### {{ msg.title }}
        {{ msg.message }}
        
        ---
        {% endfor %}
"""

LOVELACE_DASHBOARD = """
# Dashboard complet avec infos trafic et départs
type: vertical-stack
title: 🚇 Transports IDF
cards:
  # Résumé du trafic
  - type: glance
    title: État du Trafic
    entities:
      - entity: sensor.rer_a_trafic
        name: RER A
      - entity: sensor.rer_b_trafic
        name: RER B
      - entity: sensor.rer_e_trafic
        name: RER E
      - entity: sensor.metro_1_trafic
        name: M1
      - entity: sensor.metro_9_trafic
        name: M9
  
  # Prochains départs
  - type: markdown
    title: 🚉 Mes Prochains Trains
    content: |
      ### Châtelet - Les Halles
      {% set next = state_attr('sensor.chatelet_departs', 'next_departure') %}
      {% if next %}
      **Prochain:** {{ next.line }} → {{ next.direction }} - {{ next.time }}
      {% endif %}
      
      {% for i in range(2, 4) %}
      {% set dep = state_attr('sensor.chatelet_departs', 'departure_' ~ i) %}
      {% if dep %}
      {{ dep.line }} → {{ dep.direction }} - {{ dep.time }}
      {% endif %}
      {% endfor %}
  
  # Alertes
  - type: conditional
    conditions:
      - entity: sensor.rer_a_trafic
        state: "perturbation"
    card:
      type: alert
      entity: sensor.rer_a_trafic
      title: Alerte Trafic RER A
"""

# Automatisations

AUTOMATION_TRAFFIC_ALERT = """
# Notification push en cas de perturbation sur ma ligne
automation:
  - alias: "Alerte Trafic - RER A Perturbé"
    trigger:
      - platform: state
        entity_id: sensor.rer_a_trafic
        to: "perturbation"
    condition:
      # Seulement en semaine et aux heures de pointe
      - condition: time
        after: "07:00:00"
        before: "20:00:00"
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🚨 Trafic RER A perturbé"
          message: >
            {% set messages = state_attr('sensor.rer_a_trafic', 'messages') %}
            {% if messages %}
            {{ messages[0].title }}: {{ messages[0].message }}
            {% else %}
            Trafic perturbé sur le RER A
            {% endif %}
          data:
            push:
              sound:
                name: default
                critical: 1
                volume: 1.0
"""

AUTOMATION_DEPARTURE_REMINDER = """
# Rappel 10 minutes avant le départ habituel
automation:
  - alias: "Rappel Train du Matin"
    trigger:
      - platform: time
        at: "08:20:00"  # 10 min avant ton train habituel
    condition:
      - condition: state
        entity_id: binary_sensor.workday_sensor
        state: "on"
    action:
      # Vérifier le trafic
      - choose:
          - conditions:
              - condition: state
                entity_id: sensor.rer_a_trafic
                state: "perturbation"
            sequence:
              - service: notify.mobile_app_iphone
                data:
                  title: "⚠️ Attention - Trafic perturbé"
                  message: >
                    Le RER A est perturbé ce matin. Prévois plus de temps !
                    {{ state_attr('sensor.rer_a_trafic', 'messages')[0].message }}
        default:
          - service: notify.mobile_app_iphone
            data:
              title: "✅ Ton train dans 10 min"
              message: "Trafic normal sur le RER A, tu peux y aller !"
"""

AUTOMATION_NEXT_TRAIN = """
# Notification avec les prochains trains en temps réel
automation:
  - alias: "Prochains Trains - Commande Vocale"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "check_trains"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🚇 Prochains départs Châtelet"
          message: >
            {% set deps = state_attr('sensor.chatelet_departs', 'departures')[:3] %}
            {% for dep in deps %}
            {{ dep.line }} → {{ dep.direction }}: {{ dep.time_remaining }}
            {% endfor %}
"""

# Template sensors personnalisés

TEMPLATE_SENSORS = """
# Sensors templates pour des infos agrégées
template:
  - sensor:
      # Compte le nombre de lignes perturbées
      - name: "Lignes Perturbées"
        unique_id: idfm_perturbed_lines_count
        state: >
          {{ states.sensor 
             | selectattr('entity_id', 'search', '_trafic$')
             | selectattr('state', 'eq', 'perturbation')
             | list | count }}
        icon: mdi:alert-circle
        attributes:
          lignes: >
            {{ states.sensor 
               | selectattr('entity_id', 'search', '_trafic$')
               | selectattr('state', 'eq', 'perturbation')
               | map(attribute='name')
               | list }}
      
      # Prochain train dans combien de minutes (numérique)
      - name: "Prochain Train Minutes"
        unique_id: next_train_minutes
        state: >
          {% set next = state_attr('sensor.chatelet_departs', 'next_departure') %}
          {% if next and next.time %}
            {% set time = next.time | replace(' min', '') | replace('À l\\'approche', '0') %}
            {{ time | int }}
          {% else %}
            unknown
          {% endif %}
        unit_of_measurement: "min"
        icon: mdi:clock-outline
      
      # Statut global des transports
      - name: "Transports IDF Statut"
        unique_id: idfm_global_status
        state: >
          {% set perturbed = states.sensor 
             | selectattr('entity_id', 'search', '_trafic$')
             | selectattr('state', 'eq', 'perturbation')
             | list | count %}
          {% if perturbed == 0 %}
            normal
          {% elif perturbed <= 2 %}
            attention
          {% else %}
            perturbé
          {% endif %}
        icon: >
          {% set perturbed = states.sensor 
             | selectattr('entity_id', 'search', '_trafic$')
             | selectattr('state', 'eq', 'perturbation')
             | list | count %}
          {% if perturbed == 0 %}
            mdi:check-circle
          {% elif perturbed <= 2 %}
            mdi:alert
          {% else %}
            mdi:alert-circle
          {% endif %}
"""

# Scripts utiles

SCRIPTS = """
# Scripts pour actions rapides
script:
  # Vérifier le trafic de toutes mes lignes
  check_all_traffic:
    alias: "Vérifier Tout le Trafic"
    sequence:
      - service: homeassistant.update_entity
        target:
          entity_id:
            - sensor.rer_a_trafic
            - sensor.rer_b_trafic
            - sensor.rer_e_trafic
            - sensor.metro_1_trafic
            - sensor.metro_9_trafic
      - delay: "00:00:02"
      - service: notify.mobile_app_iphone
        data:
          title: "📊 État du Trafic IDF"
          message: >
            {% set sensors = [
              'sensor.rer_a_trafic',
              'sensor.rer_b_trafic',
              'sensor.rer_e_trafic'
            ] %}
            {% for sensor in sensors %}
            {{ state_attr(sensor, 'line_name') }}: {{ states(sensor) | upper }}
            {% endfor %}
  
  # Rafraîchir les prochains départs
  refresh_departures:
    alias: "Rafraîchir Départs"
    sequence:
      - service: homeassistant.update_entity
        target:
          entity_id: sensor.chatelet_departs
"""

if __name__ == "__main__":
    print("Exemples de configuration IDFM Trafic")
    print("=" * 50)
    print(EXAMPLE_CONFIG)
