# Module d'Amélioration d'Image

Ce module permet d'améliorer la qualité et la résolution des images en utilisant Stable Diffusion Forge via son API. Il inclut également des fonctionnalités avancées comme la colorisation automatique des images en noir et blanc.

## Prérequis

1. Avoir Stable Diffusion WebUI Forge installé et en cours d'exécution
2. L'API doit être accessible (par défaut sur `http://127.0.0.1:7860`)
3. Les dépendances Python nécessaires doivent être installées (voir `requirements.txt`)

## Installation

1. Installez les dépendances requises :

```bash
pip install -r requirements.txt
```

2. Assurez-vous que Stable Diffusion WebUI Forge est en cours d'exécution avec l'API activée.

## Utilisation

### En tant que module Python

```python
from fluxgym_coach.image_enhancement import enhance_image

# Amélioration simple d'une image
enhanced_image_path = enhance_image(
    "chemin/vers/image.jpg",
    output_path="chemin/vers/image_amelioree.jpg",
    scale_factor=2,
    upscaler="R-ESRGAN 4x+ Anime6B",
    denoising_strength=0.5
)

# Utilisation avancée avec la classe ImageEnhancer
from fluxgym_coach.image_enhancement import ImageEnhancer

enhancer = ImageEnhancer(api_url="http://127.0.0.1:7860")

# Personnalisation avancée
enhanced_image_path = enhancer.upscale_image(
    "chemin/vers/image.jpg",
    output_path="chemin/vers/image_amelioree.jpg",
    scale_factor=2,
    upscaler="R-ESRGAN 4x+ Anime6B",
    denoising_strength=0.5,
    prompt="high quality, high resolution, detailed",
    negative_prompt="blurry, lowres, low quality, artifacts, jpeg artifacts",
    steps=20,
    cfg_scale=7.0,
    sampler_name="DPM++ 2M"
)
```

### En ligne de commande

```bash
python -m fluxgym_coach.image_enhancement chemin/vers/image.jpg -o chemin/vers/sortie.jpg --scale 2 --upscaler "R-ESRGAN 4x+ Anime6B" --denoising-strength 0.5
```

### Paramètres de la fonction `enhance_image` et `upscale_image`

#### Paramètres principaux
- `image_path` (obligatoire) : Chemin vers l'image source à améliorer
- `output_path` : Chemin de sortie pour l'image améliorée (par défaut : `<nom>_upscaled.<ext>`)
- `api_url` : URL de l'API Stable Diffusion WebUI (par défaut : `http://127.0.0.1:7860`)
- `scale_factor` : Facteur d'échelle (1-4, par défaut : 2)
- `upscaler` : Nom de l'upscaler à utiliser (par défaut : "R-ESRGAN 4x+ Anime6B")
- `denoising_strength` : Force du débruiteur (0-1, par défaut : 0.5)

#### Paramètres de génération
- `prompt` : Prompt pour guider l'amélioration (par défaut : "high quality, high resolution, detailed")
- `negative_prompt` : Éléments à éviter (par défaut : "blurry, lowres, low quality, artifacts, jpeg artifacts")
- `steps` : Nombre d'étapes de débruiteur (par défaut : 20)
- `cfg_scale` : Échelle de configuration du classificateur (par défaut : 7.0)
- `sampler_name` : Nom de l'échantillonneur à utiliser (par défaut : "DPM++ 2M")

#### Paramètres de colorisation
- `auto_colorize` : Active la colorisation automatique des images en noir et blanc (par défaut : `True`)
- `colorize_prompt` : Prompt personnalisé pour la colorisation (optionnel)
- `colorize_negative_prompt` : Prompt négatif personnalisé pour la colorisation (optionnel)
- `colorize_steps` : Nombre d'étapes pour la colorisation (par défaut : 30)
- `colorize_cfg_scale` : Échelle CFG pour la colorisation (par défaut : 7.0)

## Configuration de Stable Diffusion Forge

Pour de meilleurs résultats, assurez-vous que Stable Diffusion Forge est correctement configuré :

1. Activez l'API dans les paramètres de Stable Diffusion WebUI Forge
2. Vérifiez que les modèles d'upscaling nécessaires sont installés
3. Ajustez la mémoire GPU allouée selon vos besoins

## Dépannage

- **Erreur de connexion** : Vérifiez que Stable Diffusion WebUI Forge est en cours d'exécution et que l'API est accessible
- **Erreur de mémoire** : Réduisez la taille du batch ou la résolution des images
- **Qualité insuffisante** : Ajustez le `denoising_strength` ou le prompt

## Exemples

### Amélioration simple

```python
from fluxgym_coach.image_enhancement import enhance_image

# Amélioration simple avec les paramètres par défaut
enhance_image("photo.jpg", "photo_enhanced.jpg", scale_factor=2)

# Désactiver la colorisation automatique
enhance_image("bw_photo.jpg", "color_photo_enhanced.jpg", auto_colorize=False)
```

### Utilisation avancée avec colorisation

```python
from fluxgym_coach.image_enhancement import ImageEnhancer

enhancer = ImageEnhancer()

# Amélioration avec colorisation personnalisée
enhancer.upscale_image(
    "old_bw_photo.jpg",
    "colorized_photo.jpg",
    scale_factor=2,
    auto_colorize=True,
    colorize_prompt="high quality, colorized, vibrant colors, detailed",
    colorize_negative_prompt="black and white, grayscale, blurry, low quality"
)
```

### Amélioration par lots

```python
from pathlib import Path
from fluxgym_coach.image_enhancement import ImageEnhancer

enhancer = ImageEnhancer()
input_dir = Path("images/input")
output_dir = Path("images/enhanced")
output_dir.mkdir(exist_ok=True)

for img_path in input_dir.glob("*.jpg"):
    output_path = output_dir / f"enhanced_{img_path.name}"
    try:
        enhancer.upscale_image(img_path, output_path, scale_factor=2)
        print(f"Image améliorée : {output_path}")
    except Exception as e:
        print(f"Erreur avec {img_path}: {e}")
```

## Détection et traitement des images N&B

Le module détecte automatiquement les images en noir et blanc et peut les coloriser si l'option `auto_colorize` est activée. La détection se base sur l'analyse des canaux de couleur et considère une image comme N&B si elle contient principalement des niveaux de gris.

### Comportement par défaut

- Si une image est détectée comme N/B et que `auto_colorize=True` :
  1. L'image est d'abord colorisée
  2. L'image colorisée est ensuite upscalée
  3. Le flag `is_bw` est retourné comme `False` dans le tuple de retour

- Si `auto_colorize=False` ou si la colorisation échoue :
  - Des tags N/B sont ajoutés au prompt pour conserver le style monochrome
  - Le flag `is_bw` est retourné comme `True`

## Notes techniques

- L'API doit être accessible depuis votre réseau pour fonctionner
- Les temps de traitement peuvent varier en fonction de la puissance de votre GPU
- La colorisation des images N/B nécessite un modèle Stable Diffusion correctement configuré
- Pour une utilisation en production, envisagez d'ajouter une file d'attente et une gestion des erreurs plus robuste
- La détection N/B peut être ajustée avec le paramètre `bw_threshold` des méthodes internes si nécessaire
