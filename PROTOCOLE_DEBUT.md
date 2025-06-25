# Protocole de Début de Session

## Principes Directeurs

1. **Exécution séquentielle** : Les étapes doivent être suivies dans l'ordre indiqué.
2. **Pas de correction immédiate** : Les erreurs rencontrées doivent être notées dans le plan de travail pour être traitées ultérieurement, dans l'ordre d'apparition.
3. **Exhaustivité** : Toutes les étapes doivent être effectuées. Si une étape n'est pas pertinente, elle doit être explicitement marquée comme telle avec une justification.
4. **Priorité** : Toutes les cases à cocher doivent être remplies avant de passer à la phase de correction.

## 1. Préparation de l'environnement

### 1.1. Vérification des dépendances
- [ ] Mettre à jour les dépôts locaux
  ```bash
  git fetch --all
  ```
- [ ] Mettre à jour la branche locale
  ```bash
  git pull --rebase
  ```
- [ ] Vérifier les dépendances Python
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Vérifier les dépendances de développement
  ```bash
  # Si le fichier requirements-dev.txt existe
  pip install -r requirements-dev.txt
  # Sinon, noter son absence dans le plan
  ```

### 1.2. Configuration de l'environnement
- [ ] Vérifier les variables d'environnement
  - Vérifier la présence de `.env` ou `.env.example`
  - Si non pertinent, rayer cette étape et noter "Configuration via config.py"
- [ ] Mettre à jour le poste de travail
  ```bash
  sudo apt update && sudo apt full-upgrade -y
  ```
  - Si non pertinent (ex: environnement conteneurisé), rayer cette étape

## 2. Revue du code et du contexte

### 2.1. État du dépôt
- [ ] Consulter les derniers commits
  ```bash
  git log --oneline -n 10
  ```
- [ ] Vérifier les branches actives
  ```bash
  git branch -a
  ```
- [ ] Consulter les notes de la session précédente
  - Vérifier la présence et consulter `PROJET.md`

### 2.2. Planification de la session
- [ ] Définir les objectifs de la session
  - Consulter `TODO.md` s'il existe
  - Sinon, noter l'absence de TODO.md
- [ ] Vérifier les TODOs dans le code
  ```bash
  grep -r "TODO" ./
  ```

## 3. Vérifications techniques

### 3.1. Tests et qualité
- [ ] Lancer la suite de tests
  ```bash
  pytest
  ```
  - Noter les échecs dans le plan
  - Ne pas corriger

- [ ] Vérifier la couverture de code
  ```bash
  # Installer pytest-cov si nécessaire
  pip install pytest-cov
  pytest --cov=.
  ```
  - Noter le pourcentage de couverture

- [ ] Vérifier le style de code
  ```bash
  flake8 .
  ```
  - Noter les erreurs de style

- [ ] Vérifier les types
  ```bash
  mypy .
  ```
  - Noter les erreurs de typage

- [ ] Formater le code
  ```bash
  black .
  ```

## 4. Organisation du travail

### 4.1. Gestion des branches
- [ ] Créer une nouvelle branche si nécessaire
  ```bash
  git checkout -b type/description-courte
  ```
  - Types : `fix/`, `feature/`, `refactor/`, `docs/`

### 4.2. Initialisation de la session
- [ ] Noter l'heure de début de session
  ```bash
  date
  ```
- [ ] Mettre à jour le plan de travail
  - Ajouter une section "Problèmes détectés"
  - Lister toutes les erreurs dans l'ordre d'apparition

## 5. Vérifications finales

- [ ] Toutes les étapes précédentes ont été cochées ou explicitement rayées
- [ ] Toutes les erreurs ont été notées dans le plan
- [ ] Aucune correction n'a été effectuée pendant l'initialisation
- [ ] La branche de travail est prête pour les corrections

## 6. Phase de correction

Une fois l'initialisation terminée :
1. Consulter la liste des problèmes dans le plan
2. Traiter chaque problème un par un dans l'ordre d'apparition
3. Tester chaque correction avant de passer à la suivante
4. Mettre à jour la documentation si nécessaire

---
*Document de procédure - Ne pas modifier ce fichier pour y ajouter des notes de session spécifiques*
