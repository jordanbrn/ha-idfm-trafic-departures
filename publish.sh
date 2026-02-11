#!/bin/bash

# Script pour publier le repo sur GitHub
# Usage: ./publish.sh

echo "🚀 Publication du repo IDFM Trafic sur GitHub"
echo ""

# Vérifier si on est dans le bon dossier
if [ ! -d "custom_components/idfm_trafic" ]; then
    echo "❌ Erreur: Exécutez ce script depuis la racine du projet"
    exit 1
fi

# Demander l'URL du repo GitHub
echo "📝 Entrez l'URL de votre repo GitHub:"
echo "   Format: git@github.com:USERNAME/ha-idfm-trafic.git"
read -p "URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ URL vide, annulation"
    exit 1
fi

# Ajouter le remote
echo ""
echo "🔗 Ajout du remote origin..."
git remote add origin "$REPO_URL"

# Renommer la branche en main
echo "🔄 Renommage de la branche en main..."
git branch -M main

# Pousser vers GitHub
echo "⬆️  Push vers GitHub..."
git push -u origin main

echo ""
echo "✅ Repo publié avec succès sur GitHub!"
echo "🌐 Visitez: https://github.com/USERNAME/ha-idfm-trafic"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Ajoutez une description au repo sur GitHub"
echo "   2. Ajoutez les topics: home-assistant, idfm, transport, france"
echo "   3. Créez une release v1.0.0 pour activer les workflows"
echo "   4. (Optionnel) Ajoutez des screenshots dans le README"
