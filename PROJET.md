# Plan de développement - Fluxgym-coach

## Notes
- Le plan est basé sur l'analyse de `PROJET.md`.
- L'objectif principal est de corriger les tests échoués et de finaliser les tâches de refactorisation.
- La priorité est de corriger les tests dans `test_image_enhancement.py`.
- La tâche de mise à jour de la documentation est terminée et commitée.
- Reprise des tâches de correction de tests et de refactorisation.
- La modification de `upscale_batch` pour retourner des objets `Path` a corrigé plusieurs tests.
- La refactorisation de `_call_api` pour lever `URLError` immédiatement sur les erreurs 4xx est terminée.
- **Résolution** : La division du test `test_call_api_error_handling` en trois tests distincts (`test_call_api_connection_error`, `test_call_api_http_404_error`, `test_call_api_invalid_json`) a résolu l'échec persistant. Le problème venait de la structure du test et non du code de l'application. Tous les tests liés à `_call_api` passent maintenant.
- **Nouvel échec** : Le test `test_batch_processing.py` échoue avec l'erreur `AssertionError: Échec du traitement de l'image 1`, car `output_path` est `None`. Cela indique que le test effectue de véritables appels réseau qui échouent car l'API n'est pas disponible. Les appels à l'API doivent être simulés (mocked).
- **Mise au point** : L'analyse répétée de l'agent concernant les tentatives de `_call_api` est incorrecte et ne s'applique pas à l'échec actuel.
- **Nouvel échec (suite)** : Après avoir ajouté un mock pour `_call_api`, le test échoue à nouveau. L'erreur `NameError: name 'patch' is not defined` a été corrigée en ajoutant l'import manquant. Le test échoue maintenant avec `AssertionError: Échec du traitement de l'image 3` car le mock de `_call_api` retourne un nombre fixe de 2 images, alors que le premier lot de test en contient 4. Le mock doit être rendu dynamique.
- **Action immédiate** : L'analyse de l'agent est bloquée sur une erreur déjà résolue. Ignorer cette analyse et se concentrer sur la tâche suivante : rendre le mock de `_call_api` dynamique dans `test_batch_processing.py`.
- **Nouvel échec (final)** : Le mock dynamique pour `_call_api` n'a pas résolu le problème. Le test régresse et échoue maintenant sur la première image (`AssertionError: Échec du traitement de l'image 1`), ce qui suggère qu'une exception est levée de manière inattendue pendant le traitement du lot. L'analyse de l'agent reste non pertinente.
- **Nouvel échec (persistant)** : La correction du mock pour `upscale_image` n'a pas résolu l'échec. Le test échoue toujours sur la première image, confirmant qu'une exception est levée prématurément dans le bloc `try` de `upscale_batch`, ce qui déclenche le mécanisme de secours (fallback). Le problème ne se situe pas dans le code du fallback lui-même, mais dans ce qui le précède. L'analyse de l'agent est à ignorer.
- **Hypothèse (invalidée)** : L'échec était supposé être dû à une exception inattendue dans le bloc `try` de `upscale_batch`. Cependant, les logs ajoutés montrent que ce bloc s'exécute avec succès et que les images sont traitées. Le fallback n'est pas déclenché. L'analyse de l'agent reste non pertinente.
- **Nouvelle hypothèse** : Puisque `upscale_batch` semble fonctionner correctement (selon les logs), le problème se situe probablement dans la fonction appelante, `batch_process_images` (dans `batch_processing.py`). Cette fonction pourrait mal interpréter ou corrompre la liste de résultats retournée par `upscale_batch`, ce qui mène à l'échec de l'assertion dans le test.
- **Erreur de l'agent** : L'agent a cherché `batch_process_images` et a ouvert `processor.py`, qui n'est pas pertinent pour le test en cours. Le test utilise `ImageEnhancer.upscale_batch` de `image_enhancement.py`. L'analyse de l'agent est donc incorrecte et doit être ignorée.
- **Mystère persistant** : Le test échoue sur la première image du premier scénario, ce qui implique que `results[0]` n'est pas mis à jour. Pourtant, la logique semble correcte et les logs (bien que confus) suggèrent que le traitement fonctionne. Le problème pourrait être un bug subtil dans la manière dont la liste `results` est initialisée, modifiée ou retournée par `upscale_batch`.
- **Découverte clé** : Les logs ajoutés dans `test_batch_processing.py` ont confirmé que `upscale_batch` retourne une liste où le premier élément est `(None, False)`, ce qui cause l'échec de l'assertion.
- **Erreur critique de l'agent (résolue)** : Une tentative d'ajout de logs dans `upscale_batch` a échoué, corrompant le fichier `image_enhancement.py`. **Le fichier a été restauré avec succès** à l'aide de `git checkout`.
- **Découverte clé (suite)** : Les logs de test ont révélé l'erreur fatale : `AttributeError: 'ImageCache' object has no attribute 'generate_key'`. Cette erreur se produisait dans un bloc `try...except` de la boucle de prétraitement de `upscale_batch`, ce qui explique pourquoi la fonction retournait `(None, False)` sans lever d'exception visible par le test.
- **Correction majeure** : La logique de traitement par lots dans la méthode `upscale_batch` a été corrigée pour garantir que chaque image du lot soit correctement traitée et que les résultats soient mis à jour à la bonne position dans la liste, résolvant ainsi l'échec du test.
- **Résolution** : La méthode `generate_key` a été implémentée dans la classe `ImageCache` pour corriger l'erreur.
- **Agent bloqué (persistant)** : L'agent continue de répéter une analyse incorrecte et non pertinente sur la gestion des erreurs de `_call_api`, ignorant complètement l'état actuel du code et les tâches planifiées.
- **Nouvelle exigence** : Pour l'upscale, c'est la plus petite des tailles (hauteur, largeur) d'une image qui doit être prise en compte. L'augmentation de la résolution ainsi que le recadrage si nécessaire doivent être effectués en premier dans le workflow.

## Task List
- [x] Mettre à jour l'ensemble de la documentation du dépôt.
  - [x] Mettre à jour le fichier `README.md`.
  - [x] Mettre à jour les fichiers `README.fr.md` et `README.en.md`.
  - [x] Mettre à jour les `CHANGELOG` (`.md`, `.fr.md`).
  - [x] Mettre à jour les fichiers `PROTOCOLE_RACINE.md` et `PROTOCOLE_RACINE.fr.md`.
  - [x] Mettre à jour les autres fichiers de documentation (`PROJET.md`, `DECISIONS.md`, `PROJECT_STATUS.md`).
  - [x] Mettre à jour la documentation dans le dossier `docs/`.
- [x] Faire un commit complet des mises à jour de la documentation.
- [ ] Refactoriser `image_enhancement.py` pour une meilleure gestion des chemins.
  - [ ] Mettre à jour `_get_output_path` pour qu'elle retourne systématiquement des chemins absolus.
- [ ] Corriger les régressions et tests échoués.
  - [ ] Corriger l'échec de `test_batch_processing.py::test_batch_processing`.
    - [x] Simuler (mock) les appels à `_call_api` ou `upscale_image` pour éviter les appels réseau réels et contrôler les résultats.
    - [x] Rendre le mock de `_call_api` dynamique pour qu'il retourne un nombre d'images correspondant à la taille du lot d'entrée.
    - [x] Investiguer le traitement des lots dans `upscale_batch`.
      - [x] Corriger la logique de traitement par lots dans `upscale_batch` pour garantir que chaque image du lot soit traitée et que les résultats soient bien mis à jour.
      - [x] Corriger le mock de `upscale_image` pour qu'il retourne le format de données attendu (tuple).
      - [x] Ajouter des logs/débogage dans le bloc `try` de `upscale_batch` pour identifier la cause de l'exception.
      - [x] Implémenter la méthode `generate_key` manquante dans `ImageCache`.
    - [x] Relancer le test pour valider le correctif.
  - [ ] Corriger l'échec de `test_cli_extra.py::test_main_processing_error`.
- [ ] Supprimer les logs de débogage.
- [ ] Exécuter la suite de tests complète pour validation finale.
- [ ] Prendre en compte la plus petite dimension (hauteur ou largeur) d'une image pour l'upscale.
- [ ] Ajouter l'étape d'augmentation de la résolution et de recadrage (si nécessaire) en tout début du workflow.

## Current Goal
Corriger l'échec de test_batch_processing.py si le test échoue encore.
