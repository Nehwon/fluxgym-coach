# Fluxgym-coach

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-100%25-success)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-0.2.1-blue)](https://github.com/Nehwon/fluxgym-coach/releases/tag/v0.2.1)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://github.com/Nehwon/fluxgym-coach/tree/main/docs)

Outil de préparation et d'amélioration de jeux de données d'images pour Fluxgym avec suréchantillonnage par IA et traitement par lots.

## 🌍 Documentation disponible

- [Documentation en français](README.fr.md) (actuelle)
- [English Documentation](README.en.md)
- [Journal des modifications](CHANGELOG.fr.md) / [Changelog](CHANGELOG.md)
- [État du Projet](ETAT_DU_PROJET.md) / [Project Status](PROJECT_STATUS.md)
- [Protocole de Développement](PROTOCOLE_RACINE.fr.md) / [Development Protocol](PROTOCOLE_RACINE.md)

## 🚀 Fonctionnalités

- **Amélioration d'images par IA**
  - Suréchantillonnage de haute qualité avec Stable Diffusion Forge
  - Traitement par lots de plusieurs images
  - Détection et colorisation automatique des images en noir et blanc
  - Système de cache intelligent pour des performances optimalisées

- **Traitement avancé**
  - Support de plusieurs formats d'images (PNG, JPEG, WEBP)
  - Paramètres de suréchantillonnage configurables
  - Gestion granulaire des erreurs
  - Journalisation détaillée de la progression

- **Conçu pour les développeurs**
  - Annotations de type dans tout le code
  - Suite de tests complète
  - Style de code propre et cohérent
  - Documentation API détaillée

## 📦 Prérequis

- Python 3.8 ou supérieur
- Serveur Stable Diffusion WebUI Forge (pour l'amélioration d'images)
- Bibliothèques Python requises (voir `setup.py` pour la liste complète) :
  - `requests` : Pour les requêtes HTTP
  - `Pillow` : Pour le traitement d'images
  - `python-multipart` : Pour le téléversement de fichiers
  - `xxhash` : Pour l'empreinte rapide des fichiers
  - `tqdm` : Pour les barres de progression
- **Déduplication intelligente** : Détection et gestion des images en double basée sur le hachage de contenu
- **Extraction complète des métadonnées** : Récupération des données EXIF et autres métadonnées techniques
- **Renommage sécurisé** : Utilisation de hachages uniques pour éviter les conflits de noms
- **Interface en ligne de commande** : Simple et intuitive pour une intégration facile dans des pipelines
- **Gestion des erreurs robuste** : Journalisation détaillée et rapports clairs

## 📦 Prérequis

### Système
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (pour le clonage du dépôt)

### Dépendances principales
- `Pillow` : Traitement d'images
- `numpy` : Calculs numériques
- `requests` : Requêtes HTTP
- `python-multipart` : Téléchargement de fichiers
- `xxhash` : Calcul rapide d'empreintes

### Pour le développement
- `pytest` : Exécution des tests
- `black` : Formatage du code
- `mypy` : Vérification de types
- `pytest-cov` : Couverture des tests

> **Note** : Pour l'amélioration d'images, un serveur Stable Diffusion WebUI Forge est requis.

## 🧪 Exécution des tests

Pour exécuter les tests unitaires :

```bash
# Installer les dépendances de test
pip install -e ".[test]"

# Exécuter tous les tests
pytest

# Exécuter les tests avec couverture
pytest --cov=fluxgym_coach --cov-report=term-missing

# Vérifier les types avec mypy
mypy .
```

## 🛠️ Développement

Le projet utilise plusieurs outils pour assurer la qualité du code :

- **mypy** : Vérification statique des types
- **pytest** : Exécution des tests unitaires
- **black** : Formatage du code
- **flake8** : Vérification du style de code

Pour configurer l'environnement de développement :

```bash
# Installer les dépendances de développement
pip install -e ".[dev]"

# Formater le code avec black
black .

# Vérifier le style avec flake8
flake8
```

## 🚀 Installation

### Prérequis

- Stable Diffusion WebUI Forge doit être installé et en cours d'exécution pour l'amélioration d'images
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (pour le clonage du dépôt)

### Étapes d'installation

1. **Cloner le dépôt** :
   ```bash
# Clone the repository
git clone git@github.com:Nehwon/fluxgym-coach.git
cd fluxgym-coach
```

2. **Créer et activer un environnement virtuel** (recommandé) :
   ```bash
   # Sur Linux/Mac
   python -m venv .venv
   source .venv/bin/activate
   
   # Sur Windows
   # python -m venv .venv
   # .venv\Scripts\activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -e .
   ```
   
4. **Installer les dépendances pour le traitement d'images** :
   ```bash
   pip install Pillow numpy requests
   ```

## 🛠️ Utilisation

### Commandes de base

```bash
# Afficher l'aide
fluxgym-coach --help

# Traiter un dossier d'images (renommage et extraction des métadonnées)
fluxgym-coach -i chemin/vers/le/dossier/source -o chemin/vers/le/dossier/destination

# Améliorer la qualité des images
fluxgym-coach -i source -o destination -p enhance --scale-factor 2
```

### Options de cache

Le système de cache peut être contrôlé via les options suivantes :

- `--no-cache` : Désactive complètement le cache
- `--force-reprocess` : Force le retraitement de toutes les images, même si elles sont en cache
- `--cache-dir CHEMIN` : Spécifie un répertoire personnalisé pour le cache
- `--clean-cache` : Nettoie les entrées obsolètes du cache avant le traitement

### Options d'amélioration d'images
```bash
python -m fluxgym_coach.image_enhancement chemin/vers/image.jpg --output chemin/de/sortie.jpg
```

#### Traitement par lots

Traiter plusieurs images en une seule commande :

```bash
# Traiter plusieurs images spécifiques
python -m fluxgym_coach.image_enhancement image1.jpg image2.jpg image3.jpg --output dossier/sortie/

# Utiliser un motif glob pour sélectionner des fichiers
python -m fluxgym_coach.image_enhancement "dossier/images/*.jpg" --output dossier/sortie/

# Spécifier la taille des lots (par défaut: 5)
python -m fluxgym_coach.image_enhancement "dossier/images/*.jpg" --batch-size 10 --output dossier/sortie/

# Désactiver le cache (forcer le retraitement)
python -m fluxgym_coach.image_enhancement "dossier/images/*.jpg" --no-cache --output dossier/sortie/

# Forcer le retraitement de toutes les images, même en cache
python -m fluxgym_coach.image_enhancement "dossier/images/*.jpg" --force-reprocess --output dossier/sortie/

# Spécifier un répertoire personnalisé pour le cache
python -m fluxgym_coach.image_enhancement "dossier/images/*.jpg" --cache-dir /chemin/vers/cache --output dossier/sortie/

# Nettoyer le cache avant le traitement
python -m fluxgym_coach.image_enhancement "dossier/images/*.jpg" --clean-cache --output dossier/sortie/

# Combiner plusieurs options de cache
python -m fluxgym_coach.image_enhancement "dossier/images/*.jpg" --cache-dir /chemin/vers/cache --clean-cache --output dossier/sortie/

# Désactiver la colorisation automatique des images N&B
python -m fluxgym_coach.image_enhancement "dossier/images/*.jpg" --no-colorize --output dossier/sortie/
```

#### Options disponibles

- `--output`, `-o` : Chemin de sortie (fichier pour une image, répertoire pour plusieurs images, par défaut: <nom_original>_enhanced.<format>)
- `--scale` : Facteur d'échelle (1-4, par défaut: 2)
- `--api-url` : URL de l'API Stable Diffusion WebUI (par défaut: http://127.0.0.1:7860)
- `--batch-size` : Taille des lots pour le traitement par lots (par défaut: 5)
- `--no-colorize` : Désactive la colorisation automatique des images noir et blanc
- `--upscaler` : Modèle d'upscaling à utiliser (par défaut: "R-ESRGAN 4x+ Anime6B")
- `--prompt` : Prompt positif pour guider l'amélioration
- `--negative-prompt` : Éléments à éviter dans l'image améliorée

### Exemples avancés

```bash
# Traiter toutes les images JPG et PNG d'un répertoire
python -m fluxgym_coach.image_enhancement "dossier/*.jpg" "dossier/*.png" --output resultats/

# Utiliser un facteur d'échelle personnalisé et un upscaler spécifique
python -m fluxgym_coach.image_enhancement "images/*.jpg" --scale 3 --upscaler "4x-UltraSharp" --output upscaled/

# Traiter des images avec un prompt personnalisé pour guider l'amélioration
python -m fluxgym_coach.image_enhancement "portraits/*.jpg" --prompt "high quality portrait, detailed face, professional photography" --output portraits_enhanced/
```

### Gestion des erreurs

- Les images qui échouent au traitement sont ignorées, permettant au traitement de se poursuivre avec les autres images
- Un résumé est affiché à la fin du traitement avec le nombre d'images traitées avec succès
- Les erreurs détaillées sont enregistrées dans les logs pour analyse

### Options disponibles

```
--input DIR      Dossier source contenant les images à traiter (obligatoire)
--output DIR     Dossier de destination pour les résultats (obligatoire)
--process TYPE   Type de traitement : 'all', 'images' ou 'metadata' (défaut: 'all')
--verbose        Active le mode verbeux pour plus de détails
--config FILE    Chemin vers un fichier de configuration personnalisé
```

### Exemples

**Traitement complet (images + métadonnées)** :
```bash
python -m fluxgym_coach.cli --input ~/images/ --output datasets/ --process all
```

**Extraction des métadonnées uniquement** :
```bash
python -m fluxgym_coach.cli --input ~/images/ --output datasets/ --process metadata
```

**Mode verbeux** :
```bash
python -m fluxgym_coach.cli --input ~/images/ --output datasets/ --verbose
```

## 🔧 Configuration

Le fichier de configuration par défaut est chargé depuis `~/.config/fluxgym/config.json`. Vous pouvez le personnaliser selon vos besoins ou en spécifiant un autre fichier avec l'option `--config`.

## 📊 Structure des dossiers

```
output/
├── images/           # Images traitées et dédupliquées
├── metadata/         # Fichiers de métadonnées au format JSON
└── logs/             # Fichiers de journalisation
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📝 Protocole de Développement

Ce projet suit un protocole de développement détaillé qui couvre les standards de code, le workflow de développement, les bonnes pratiques et plus encore. Consultez le fichier [PROTOCOLE.md](PROTOCOLE.md) pour plus d'informations.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🧪 Tests

Pour exécuter les tests unitaires :

```bash
pytest tests/
```

Pour exécuter les tests d'intégration :

```bash
pytest tests/integration/
```

## 📂 Structure du projet

```
fluxgym-coach/
├── fluxgym_coach/           # Code source du package
│   ├── __init__.py          # Initialisation du package
│   ├── cli.py               # Interface en ligne de commande
│   ├── processor.py         # Traitement des images et déduplication
│   ├── metadata.py          # Extraction et gestion des métadonnées
│   └── utils/               # Utilitaires
│       ├── __init__.py
│       ├── config.py        # Gestion de la configuration
│       └── validators.py    # Validation des entrées
├── tests/                   # Tests unitaires et d'intégration
│   ├── integration/
│   └── unit/
├── .gitignore
├── CHANGELOG.md            # Historique des modifications
├── pyproject.toml          # Configuration du projet
└── README.md               # Ce fichier
```

## 👥 Auteurs

- Fabrice Lamachère - Développement initial

## 🙏 Remerciements

- Toute personne ou ressource ayant contribué au projet

---

Développé avec ❤️ pour Fluxgym
