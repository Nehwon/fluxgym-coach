# Protocole de Développement

## Table des matières
1. [Communication](#1-communication)
2. [Standards Techniques](#2-standards-techniques)
3. [Gestion de Version](#3-gestion-de-version)
4. [Docker et Conteneurisation](#4-docker-et-conteneurisation)
5. [Bonnes Pratiques de Développement](#5-bonnes-pratiques-de-développement)
6. [Documentation](#6-documentation)
7. [Dépannage](#7-dépannage)

## 1. Communication

### Principes généraux
- **Langue** : Français (sauf pour le code et les identifiants techniques)
- **Style** : Professionnel mais décontracté
- **Fréquence des mises à jour** : Continue, au fil du développement

### Outils recommandés
- Suivi des tâches : Gitea Issues ou équivalent
- Communication asynchrone : Email ou outil de messagerie d'équipe
- Réunions : Agenda partagé avec ordre du jour défini à l'avance

### Règles de communication
- Toujours mentionner le contexte du projet
- Utiliser des références claires aux tickets ou problèmes
- Documenter les décisions importantes dans le fichier `DECISIONS.md`

## 2. Standards Techniques

### Langages et Frameworks
- **Python** : PEP 8, typage statique avec mypy
- **JavaScript/TypeScript** : ESLint, Prettier
- **Autres langages** : Suivre les conventions standards de la communauté

### Qualité du code
- Tests unitaires avec une couverture minimale de 80%
- Revue de code obligatoire avant fusion (Pull Request)
- Intégration continue avec vérification des tests et du linting

### Sécurité
- Ne jamais stocker de données sensibles en clair dans le code
- Utiliser des variables d'environnement pour les configurations sensibles
- Mettre à jour régulièrement les dépendances pour corriger les vulnérabilités connues

## 3. Gestion de Version

### Principes de base
- **Git** comme système de contrôle de version
- **Workflow** : Git Flow ou GitHub Flow selon la taille du projet
- **Messages de commit** : Suivre la convention [Conventional Commits](https://www.conventionalcommits.org/)

### Structure des branches
- `main`/`master` : Branche de production
- `develop` : Branche d'intégration
- `feature/*` : Nouvelles fonctionnalités
- `bugfix/*` : Corrections de bugs
- `hotfix/*` : Corrections critiques pour la production

## 4. Docker et Conteneurisation

### Bonnes pratiques Docker Compose

#### Configuration
- **Version** : Ne pas utiliser l'attribut `version` obsolète
- **Syntaxe** : Toujours utiliser la dernière version de la syntaxe
- **Commandes** : Préférer `docker compose` (sans tiret) à l'ancienne syntaxe `docker-compose`

Exemple de configuration minimale :

```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
```

### Gestion des Volumes

#### Bonnes pratiques
1. **Déclaration explicite** : Toujours déclarer les volumes dans le fichier `docker-compose.yml`
2. **Nettoyage** : Supprimer les volumes inutilisés régulièrement
3. **Persistance** : Utiliser des volumes nommés pour les données critiques

#### Commandes utiles
```bash
# Lister les volumes
docker volume ls

# Supprimer un volume spécifique
docker volume rm nom_du_volume

# Nettoyer les volumes inutilisés
docker volume prune

# Recréer les volumes (avec mise à jour)
docker compose up -d --force-recreate --renew-anon-volumes
```

### Migration des Données

#### Stratégie de migration
1. **Sauvegarde** : Toujours effectuer une sauvegarde complète avant migration
2. **Atomicité** : Utiliser des transactions pour les opérations critiques
3. **Validation** : Tester la restauration des sauvegardes en environnement de test

#### Exemple de procédure
```bash
# 1. Sauvegarde des données
docker exec -t postgres pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql

# 2. Arrêt des services
docker compose down

# 3. Mise à jour des conteneurs
docker compose pull

docker compose up -d --force-recreate

# 4. Vérification de l'intégrité des données
docker compose exec -T postgres psql -U postgres -c "SELECT 'OK' AS status;"
```

## 5. Bonnes Pratiques de Développement

### Gestion des Dépendances
- **Mise à jour** : Maintenir les dépendances à jour
- **Sécurité** : Vérifier les vulnérabilités connues
- **Verrouillage** : Utiliser des fichiers de verrouillage (ex: `package-lock.json`, `Pipfile.lock`)

### Tests
- **Types de tests** :
  - Tests unitaires
  - Tests d'intégration
  - Tests de bout en bout
- **Couverture de code** : Viser au moins 80% de couverture
- **CI/CD** : Exécuter automatiquement les tests à chaque push

### Revue de Code
- **Processus** :
  1. Créer une Pull Request
  2. Assigner au moins un réviseur
  3. Résoudre les commentaires
  4. Fusionner après approbation
- **Bonnes pratiques** :
  - Commentaires constructifs
  - Respect des conventions de codage
  - Vérification de la documentation

## 6. Documentation

### Structure de Documentation
```
docs/
├── api/           # Documentation de l'API
├── architecture/  # Diagrammes et explications
├── deployment/    # Procédures de déploiement
├── guides/        # Guides pas à pas
└── README.md      # Page d'accueil de la documentation
```

### Standards de Documentation
- **Code** : Documentation en français dans le code source
- **APIs** : Utiliser OpenAPI/Swagger
- **Changements** : Mettre à jour le CHANGELOG.md pour chaque version

## 7. Dépannage

### Problèmes Courants

#### Problèmes de Conteneurs
- **Conteneur ne démarre pas** :
  ```bash
  # Voir les logs
docker compose logs -f

  # Accéder au conteneur
docker compose exec service_name sh
  ```

#### Problèmes de Réseau
- **Vérifier la connectivité** :
  ```bash
  # Depuis l'hôte
  curl -v http://localhost:port

  # Depuis un conteneur
  docker compose run --rm curl http://service:port
  ```

#### Problèmes de Données
- **Sauvegarde** :
  ```bash
  # Sauvegarder un volume
  docker run --rm -v volume_name:/source -v $(pwd):/backup \
    alpine tar czf /backup/backup.tar.gz -C /source .
  ```

### Journalisation et Surveillance
- **Accès aux logs** :
  ```bash
  # Suivre les logs en temps réel
docker compose logs -f

  # Voir les logs d'un service spécifique
docker compose logs service_name
  ```

## Annexe A : Versionnement Sémantique (SemVer)

### Format de Version
`MAJEURE.MINEURE.CORRECTIF` (ex: `1.2.3`)

### Règles d'Incrimination
- **MAJEURE** : Changements incompatibles avec les versions précédentes
- **MINEURE** : Ajout de fonctionnalités rétrocompatibles
- **CORRECTIF** : Corrections de bugs rétrocompatibles

### Exemples
- `0.0.1` : Version initiale (développement)
- `1.0.0` : Première version stable
- `1.1.0` : Ajout de fonctionnalités rétrocompatibles
- `1.1.1` : Correction de bugs
- `2.0.0` : Changements incompatibles

## Annexe B : Modèle de CHANGELOG.md

```markdown
# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versionnage Sémantique](https://semver.org/spec/v2.0.0.html).

## [Non publié]
### Ajouté
- Nouvelle fonctionnalité X

### Modifié
- Amélioration des performances de Y

### Supprimé
- Fonctionnalité obsolète Z

## [1.0.0] - 2025-01-01
### Ajouté
- Version initiale du projet
- Documentation de base
```

## 4. Gestion de version (Git)

### Bridage de l'IA
- Toutes IA éditant un fichier fondamental du dépôt (ce fichier, PROTOCOLE_RACINE.md, README.md, CHANGELOG.md, TODO.md, ETAT_DU_PROJET.md) doit impérativement attendre une validation claire de l'utilisateur avant de add, commit ou push ses modifications.

### Procédure de commit
Après chaque modification d'un fichier :
1. Vérifier l'état des fichiers modifiés :
   ```bash
   git status
   ```
2. Ajouter les fichiers modifiés :
   ```bash
   git add <fichiers_modifiés>
   ```
3. Créer un commit avec un message clair :
   ```bash
   git commit -m "NOM_DU_PROJET/NOM_DU_DOSSIER: Description précise des modifications effectuées"
   ```
   Exemple : `DOCS: Mise à jour des consignes de documentation`

### Stratégie de push
Effectuer un push :
- Tous les 10 commits
- Toutes les 30 minutes
- Avant toute pause prolongée

## 5. Documentation des dossiers
Pour chaque dossier contenant des modifications :
- Créer un fichier `README.md` contenant :
  - Description des fonctionnalités
  - Options disponibles
  - Prérequis
  - Instructions d'installation et de configuration
  - Exemples d'utilisation
  - Lien vers le fichier `changelog.md`

- Documentation HTML :
  - Créer une page HTML dédiée au dossier

## 6. Procédure d'archivage

### Structure des archives
Les anciens fichiers doivent être archivés dans une arborescence parallèle `archives/` qui reflète la structure du projet principal :
```
archives/
├── YYYY-MM-DD/
│   ├── chemin/vers/le/fichier
│   └── ...
└── YYYY-MM-DD/
    └── ...
```

### Règles d'archivage
1. **Emplacement** : Créer un sous-dossier `archives/` à la racine du projet
2. **Structure** : Conserver la même structure de dossiers que le projet principal
3. **Nommage** : Utiliser le format `YYYY-MM-DD` pour les dossiers d'archives
4. **Compression** : Compresser les fichiers dans une archive au format `.tar.gz`
5. **Nom des archives** : `archives_YYYY-MM-DD_HH-MM-SS.tar.gz`

### Commande d'archivage
```bash
# Se placer à la racine du projet
cd /chemin/vers/le/projet

# Créer le dossier d'archives s'il n'existe pas
mkdir -p archives/$(date +%Y-%m-%d)

# Copier les fichiers à archiver en préservant la structure
# Remplacer 'dossier_a_archiver' par le chemin relatif des fichiers à archiver
rsync -a --relative dossier_a_archiver/ archives/$(date +%Y-%m-%d)/

# Créer une archive compressée
cd archives
tar -czvf "archives_$(date +%Y-%m-%d_%H-%M-%S).tar.gz" "$(date +%Y-%m-%d)"

# Supprimer le dossier temporaire (optionnel)
# rm -rf "$(date +%Y-%m-%d)"
```

### Bonnes pratiques
- Archiver avant toute modification majeure
- Documenter le contenu de chaque archive dans le `changelog.md`
- Vérifier l'intégrité des archives après leur création
- Nettoyer régulièrement les archives obsolètes
  - Lier cette page à la documentation principale
  - Inclure des exemples de code commentés
  - Documenter les cas d'utilisation spécifiques

## 5. Gestion de projet
- **Organisation** : Approche logique et structurée
- **Versioning** : Sémantique (majeur.mineur.bug)
  - Version 1.0.0 uniquement en fin de développement
  - Incrémentation selon les corrections et évolutions
- **Gestion des erreurs** : Documentation précise des problèmes et solutions

## 6. Procédure de fin d'étape majeure
À la fin de chaque étape de création majeure :

1. **Mise à jour du README.md du dossier**
   - Documenter les nouvelles fonctionnalités
   - Mettre à jour la configuration si nécessaire
   - Ajouter des exemples d'utilisation

2. **Mise à jour du README.md racine**
   - Ajouter un résumé des modifications
   - Mettre à jour les dépendances
   - Mettre à jour les instructions d'installation

3. **Gestion du changelog.md**
   - Créer le fichier s'il n'existe pas avec l'en-tête approprié
   - Ajouter une nouvelle entrée pour la version courante
   - Documenter :
     - Nouvelles fonctionnalités
     - Corrections de bugs
     - Modifications importantes
     - Dépréciations

## 7. Qualité attendue
- **Niveau de détail** : Très élevé
- **Documentation** :
  - Format : HTML et Markdown
  - Contenu : Exhaustif et précis
- **Tests** :
  - Validation rigoureuse
  - Prévention des régressions
  - Documentation des cas de test

## 8. Sécurité
- **Données sensibles** : Chiffrement GPG obligatoire
- **Accès** : Restreint selon les besoins
- **Confidentialité** : Respect des données personnelles et sensibles

## 9. Révision et validation

## 10. Bonnes pratiques Docker Compose

### 10.1 Utilisation de Docker Compose

- **Commande à utiliser** :
  - Toujours utiliser `docker compose` (v2) au lieu de `docker-compose` (v1)
  - La syntaxe avec espace est la version moderne et recommandée

### 10.2 Fichier docker-compose.yaml

- **Version** :
  - Ne pas inclure l'attribut `version:` dans les fichiers docker-compose.yaml
  - Cet attribut est obsolète dans les versions récentes de Docker Compose

- **Variables d'environnement** :
  - Utiliser des fichiers `.env` pour stocker les variables sensibles
  - Échapper les caractères spéciaux dans les mots de passe
  - Pour les mots de passe complexes, générer des chaînes alphanumériques :
    ```bash
    openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32
    ```

- **Ports** :
  - Éviter d'utiliser le port 22 pour les services SSH
  - Utiliser des variables d'environnement pour les numéros de port

### 10.3 Bonnes pratiques de configuration

- **Volumes** :
  - Toujours définir des volumes nommés pour la persistance des données
  - Documenter l'emplacement des volumes sur l'hôte

- **Réseaux** :
  - Créer des réseaux personnalisés pour l'isolation
  - Utiliser des noms de réseau explicites

- **Sécurité** :
  - Ne jamais exposer de ports sensibles sur des interfaces non sécurisées
  - Utiliser des variables d'environnement pour les informations sensibles
  - Mettre à jour régulièrement les images utilisées

### 10.4 Commandes utiles

```bash
# Démarrer les services en arrière-plan
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter et supprimer les conteneurs
docker compose down

# Reconstruire et redémarrer un service
docker compose up -d --build <nom_du_service>

# Vérifier l'état des conteneurs
docker compose ps
```

### 10.5 Dépannage

- **Problèmes de port** :
  ```bash
  # Vérifier les ports en écoute
  sudo lsof -i -P -n | grep LISTEN
  ```
- **Problèmes de variables d'environnement** :
  - Vérifier que les variables sont correctement définies dans le fichier .env
  - S'assurer que les caractères spéciaux sont correctement échappés
  - Utiliser des guillemets simples pour les valeurs contenant des caractères spéciaux
- Revue des modifications majeures avant intégration
- Validation des corrections de bugs critiques
- Documentation des décisions importantes
- Vérification de la complétude de la documentation

## Hiérarchie des Protocoles

### Principe Fondamental
La gestion des protocoles suit un système hiérarchique clair qui détermine comment les règles sont appliquées à travers la structure des dossiers. Cette hiérarchie assure la cohérence tout en permettant la flexibilité nécessaire à chaque projet.

### Niveaux de Protocoles

1. **PROTOCOLE_RACINE.md (Niveau Global)**
   - Emplacement : Racine du dépôt
   - Portée : S'applique à l'ensemble du dépôt
   - Rôle : Définit les règles et standards généraux
   - Priorité : La plus basse (peut être surchargé par des protocoles plus spécifiques)

2. **PROTOCOLE.md (Niveau Projet/Dossier)**
   - Emplacement : À la racine de chaque projet ou sous-dossier
   - Portée : S'applique uniquement au dossier contenant et à ses sous-dossiers
   - Rôle : Définit des règles spécifiques au projet
   - Priorité : Écrasent les règles du PROTOCOLE_RACINE.md pour leur périmètre

### Règles d'Application

#### Ordre de Priorité
1. PROTOCOLE.md du dossier le plus spécifique (le plus profond dans l'arborescence)
2. PROTOCOLE.md du dossier parent
3. PROTOCOLE_RACINE.md

#### Règles Spécifiques
- **Héritage** : Les protocoles héritent des règles des niveaux supérieurs sauf si elles sont explicitement surchargées
- **Spécificité** : Une règle plus spécifique écrase toujours une règle plus générale
- **Cohérence** : Les règles ne peuvent être assouplies que si cela est explicitement autorisé

### Gestion des Flags [bypass]

#### Principes
- **Interdiction stricte** : WindSurf ne doit jamais créer ou modifier de flag [bypass] de sa propre initiative
- **Décision utilisateur** : Seul l'utilisateur peut ajouter, modifier ou supprimer un flag [bypass]
- **Conseil** : WindSurf peut suggérer l'utilisation d'un flag [bypass] mais ne peut pas l'appliquer

#### Cas d'Usage Recommandés
- Contournement temporaire d'une règle de sécurité
- Exécution d'une commande nécessitant des privilèges élevés
- Débogage avancé nécessitant des actions non standard

### Fichiers Obligatoires par Projet
À la création de tout nouveau projet, les fichiers suivants doivent être créés à la racine du dossier du projet :
1. `README.md` : Documentation du projet
2. `CHANGELOG.md` : Historique des modifications
3. `TODO.md` : Liste des tâches à effectuer
4. `ETAT_DU_PROJET.md` : État d'avancement actuel

### Exemple de Hiérarchie
```
/ (racine du dépôt)
├── PROTOCOLE_RACINE.md  <-- Règles globales
├── projet1/
│   ├── PROTOCOLE.md      <-- Règles spécifiques à projet1
│   ├── README.md
│   └── ...
└── projet2/
    ├── sous-projet/
    │   ├── PROTOCOLE.md  <-- Règles spécifiques à sous-projet
    │   └── ...
    └── ...
```

### Règles de Rédaction
1. **Clarté** : Les règles doivent être formulées de manière non ambiguë
2. **Exhaustivité** : Couvrir tous les cas d'usage courants
3. **Exemples** : Inclure des exemples concrets d'application
4. **Références** : Lier vers la documentation pertinente