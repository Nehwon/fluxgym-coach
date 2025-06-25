# Protocole de Fin de Session

Ce document décrit les étapes à suivre pour terminer une session de travail de manière propre et organisée.

## 1. Mise à jour de la documentation

### 1.1. Fichiers de suivi de version
- [ ] Mettre à jour `CHANGELOG.md` et `CHANGELOG.fr.md`
  - Ajouter une section pour la version en cours
  - Lister les changements majeurs, corrections et nouvelles fonctionnalités
  - Utiliser les catégories : `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

### 1.2. État du projet
- [ ] Mettre à jour `ETAT_DU_PROJET.md` et `PROJECT_STATUS.md`
  - Mettre à jour la version actuelle
  - Actualiser l'état d'avancement
  - Mettre à jour la liste des tâches
  - Documenter les problèmes connus

### 1.3. Documentation technique
- [ ] Mettre à jour la documentation technique si nécessaire
  - Mettre à jour les commentaires du code
  - Mettre à jour la documentation des fonctions/modules modifiés

## 2. Gestion de version

### 2.1. Numéro de version
- [ ] Mettre à jour le fichier `VERSION` si nécessaire
  - Suivre le versioning sémantique (MAJOR.MINOR.PATCH)
  - Incrémenter selon les règles :
    - MAJOR : Changements non rétrocompatibles
    - MINOR : Nouvelles fonctionnalités rétrocompatibles
    - PATCH : Corrections de bugs rétrocompatibles

## 3. Vérifications de qualité

### 3.1. Tests
- [ ] Exécuter la suite de tests complète
  ```bash
  pytest tests/
  ```
- [ ] Vérifier que tous les tests passent
- [ ] Documenter tout échec de test non résolu

### 3.2. Qualité du code
- [ ] Vérifier la conformité PEP 8
  ```bash
  flake8 .
  ```
- [ ] Vérifier les types
  ```bash
  mypy .
  ```
- [ ] Formater le code
  ```bash
  black .
  ```

## 4. Gestion du code source

### 4.1. Commit final
- [ ] Vérifier les modifications en attente
  ```bash
  git status
  ```
- [ ] Ajouter les fichiers modifiés
  ```bash
  git add .
  ```
- [ ] Créer un commit avec un message clair et descriptif
  ```bash
  git commit -m "type(scope): description concise des changements"
  ```
  - Types de commit : feat, fix, docs, style, refactor, test, chore
  - Exemple : `fix(image): correct batch processing errors`

### 4.2. Synchronisation distante
- [ ] Récupérer les derniers changements
  ```bash
  git pull --rebase
  ```
- [ ] Pousser les modifications
  ```bash
  git push
  ```

## 5. Documentation de la session

### 5.1. Mise à jour du plan
- [ ] Mettre à jour le fichier de plan de travail
  - Cocher les tâches terminées
  - Ajouter les nouvelles tâches identifiées
  - Mettre à jour les priorités si nécessaire

### 5.2. Notes pour la prochaine session
- [ ] Documenter les points à reprendre
- [ ] Noter les problèmes non résolus
- [ ] Lister les prochaines étapes

## 6. Vérifications finales

- [ ] Tous les tests passent
- [ ] La documentation est à jour
- [ ] Le code est conforme aux standards
- [ ] Les modifications ont été validées localement
- [ ] Les changements ont été poussés sur le dépôt distant

---
*Document de procédure - Ne pas modifier ce fichier pour y ajouter des notes de session*
