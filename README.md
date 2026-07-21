
![CI](https://github.com/kodjo-valentin/pharmacy-finder-abidjan/actions/workflows/ci-security.yml/badge.svg)

# 💊 Pharmacy Finder Abidjan

Agent géospatial intelligent permettant de localiser les pharmacies les plus proches d'un quartier d'Abidjan, en langage naturel, avec visualisation interactive sur fond satellite.

## 🎯 Contexte du projet

Ce projet est né d'une question simple : *est-il possible de construire son propre agent IA capable de comprendre une question géographique en français et de répondre avec des données réelles, affichées sur une carte ?*

Inspiré par les démonstrations d'agents IA géospatiaux d'Esri (AI-Powered Maps), ce projet reproduit le mécanisme de bout en bout — données réelles, calcul spatial précis, et interface conversationnelle — en partant de zéro.

## lien: https://kodjo-valentin.github.io/pharmacy-finder-abidjan/

## ✨ Fonctionnalités

- 🗣️ **Recherche en langage naturel** : "Trouve-moi une pharmacie près de Cocody dans un rayon de 1km"
- 📍 **Géocodage automatique** des noms de quartiers (via Nominatim/OpenStreetMap)
- 📏 **Calcul de distance géographique réel** (pas une approximation) via PostGIS
- 🗺️ **Visualisation interactive** sur fond satellite avec affichage du rayon de recherche
- 🤖 **Agent IA** (Google Gemini) qui orchestre la recherche via function calling

## 🏗️ Architecture

```
Utilisateur (langage naturel)
        │
        ▼
   Frontend HTML/Leaflet (carte + zone de question)
        │
        ▼ (requête HTTP)
   Backend FastAPI
        │
        ▼
   Agent Gemini (function calling)
        │
        ├──► Géocodage (Nominatim) : "Cocody" → coordonnées GPS
        │
        └──► Requête spatiale (PostGIS) : ST_DWithin + ST_Distance
                    │
                    ▼
            Base de données PostgreSQL/PostGIS
            (543 pharmacies extraites d'OpenStreetMap)
```

## 🛠️ Stack technique

| Composant | Technologie |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Agent IA | Google Gemini 2.5 Flash (function calling) |
| Base de données | PostgreSQL 18 + PostGIS |
| Géocodage | Nominatim (via `geopy`) |
| Frontend | HTML / Leaflet.js |
| Fond de carte | Esri World Imagery (satellite) |
| Source des données | OpenStreetMap (extraction via Overpass Turbo) |
| ORM | SQLAlchemy + pg8000 |

## 📊 Données

- **543 pharmacies** extraites d'Abidjan via Overpass Turbo (OpenStreetMap)
- Stockées dans une table PostGIS avec géométrie `Point` (SRID 4326)
- Index spatial GIST pour des requêtes de proximité performantes

## 🚀 Comment ça marche

1. L'utilisateur tape une question en français dans le champ de recherche
2. Le frontend envoie la question au backend FastAPI
3. L'agent Gemini interprète la question et appelle automatiquement la fonction `find_nearest_pharmacies(quartier, rayon_km)`
4. Cette fonction :
   - Géocode le quartier mentionné (Nominatim)
   - Exécute une requête PostGIS (`ST_DWithin` + `ST_Distance` en mode `geography` pour des distances réelles en mètres)
   - Retourne les pharmacies triées par distance croissante
5. Le frontend affiche :
   - La réponse en langage naturel de l'agent
   - Un marqueur sur la position recherchée
   - Un cercle semi-transparent représentant le rayon de recherche
   - Un marqueur vert pour chaque pharmacie trouvée, avec sa distance exacte au clic

## 📦 Installation locale

### Prérequis
- Python 3.13
- PostgreSQL 18 avec extension PostGIS
- Une clé API Google Gemini (gratuite via [Google AI Studio](https://aistudio.google.com))

### Étapes

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd pharmacy-finder/backend

# 2. Créer et activer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
# Créer un fichier .env avec :
# GEMINI_API_KEY=votre_cle
# DB_PASSWORD=votre_mot_de_passe_postgres

# 5. Créer la base de données PostGIS
# Dans pgAdmin ou psql :
# CREATE DATABASE pharmacy_finder;
# CREATE EXTENSION postgis;
# (puis exécuter le script de création de table dans docs/create_table_pharmacies.sql)

# 6. Importer les données des pharmacies
python app/db/import_pharmacies.py

# 7. Lancer le serveur
uvicorn app.main:app --reload

# 8. Ouvrir frontend/index.html dans un navigateur
```

## 🧠 Ce que j'ai appris en construisant ce projet

- Function calling avec un LLM (Gemini) pour orchestrer des outils Python
- Requêtes spatiales PostGIS avec calcul de distance réelle (`geography` vs `geometry`)
- Géocodage via Nominatim
- Débogage d'environnements Python sur Windows (versions multiples, venv, encodage)
- Extraction de données OpenStreetMap via Overpass Turbo
- Construction d'une interface cartographique interactive avec Leaflet.js

## 🔮 Pistes d'amélioration futures

- [ ] Géolocalisation automatique du navigateur (au lieu de taper un quartier)
- [ ] Filtrer par pharmacies de garde / ouvertes actuellement
- [ ] Calcul d'itinéraire (pas juste la distance à vol d'oiseau)
- [ ] Étendre à d'autres types de lieux (hôpitaux, écoles, stations-service)
- [ ] Déploiement en ligne (Render + base PostGIS hébergée)

## 👤 Auteur

Valentin KODJO Étudiant en Licence Professionnelle Géomatique et Stratégies Spatiales, Université Félix Houphouët-Boigny (Abidjan).

---

*Ce projet s'inscrit dans une démarche d'autoformation à l'intersection de la géomatique, de la data science et de l'IA appliquées au contexte africain.*
