# Plan: Étude et amélioration du projet Fluxgym-coach

## Notes
- Le projet Fluxgym-coach est un outil d'amélioration d'images pour le coaching sportif, utilisant une architecture modulaire et l'API Stable Diffusion Forge.
- Installation standard Python (>=3.8), dépendances listées dans pyproject.toml, point d'entrée CLI via fluxgym_coach/cli.py.
- Fonctionnalités principales : upscaling, cache intelligent, gestion des erreurs, support multi-formats.
- Modules clés identifiés : image_enhancement.py (amélioration d'image), processor.py (pipeline traitement), image_cache.py (gestion du cache).
- La structure du dépôt et la documentation sont bien organisées.
- Refactorisation : colorisation et traitement par lots extraits dans des plugins, code simplifié, architecture prête pour extensions via plugins (cf. PROJET.md)
- Nouvelle priorité : stabiliser et documenter le workflow "un par un" avant de traiter le batch
- Le workflow "un par un" inclut désormais : génération de description, révision/validation utilisateur, possibilité de retraitement, et sauvegarde enrichie.
- Une interface utilisateur Streamlit (interface.py) a été ajoutée pour tester le mode "un par un" visuellement.
- Correction apportée à l'interface : la génération de description utilise désormais correctement les métadonnées extraites via MetadataExtractor.
- Suite à la remarque utilisateur, la génération de description s'appuie désormais sur un modèle IA (BLIP) pour produire une description visuelle réelle de l'image, et non plus sur le nom du fichier ou de simples métadonnées.
- Amélioration : la génération de description utilise désormais un modèle avancé (BLIP2) avec prompts multiples pour produire une description visuelle détaillée et contextualisée (personnes, actions, environnement, éléments sportifs, couleurs, composition).
- Nouvelle exigence : lors du chargement d'une image, elle doit être renommée avec son hash, convertie en PNG, enregistrée dans un dossier temporaire, et l'utilisateur doit être informé de ces étapes. Ce dossier temporaire doit être vidé au démarrage de l'application et après chaque traitement d'image.
- Problème identifié : la génération de description reste trop générique (ex : "A young boy standing in front of a building") et manque de détails sur les personnes, leur apparence, habillement, couleurs, etc. Il faut enrichir la description générée et les tags pour répondre à l'usage coaching sportif ou analyse visuelle détaillée.
- Nouvelle exigence : proposer à l'utilisateur le choix du modèle BLIP, BLIP-2 ou BLIP-3o (avec indication de leur taille avant téléchargement), exporter la fonction de génération de description, afficher les images générées côte à côte pour comparaison, et rendre l'interface responsive/optimisée pour une seule page (1920x1080 ou adaptatif).
- Nouvelle exigence : la fonction de génération de description doit être externalisée dans un module séparé, documentée étape par étape pour faciliter le debug, puis importée dans l'interface principale pour garder un workflow clair et séquentiel.

## Liste des tâches
- [x] Lister les fichiers et explorer la structure du dépôt
- [x] Lire le README pour comprendre le but et les fonctionnalités
- [x] Examiner pyproject.toml pour les dépendances et configuration
- [x] Identifier le point d'entrée principal (CLI)
- [x] Étudier les modules principaux : image_enhancement, processor, image_cache
- [x] Approfondir la compréhension des flux de traitement d'image et du cache
- [x] Identifier les axes d'amélioration ou d'extension possibles
- [x] Définir et documenter le workflow complet "un par un" (créer Workflow.md)
- [x] Ajouter la génération et validation de description dans le workflow "un par un"
- [x] Créer une interface utilisateur Streamlit pour le mode "un par un"
- [x] Corriger la génération de description pour utiliser un modèle IA (BLIP)
- [x] Corriger la génération de description dans l'interface (métadonnées)
- [x] Améliorer la précision de la génération de description (BLIP2, prompts détaillés)
- [ ] Tester la robustesse de la génération de description sur différents cas d'images
- [ ] Tester et stabiliser l'interface utilisateur (mode "un par un")
- [ ] Vérifier et stabiliser le mode "un par un" (upscaling simple)
- [ ] Compléter les tests unitaires pour le module batch
- [ ] Développer le plugin de colorisation externe
- [ ] Finaliser l'implémentation du moteur de plugins
- [ ] Documenter l'API des plugins
- [ ] Ajouter des exemples d'utilisation avancée
- [ ] Implémenter le workflow de prétraitement d'image : renommage par hash, conversion PNG, stockage temporaire, notification utilisateur, nettoyage du dossier temporaire au démarrage et après traitement
- [ ] Améliorer la qualité et la richesse de la génération de description (focus : attributs humains, habillement, couleurs, posture, expression, etc.)
- [ ] Exporter la fonction de génération de description pour usage externe
  - [ ] Documenter étape par étape chaque sous-processus de génération de description pour faciliter le debug
  - [ ] Importer proprement cette fonction dans interface.py et l'utiliser dans le workflow principal
- [ ] Proposer le choix du modèle BLIP/BLIP-2/BLIP-3o à l'utilisateur avec indication de taille
- [ ] Afficher les images générées côte à côte pour comparaison
- [ ] Rendre l'interface responsive et optimisée pour un affichage sur une seule page (1920x1080 et adaptatif)

## Objectif actuel
Exporter la génération de description (documentée) et intégrer proprement dans l'UI
