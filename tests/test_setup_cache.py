"""Tests pour la fonction setup_cache du module cli."""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fluxgym_coach.cli import setup_cache


@patch("fluxgym_coach.cli.get_default_cache")
def test_setup_cache_no_cache(mock_get_default_cache):
    """Teste que le cache est désactivé avec --no-cache."""
    args = MagicMock()
    args.no_cache = True
    args.cache_dir = None
    args.clean_cache = False
    args.force_reprocess = False
    
    result = setup_cache(args)
    
    assert result is None
    mock_get_default_cache.assert_not_called()


@patch("fluxgym_coach.cli.get_default_cache")
def test_setup_cache_custom_dir(mock_get_default_cache, tmp_path: Path):
    """Teste l'utilisation d'un répertoire de cache personnalisé."""
    custom_dir = tmp_path / "custom_cache"
    mock_cache = MagicMock()
    mock_get_default_cache.return_value = mock_cache
    
    args = MagicMock()
    args.no_cache = False
    args.cache_dir = str(custom_dir)
    args.clean_cache = False
    args.force_reprocess = False
    
    result = setup_cache(args)
    
    assert result == mock_cache
    mock_get_default_cache.assert_called_once_with(cache_dir=custom_dir)


@patch("fluxgym_coach.cli.get_default_cache")
def test_setup_cache_clean(mock_get_default_cache):
    """Teste le nettoyage du cache avec --clean-cache."""
    mock_cache = MagicMock()
    mock_get_default_cache.return_value = mock_cache
    
    args = MagicMock()
    args.no_cache = False
    args.cache_dir = None
    args.clean_cache = True
    args.force_reprocess = False
    
    result = setup_cache(args)
    
    assert result == mock_cache
    mock_cache.clean_old_entries.assert_called_once()


@patch("fluxgym_coach.cli.get_default_cache")
def test_setup_cache_force_reprocess(mock_get_default_cache):
    """Teste le mode force-reprocess."""
    mock_cache = MagicMock()
    mock_get_default_cache.return_value = mock_cache
    
    args = MagicMock()
    args.no_cache = False
    args.cache_dir = None
    args.clean_cache = False
    args.force_reprocess = True
    
    result = setup_cache(args)
    
    assert result == mock_cache
    # Vérifie que clean_old_entries n'est pas appelé
    mock_cache.clean_old_entries.assert_not_called()


@patch("fluxgym_coach.cli.get_default_cache")
def test_setup_cache_error(mock_get_default_cache, caplog):
    """Teste la gestion des erreurs lors de l'initialisation du cache."""
    mock_get_default_cache.side_effect = Exception("Erreur de cache")
    
    args = MagicMock()
    args.no_cache = False
    args.cache_dir = None
    args.clean_cache = False
    args.force_reprocess = False
    
    with caplog.at_level(logging.WARNING):
        result = setup_cache(args)
    
    assert result is None
    assert "Impossible d'initialiser le cache" in caplog.text
