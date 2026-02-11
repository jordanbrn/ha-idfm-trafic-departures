#!/bin/bash

# Script pour créer une release GitHub
# Usage: ./create_release.sh VERSION

VERSION=${1:-"1.0.0"}

echo "🚀 Création de la release v$VERSION"
echo ""

# Vérifier si on est dans le bon dossier
if [ ! -d "custom_components/idfm_trafic" ]; then
    echo "❌ Erreur: Exécutez ce script depuis la racine du projet"
    exit 1
fi

# Vérifier si tout est commité
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Attention: Il y a des modifications non commitées"
    read -p "Voulez-vous continuer quand même ? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Annulé"
        exit 1
    fi
fi

# Créer le tag
echo "🏷️  Création du tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION

## ✨ Fonctionnalités

- 🚇 Infos trafic en temps réel (Métro, RER, Train, Tram)
- 🚉 Prochains départs par station
- 🎨 Configuration UI complète
- 🔧 Options modifiables après installation
- 🇫🇷 Support français et anglais

## 🐛 Corrections

- Fix: Format JSON valide pour HACS
- Fix: Mise à jour des sensors
- Fix: Support des options de configuration

## 📦 Installation

Voir le [README](https://github.com/jordanbrn/ha-idfm-trafic-departures#installation)"

# Pousser le tag
echo "⬆️  Push du tag vers GitHub..."
git push origin "v$VERSION"

echo ""
echo "✅ Tag v$VERSION créé et poussé avec succès !"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Va sur: https://github.com/jordanbrn/ha-idfm-trafic-departures/releases/new?tag=v$VERSION"
echo "   2. Le tag v$VERSION devrait être pré-sélectionné"
echo "   3. Titre: v$VERSION - Initial Release"
echo "   4. Description: (pré-remplie ci-dessous)"
echo "   5. Coche 'Set as the latest release'"
echo "   6. Clique sur 'Publish release'"
echo ""
echo "Le workflow GitHub Actions créera automatiquement le fichier ZIP !"
