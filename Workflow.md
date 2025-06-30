# Workflow de Traitement d'Image "Un par un"

Ce document décrit le flux de traitement complet pour l'amélioration d'une seule image avec Fluxgym-coach, y compris la génération de description et la validation par l'utilisateur.

## Vue d'ensemble

Le traitement d'une image suit ces étapes principales :

1. **Initialisation**
2. **Validation de l'entrée**
3. **Gestion du cache**
4. **Prétraitement**
5. **Appel à l'API Stable Diffusion**
6. **Post-traitement**
7. **Génération de description**
   - Analyse de l'image pour générer une description automatique
   - Proposition de tags pertinents
   - Extraction des métadonnées techniques

8. **Révision par l'utilisateur**
   - Affichage de la description générée
   - Édition et validation par l'utilisateur
   - Ajustement des paramètres si nécessaire

9. **Validation finale**
   - Aperçu du résultat final
   - Validation ou rejet par l'utilisateur
   - Option de retraitement avec paramètres ajustés

10. **Sauvegarde et archivage**
    - Enregistrement de l'image améliorée
    - Stockage des métadonnées et descriptions
    - Mise à jour de la base de données d'apprentissage

11. **Feedback et amélioration**
    - Collecte des retours utilisateur
    - Amélioration du modèle basée sur les validations
    - Ajustement des paramètres par défaut

## Interface Utilisateur

Pour tester le mode "un par un" de manière visuelle, nous allons créer une interface simple avec Streamlit. Cette interface permettra de :

1. Sélectionner une image à traiter
2. Afficher un aperçu de l'image d'origine
3. Générer et afficher une description de l'image
4. Permettre la modification de la description
5. Lancer le traitement d'amélioration
6. Afficher un aperçu du résultat
7. Valider ou rejeter le résultat

### Installation de l'interface

```bash
pip install streamlit
```

### Lancement de l'interface

```bash
streamlit run interface.py
```

## Détail des Étapes

### 1. Initialisation

- Création d'une instance de `ImageEnhancer`
- Configuration de l'URL de l'API (par défaut: http://127.0.0.1:7860)
- Initialisation du système de cache

```python
enhancer = ImageEnhancer(
    api_url="http://127.0.0.1:7860",
    cache=ImageCache(),
    use_cache=True
)
```

### 2. Validation de l'Entrée

- Vérification de l'existence du fichier
- Validation de l'extension du fichier
- Vérification des permissions de lecture

### 3. Gestion du Cache

- Génération d'une clé de cache basée sur :
  - Chemin du fichier
  - Paramètres de traitement (facteur d'échelle, prompt, etc.)
- Vérification si le résultat est déjà en cache
- Si oui, retour du résultat mis en cache

### 4. Prétraitement

- Chargement de l'image avec PIL
- Conversion au format RGB si nécessaire
- Redimensionnement si l'image est trop petite
- Vérification si l'image est en noir et blanc

### 5. Appel à l'API Stable Diffusion

- Préparation du payload avec les paramètres :
  ```python
  payload = {
      "resize_mode": 0,
      "upscaling_resize": scale_factor * 100,
      "upscaler_1": upscaler,
      "denoising_strength": denoising_strength,
      "prompt": prompt,
      "negative_prompt": negative_prompt,
      "steps": steps,
      "cfg_scale": cfg_scale,
      "sampler_name": sampler_name,
      "alwayson_scripts": {}
  }
  ```
- Appel à l'API avec gestion des réessais
- Récupération de l'image encodée en base64

### 6. Post-traitement

- Décodage de l'image depuis base64
- Application d'éventuels effets supplémentaires
- Vérification de la qualité du résultat

### 7. Sauvegarde des Résultats

- Création du répertoire de sortie si nécessaire
- Sauvegarde de l'image au format demandé
- Mise à jour du cache avec le nouveau résultat

## Exemple d'Utilisation

```python
from pathlib import Path
from fluxgym_coach.image_enhancement import ImageEnhancer

# Initialisation
enhancer = ImageEnhancer()

# Traitement d'une image
input_path = Path("chemin/vers/image.jpg")
output_path = Path("chemin/de/sortie/image_amelioree.png")

try:
    result_path, was_processed = enhancer.upscale_image(
        image_path=input_path,
        output_path=output_path,
        scale_factor=2,
        upscaler="R-ESRGAN_4x+",
        denoising_strength=0.5,
        prompt="high quality, high resolution, detailed",
        negative_prompt="blurry, lowres, low quality, artifacts, jpeg artifacts",
        steps=20,
        cfg_scale=7.0,
        sampler_name="Euler a",
        output_format="PNG"
    )
    
    if was_processed:
        print(f"Image traitée et sauvegardée : {result_path}")
    else:
        print(f"Image récupérée depuis le cache : {result_path}")
        
except Exception as e:
    print(f"Erreur lors du traitement : {str(e)}")
```

## Gestion des Erreurs

Le système gère plusieurs types d'erreurs :
- Fichier introuvable ou illisible
- Format d'image non supporté
- Échec de connexion à l'API
- Réponse invalide de l'API
- Problèmes d'écriture sur le disque

## Paramètres Recommandés

Pour une qualité optimale :
- `scale_factor`: 2 (pour un bon équilibre qualité/temps)
- `upscaler`: "R-ESRGAN_4x+" (bon pour les photos)
- `denoising_strength`: 0.5 (ajuster selon le bruit de l'image)
- `steps`: 20-30 (plus pour une meilleure qualité, mais plus long)
- `cfg_scale`: 7.0 (bon équilibre créativité/fidélité)
