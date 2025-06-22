"""Tests pour l'interface en ligne de commande de Fluxgym-coach."""

from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from fluxgym_coach.cli import parse_args, validate_paths, main
from fluxgym_coach.image_cache import ImageCache

# ... (autres fonctions de test inchangées) ...

@patch("fluxgym_coach.processor.ImageProcessor")
@patch("fluxgym_coach.cli.get_default_cache")
@patch("fluxgym_coach.cli.parse_args")
@patch("fluxgym_coach.cli.validate_paths")
@patch("fluxgym_coach.cli.find_image_files")
@patch("fluxgym_coach.metadata.process_metadata")
def test_main_success(
    mock_process_metadata,
    mock_find_image_files,
    mock_validate_paths,
    mock_parse_args,
    mock_get_default_cache,
    mock_image_processor_class,
    tmp_path: Path,
):
    """Teste le flux principal avec succès avec gestion du cache."""
    # Configurer les chemins de test
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    
    # Créer des fichiers image simulés
    image_files = [input_dir / f"image_{i}.jpg" for i in range(3)]
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
    
    # Configurer le mock du processeur
    mock_processor = MagicMock()
    mock_processor.process_directory.return_value = [(f, f) for f in image_files]
    mock_image_processor_class.return_value = mock_processor
    
    # Configurer les valeurs de retour des autres mocks
    mock_validate_paths.return_value = (input_dir, output_dir)
    mock_find_image_files.return_value = image_files
    mock_process_metadata.return_value = len(image_files)  # Toutes les métadonnées traitées
    
    # Exécuter la fonction main
    with patch("sys.argv", ["fluxgym-coach", "--input", str(input_dir), "--output", str(output_dir)]):
        result = main()
    
    # Vérifier le résultat
    assert result == 0
    
    # Vérifier les appels aux fonctions
    mock_parse_args.assert_called_once()
    mock_validate_paths.assert_called_once_with(str(input_dir), str(output_dir))
    mock_find_image_files.assert_called_once_with(input_dir)
    mock_process_metadata.assert_called_once_with(image_files, output_dir)
    
    # Vérifier que le cache a été initialisé correctement
    mock_get_default_cache.assert_called_once()
    
    # Vérifier que le processeur d'images a été initialisé correctement
    mock_image_processor_class.assert_called_once_with(
        input_dir=input_dir,
        output_dir=output_dir,
        cache=mock_cache,
        cache_params={'force_reprocess': False}
    )
    mock_processor.process_directory.assert_called_once()

# ... (autres fonctions de test inchangées) ...
