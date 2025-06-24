# Décisions Techniques Importantes

## 2024-06-24 - Gestion du Cache d'Images

### Contexte
Le système de cache ne détecte pas correctement les images déjà traitées lors du traitement par lots, en particulier dans le scénario avec un mélange d'images en cache et de nouvelles images.

### Décision
Refactorisation de la méthode `upscale_batch` pour :
1. Initialiser correctement la liste des résultats
2. Gérer séparément les images en cache et les nouvelles images
3. Préserver l'ordre des résultats

### Impact
- Meilleure fiabilité du cache
- Traitement plus efficace des lots d'images
- Conservation de l'ordre des résultats

## 2024-06-24 - Correction du Payload HTTP 422

### Contexte
L'API retournait une erreur 422 (Unprocessable Entity) à cause de paramètres manquants dans la requête batch.

### Décision
Ajout des paramètres manquants `colorize_prompt` et `colorize_negative_prompt` avec des valeurs par défaut à `None`.

### Impact
- Correction des erreurs 422
- Meilleure compatibilité avec l'API Stable Diffusion
