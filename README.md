# SAYDO CRM - Gestion des Orthodontistes

Solution CRM complète pour le suivi et l'engagement des orthodontistes en France.

## 🚀 Documentation

- [**Guide complet : Scraping & Import dans le CRM**](./SCRAPING_CRM_GUIDE.md) : Tout ce qu'il faut savoir sur la collecte de données et l'intégration.

## 🛠️ Installation rapide

1. Cloner le dépôt
2. Lancer l'environnement avec Docker :
   ```bash
   docker-compose up --build
   ```
3. Accéder à l'interface : `http://localhost:5173`

## 🏗️ Structure du projet

- `backend/` : API FastAPI et scripts de scraping.
- `frontend/` : Interface React (Vite).
- `docker-compose.yml` : Orchestration des services (App, DB).
