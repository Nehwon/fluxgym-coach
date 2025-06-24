# Projet FluxGym Coach - Amélioration d'images par lots

## Contexte

Ce projet vise à corriger un bug dans la méthode `upscale_batch` du module `image_enhancement.py` qui gère le traitement par lots d'images avec mise en cache.

## Problème identifié

Lors du traitement par lots d'images avec un mélange d'images déjà en cache et de nouvelles images, la première image du lot n'est pas correctement détectée comme étant dans le cache, ce qui entraîne un échec du test.

## Plan de correction

### Tâches principales

1. **Refactorisation de `upscale_batch` dans `image_enhancement.py`**
   - [ ] Initialiser une liste de résultats de la même taille que `image_paths` avec des valeurs par défaut
   - [ ] Créer une liste des images à traiter en parallèle
   - [ ] Mettre à jour les résultats à leur index correct lors du traitement
   - [ ] Implémenter la même logique pour le mécanisme de repli

2. **Correction du payload HTTP 422**
   - [x] Analyse de la construction du payload pour l'endpoint `extra-batch-images`
   - [x] Correction du calcul de `upscaling_resize_w` et `upscaling_resize_h`

3. **Validation des correctifs**
   - [x] Création d'un script de test complet
   - [x] Correction des problèmes d'interaction avec le cache
   - [ ] Analyse et correction de l'échec dans le scénario 2 (images mises en cache)
   - [ ] Nettoyage du code de débogage

### Prochaines étapes

1. Analyser les logs détaillés pour identifier la cause de l'échec de la mise en cache
2. Corriger la logique de gestion du cache dans `upscale_batch`
3. Valider le bon fonctionnement avec les tests
4. Nettoyer le code et mettre à jour la documentation

## Notes techniques

- Le cache utilise une clé unique basée sur le chemin du fichier source et les paramètres de traitement
- La méthode `is_cached` vérifie l'existence du fichier source, la correspondance du hash, et la présence du fichier de sortie
- Le traitement par lots utilise l'API Stable Diffusion WebUI avec un mécanisme de repli pour le traitement séquentiel en cas d'échec
