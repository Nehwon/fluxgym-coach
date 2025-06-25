# Protocole de Développement Fluxgym-coach

> **Note** : Ce document est également disponible en [anglais](PROTOCOLE_RACINE.md).

[![Licence : GPL v3](https://img.shields.io/badge/Licence-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Style de code : black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Table des matières
1. [Communication](#1-communication)
2. [Standards Techniques](#2-standards-techniques)
3. [Gestion de Version](#3-gestion-de-version)
4. [Workflow de Développement](#4-workflow-de-développement)
5. [Qualité du Code](#5-qualité-du-code)
6. [Documentation](#6-documentation)
7. [Sécurité](#7-sécurité)
8. [Spécificités du Projet](#8-spécificités-du-projet)

## 1. Communication

### Principes généraux
- **Langue** : Français (sauf pour le code et les identifiants techniques)
- **Style** : Professionnel mais accessible
- **Fréquence des mises à jour** : Continue, tout au long du développement
- **Fuseau horaire** : UTC+1 (Paris) est le fuseau horaire de référence

### Outils recommandés
- **Suivi des tâches** : [GitHub Issues](https://github.com/Nehwon/fluxgym-coach/issues)
- **Revue de code** : GitHub Pull Requests
- **Documentation** : Markdown dans le dépôt
- **Communication** : Asynchrone en priorité, avec une documentation claire

### Règles de communication
- Toujours fournir le contexte dans les descriptions de problèmes
- Référencer les problèmes/PRs associés avec `#numéro_du_problème`
- Documenter les décisions importantes dans `DECISIONS.md`
- Maintenir les discussions ciblées et actionnables
- Utiliser des titres clairs et descriptifs pour les problèmes et PRs

## 2. Standards Techniques

### Technologies principales
- **Python** : 3.8+
- **Traitement d'images** : Pillow, OpenCV
- **API** : REST avec FastAPI
- **Cache** : Implémentation personnalisée avec stockage basé sur les fichiers

### Environnement de développement
- **Version de Python** : 3.8+ (voir `.python-version`)
- **Gestion des paquets** : `pip` avec `requirements.txt` et `setup.py`
- **Environnement virtuel** : Recommandé (venv, pipenv, ou conda)
- **Vérification du code** : flake8, black, mypy
- **Tests** : pytest avec couverture de code

### Dépendances
- Maintenir le nombre de dépendances au minimum
- Documenter toutes les dépendances dans `requirements.txt`
- Épingler les dépendances de production dans `setup.py`
- Utiliser `requirements-dev.txt` pour les dépendances de développement

## 3. Gestion de Version

### Stratégie de branches
- `main` : Code prêt pour la production
- `develop` : Branche d'intégration pour les fonctionnalités
- `feature/*` : Nouvelles fonctionnalités et améliorations
- `bugfix/*` : Corrections de bugs
- `hotfix/*` : Corrections critiques pour la production

### Directives de commit
- Suivre les [Conventional Commits](https://www.conventionalcommits.org/)
- Utiliser le présent ("Ajoute une fonctionnalité" et non "Ajout d'une fonctionnalité")
- Faire des commits atomiques et ciblés
- Référencer les problèmes dans les messages de commit (ex: `#123`)

### Pull Requests
- Garder les PR petites et ciblées
- Inclure les tests pertinents
- Mettre à jour la documentation si nécessaire
- Demander des relectures à au moins un mainteneur
- Tous les tests doivent passer avant la fusion

## 4. Workflow de Développement

### Pour commencer
1. Forker le dépôt
2. Créer une branche de fonctionnalité : `git checkout -b feature/nouvelle-fonctionnalite`
3. Effectuer vos modifications
4. Exécuter les tests : `pytest`
5. Committer vos modifications : `git commit -m 'feat: ajoute une nouvelle fonctionnalité'`
6. Pousser vers la branche : `git push origin feature/nouvelle-fonctionnalite`
7. Ouvrir une Pull Request

### Processus de revue de code
1. Créer une PR brouillon tôt pour obtenir des retours
2. Demander des relectures aux membres pertinents de l'équipe
3. Adresser tous les commentaires de revue
4. S'assurer que tous les tests CI passent
5. Obtenir au moins une approbation avant la fusion

## 5. Qualité du Code

### Tests
- Écrire des tests unitaires pour tout nouveau code
- Viser au moins 80% de couverture de test
- Utiliser des fixtures et des tests paramétrés quand c'est approprié
- Exécuter les tests localement avant de pousser

### Vérification et formatage
- Utiliser `black` pour le formatage du code
- Exécuter `flake8` pour l'analyse statique
- Utiliser `mypy` pour la vérification des types
- Les hooks de pre-commit sont recommandés

### Performance
- Profiler le code avant d'optimiser
- Documenter les considérations de performance
- Utiliser des structures de données appropriées
- Prendre en compte l'utilisation de la mémoire pour le traitement d'images volumineux

## 6. Documentation

### Documentation du code
- Suivre les docstrings au format Google
- Documenter toutes les API publiques
- Inclure des indications de type pour toutes les signatures de fonction
- Documenter les exceptions qui peuvent être levées

### Documentation du projet
- Maintenir `README.md` à jour
- Documenter les décisions d'architecture dans `DECISIONS.md`
- Mettre à jour `CHANGELOG.md` pour chaque version
- Documenter les variables d'environnement dans `.env.example`

## 7. Sécurité

### Principes généraux
- Ne jamais commettre de données sensibles
- Utiliser des variables d'environnement pour la configuration
- Maintenir les dépendances à jour
- Suivre le principe du moindre privilège

### Authentification
- Utiliser une authentification par jeton sécurisée
- Implémenter une gestion de session appropriée
- Valider toutes les entrées utilisateur
- Nettoyer les sorties pour prévenir les attaques XSS

### Dépendances
- Auditer régulièrement les dépendances pour les vulnérabilités
- Utiliser Dependabot ou des outils similaires
- Épingler toutes les dépendances à des versions spécifiques
- Documenter les dépendances liées à la sécurité

## 8. Spécificités du Projet

### Traitement d'images
- Supporter les formats d'image courants (PNG, JPEG, WEBP)
- Gérer efficacement les images volumineuses
- Implémenter une gestion d'erreur appropriée pour les images corrompues
- Documenter les besoins en mémoire

### Mise en cache
- Utiliser des clés de cache cohérentes
- Implémenter une invalidation du cache
- Documenter le comportement du cache
- Prendre en compte les limites de taille du cache

### Gestion des erreurs
- Utiliser des types d'exception appropriés
- Fournir des messages d'erreur utiles
- Journaliser les erreurs avec suffisamment de contexte
- Implémenter une dégradation gracieuse

## 3. Gestion de Version

### Principes de base
- **Git** comme système de contrôle de version
- **Workflow** : Git Flow ou GitHub Flow selon la taille du projet
- **Messages de commit** : Suivre la convention [Conventional Commits](https://www.conventionalcommits.org/)

### Structure des branches
- `main` : Branche de production
- `develop` : Branche d'intégration
- `feature/*` : Nouvelles fonctionnalités (ex: `feature/description-module`)
- `bugfix/*` : Corrections de bugs
- `hotfix/*` : Corrections critiques pour la production
- `docs/*` : Documentation

## 4. Docker et Conteneurisation

### Bonnes pratiques Docker Compose

#### Configuration
- **Version** : Ne pas utiliser l'attribut `version` obsolète
- **Syntaxe** : Toujours utiliser la dernière version de la syntaxe
- **Commandes** : Préférer `docker compose` (sans tiret) à l'ancienne syntaxe `docker-compose`

Exemple de configuration minimale :

```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
```

### Gestion des Volumes

#### Bonnes pratiques
1. **Déclaration explicite** : Toujours déclarer les volumes dans le fichier `docker-compose.yml`
2. **Nettoyage** : Supprimer les volumes inutilisés régulièrement
3. **Persistance** : Utiliser des volumes nommés pour les données critiques

#### Commandes utiles
```bash
# Lister les volumes
docker volume ls

# Supprimer un volume spécifique
docker volume rm nom_du_volume

# Nettoyer les volumes inutilisés
docker volume prune

# Recréer les volumes (avec mise à jour)
docker compose up -d --force-recreate --renew-anon-volumes
```

## 5. Bonnes Pratiques de Développement

### Structure du Projet
```
fluxgym_coach/
├── __init__.py
├── cli.py          # Point d'entrée CLI
├── config.py       # Gestion de la configuration
├── metadata.py     # Extraction des métadonnées
└── utils/          # Utilitaires
    ├── __init__.py
    ├── validators.py
    └── config.py
```

### Standards de Code Python
- Respecter la PEP 8
- Typage statique avec mypy (fichier de configuration : `mypy.ini`)
- Documentation des fonctions avec docstrings Google style
- Tests unitaires pour chaque nouvelle fonctionnalité

### Gestion des Dépendances
- Utiliser `pyproject.toml` pour la configuration du projet
- Verrouiller les versions avec `poetry lock`
- Mettre à jour régulièrement les dépendances

## 6. Documentation

### Structure de la Documentation
```
docs/
├── api/           # Documentation de l'API
├── architecture/  # Diagrammes et explications
├── deployment/    # Procédures de déploiement
├── guides/        # Guides pas à pas
└── README.md      # Page d'accueil de la documentation
```

### Règles de Documentation
- Documenter chaque fonction et classe avec des docstrings
- Maintenir un fichier `CHANGELOG.md` à jour
- Mettre à jour la documentation lors de chaque modification majeure

## 7. Dépannage

### Problèmes Courants
1. **Problèmes de cache** : Essayer de vider le cache avec `--force-reprocess`
2. **Erreurs de dépendances** : Vérifier les versions avec `poetry check`
3. **Problèmes de configuration** : Vérifier les fichiers de configuration et les variables d'environnement

### Journalisation
- Utiliser le module `logging` de Python
- Niveaux de log appropriés (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Journaliser les erreurs avec suffisamment de contexte pour le débogage

## 8. Spécificités du Projet

### Gestion du Cache
- **Emplacement du cache** : Par défaut dans `~/.cache/fluxgym-coach`, personnalisable via `--cache-dir`
- **Clé de cache** : Basée sur le contenu du fichier et les paramètres de traitement
- **Options de ligne de commande** :
  - `--no-cache` : Désactive complètement le cache
  - `--force-reprocess` : Force le retraitement même si l'image est en cache
  - `--cache-dir` : Spécifie un répertoire personnalisé pour le cache
- **Implémentation** :
  - Utilisation de `xxhash` pour le calcul rapide des empreintes
  - Stockage des métadonnées dans un fichier JSON
  - Nettoyage automatique des entrées invalides
  - Support du cache distribué (à implémenter)

### Traitement par Lots
- Utiliser la méthode `upscale_batch` pour traiter plusieurs images
- Limiter la taille des lots pour éviter les dépassements de mémoire
- Gérer les erreurs de manière granulaire (une image en échec ne doit pas bloquer le traitement des autres)
- Fournir un retour d'état clair sur la progression du traitement
- Documenter les paramètres importants (taille des lots, gestion des erreurs, etc.)
- Utiliser le système de cache pour éviter de retraiter les images inchangées

### Tests
- Utiliser pytest comme framework de test
- Nom des fichiers de test : `test_*.py`
- Couverture de code minimale : 80% (100% pour les fonctionnalités critiques)
- Pour les tests du système de cache :
  - Tester le comportement avec et sans cache
  - Vérifier la détection des fichiers modifiés
  - Tester la persistance du cache entre les sessions
  - Vérifier la gestion des erreurs (fichiers corrompus, permissions, etc.)
- Pour les tests de traitement par lots :
  - Tester avec différentes tailles de lots
  - Vérifier la gestion des erreurs (fichiers corrompus, images trop grandes, etc.)
  - Tester avec des images en noir et blanc et en couleur
  - Vérifier la génération des noms de fichiers de sortie
- Exécuter les tests avant chaque commit :
  ```bash
  pytest tests/ --cov=fluxgym_coach
  ```
