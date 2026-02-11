# Guide de Publication GitHub

## 🚀 Publier sur GitHub

### Méthode Automatique (Recommandée)

```bash
./publish.sh
```

Le script vous demandera l'URL de votre repo GitHub et fera tout automatiquement.

---

### Méthode Manuelle

1. **Créer le repo sur GitHub**
   - Va sur https://github.com/new
   - Nom: `ha-idfm-trafic`
   - Description: `Home Assistant integration for IDFM traffic and departures`
   - Public
   - **Ne pas** initialiser avec README, .gitignore ou license

2. **Connecter le repo local**

   ```bash
   git remote add origin git@github.com:USERNAME/ha-idfm-trafic.git
   git branch -M main
   git push -u origin main
   ```

3. **Configurer le repo sur GitHub**
   - Ajoute une description
   - Ajoute les topics: `home-assistant`, `idfm`, `transport`, `france`, `integration`
   - Active les Issues
   - Configure les GitHub Actions (déjà dans le repo)

---

## 📦 Créer la première release

1. **Sur GitHub, va dans Releases → Create a new release**

2. **Tag version**: `v1.0.0`

3. **Release title**: `v1.0.0 - Initial Release`

4. **Description**:

   ```markdown
   ## 🎉 First Release!

   ### Features

   - ✅ Real-time traffic info for Metro, RER, Train, Tram
   - ✅ Next departures by station
   - ✅ UI configuration flow
   - ✅ French & English support
   - ✅ Complete documentation

   ### Installation

   See [README.md](https://github.com/USERNAME/ha-idfm-trafic#installation)
   ```

5. **Publish release** → Cela générera automatiquement le ZIP via GitHub Actions

---

## 🏪 Ajouter à HACS (Optionnel)

Pour que les utilisateurs puissent installer via HACS:

1. **Attends que le repo soit stable** (quelques releases)

2. **Crée une PR sur le repo HACS**:
   - Fork: https://github.com/hacs/default
   - Édite: `custom_components/default.json`
   - Ajoute ton repo:
     ```json
     {
       "name": "IDFM Trafic",
       "country": ["FR"],
       "domains": ["sensor"],
       "homeassistant": "2024.1.0",
       "render_readme": true
     }
     ```

3. **En attendant**, les utilisateurs peuvent installer via HACS en ajoutant manuellement le repo

---

## 📸 Améliorer le README (Recommandé)

1. **Prends des screenshots** de tes cartes Lovelace

2. **Upload sur GitHub**:
   - Crée un dossier `docs/images/`
   - Upload les images
   - Remplace dans README.md:
     ```markdown
     ![Traffic Card](docs/images/traffic-card.png)
     ![Departures Card](docs/images/departures-card.png)
     ```

---

## ✅ Checklist Finale

- [ ] Repo créé sur GitHub
- [ ] Code pushé
- [ ] Description et topics ajoutés
- [ ] Release v1.0.0 créée
- [ ] GitHub Actions fonctionnent (badge vert)
- [ ] README avec screenshots
- [ ] Issues activées
- [ ] License vérifiée

---

## 🎯 Après Publication

**Partage ton projet:**

- Reddit: r/homeassistant
- Forum Home Assistant
- Discord Home Assistant FR
- Twitter avec #HomeAssistant

**Maintiens le projet:**

- Réponds aux issues
- Accepte les PRs
- Fais des releases régulières
- Garde la doc à jour

---

Bon courage ! 🚀
