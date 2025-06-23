# FluxGym Coach - Amélioration d'images avec IA

## Table des matières
- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Feuille de route](#feuille-de-route)
- [Contribution](#contribution)
- [Licence](#licence)

## Aperçu

FluxGym Coach est un outil d'amélioration d'images basé sur l'IA, utilisant Stable Diffusion Forge pour augmenter la résolution et améliorer la qualité des images. Il supporte également la colorisation automatique des images en noir et blanc.

## Fonctionnalités

- Augmentation de la résolution des images (jusqu'à 4x)
- Colorisation automatique des images en noir et blanc
- Gestion du cache pour éviter les retraitements inutiles
- Traitement par lots pour les grands ensembles d'images
- Support de différents modèles d'upscaling
- Interface en ligne de commande facile à utiliser

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/fluxgym-coach.git
   cd fluxgym-coach
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Assurez-vous que Stable Diffusion WebUI est en cours d'exécution et accessible à l'adresse `http://127.0.0.1:7860`

## Utilisation

### Pour améliorer une seule image :
```bash
python -m fluxgym_coach.image_enhancement --input image.jpg --output output.png
```

### Pour améliorer un dossier d'images :
```bash
python -m fluxgym_coach.image_enhancement --input dossier_images/ --output dossier_sortie/
```

### Options disponibles :
- `--scale` : Facteur d'échelle (1-4, par défaut: 2)
- `--upscaler` : Modèle d'upscaling à utiliser
- `--colorize` : Activer la colorisation automatique
- `--batch-size` : Nombre d'images à traiter en parallèle (par défaut: 5)
- `--force` : Forcer le retraitement même si l'image est en cache

## Feuille de route

### Version 0.3.0 (En cours)
- [x] **Phase 1 : Planification**
  - [x] Analyser les fichiers TODO.md et PROJET.md
  - [x] Définir les fonctionnalités prioritaires

- [ ] **Phase 2 : Performances et Stabilité**
  - [x] Analyser l'utilisation de la mémoire
  - [ ] Optimiser l'utilisation de la mémoire pour les grands lots
    - [x] Analyser le code existant
    - [ ] Implémenter un traitement par lots (chunking)
    - [ ] Ajouter un paramètre batch_size
    - [ ] Gérer correctement la mémoire entre les lots
  - [ ] Permettre le fonctionnement sous VRAM faible (10-12 Go)
  - [ ] Implémenter le nettoyage automatique du cache
  - [ ] Améliorer la gestion des erreurs et le logging

- [ ] **Phase 3 : Application Web et Dockerisation**
  - [ ] Développer une interface web
  - [ ] Dockeriser l'application

- [ ] **Phase 4 : Intégration des Modèles**
  - [ ] Intégrer la dernière version de Fluxgym
  - [ ] Intégrer Stable Diffusion Forge avec support Nvidia RTX 40XX

- [ ] **Phase 5 : Fonctionnalités Avancées**
  - [ ] Ajouter des options de prétraitement (détection de visages, etc.)
  - [ ] Améliorer la qualité de la colorisation
  - [ ] Ajouter le support des vidéos

- [ ] **Phase 6 : Finalisation**
  - [ ] Documentation complète
  - [ ] Tests automatisés
  - [ ] Optimisation des performances
  - [ ] Préparation de la release

## Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

Dernière mise à jour : 23 juin 2024
