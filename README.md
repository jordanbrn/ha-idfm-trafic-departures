# IDFM Trafic - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/jordanetinault/ha-idfm-trafic.svg)](https://github.com/jordanetinault/ha-idfm-trafic/releases)
[![License](https://img.shields.io/github/license/jordanetinault/ha-idfm-trafic.svg)](LICENSE)

Intégration Home Assistant pour les **infos trafic** et **prochains départs** des transports en commun d'Île-de-France (Métro, RER, Train, Tramway).

Utilise l'API officielle [PRIM (Île-de-France Mobilités)](https://prim.iledefrance-mobilites.fr/).

![Preview](https://via.placeholder.com/800x400?text=Screenshot+Coming+Soon)

## ✨ Fonctionnalités

- 🚇 **Infos trafic en temps réel** par ligne (Métro, RER, Train, Tram)
- 🚉 **Prochains départs** par station avec directions
- 📊 **Attributs détaillés** : messages de perturbations, sévérité, temps d'attente
- 🎨 **Configuration UI** simple et intuitive
- 🔄 **Mise à jour automatique** toutes les minutes
- 🇫🇷 **Interface en français** (et anglais)

## 📦 Installation

### Via HACS (recommandé)

1. Ouvrez **HACS** dans Home Assistant
2. Cliquez sur **Integrations**
3. Cliquez sur le menu **⋮** en haut à droite
4. Sélectionnez **Custom repositories**
5. Ajoutez l'URL : `https://github.com/jordanetinault/ha-idfm-trafic`
6. Catégorie : **Integration**
7. Cliquez sur **Add**
8. Recherchez **"IDFM Trafic"** et installez
9. **Redémarrez** Home Assistant

### Installation manuelle

1. Téléchargez la dernière version depuis [Releases](https://github.com/jordanetinault/ha-idfm-trafic/releases)
2. Copiez le dossier `custom_components/idfm_trafic` dans votre dossier `config/custom_components/`
3. Redémarrez Home Assistant

## 🔧 Configuration

### 1. Obtenir une clé API IDFM

1. Créez un compte sur [PRIM](https://prim.iledefrance-mobilites.fr/)
2. Créez une application
3. Copiez votre clé API

### 2. Ajouter l'intégration

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur **+ Ajouter une intégration**
3. Recherchez **"IDFM Trafic"**
4. Entrez votre clé API
5. Sélectionnez les lignes à surveiller
6. (Optionnel) Ajoutez des IDs de stations pour les départs

## 📍 Trouver les IDs de stations

### Méthode 1 : Via l'API

```bash
curl -H "apiKey: VOTRE_CLE_API" \
  "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/coverage/fr-idf/places?q=Chatelet&type[]=stop_area"
```

### Méthode 2 : Stations principales

| Station | ID |
|---------|-----|
| Châtelet - Les Halles | `stop_area:IDFM:71570` |
| Gare du Nord | `stop_area:IDFM:71249` |
| Gare de Lyon | `stop_area:IDFM:71505` |
| Saint-Lazare | `stop_area:IDFM:71364` |
| La Défense | `stop_area:IDFM:71386` |
| Nation | `stop_area:IDFM:71934` |
| République | `stop_area:IDFM:71522` |
| Montparnasse | `stop_area:IDFM:71349` |

## 📊 Utilisation

### Sensors créés

**Pour chaque ligne :**
- `sensor.rer_a_trafic` : État du trafic (normal / perturbation / information)
- Attributs : `severity`, `messages`, `line_color`, `updated_at`

**Pour chaque station :**
- `sensor.chatelet_departs` : Nombre de prochains départs
- Attributs : `departures`, `next_departure`, `departure_1` à `departure_5`

### Exemples de cartes Lovelace

<details>
<summary>📱 Carte Trafic Simple</summary>

```yaml
type: entities
title: État du Trafic
entities:
  - entity: sensor.rer_a_trafic
  - entity: sensor.rer_e_trafic
  - entity: sensor.metro_1_trafic
  - entity: sensor.metro_9_trafic
```
</details>

<details>
<summary>🚉 Carte Prochains Départs</summary>

```yaml
type: markdown
title: 🚉 Prochains Départs - Châtelet
content: |
  {% for i in range(1, 6) %}
  {% set dep = state_attr('sensor.chatelet_departs', 'departure_' ~ i) %}
  {% if dep %}
  **{{ dep.line }}** → {{ dep.direction }} - ⏱️ {{ dep.time }}
  {% endif %}
  {% endfor %}
```
</details>

<details>
<summary>⚠️ Alertes Conditionnelles</summary>

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
</details>

Plus d'exemples dans le [fichier examples.py](custom_components/idfm_trafic/examples.py)

### Automatisations

<details>
<summary>🔔 Notification en cas de perturbation</summary>

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
</details>

## 🔍 IDs des lignes

<details>
<summary>🚇 Métros (1-14)</summary>

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
</details>

<details>
<summary>🚆 RER (A-E)</summary>

- RER A : `line:IDFM:C01742`
- RER B : `line:IDFM:C01743`
- RER C : `line:IDFM:C01727`
- RER D : `line:IDFM:C01728`
- RER E : `line:IDFM:C01729`
</details>

<details>
<summary>🚊 Tramways</summary>

- Tramway T1 : `line:IDFM:C01389`
- Tramway T2 : `line:IDFM:C01390`
- Tramway T3a : `line:IDFM:C01391`
- Tramway T3b : `line:IDFM:C01679`
</details>

## 🐛 Dépannage

### Les sensors ne se créent pas

1. Vérifiez que votre clé API est valide
2. Consultez les logs : **Configuration** → **Logs**
3. Vérifiez que les IDs de lignes/stations sont corrects

### Activer les logs de debug

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.idfm_trafic: debug
```

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Forkez le projet
2. Créez votre branche (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📝 Roadmap

- [ ] Support des Transilien (trains de banlieue)
- [ ] Support des bus
- [ ] Carte personnalisée Lovelace
- [ ] Mode "favoris" pour stations fréquentes
- [ ] Alertes intelligentes basées sur l'historique

## 📄 Licence

MIT License - voir [LICENSE](LICENSE)

## 🙏 Remerciements

- [Île-de-France Mobilités](https://www.iledefrance-mobilites.fr/) pour l'API PRIM
- La communauté Home Assistant
- Tous les contributeurs

## ⭐ Si vous aimez ce projet

N'hésitez pas à mettre une étoile sur GitHub ! ⭐

---

**Développé avec ❤️ pour les voyageurs franciliens**
