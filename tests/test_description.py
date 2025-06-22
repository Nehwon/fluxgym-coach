"""Tests pour le module description de Fluxgym-coach."""
from pathlib import Path
from unittest.mock import patch

from fluxgym_coach.description import (
    generate_description,
    save_description,
    process_descriptions,
)


def test_generate_description_basic():
    """Test de génération de description avec des métadonnées minimales."""
    metadata = {
        "filename": "test.jpg",
        "file_size": 1024,
        "exif": {
            "DateTimeOriginal": "2023:01:01 12:00:00",
            "Make": "TestCam",
            "Model": "X100",
            "FNumber": 2.8,
            "ExposureTime": "1/250",
            "FocalLength": "50.0 mm",
            "ISOSpeedRatings": 200,
        },
    }

    description = generate_description(metadata)
    assert "test.jpg" in description
    assert "01/01/2023 12:00" in description
    assert "TestCam X100" in description
    assert "f/2.8" in description
    assert "1/250s" in description
    assert "50.0mm" in description
    # Le format réel est "ISO: 200" et non "ISO 200"
    assert "ISO: 200" in description


def test_generate_description_minimal():
    """Test de génération avec un minimum de métadonnées."""
    metadata = {"filename": "minimal.jpg"}
    description = generate_description(metadata)
    assert "minimal.jpg" in description
    assert "Aucune métadonnée" not in description


def test_save_description(tmp_path):
    """Test de sauvegarde d'une description dans un fichier."""
    test_file = tmp_path / "test_description.txt"
    test_text = "Ceci est un test de description."
    result = save_description(test_text, test_file)
    assert result is True
    assert test_file.exists()
    assert test_file.read_text() == test_text


@patch("fluxgym_coach.metadata.MetadataExtractor")
def test_process_descriptions(MetadataExtractorMock, tmp_path):
    """Test du traitement d'une liste d'images pour générer des descriptions."""
    # Configuration du mock
    mock_metadata = {
        "filename": "test.jpg",
        "file_size": 1024,
        "exif": {"Make": "Test"},
        # Nécessaire pour extract_and_save_metadata
        "content_hash": "testhash123",
    }

    # Créer une instance mockée
    mock_instance = MetadataExtractorMock.return_value
    mock_instance.extract_and_save_metadata.return_value = mock_metadata

    # Création d'un fichier image de test
    test_image = tmp_path / "test.jpg"
    test_image.touch()

    # Créer un dossier de sortie
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Appel de la fonction à tester
    success_count = process_descriptions([test_image], output_dir)

    # Vérifications
    assert success_count == 1
    output_file = output_dir / "test_description.txt"
    assert output_file.exists()
    content = output_file.read_text()
    assert "test.jpg" in content


def test_process_descriptions_empty_list():
    """Test avec une liste vide d'images."""
    assert process_descriptions([], Path("/tmp")) == 0
