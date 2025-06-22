# Plan de développement : Fluxgym-coach

## Notes
- Le projet `Fluxgym-coach` est un assistant pour la préparation de datasets d'images pour l'outil Fluxgym.
- Le développement doit suivre les directives définies dans `PROTOCOLE_RACINE.md`.
- La version actuelle est 0.4.0 en développement.
- La méthode `colorize_image` a été ajoutée et `upscale_image` a été modifiée pour gérer la recoloration automatique des images N&B.
- La logique de la variable `is_bw` a été corrigée dans `upscale_image`.
- Tous les tests pour `image_enhancement.py` passent maintenant.
- Le mock de la méthode `_call_api` a finalement réussi en remplaçant directement la méthode sur l'instance de l'objet (`monkey patching`).
- L'analyse du code montre que `upscale_image` traite les images une par une. L'optimisation passe par l'implémentation d'une méthode de traitement par lots (`batch processing`).
- L'analyse de l'API Stable Diffusion WebUI suggère que le traitement par lots pour l'upscaling d'images doit passer par l'endpoint `/sdapi/v1/extra-batch-images`.
- La méthode `upscale_batch` a été implémentée pour traiter plusieurs images en une seule requête API.
- La fonction utilitaire `enhance_image` a été mise à jour pour gérer à la fois le traitement d'une seule image et le traitement par lots.
- Les tests unitaires pour `upscale_batch` ont été ajoutés et tous les tests passent.
- L'interface en ligne de commande a été mise à jour pour gérer le traitement par lots, y compris la gestion des motifs glob pour les chemins de fichiers.
- La documentation du projet a été entièrement mise à jour pour refléter les fonctionnalités de traitement par lots.
- Une classe `ImageCache` a été créée dans `fluxgym_coach/image_cache.py` pour gérer la mise en cache des images traitées.
- La dépendance `xxhash` a été ajoutée pour le calcul rapide des empreintes de fichiers.
- La logique de cache a été intégrée avec succès dans la méthode `upscale_batch`.

## Fonctionnalités actuelles
- Amélioration de la qualité des images avec Stable Diffusion Forge
- Traitement par lots des images
- Cache pour éviter le retraitement des images inchangées
- Colorisation automatique des images en noir et blanc
- Interface en ligne de commande conviviale

## Prochaines étapes
1. Ajouter les options de ligne de commande pour contrôler le cache
2. Écrire des tests unitaires pour la méthode `upscale_batch` avec cache
3. Mettre à jour la documentation de la méthode `upscale_batch`
4. Tester les performances avec et sans cache
5. Créer une interface utilisateur graphique
6. Dockeriser l'application
7. Intégrer avec Fluxgym

## Structure du projet
```
fluxgym-coach/
├── fluxgym_coach/
│   ├── __init__.py
│   ├── image_enhancement.py
│   ├── image_cache.py
│   └── __main__.py
├── tests/
│   ├── __init__.py
│   ├── test_image_enhancement.py
│   └── test_image_cache.py
├── docs/
│   ├── CHANGELOG.md
│   ├── ETAT_DU_PROJET.md
│   ├── PROJET.md
│   ├── PROTOCOLE.md
│   └── TODO.md
├── examples/
├── README.md
└── pyproject.toml
```

## Dépendances
- Python 3.8+
- Pillow
- requests
- xxhash
- black (pour le formatage)
- pytest (pour les tests)

## Installation
```bash
pip install -e .
```

## Utilisation
```bash
python -m fluxgym_coach image1.jpg image2.jpg --output output_dir --scale 2
```

## Options de ligne de commande
```
usage: python -m fluxgym_coach [-h] [--output OUTPUT] [--api-url API_URL] [--scale {1,2,3,4}]
                              [--upscaler UPSCALER] [--denoising-strength DENOISING_STRENGTH]
                              [--prompt PROMPT] [--negative-prompt NEGATIVE_PROMPT]
                              [--steps STEPS] [--cfg-scale CFG_SCALE] [--sampler SAMPLER]
                              [--format {PNG,JPEG,JPG,WEBP}] [--no-colorize]
                              [--colorize-prompt COLORIZE_PROMPT]
                              [--colorize-negative-prompt COLORIZE_NEGATIVE_PROMPT] [--no-cache]
                              [--force-reprocess] [--cache-dir CACHE_DIR] [--force] [-v]
                              image_paths [image_paths ...]

positional arguments:
  image_paths           Chemin(s) vers l'image ou les images à améliorer. Peut être un fichier
                        unique, une liste de fichiers, ou un motif glob (ex: 'images/*.jpg')

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Chemin de sortie (fichier pour une image, répertoire pour plusieurs
                        images, par défaut: <nom_original>_enhanced.<format>)
  --api-url API_URL     URL de l'API Stable Diffusion Forge (défaut: http://127.0.0.1:7860)
  --scale {1,2,3,4}     Facteur d'échelle (1-4, défaut: 2)
  --upscaler UPSCALER   Nom de l'upscaler à utiliser (défaut: R-ESRGAN 4x+ Anime6B)
  --denoising-strength DENOISING_STRENGTH
                        Force du débruiteur (0-1, défaut: 0.5)
  --prompt PROMPT       Prompt pour guider l'amélioration
  --negative-prompt NEGATIVE_PROMPT
                        Éléments à éviter dans l'image
  --steps STEPS         Nombre d'étapes de débruiteur
  --cfg-scale CFG_SCALE
                        Échelle de configuration du classificateur
  --sampler SAMPLER     Nom de l'échantillonneur à utiliser
  --format {PNG,JPEG,JPG,WEBP}
                        Format de sortie (défaut: PNG)
  --no-colorize        Désactive la colorisation automatique des images N/B
  --colorize-prompt COLORIZE_PROMPT
                        Prompt personnalisé pour la colorisation
  --colorize-negative-prompt COLORIZE_NEGATIVE_PROMPT
                        Prompt négatif personnalisé pour la colorisation
  --no-cache            Désactive complètement le cache
  --force-reprocess     Force le retraitement même si l'image est en cache
  --cache-dir CACHE_DIR
                        Définit un répertoire personnalisé pour le cache
  --force               Force le retraitement même si le fichier de sortie existe déjà
  -v, --verbose         Active les logs détaillés
```

## Licence
MIT
