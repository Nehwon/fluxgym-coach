"""Tests pour le module de métadonnées de Fluxgym-coach."""

import json
import shutil
from pathlib import Path

from fluxgym_coach.metadata import MetadataExtractor, process_metadata


def test_metadata_extractor_initialization(temp_dir: Path):
    """Teste l'initialisation de MetadataExtractor."""
    output_dir = temp_dir / "output"

    # Initialiser l'extracteur (variable inutilisée car on teste juste l'initialisation)
    _ = MetadataExtractor(output_dir)

    # Vérifier que le dossier de métadonnées a été créé
    metadata_dir = output_dir / "metadata"
    assert metadata_dir.exists()
    assert metadata_dir.is_dir()


def test_extract_basic_metadata(sample_image: Path, temp_dir: Path):
    """Teste l'extraction des métadonnées de base."""
    extractor = MetadataExtractor(temp_dir)

    # Extraire les métadonnées
    metadata = extractor.extract_basic_metadata(sample_image)

    # Vérifier les métadonnées de base
    assert metadata["filename"] == sample_image.name
    assert metadata["filepath"] == str(sample_image.absolute())
    assert metadata["size_bytes"] > 0
    assert "last_modified" in metadata
    assert "created" in metadata

    # Vérifier les métadonnées de l'image
    assert metadata["format"] == "JPEG"
    assert metadata["width"] == 100
    assert metadata["height"] == 100
    assert metadata["mode"] == "RGB"


def test_extract_exif_data(sample_image_with_metadata: Path, temp_dir: Path):
    """Teste l'extraction des données EXIF."""
    extractor = MetadataExtractor(temp_dir)

    # Extraire les métadonnées EXIF
    exif_data = extractor.extract_exif_data(sample_image_with_metadata)

    # Vérifier que des métadonnées ont été extraites
    # Note: Les données EXIF exactes peuvent varier selon l'image de test
    assert isinstance(exif_data, dict)
    assert len(exif_data) > 0


def test_save_metadata(sample_image: Path, temp_dir: Path):
    """Teste la sauvegarde des métadonnées dans un fichier."""
    extractor = MetadataExtractor(temp_dir)

    # Créer des métadonnées de test avec un hachage de contenu simulé
    test_metadata = {
        "filename": sample_image.name,
        "filepath": str(sample_image.absolute()),
        "size_bytes": 12345,
        "test_field": "valeur_test",
        "content_hash": "test_hash_123",  # Ajout du hachage de contenu requis
    }

    # Sauvegarder les métadonnées
    metadata_file = extractor.save_metadata(sample_image, test_metadata)

    # Vérifier que le fichier a été créé avec le bon nom
    assert metadata_file.exists()
    assert metadata_file.suffix == ".json"
    assert metadata_file.stem == f"{test_metadata['content_hash']}_metadata"

    # Vérifier le contenu du fichier
    with open(metadata_file, "r", encoding="utf-8") as f:
        saved_metadata = json.load(f)

    # Vérifier que les métadonnées ont été sauvegardées correctement
    assert saved_metadata["filename"] == test_metadata["filename"]
    assert saved_metadata["test_field"] == "valeur_test"
    assert saved_metadata["content_hash"] == "test_hash_123"


def test_extract_and_save_metadata(sample_image: Path, temp_dir: Path):
    """Teste l'extraction et la sauvegarde complètes des métadonnées."""
    extractor = MetadataExtractor(temp_dir)

    # Extraire et sauvegarder les métadonnées
    metadata = extractor.extract_and_save_metadata(sample_image)

    # Vérifier que les métadonnées ont été extraites
    assert metadata is not None
    assert "filename" in metadata
    assert "format" in metadata
    assert "content_hash" in metadata  # Le hachage de contenu doit être présent

    # Vérifier que le fichier de métadonnées a été créé avec le bon nom
    content_hash = metadata["content_hash"]
    metadata_file = temp_dir / "metadata" / f"{content_hash}_metadata.json"
    assert metadata_file.exists()

    # Vérifier que le fichier contient les métadonnées attendues
    with open(metadata_file, "r", encoding="utf-8") as f:
        saved_metadata = json.load(f)

    # Vérifier les métadonnées de base
    assert saved_metadata["filename"] == sample_image.name
    assert saved_metadata["width"] == 100
    assert saved_metadata["height"] == 100
    assert saved_metadata["content_hash"] == content_hash


def test_process_metadata_function(sample_image: Path, temp_dir: Path):
    """Teste la fonction process_metadata avec déduplication basée sur le hachage."""
    # Créer une structure de dossiers de test
    input_dir = temp_dir / "input"
    input_dir.mkdir()

    # Copier l'image de test plusieurs fois avec des noms différents
    image_paths = []
    for i in range(3):
        dest = input_dir / f"img_{i}.jpg"
        shutil.copy2(sample_image, dest)
        image_paths.append(dest)

    output_dir = temp_dir / "output"

    # Appeler la fonction process_metadata
    processed_count = process_metadata(image_paths, output_dir)

    # Vérifier que toutes les images ont été traitées avec succès
    assert processed_count == 3

    # Vérifier que le dossier de métadonnées a été créé
    metadata_dir = output_dir / "metadata"
    assert metadata_dir.exists()

    # Récupérer la liste des fichiers de métadonnées
    metadata_files = list(metadata_dir.glob("*.json"))

    # Vérifier qu'un seul fichier de métadonnées a été créé (déduplication)
    assert (
        len(metadata_files) == 1
    ), "Un seul fichier de métadonnées devrait être créé pour des images identiques"

    # Vérifier que le fichier contient les métadonnées attendues
    with open(metadata_files[0], "r", encoding="utf-8") as f:
        saved_metadata = json.load(f)

    assert saved_metadata["filename"] == "img_0.jpg"  # Le nom du premier fichier traité
    assert "content_hash" in saved_metadata
    assert "width" in saved_metadata
    assert "height" in saved_metadata
