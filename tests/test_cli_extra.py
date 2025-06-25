"""Tests supplémentaires pour l'interface en ligne de commande de Fluxgym-coach."""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from fluxgym_coach.cli import main
from fluxgym_coach.image_cache import ImageCache


@patch("fluxgym_coach.processor.ImageProcessor")
@patch("fluxgym_coach.cli.get_default_cache")
@patch("fluxgym_coach.cli.parse_args")
@patch("fluxgym_coach.cli.validate_paths")
@patch("fluxgym_coach.cli.find_image_files")
@patch("fluxgym_coach.metadata.process_metadata")
def test_main_verbose(
    mock_process_metadata,
    mock_find_image_files,
    mock_validate_paths,
    mock_parse_args,
    mock_get_default_cache,
    mock_image_processor_class,
    tmp_path: Path,
):
    """Teste le mode verbeux du programme."""
    # Configurer les chemins de test
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Créer des fichiers image simulés
    image_files = [input_dir / f"image_{i}.jpg" for i in range(2)]
    for i, img in enumerate(image_files):
        img.write_text(f"test image {i}")

    # Configurer les mocks pour les arguments en mode verbeux
    mock_args = MagicMock()
    mock_args.input = str(input_dir)
    mock_args.output = str(output_dir)
    mock_args.process = "all"
    mock_args.verbose = True  # Mode verbeux activé
    mock_args.no_cache = False
    mock_args.force_reprocess = False
    mock_args.cache_dir = None
    mock_args.clean_cache = False
    mock_parse_args.return_value = mock_args

    # Configurer le mock du cache
    mock_cache = MagicMock(spec=ImageCache)
    mock_get_default_cache.return_value = mock_cache

    # Configurer le mock du processeur
    mock_processor = MagicMock()
    mock_processor.process_directory.return_value = [(f, f) for f in image_files]
    mock_image_processor_class.return_value = mock_processor

    # Configurer les valeurs de retour des autres mocks
    mock_validate_paths.return_value = (input_dir, output_dir)
    mock_find_image_files.return_value = image_files
    mock_process_metadata.return_value = len(image_files)

    # Exécuter la fonction main en mode verbeux
    with patch(
        "sys.argv",
        [
            "fluxgym-coach",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
            "--verbose",
        ],
    ):
        with patch("logging.basicConfig") as mock_logging_config:
            result = main()

    # Vérifier le résultat
    assert result == 0

    # Vérifier que la configuration du logging a été appelée avec le bon niveau
    # Le deuxième appel devrait être avec le niveau DEBUG (car verbose=True)
    debug_calls = [
        call
        for call in mock_logging_config.call_args_list
        if call[1].get("level") == logging.DEBUG
    ]
    assert len(debug_calls) > 0, "Aucun appel à basicConfig avec level=DEBUG"

    # Vérifier les appels aux fonctions
    mock_parse_args.assert_called_once()
    mock_validate_paths.assert_called_once_with(str(input_dir), str(output_dir))
    mock_find_image_files.assert_called_once_with(input_dir)
    mock_process_metadata.assert_called_once_with(image_files, output_dir)
    mock_processor.process_directory.assert_called_once()


@patch("fluxgym_coach.processor.ImageProcessor")
@patch("fluxgym_coach.cli.get_default_cache")
@patch("fluxgym_coach.cli.parse_args")
@patch("fluxgym_coach.cli.validate_paths")
@patch("fluxgym_coach.cli.find_image_files")
@patch("fluxgym_coach.metadata.process_metadata")
def test_main_processing_error(
    mock_process_metadata,
    mock_find_image_files,
    mock_validate_paths,
    mock_parse_args,
    mock_get_default_cache,
    mock_image_processor_class,
    tmp_path: Path,
    caplog,
):
    """Teste la gestion des erreurs lors du traitement des images."""
    # Configurer les chemins de test
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Créer des fichiers image simulés
    image_files = [input_dir / f"image_{i}.jpg" for i in range(2)]
    for i, img in enumerate(image_files):
        img.write_text(f"test image {i}")

    # Configurer les mocks pour les arguments
    mock_args = MagicMock()
    mock_args.input = str(input_dir)
    mock_args.output = str(output_dir)
    mock_args.process = "all"
    mock_args.verbose = False
    mock_args.no_cache = False
    mock_args.force_reprocess = False
    mock_args.cache_dir = None
    mock_args.clean_cache = False
    mock_parse_args.return_value = mock_args

    # Configurer le mock du cache
    mock_cache = MagicMock(spec=ImageCache)
    mock_get_default_cache.return_value = mock_cache

    # Configurer le mock du processeur pour simuler une erreur
    mock_processor = MagicMock()
    error_msg = "Erreur de traitement simulée"
    # Simuler une erreur lors du traitement des métadonnées
    mock_process_metadata.side_effect = Exception(error_msg)

    # Configurer les valeurs de retour des autres mocks
    mock_validate_paths.return_value = (input_dir, output_dir)
    mock_find_image_files.return_value = image_files

    # Exécuter la fonction main et vérifier qu'elle se termine avec un code d'erreur
    with patch(
        "sys.argv",
        ["fluxgym-coach", "--input", str(input_dir), "--output", str(output_dir)],
    ):
        result = main()

    # Vérifier que la fonction retourne un code d'erreur
    assert result != 0, "Le programme aurait dû retourner un code d'erreur"

    # Vérifier que les fonctions ont été appelées
    mock_parse_args.assert_called_once()
    mock_validate_paths.assert_called_once_with(str(input_dir), str(output_dir))
    mock_find_image_files.assert_called_once_with(input_dir)
    # Vérifier que process_metadata a été appelé avec les bons arguments
    mock_process_metadata.assert_called_once_with(image_files, output_dir)
    # Vérifier que process_directory n'est pas appelé en cas d'erreur dans process_metadata
    mock_processor.process_directory.assert_not_called()
