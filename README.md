# Fluxgym-coach

> Outil d'amélioration d'images pour le coaching sportif avec architecture modulaire

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Description

Fluxgym-coach est un outil d'amélioration d'images spécialement conçu pour les coachs sportifs. Il permet d'améliorer la qualité des images d'exercices à l'aide de l'API Stable Diffusion, avec une architecture modulaire et extensible.

## ✨ Fonctionnalités

- Amélioration de la qualité des images (upscaling)
- Architecture modulaire basée sur des plugins
- Cache intelligent pour éviter les retraitements inutiles
- Gestion robuste des erreurs et des reprises
- Interface simple et cohérente
- Support pour différents types d'images (PNG, JPG, etc.)

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Serveur Stable Diffusion Forge en cours d'exécution (par défaut sur http://127.0.0.1:7860)

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

3. Installer le package en mode développement :
   ```bash
   pip install -e .
   ```

## 🛠 Utilisation

### Améliorer une image unique

```python
from fluxgym_coach import ImageEnhancer

# Créer une instance de l'améliorateur d'images
enhancer = ImageEnhancer(api_url="http://127.0.0.1:7860")

# Améliorer une image
output_path, success = enhancer.upscale_image(
    "chemin/vers/image.jpg",
    output_path="chemin/de/sortie/image_amelioree.png",
    scale_factor=2,
    upscaler="R-ESRGAN_4x+",
    denoising_strength=0.5
)

if success:
    print(f"Image améliorée enregistrée : {output_path}")
else:
    print("Échec de l'amélioration de l'image")
```

### Options disponibles

- `scale_factor` (int): Facteur d'agrandissement (1-4)
- `upscaler` (str): Nom de l'upscaler à utiliser (par défaut: "R-ESRGAN_4x+")
- `denoising_strength` (float): Force du débruiteur (0-1)
- `prompt` (str): Prompt pour guider l'amélioration
- `negative_prompt` (str): Éléments à éviter
- `steps` (int): Nombre d'étapes de débruiteur
- `cfg_scale` (float): Échelle de configuration du classificateur
- `sampler_name` (str): Nom de l'échantillonneur à utiliser
- `output_format` (str): Format de sortie (PNG par défaut)

## 🔌 Architecture modulaire

L'application est conçue avec une architecture modulaire qui permet d'ajouter facilement de nouvelles fonctionnalités via des plugins. Les fonctionnalités non essentielles (comme le traitement par lots ou la colorisation) sont disponibles sous forme de plugins séparés.

### Création d'un plugin

Pour créer un nouveau plugin, créez une classe qui hérite de `BasePlugin` et implémentez les méthodes nécessaires. Consultez la documentation des plugins pour plus de détails.

## 📊 Performances

- Utilisation efficace de la mémoire
- Cache intelligent pour éviter les retraitements inutiles
- Gestion des erreurs robuste avec mécanisme de nouvelle tentative
- Support du traitement asynchrone pour les opérations longues

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
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
