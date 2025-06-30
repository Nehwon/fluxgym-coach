"""
Interface utilisateur Streamlit pour tester le mode "un par un" de Fluxgym-coach.
Permet de charger une image, générer une description, et lancer l'amélioration.
"""

import streamlit as st
from pathlib import Path
from PIL import Image
import sys
import os
import torch
import time
import hashlib
import shutil
import io
from datetime import datetime
from transformers import AutoProcessor, BlipForConditionalGeneration

# Configuration des dossiers
BASE_DIR = Path(__file__).parent.absolute()
TEMP_DIR = BASE_DIR / 'temp_processing'
TEMP_DIR.mkdir(exist_ok=True)

def clean_temp_dir():
    """Vide le dossier temporaire."""
    for item in TEMP_DIR.glob('*'):
        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            print(f"Erreur lors de la suppression de {item}: {e}")

def process_uploaded_image(uploaded_file):
    """
    Traite le fichier uploadé :
    1. Calcule son hash
    2. Crée un nom de fichier unique avec le hash
    3. Convertit en PNG si nécessaire
    4. Enregistre dans le dossier temporaire
    
    Retourne le chemin du fichier traité
    """
    # Nettoyer d'abord le dossier temporaire
    clean_temp_dir()
    
    # Lire le contenu du fichier
    file_bytes = uploaded_file.getvalue()
    
    # Calculer le hash du fichier
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # Créer un nom de fichier unique avec horodatage
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file_hash[:12]}.png"
    filepath = TEMP_DIR / filename
    
    # Sauvegarder le fichier
    with open(filepath, 'wb') as f:
        f.write(file_bytes)
    
    # Si ce n'est pas un PNG, convertir
    if not uploaded_file.name.lower().endswith('.png'):
        from PIL import Image
        img = Image.open(filepath)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img.save(filepath, 'PNG')
    
    return filepath

# Ajout du dossier parent au path pour importer les modules du projet
sys.path.append(str(Path(__file__).parent))

from fluxgym_coach.image_enhancement import ImageEnhancer
from fluxgym_coach.metadata import MetadataExtractor

def main():
    st.set_page_config(
        page_title="Fluxgym-coach - Amélioration d'images",
        page_icon="🖼️",
        layout="wide"
    )
    
    st.title("🖼️ Fluxgym-coach - Mode Un par un")
    st.write("""
    Chargez une image pour l'améliorer avec l'IA. 
    Vous pourrez générer une description, ajuster les paramètres, et valider le résultat.
    """)
    
    # Initialisation des modèles
    if 'enhancer' not in st.session_state:
        st.session_state.enhancer = ImageEnhancer()
        
    @st.cache_resource
    def load_image_captioning_model():
        """Charge le modèle de génération de légende d'image."""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            # Désactiver les messages de warning de chargement
            import logging
            logging.getLogger("transformers").setLevel(logging.ERROR)
            
            # Utilisation d'un modèle BLIP standard plus stable
            model_name = "Salesforce/blip-image-captioning-base"
            
            # Charger le processeur et le modèle
            processor = AutoProcessor.from_pretrained(model_name)
            model = BlipForConditionalGeneration.from_pretrained(model_name).to(device)
            
            # Désactiver le mode évaluation
            model.eval()
            
            return processor, model, device
            
        except Exception as e:
            st.error(f"Erreur lors du chargement du modèle : {str(e)}")
            return None, None, None
            
    def generate_detailed_description(image, processor, model, device):
        """Génère une description détaillée avec des attributs visuels précis."""
        try:
            # Configuration de la génération
            generation_kwargs = {
                "max_length": 300,
                "num_beams": 5,
                "no_repeat_ngram_size": 2,
                "early_stopping": True,
                "do_sample": True,
                "top_p": 0.95,
                "temperature": 0.7
            }
            
            # 1. Description des personnes
            person_prompt = "Décris en détail chaque personne visible dans l'image. Pour chaque personne, indique :\n" \
                          "- Âge approximatif et genre\n" \
                          "- Couleur et style de cheveux\n" \
                          "- Couleur des yeux et expression du visage\n" \
                          "- Posture et gestes\n" \
                          "- Émotion et attitude"
            
            inputs = processor(image, text=person_prompt, return_tensors="pt").to(device)
            generated_ids = model.generate(**inputs, **generation_kwargs)
            person_description = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # 2. Description des vêtements et accessoires
            clothes_prompt = "Décris les vêtements et accessoires de chaque personne :\n" \
                           "- Type de tenue (décontractée, formelle, sportive, etc.)\n" \
                           "- Couleurs et motifs\n" \
                           "- Accessoires (lunettes, bijoux, chapeaux, etc.)\n" \
                           "- État et style général"
            
            inputs = processor(image, text=clothes_prompt, return_tensors="pt").to(device)
            generated_ids = model.generate(**inputs, **generation_kwargs)
            clothes_description = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # 3. Description de l'environnement
            env_prompt = "Décris l'environnement de l'image :\n" \
                       "- Type de lieu (intérieur/extérieur, urbain/naturel, etc.)\n" \
                       "- Éléments du décor\n" \
                       "- Éclairage et ambiance\n" \
                       "- Conditions météorologiques si visibles"
            
            inputs = processor(image, text=env_prompt, return_tensors="pt").to(device)
            generated_ids = model.generate(**inputs, **generation_kwargs)
            env_description = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # 4. Description des actions
            action_prompt = "Décris ce qui se passe dans l'image :\n" \
                          "- Actions des personnes\n" \
                          "- Interactions entre les personnes ou avec des objets\n" \
                          "- Activité principale\n" \
                          "- Mouvement ou dynamique de la scène"
            
            inputs = processor(image, text=action_prompt, return_tensors="pt").to(device)
            generated_ids = model.generate(**inputs, **generation_kwargs)
            action_description = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # 5. Analyse visuelle
            visual_prompt = "Analyse les aspects visuels de l'image :\n" \
                          "- Couleurs dominantes\n" \
                          "- Composition et cadrage\n" \
                          "- Éléments qui attirent l'attention\n" \
                          "- Ambiance générale"
            
            inputs = processor(image, text=visual_prompt, return_tensors="pt").to(device)
            generated_ids = model.generate(**inputs, **generation_kwargs)
            visual_description = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Génération des tags
            tags_prompt = "Génère une liste de mots-clés détaillés pour cette image, en incluant :\n" \
                        "1. Types de personnes (ex: homme adulte, enfant, femme âgée)\n" \
                        "2. Couleurs dominantes\n" \
                        "3. Émotions et expressions\n" \
                        "4. Actions et activités\n" \
                        "5. Éléments remarquables\n" \
                        "Format de réponse : Liste les mots-clés séparés par des virgules, sans numérotation."
            
            inputs = processor(image, text=tags_prompt, return_tensors="pt").to(device)
            generated_ids = model.generate(**inputs, **generation_kwargs)
            tags_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Nettoyage et formatage
            def clean_text(text):
                text = text.replace("Caption:", "").strip()
                if text and not text.endswith('.'):
                    text += "."
                return text[0].upper() + text[1:]  # Majuscule au début
            
            # Construction de la description finale
            final_description = "\n\n".join([
                f"PERSONNES : {clean_text(person_description)}",
                f"VÊTEMENTS : {clean_text(clothes_description)}",
                f"ENVIRONNEMENT : {clean_text(env_description)}",
                f"ACTIONS : {clean_text(action_description)}",
                f"ANALYSE VISUELLE : {clean_text(visual_description)}"
            ])
            
            # Nettoyage et formatage des tags
            tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
            tags = list(dict.fromkeys(tags))  # Supprimer les doublons
            tags = [tag[0].upper() + tag[1:] for tag in tags]  # Majuscule au début
            
            # Format final
            result = f"{final_description}\n\nÉLÉMENTS CLÉS: {', '.join(tags[:15])}"
            
            return result
            
        except Exception as e:
            print(f"Erreur lors de la génération de la description: {str(e)}")
            return "Impossible de générer une description pour cette image."
    
    # Nettoyer le dossier temporaire au démarrage
    if 'temp_cleaned' not in st.session_state:
        clean_temp_dir()
        st.session_state.temp_cleaned = True
    
    # Section de téléchargement d'image
    st.header("1. Chargement de l'image")
    uploaded_file = st.file_uploader("Téléchargez une image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Traiter l'image (hash, conversion PNG, sauvegarde temporaire)
        with st.spinner("Traitement de l'image..."):
            try:
                # Traitement de l'image
                processed_path = process_uploaded_image(uploaded_file)
                
                # Charger l'image traitée
                image = Image.open(processed_path)
                
                # Afficher les informations de traitement
                st.success("✅ Image traitée avec succès")
                st.info(f"Nom du fichier : {processed_path.name}")
                st.info(f"Taille : {os.path.getsize(processed_path) / 1024:.1f} Ko")
                
                # Afficher l'image
                st.image(image, caption="Image traitée et prête pour l'analyse", use_container_width=True)
                
                # Section de description
                st.header("2. Description de l'image")
                
                # Charger le modèle de génération de description
                with st.spinner("Chargement du modèle de description..."):
                    processor, model, device = load_image_captioning_model()
                
                if processor is not None and model is not None:
                    # Générer la description
                    with st.spinner("Analyse de l'image et génération de la description..."):
                        description = generate_detailed_description(image, processor, model, device)
                    
                    # Afficher la description
                    st.text_area("Description générée", description, height=200)
                    
                    # Section de paramètres d'amélioration
                    st.header("3. Paramètres d'amélioration")
                    
                    # Options d'amélioration
                    enhancement_options = {
                        "upscale": st.checkbox("Augmenter la résolution", value=True),
                        "denoise": st.checkbox("Réduction du bruit", value=True),
                        "contrast": st.checkbox("Amélioration du contraste", value=True)
                    }
                    
                    # Bouton de traitement
                    if st.button("Traiter l'image"):
                        with st.spinner("Traitement en cours..."):
                            # Ici, vous ajouterez le code pour traiter l'image
                            # avec les options sélectionnées
                            processed_image = image  # Pour l'instant, on retourne l'image originale
                            
                            # Afficher l'image traitée
                            st.image(processed_image, caption="Image traitée", use_container_width=True)
                            
                            # Bouton de téléchargement
                            buffered = io.BytesIO()
                            processed_image.save(buffered, format="PNG")
                            st.download_button(
                                label="Télécharger l'image traitée",
                                data=buffered.getvalue(),
                                file_name=f"{processed_path.stem}_traitee.png",
                                mime="image/png"
                            )
                            
                            # Nettoyer le dossier temporaire après le traitement
                            clean_temp_dir()
                            
            except Exception as e:
                st.error(f"Erreur lors du traitement de l'image : {str(e)}")
                st.exception(e)
                
    # Boutons de validation
    if 'processed_image' in st.session_state:
        st.subheader("Validation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Valider et continuer"):
                # Logique pour passer à l'image suivante
                st.success("Image validée avec succès !")
                # Nettoyage après validation
                if 'processed_image' in st.session_state:
                    del st.session_state.processed_image
                
        with col2:
            if st.button("🔄 Recommencer"):
                # Réinitialiser l'état
                if 'processed_image' in st.session_state:
                    del st.session_state.processed_image
                st.rerun()

if __name__ == "__main__":
    main()
