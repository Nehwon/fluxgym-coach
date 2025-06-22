# Protocole de Développement Fluxgym-coach

## Table des matières
1. [Communication](#1-communication)
2. [Standards Techniques](#2-standards-techniques)
3. [Gestion de Version](#3-gestion-de-version)
4. [Docker et Conteneurisation](#4-docker-et-conteneurisation)
5. [Bonnes Pratiques de Développement](#5-bonnes-pratiques-de-développement)
6. [Documentation](#6-documentation)
7. [Dépannage](#7-dépannage)
8. [Spécificités du Projet](#8-spécificités-du-projet)

## 1. Communication

### Principes généraux
- **Langue** : Français (sauf pour le code et les identifiants techniques)
- **Style** : Professionnel mais décontracté
- **Fréquence des mises à jour** : Continue, au fil du développement

### Outils recommandés
- Suivi des tâches : Gitea Issues ou équivalent
- Communication asynchrone : Email ou outil de messagerie d'équipe
- Réunions : Agenda partagé avec ordre du jour défini à l'avance

### Règles de communication
- Toujours mentionner le contexte du projet
- Utiliser des références claires aux tickets ou problèmes
- Documenter les décisions importantes dans le fichier `DECISIONS.md`

## 2. Standards Techniques

### Langages et Frameworks
- **Python** : PEP 8, typage statique avec mypy
- **JavaScript/TypeScript** : ESLint, Prettier
- **Autres langages** : Suivre les conventions standards de la communauté

### Qualité du code
- Tests unitaires avec une couverture minimale de 80%
- Revue de code obligatoire avant fusion (Pull Request)
- Intégration continue avec vérification des tests et du linting

### Sécurité
- Ne jamais stocker de données sensibles en clair dans le code
- Utiliser des variables d'environnement pour les configurations sensibles
- Mettre à jour régulièrement les dépendances pour corriger les vulnérabilités connues

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
