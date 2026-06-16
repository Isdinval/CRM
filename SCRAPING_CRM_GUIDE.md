# 📄 Guide Complet : Scraping & Importation CRM

Ce document détaille les procédures de collecte de données (scraping) des orthodontistes et leur intégration dans le CRM SAYDO.

---

## 🎯 Qui doit lire quoi ?

| Public | Sections concernées |
| :--- | :--- |
| **Développeurs / Admins** | 🛠️ **Section 1** : Scraping technique<br>🏗️ **Section 2A** : Importation technique (Backend/DB) |
| **Équipe Commerciale** | 💻 **Section 2B** : Interface Utilisateur (Frontend) |

---

## 🛠️ Section 1 : Scraping des Orthodontistes

Cette section explique comment configurer et exécuter les scripts de collecte de données.

### 1.1 Configuration des Sources Principales

#### 🦷 AMELI (Source de référence)
C'est la source principale pour obtenir les numéros RPPS et les adresses officielles.
- **Code Métier** : Le script `scrape_ameli.py` utilise le code **10018017** (Orthodontie).
- **Anti-Détection** : Rotation des User-Agents et gestion des sessions via Playwright.
- **Limites** : Il est recommandé de ne pas dépasser 500 requêtes par heure pour éviter le bannissement d'IP.

#### 🏥 Doctolib (Enrichissement)
Utilisé pour récupérer les avis clients et confirmer la disponibilité.
- **Filtres** : Cible `https://www.doctolib.fr/orthodontiste/france`.
- **Stratégie** : Utilisation de délais aléatoires entre les pages pour simuler un comportement humain.
- **Données** : Extraction des notes, nombre d'avis et spécialités secondaires.

#### 📍 Google Maps (SerpAPI)
Fournit la présence locale et les coordonnées téléphoniques.
- **Configuration** : Nécessite une clé API dans le fichier `.env` : `SERPAPI_KEY=votre_cle`.
- **Test** : Limité à 20 villes par défaut pour économiser les crédits API en phase de test.

### 1.2 Exécution du Pipeline (CLI)
Le script central est `backend/scripts/pipeline.py`.

**Commandes courantes :**
```bash
# Lancer le pipeline complet
python backend/scripts/pipeline.py

# Tester uniquement sur AMELI et Doctolib (Échantillon)
python backend/scripts/pipeline.py --sources ameli,doctolib

# Simuler l'import (sans écrire en base de données)
python backend/scripts/pipeline.py --dry-run

# Traiter des données déjà scrapées (évite de relancer les navigateurs)
python backend/scripts/pipeline.py --skip-scrape
```

### 1.3 Interprétation des Logs & Rapports
- **Rapport d'exécution** : `backend/scripts/logs/import_report_YYYY-MM-DD.json` (Stats de succès par source).
- **Logs techniques** : `backend/scripts/logs/import.log` (Détails des erreurs réseau ou parsing).

---

## 🏗️ Section 2A : Importation Technique

### 2.1 Connexion à la Base de Données
Le pipeline utilise SQLAlchemy pour se connecter à PostgreSQL.
- **Variable d'environnement** : `DATABASE_URL` (ex: `postgresql://postgres:postgres@db:5432/crm`).
- **Logique d'import** : Gérée dans `backend/scripts/services/db_import.py`.

### 2.2 Schéma des Tables
- **`orthodontists`** : Contient toutes les infos du prospect (RPPS, email, score, tier).
- **`pipeline_jobs`** : Table de suivi des exécutions (statut, date, nombre de lignes traitées).

### 2.3 Processus d'Upsert (Mise à jour)
Le script utilise une logique de **"Update on Conflict"** :
1. Si le numéro **RPPS** existe déjà, les informations sont mises à jour.
2. Si le RPPS est absent mais que l'**Email** existe, la fiche est mise à jour.
3. Sinon, une nouvelle entrée est créée.

---

## 💻 Section 2B : Interface Utilisateur (CRM)

### 2.1 Accès à la page d'Import
Dans le menu latéral du CRM, cliquez sur l'icône ⚙️ **Administration** puis **"Import des données"**.

### 2.2 Lancement d'un Import Web
1. **Sélection des sources** : Cochez les sources souhaitées (ex: AMELI + Google Maps).
2. **Options** : Activez "Enrichissement PubMed" si vous souhaitez cibler les profils académiques.
3. **Lancement** : Cliquez sur **"Démarrer le pipeline"**.

### 2.3 Surveillance et Rapport Final
- **Barre de progression** : Suivez l'avancement en temps réel (Scraping -> Déduplication -> Import).
- **Stats de fin** : À la fin de l'import, un tableau récapitulatif affiche :
    - Nombre de **nouveaux** prospects.
    - Nombre de prospects **mis à jour**.
    - Répartition par **Tier** (Ambassadeur, Champion, etc.).

---

**Note** : En cas de blocage persistant d'une source (Captcha), contactez l'administrateur pour mettre à jour les proxies de scraping.
