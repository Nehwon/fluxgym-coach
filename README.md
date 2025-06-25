# Fluxgym-coach

> Outil d'analyse et d'amélioration d'images pour le coaching sportif

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Description

Fluxgym-coach est un outil d'analyse et d'amélioration d'images spécialement conçu pour les coachs sportifs. Il permet de traiter des images d'exercices, d'en extraire des métadonnées pertinentes et de générer des descriptions automatiques.

## ✨ Fonctionnalités

- Traitement par lots d'images
- Amélioration automatique de la qualité des images
- Extraction des métadonnées EXIF
- Génération de descriptions d'images par IA
- Interface en ligne de commande intuitive
- Cache intelligent pour éviter les retraitements inutiles

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. Cloner le dépôt :
   ```bash
   git clone https://gitea.lamachere.fr/fabrice/fluxgym-coach.git
   cd fluxgym-coach
   ```

2. Créer un environnement virtuel (recommandé) :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## 🛠 Utilisation

### Traiter une image unique
```bash
python -m fluxgym_coach.cli --input chemin/vers/image.jpg --output dossier/sortie/
```

### Traiter un dossier d'images
```bash
python -m fluxgym_coach.cli --input dossier/images/ --output dossier/sortie/ --batch
```

### Générer une description d'image
```bash
python -m fluxgym_coach.cli --input image.jpg --description
```

### Options disponibles
- `--input, -i` : Chemin vers un fichier image ou un dossier contenant des images
- `--output, -o` : Dossier de sortie (optionnel, par défaut: "outputs")
- `--batch, -b` : Traitement par lots (pour les dossiers)
- `--description, -d` : Générer une description de l'image
- `--enhance, -e` : Améliorer la qualité de l'image
- `--cache, -c` : Activer le cache (par défaut: True)
- `--verbose, -v` : Mode verbeux

## 🧪 Tests

Pour exécuter les tests :

```bash
pytest tests/
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## 📞 Contact

Fabrice - fabrice@lamachere.fr

Lien du projet : [https://gitea.lamachere.fr/fabrice/fluxgym-coach](https://gitea.lamachere.fr/fabrice/fluxgym-coach)
