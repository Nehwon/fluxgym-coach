# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2024-06-24

### Corrigé
- **Gestion du cache** :
  - Correction de la détection du cache pour le traitement par lots
  - Amélioration de la génération des clés de cache pour une meilleure fiabilité
  - Ajout de logs détaillés pour les opérations de cache
- **Traitement par lots** :
  - Correction de l'agrégation des résultats dans la méthode `upscale_batch`
  - Amélioration de la gestion des erreurs pour les images en cache/non-cache
  - Correction de l'erreur HTTP 422 dans les appels API par lots

### Ajouté
- **Documentation** :
  - Ajout de DECISIONS.md pour le suivi des décisions techniques
  - Mise à jour de la structure de la documentation du projet
  - Amélioration de la documentation du code

### Modifié
- **Qualité du code** :
  - Refactorisation du code de gestion du cache
  - Amélioration des messages d'erreur et des logs
  - Amélioration de la maintenabilité du code

## [0.2.0] - 2024-06-23

## [0.1.0] - 2025-06-23

### Ajouté
- **Tests et Benchmarks** :
  - Script de benchmark pour mesurer les performances du cache
  - Génération d'images de test avec dégradés et texte
  - Mesure des temps d'exécution avec et sans cache
  - Statistiques détaillées (moyenne, min, max, écart-type)
  - Support pour des exécutions multiples pour des résultats fiables

### Modifié
- **Documentation** :
  - Fusion de `PROTOCOLE.md` et `PROTOCOLE_RACINE.md` en un seul fichier
  - Mise à jour du fichier `PROJET.md` avec le plan de développement actuel
  - Ajout de règles de contribution dans `PROTOCOLE_RACINE.md`
  - Amélioration de la documentation des tests

### Corrigé
- **Cache** :
  - Correction de la détection des fichiers modifiés
  - Amélioration de la gestion des erreurs lors de la lecture/écriture du cache
  - Nettoyage automatique des entrées de cache invalides

### Modifications Techniques
- Migration vers Python 3.8+
- Ajout des dépendances : `numpy`, `Pillow` pour les tests
- Mise à jour des dépendances de développement

## [0.0.1] - 2025-06-22

### Ajouté
- **Système de cache** :
  - Nouvelle classe `ImageCache` pour gérer la mise en cache des images traitées
  - Intégration du cache dans la méthode `upscale_batch`
  - Vérification des empreintes de fichiers pour détecter les modifications
  - Options de ligne de commande pour contrôler le cache (`--no-cache`, `--force-reprocess`, `--cache-dir`)
  - Support du cache pour éviter le retraitement des images inchangées
  - Gestion des paramètres de traitement dans la clé de cache
  - Utilisation de `xxhash` pour le calcul rapide des empreintes de fichiers

- **Traitement par lots** :
  - Nouvelle méthode `upscale_batch` pour traiter plusieurs images en une seule requête
  - Support des motifs glob pour la sélection des fichiers
  - Gestion des erreurs granulaire (une image en échec ne bloque pas le traitement des autres)
  - Affichage détaillé de la progression
  - Option pour désactiver la colorisation automatique
  - Taille de lot configurable

- **Colorisation automatique** :
  - Détection intelligente des images en noir et blanc
  - Colorisation automatique via l'API Stable Diffusion
  - Paramètres personnalisables pour la colorisation
  - Gestion des échecs de colorisation avec repli sur le mode N/B

- **Tests unitaires** :
  - Couverture complète du module `image_enhancement.py` (100%)
  - Tests pour la méthode `upscale_batch`
  - Tests pour la gestion des erreurs dans le traitement par lots
  - Fixtures pour les tests d'images
  - Mocks pour les appels API avec `requests`
  - Tests de gestion des erreurs d'API
  - Tests pour la détection des images en noir et blanc
  - Tests pour le prétraitement des images avec canal alpha
  - Tests pour la gestion des formats non supportés
  - Tests pour la validation des paramètres

- **Configuration** :
  - Mise en place de mypy pour la vérification de types
  - Configuration de pytest pour la couverture de code
  - Intégration avec les outils de qualité de code

### Ajouté
- **Système de cache** :
  - Nouvelle classe `ImageCache` pour gérer la mise en cache des images traitées
  - Intégration du cache dans la méthode `upscale_batch`
  - Vérification des empreintes de fichiers pour détecter les modifications
  - Options de ligne de commande pour contrôler le cache (`--no-cache`, `--force-reprocess`, `--cache-dir`)
  - Support du cache pour éviter le retraitement des images inchangées
  - Gestion des paramètres de traitement dans la clé de cache
  - Utilisation de `xxhash` pour le calcul rapide des empreintes de fichiers

### Ajouté
- **Traitement par lots** :
  - Nouvelle méthode `upscale_batch` pour traiter plusieurs images en une seule requête
  - Support des motifs glob pour la sélection des fichiers
  - Gestion des erreurs granulaire (une image en échec ne bloque pas le traitement des autres)
  - Affichage détaillé de la progression
  - Option pour désactiver la colorisation automatique
  - Taille de lot configurable

- **Colorisation automatique** :
  - Détection intelligente des images en noir et blanc
  - Colorisation automatique via l'API Stable Diffusion
  - Paramètres personnalisables pour la colorisation
  - Gestion des échecs de colorisation avec repli sur le mode N/B

- **Tests unitaires** :
  - Couverture complète du module `image_enhancement.py` (100%)
  - Tests pour la méthode `upscale_batch`
  - Tests pour la gestion des erreurs dans le traitement par lots
  - Fixtures pour les tests d'images
  - Mocks pour les appels API avec `requests`
  - Tests de gestion des erreurs d'API
  - Tests pour la détection des images en noir et blanc
  - Tests pour le prétraitement des images avec canal alpha
  - Tests pour la gestion des formats non supportés
  - Tests pour la validation des paramètres

- **Configuration** :
  - Mise en place de mypy pour la vérification de types
  - Configuration de pytest pour la couverture de code
  - Intégration avec les outils de qualité de code

- **Améliorations** :
  - Meilleure gestion de la mémoire lors du traitement par lots
  - Conversion forcée en PNG pour les images de sortie
  - Détection améliorée des images en noir et blanc
  - Documentation mise à jour avec les nouvelles fonctionnalités
  - Interface en ligne de commande améliorée avec plus d'options

### Modifié
- **Refactoring** :
  - Correction des erreurs de typage signalées par mypy
  - Amélioration de la structure du code
  - Optimisation des imports
  - Mise à jour des dépendances

- **Documentation** :
  - Mise à jour du README avec les instructions de test
  - Ajout d'exemples d'utilisation
  - Documentation des nouvelles fonctionnalités

### Corrigé
- **Bugs** :
  - Correction des fuites de mémoire dans le traitement par lots
  - Résolution du problème de redimensionnement non proportionnel

## [Non publié] - 2025-06-21

### Ajouté
- Intégration de Stable Diffusion Forge pour l'amélioration d'images
  - Support de l'upscaling avec différents facteurs d'échelle
  - Détection automatique des images en noir et blanc
  - Conversion automatique des formats d'image (WebP, JPG, PNG, etc.)
  - Redimensionnement intelligent avec conservation des proportions
- Nouveau module `image_enhancement.py` pour gérer l'amélioration d'images
- Documentation complète pour l'API d'amélioration d'images
- Tests unitaires pour les nouvelles fonctionnalités

### Corrigé
- **Bugs** :
  - Correction des fuites de mémoire dans le traitement par lots
  - Résolution du problème de redimensionnement non proportionnel
  - Correction de la gestion des erreurs lors de l'appel à l'API
  - Problème de format de sortie non respecté

- **Sécurité** :
  - Mise à jour des dépendances vulnérables
  - Renforcement de la validation des entrées
  - Amélioration de la gestion des erreurs

- **Performances** :
  - Optimisation de l'utilisation de la mémoire
  - Réduction du temps d'exécution des tests
  - Amélioration de la réactivité de l'interface

### Supprimé
- Code obsolète et non utilisé
- Fichiers de configuration redondants
- Anciennes versions des dépendances
- Correction des erreurs de style dans les tests
- Amélioration de la gestion des erreurs et des messages de log
- Mise à jour des dépendances dans `requirements.txt`
- Correction des problèmes de compatibilité avec Python 3.13

## [0.2.0] - 2025-06-20

### Modifié
- Refactorisation du module `metadata.py` pour utiliser un hachage de contenu pour nommer les fichiers de métadonnées
- Amélioration de la déduplication des métadonnées pour les images identiques
- Mise à jour des tests pour refléter les changements de comportement
- Création de la branche `feature/fluxgym-coach` pour le développement

## [0.1.0] - 2025-06-20

### Ajouté
- Structure initiale du projet
- Module de traitement d'images avec renommage par hachage
- Module d'extraction de métadonnées EXIF et de base
- Interface en ligne de commande (CLI) de base
- Système de configuration
- Utilitaires de validation
- Documentation de base

### Modifié
- Initialisation du projet

### Supprimé
- Aucune suppression pour le moment

[0.1.0]: https://gitea.lamachere.fr/fabrice/docker/tree/feature/fluxgym-coach