# Plan

## Notes
- Le dépôt distant est `ssh://git@gitea.lamachere.fr:2222/fabrice/Fluxgym-coach.git`.
- La branche `main` a été corrigée en utilisant la branche `master` comme base, et a été forcée sur le dépôt distant.
- Le fichier `.gitignore` a été mis à jour pour exclure les fichiers compilés Python.
- Le travail reprend sur la base des fichiers `TODO.md` et `PROJET.md`.
- Le projet est maintenant nettoyé et prêt pour le développement.
- Les tests unitaires pour `ImageCache` ont été créés et passent avec succès.
- `ImageProcessor` a été mis à jour pour utiliser `ImageCache`.
- Les tests pour `ImageProcessor` ont été mis à jour et passent avec succès.
- Le test `test_main_success` dans `tests/test_cli.py` a été corrigé avec succès en ajustant les mocks.
- Les tests pour `setup_cache` ont été créés dans un fichier séparé (`tests/test_setup_cache.py`) et passent avec succès, après des difficultés à modifier `test_cli.py` directement.
- Les tests `test_main_verbose` et `test_main_processing_error` ont été recréés dans un nouveau fichier (`tests/test_cli_extra.py`) et passent avec succès.

## Règles à respecter
- Tous les développements doivent respecter les règles définies dans `PROTOCOLE_RACINE.md`
- Les messages de commit doivent suivre la convention [Conventional Commits](https://www.conventionalcommits.org/)
- Les Pull Requests doivent être revues par au moins un autre développeur
- La couverture de code doit être maintenue au-dessus de 80%

## Task List
- [x] Configurer le dépôt distant.
- [x] Récupérer les données du dépôt distant.
- [x] Basculer sur la branche `main`.
- [x] Vérifier la présence du fichier `LICENSE`.
- [x] Ajouter tous les fichiers non suivis à l'index.
- [x] Créer un commit pour les nouveaux fichiers.
- [x] Pousser le commit vers le dépôt distant.
- [x] Valider que tous les fichiers locaux sont présents sur le dépôt distant.
- [x] Investiguer la disparition des fichiers source `.py`.
- [x] Restaurer les fichiers source depuis le dépôt Git (trouvés sur la branche `master`).
- [x] Réinitialiser la branche `main` pour qu'elle corresponde à l'état de la branche `master`.
- [x] Forcer le push de la branche `main` corrigée vers le dépôt distant (`git push --force`).
- [x] Mettre à jour le fichier `.gitignore` pour ignorer les fichiers `.pyc` et les répertoires `__pycache__`.
- [x] Nettoyer les fichiers inutiles (comme les `.pyc`) de l'index Git.
- [x] Créer un commit pour la mise à jour du `.gitignore` et le nettoyage de l'index.
- [x] Pousser les modifications du `.gitignore` vers le dépôt distant.
- [x] Créer le fichier de test `tests/test_image_cache.py`.
- [x] Écrire les tests unitaires pour la classe `ImageCache`.
  - [x] Tester le calcul de hash (`calculate_file_hash`).
  - [x] Tester la génération de clé de cache (`get_cache_key`).
  - [x] Tester l'ajout et la vérification d'entrées dans le cache (`add_to_cache`, `is_cached`).
  - [x] Tester la persistance du cache sur disque (`_load_cache`, `_save_cache`).
- [x] Intégrer `ImageCache` dans `ImageProcessor`.
  - [x] Modifier `ImageProcessor.__init__` pour accepter une instance de `ImageCache`.
  - [x] Mettre à jour `process_image` pour utiliser `ImageCache`.
  - [x] Supprimer la méthode `generate_file_hash` de `ImageProcessor` car elle est redondante.
- [x] Mettre à jour les tests dans `test_processor.py` pour refléter l'utilisation de `ImageCache`.
- [x] Corriger les tests qui échouent dans `test_processor.py`.
  - [x] Corriger `test_process_image` pour ne plus utiliser `generate_file_hash`.
  - [x] Corriger l'assertion dans `test_process_images_function`.
- [x] Ajouter les options de ligne de commande pour contrôler le cache.
- [x] Utiliser le cache configuré dans le traitement des images (`cli.py`).
- [x] Mettre à jour les tests pour `cli.py` pour couvrir les options de cache.
  - [x] Mettre à jour les imports dans `test_cli.py`.
  - [x] Mettre à jour `test_parse_args` pour inclure les options de cache.
  - [x] Corriger le test `test_main_success`.
    - [x] Aligner les décorateurs `@patch` avec les arguments de la fonction.
    - [x] Corriger le chemin du patch pour `get_default_cache` (doit être `fluxgym_coach.cli.get_default_cache`).
    - [x] S'assurer que le test passe et que les assertions sont correctes.
  - [x] Ajouter des tests pour la fonction `setup_cache`.
    - [x] Tester la désactivation du cache (`--no-cache`).
    - [x] Tester le répertoire de cache personnalisé.
    - [x] Tester le nettoyage du cache (`--clean-cache`).
    - [x] Tester le mode forcé (`--force-reprocess`).
    - [x] Tester la gestion des erreurs d'initialisation.
  - [x] Recréer `test_main_verbose` avec les mocks appropriés.
  - [x] Recréer `test_main_processing_error` avec les mocks appropriés.
- [x] Mettre à jour la documentation pour les fonctionnalités de cache.
- [ ] Tester les performances avec et sans le cache.

## Current Goal
Tester les performances du cache.