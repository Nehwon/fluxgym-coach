"""Tests pour le module de traitement d'images de Fluxgym-coach."""

import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from fluxgym_coach.processor import ImageProcessor, process_images
from fluxgym_coach.image_cache import ImageCache


# Les fixtures temp_dir et sample_image sont définies dans conftest.py


@pytest.fixture
def mock_cache():
    """Crée un mock pour ImageCache."""
    cache = MagicMock(spec=ImageCache)
    cache.calculate_file_hash.return_value = "testhash123"
    return cache


def test_image_processor_initialization(temp_dir: Path) -> None:
    """Teste l'initialisation de ImageProcessor."""
    # Créer les chemins de test
    input_dir = temp_dir / "input"
    output_dir = temp_dir / "output"

    # Initialiser le processeur sans cache personnalisé
    processor = ImageProcessor(input_dir, output_dir)

    # Vérifier que les attributs sont correctement définis
    assert processor.input_dir == input_dir
    assert processor.output_dir == output_dir
    assert hasattr(processor, "cache")
    assert processor.cache is not None

    # Vérifier que le dossier de sortie a été créé
    assert output_dir.exists()
    assert output_dir.is_dir()

    # Tester avec un cache personnalisé
    mock_cache = MagicMock()
    processor_with_cache = ImageProcessor(input_dir, output_dir, cache=mock_cache)
    assert processor_with_cache.cache is mock_cache


def test_is_image_file(sample_image: Path, temp_dir: Path) -> None:
    """Teste la détection des fichiers images."""
    processor = ImageProcessor(temp_dir, temp_dir / "output")

    # Vérifier que le fichier image de test existe
    assert sample_image.exists(), f"Le fichier de test {sample_image} n'existe pas"

    # Vérifier qu'un fichier image est détecté comme tel
    assert (
        processor.is_image_file(sample_image) is True
    ), f"Le fichier {sample_image} devrait être détecté comme une image"

    # Vérifier qu'un fichier texte n'est pas détecté comme image
    text_file = temp_dir / "test.txt"
    text_file.write_text("Ceci n'est pas une image")
    assert (
        processor.is_image_file(text_file) is False
    ), "Un fichier texte ne devrait pas être détecté comme une image"


def test_cache_usage(sample_image: Path, temp_dir: Path, mock_cache) -> None:
    """Teste l'utilisation du cache dans ImageProcessor."""
    output_dir = temp_dir / "output"

    # Configurer le mock pour simuler un fichier non en cache
    mock_cache.is_cached.return_value = (False, None)

    # Initialiser le processeur avec le mock
    processor = ImageProcessor(temp_dir, output_dir, cache=mock_cache)

    # Appeler process_image
    result = processor.process_image(sample_image)

    # Vérifier que le cache a été utilisé correctement
    mock_cache.is_cached.assert_called_once()
    mock_cache.add_to_cache.assert_called_once()
    assert result is not None
    assert result[0] == sample_image
    assert result[1].parent == output_dir


def test_process_image(sample_image: Path, temp_dir: Path, mock_cache) -> None:
    """Teste le traitement d'une seule image."""
    output_dir = temp_dir / "output"

    # Configurer le mock pour simuler un fichier non en cache
    mock_cache.is_cached.return_value = (False, None)
    mock_cache.calculate_file_hash.return_value = "testhash123"

    # Initialiser le processeur avec le mock
    processor = ImageProcessor(temp_dir, output_dir, cache=mock_cache)

    # Vérifier que le fichier de test existe
    assert sample_image.exists(), f"Le fichier de test {sample_image} n'existe pas"

    # Traiter l'image
    result = processor.process_image(sample_image)

    # Vérifier que le résultat est un tuple (chemin_original, nouveau_chemin)
    assert result is not None, "Le résultat du traitement ne devrait pas être None"
    assert len(result) == 2, "Le résultat devrait être un tuple de 2 éléments"
    assert result[0] == sample_image, "Le premier élément devrait être le chemin source"
    assert (
        result[1].parent == output_dir
    ), "Le fichier de sortie devrait être dans le dossier de sortie"

    # Vérifier que le cache a été utilisé correctement
    mock_cache.is_cached.assert_called_once()
    mock_cache.add_to_cache.assert_called_once()

    # Vérifier que le fichier de sortie existe
    assert result[1].exists(), "Le fichier de sortie devrait exister"

    # Vérifier que le fichier de sortie est une image valide
    assert processor.is_image_file(
        result[1]
    ), "Le fichier de sortie devrait être une image valide"


def test_process_image_duplicate(
    sample_image: Path, temp_dir: Path, mock_cache
) -> None:
    """Teste le traitement d'une image en double avec le cache."""
    output_dir = temp_dir / "output"

    # Configurer le mock pour simuler un fichier déjà en cache au deuxième appel
    cached_path = output_dir / "cached_image.jpg"
    mock_cache.is_cached.side_effect = [(False, None), (True, cached_path)]

    # Initialiser le processeur avec le mock
    processor = ImageProcessor(temp_dir, output_dir, cache=mock_cache)

    # Vérifier que le fichier de test existe
    assert sample_image.exists(), f"Le fichier de test {sample_image} n'existe pas"

    # Premier appel - pas dans le cache
    result1 = processor.process_image(sample_image)
    assert result1 is not None, "Le premier traitement a échoué"

    # Deuxième appel - déjà dans le cache
    result2 = processor.process_image(sample_image)

    # Vérifier que le résultat est le même que la première fois
    assert result2 is not None, "Le deuxième traitement a échoué"
    assert result2[0] == result1[0], "La source devrait être la même"


def test_process_directory(sample_image: Path, temp_dir: Path) -> None:
    """Teste le traitement d'un répertoire d'images."""
    # Créer une structure de dossiers de test
    input_dir = temp_dir / "input_images"
    input_dir.mkdir(exist_ok=True)

    # Copier l'image de test plusieurs fois avec des noms différents
    for i in range(3):
        shutil.copy2(sample_image, input_dir / f"image_{i}.jpg")

    output_dir = temp_dir / "output_images"

    # Traiter le répertoire
    processor = ImageProcessor(input_dir, output_dir)
    results = list(processor.process_directory())

    # Vérifier que toutes les images ont été traitées
    assert len(results) == 3, "Toutes les images n'ont pas été traitées"

    # Vérifier que tous les fichiers de sortie existent
    for original_path, new_path in results:
        assert original_path is not None, "Le chemin source ne devrait pas être None"
        assert new_path is not None, "Le chemin de destination ne devrait pas être None"
        assert new_path.exists(), f"Le fichier de sortie {new_path} n'existe pas"
        assert (
            new_path.parent == output_dir
        ), f"Le fichier de sortie {new_path} n'est pas dans le bon répertoire"


def test_process_images_function(sample_image: Path, temp_dir: Path) -> None:
    """Teste la fonction process_images avec un cache."""
    # Créer une structure de dossiers de test
    input_dir = temp_dir / "input"
    input_dir.mkdir(exist_ok=True)
    output_dir = temp_dir / "output"

    # Créer quelques fichiers de test
    test_files = []
    for i in range(3):
        test_file = input_dir / f"img_{i}.jpg"
        shutil.copy2(sample_image, test_file)
        test_files.append(test_file)

    # Utiliser patch pour simuler get_default_cache
    with patch("fluxgym_coach.processor.get_default_cache") as mock_get_cache:
        mock_cache = MagicMock()
        mock_get_cache.return_value = mock_cache

        # Configurer le mock pour simuler des fichiers non en cache
        mock_cache.is_cached.return_value = (False, None)
        mock_cache.calculate_file_hash.return_value = "testhash123"

        # Appeler la fonction à tester
        count = process_images(input_dir, output_dir)

        # Vérifier que get_default_cache a été appelé
        mock_get_cache.assert_called_once()

        # Vérifier que le cache a été utilisé pour chaque fichier
        assert (
            mock_cache.is_cached.call_count == 3
        ), "Devrait vérifier le cache pour chaque fichier"

        # Vérifier les résultats
        assert count == 3, f"Devrait traiter 3 images, traitées: {count}"

        # Vérifier que le dossier de sortie a été créé
        assert output_dir.exists() and output_dir.is_dir()
