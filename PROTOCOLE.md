# Protocole de Développement Fluxgym-coach

## 📌 Introduction
Ce document complète le [PROTOCOLE_RACINE.md](../PROTOCOLE_RACINE.md) avec des règles spécifiques au projet Fluxgym-coach.

## 🔄 Gestion des Branches
- Branche principale : `main` (branche de production)
- Branche de développement : `develop`
- Branche de fonctionnalité : `feature/*` (ex: `feature/description-module`)
- Branche de correction : `bugfix/*`
- Branche de documentation : `docs/*`

## 🏗️ Structure du Projet

### Organisation du Code
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

## 🛠️ Standards de Code

### Python
- Respecter la PEP 8
- Typage statique avec mypy (fichier de configuration : `mypy.ini`)
- Documentation des fonctions avec docstrings Google style
- Tests unitaires pour chaque nouvelle fonctionnalité

### Traitement par lots
- Utiliser la méthode `upscale_batch` pour traiter plusieurs images
- Limiter la taille des lots pour éviter les dépassements de mémoire
- Gérer les erreurs de manière granulaire (une image en échec ne doit pas bloquer le traitement des autres)
- Fournir un retour d'état clair sur la progression du traitement
- Documenter les paramètres importants (taille des lots, gestion des erreurs, etc.)
- Utiliser le système de cache pour éviter de retraiter les images inchangées

### Gestion du cache
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

## 📦 Gestion des Dépendances
- Utiliser `pyproject.toml` pour la configuration du projet
- Verrouiller les versions avec `poetry lock`
- Mettre à jour régulièrement les dépendances

## 🔄 Workflow de Développement

1. Créer une branche depuis `develop`
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/nouvelle-fonctionnalite
   ```

2. Développer la fonctionnalité
   - Faire des commits atomiques
   - Écrire des messages de commit clairs et descriptifs
   - Documenter le code

3. Soumettre une Pull Request
   - La PR doit être revue par au moins un développeur
   - Tous les tests doivent passer
   - La couverture de code doit être maintenue

4. Fusionner dans `develop`
   - Squash des commits si nécessaire
   - Supprimer la branche après fusion

## 📝 Documentation

### Documentation du Code
- Documenter toutes les fonctions et classes
- Inclure des exemples d'utilisation
- Maintenir à jour le `README.md`

### Journal des Changements
- Mettre à jour le `CHANGELOG.md` pour chaque version
- Suivre le format [Keep a Changelog](https://keepachangelog.com/)

## 🔍 Revue de Code

### Avant la Revue
- Exécuter tous les tests
- Vérifier la couverture de code
- S'assurer que la documentation est à jour

### Pendant la Revue
- Vérifier la qualité du code
- S'assurer que le code respecte les standards
- Vérifier la couverture des tests

## 🚀 Déploiement

### Versionnage
- Suivre le versionnage sémantique (SemVer)
- Créer un tag pour chaque version
- Documenter les changements dans le CHANGELOG

### Processus de Publication
1. Mettre à jour le numéro de version dans `pyproject.toml`
2. Mettre à jour le `CHANGELOG.md`
3. Créer un tag annoté
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   ```
4. Pousser les changements et les tags
   ```bash
   git push origin main --tags
   ```

## 🔒 Sécurité
- Ne jamais stocker de données sensibles en clair
- Utiliser des variables d'environnement pour les configurations sensibles
- Vérifier les vulnérabilités connues avec `safety check`

## 🤖 Intégration Continue
- Exécuter les tests à chaque push
- Vérifier la qualité du code avec flake8
- Vérifier les types avec mypy
- Vérifier la couverture de code

## 🔄 Gestion des Problèmes
- Créer une issue pour chaque problème
- Utiliser les modèles d'issue fournis
- Assigner des labels appropriés
- Référencer les numéros d'issue dans les commits

## 📚 Ressources
- [Documentation Python](https://docs.python.org/)
- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Documentation Pytest](https://docs.pytest.org/)
- [Documentation Mypy](https://mypy.readthedocs.io/)

## 👥 Contribution
Voir le fichier `CONTRIBUTING.md` pour les directives détaillées sur la contribution au projet.
