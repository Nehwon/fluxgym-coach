"""Tests pour le module de cache d'images de Fluxgym-coach."""

import json
import os
import time
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from fluxgym_coach.image_cache import ImageCache


def test_image_cache_initialization(temp_dir: Path) -> None:
    """Teste l'initialisation de ImageCache."""
    # Test avec un fichier de cache
    cache_file = temp_dir / "test_cache.json"
    cache = ImageCache(cache_file)
    
    assert cache.cache_file == cache_file
    assert cache.cache['version'] == 1
    assert cache.cache['entries'] == {}
    
    # Test sans fichier de cache (cache en mémoire uniquement)
    cache = ImageCache()
    assert cache.cache_file is None
    assert cache.cache['version'] == 1


def test_calculate_file_hash(temp_dir: Path) -> None:
    """Teste le calcul d'empreinte de fichier."""
    # Créer un fichier de test
    test_file = temp_dir / "test.txt"
    test_content = "Contenu de test"
    test_file.write_text(test_content, encoding='utf-8')
    
    # Obtenir le hash initial
    initial_hash = ImageCache.calculate_file_hash(test_file)
    
    # Le hash devrait être le même pour le même contenu
    assert ImageCache.calculate_file_hash(test_file) == initial_hash
    
    # Modifier le fichier et vérifier que le hash change
    test_file.write_text("Contenu modifié", encoding='utf-8')
    assert ImageCache.calculate_file_hash(test_file) != initial_hash


def test_get_cache_key() -> None:
    """Teste la génération de clé de cache."""
    # Test avec un chemin simple sans paramètres
    cache_key = ImageCache("").get_cache_key("/chemin/image.jpg")
    assert cache_key == "/chemin/image.jpg:"
    
    # Test avec des paramètres
    params = {"scale": 2, "quality": 90}
    cache_key = ImageCache("").get_cache_key("/chemin/image.jpg", params)
    # L'ordre des clés dans les paramètres ne devrait pas affecter la clé de cache
    assert cache_key.startswith("/chemin/image.jpg:{")
    assert "scale" in cache_key
    assert "quality" in cache_key


def test_cache_operations(temp_dir: Path) -> None:
    """Teste les opérations de base du cache."""
    cache_file = temp_dir / "test_cache.json"
    test_file = temp_dir / "test.jpg"
    output_file = temp_dir / "output.jpg"
    
    # Créer un fichier de test avec du contenu
    test_file.write_text("test content")
    output_file.write_text("output content")
    
    cache = ImageCache(cache_file)
    
    # Le fichier ne devrait pas être dans le cache initialement
    assert not cache.is_cached(test_file)
    
    # Ajouter le fichier au cache
    cache.add_to_cache(test_file, output_path=output_file)
    
    # Le fichier devrait maintenant être dans le cache
    assert cache.is_cached(test_file)
    
    # Vérifier que le fichier de sortie est pris en compte
    assert cache.is_cached(test_file, output_path=output_file)
    assert not cache.is_cached(test_file, output_path=temp_dir / "other.jpg")
    
    # Vérifier que la modification du fichier source est détectée
    test_file.write_text("modified content")
    assert not cache.is_cached(test_file)


def test_persistent_cache(temp_dir: Path) -> None:
    """Teste la persistance du cache sur disque."""
    cache_file = temp_dir / "persistent_cache.json"
    test_file = temp_dir / "persistent_test.jpg"
    test_file.write_text("test content")
    
    # Créer un cache et y ajouter une entrée
    cache = ImageCache(cache_file)
    cache.add_to_cache(test_file)
    assert cache.is_cached(test_file)
    
    # Sauvegarder explicitement le cache
    cache._save_cache()
    
    # Vérifier que le fichier de cache a été créé
    assert cache_file.exists()
    
    # Recréer le cache à partir du fichier
    new_cache = ImageCache(cache_file)
    assert new_cache.is_cached(test_file)


def test_cache_with_parameters(temp_dir: Path) -> None:
    """Teste le cache avec différents paramètres de traitement."""
    cache = ImageCache()
    test_file = temp_dir / "param_test.jpg"
    test_file.touch()
    
    # Ajouter avec des paramètres
    params1 = {"scale": 2, "quality": 90}
    cache.add_to_cache(test_file, params=params1)
    
    # Doit correspondre avec les mêmes paramètres
    assert cache.is_cached(test_file, params=params1)
    
    # Ne doit pas correspondre avec des paramètres différents
    params2 = {"scale": 2, "quality": 80}
    assert not cache.is_cached(test_file, params=params2)
    
    # L'ordre des paramètres ne devrait pas importer
    params3 = {"quality": 90, "scale": 2}
    assert cache.is_cached(test_file, params=params3)


def test_cache_cleanup(temp_dir: Path) -> None:
    """Teste le nettoyage des entrées de cache obsolètes."""
    cache_file = temp_dir / "cleanup_cache.json"
    test_file = temp_dir / "cleanup_test.jpg"
    output_file = temp_dir / "output.jpg"
    
    # Créer un fichier de test et son fichier de sortie
    test_file.write_text("test content")
    output_file.write_text("output content")
    
    # Créer un cache et y ajouter une entrée
    cache = ImageCache(cache_file)
    cache.add_to_cache(test_file, output_path=output_file)
    
    # Vérifier que l'entrée est bien dans le cache
    assert cache.is_cached(test_file, output_path=output_file)
    
    # Supprimer le fichier de sortie
    output_file.unlink()
    
    # Vérifier que le cache détecte que le fichier de sortie est manquant
    assert not cache.is_cached(test_file, output_path=output_file)


@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
@patch("json.load")
def test_cache_error_handling(mock_load, mock_dump, mock_file, temp_dir):
    """Teste la gestion des erreurs lors de la lecture/écriture du cache."""
    # Simuler une erreur de lecture du cache
    mock_load.side_effect = json.JSONDecodeError("Erreur de test", "", 0)
    cache = ImageCache(temp_dir / "error_cache.json")
    
    # Le cache devrait être vide en cas d'erreur
    assert cache.cache["entries"] == {}
    
    # Simuler une erreur d'écriture du cache
    test_file = temp_dir / "error_test.jpg"
    test_file.touch()
    mock_dump.side_effect = IOError("Erreur d'écriture")
    
    # L'ajout au cache ne devrait pas lever d'exception
    cache.add_to_cache(test_file)
    
    # Vérifier que l'ajout a quand même fonctionné (en mémoire)
    assert cache.is_cached(test_file)


def test_is_cached_with_return_path(temp_dir: Path) -> None:
    """Teste is_cached avec le paramètre return_cached_path."""
    # Créer un cache et un fichier de test
    cache = ImageCache()
    test_file = temp_dir / "test_with_path.jpg"
    output_file = temp_dir / "output_with_path.jpg"
    
    # Créer les fichiers nécessaires
    test_file.write_text("test content")
    output_file.write_text("output content")
    
    # Ajouter au cache
    cache.add_to_cache(test_file, output_path=output_file)
    
    # Tester sans le paramètre return_cached_path (compatibilité arrière)
    assert cache.is_cached(test_file) is True
    
    # Tester avec return_cached_path=True
    is_cached, cached_path = cache.is_cached(test_file, return_cached_path=True)
    assert is_cached is True
    assert cached_path == output_file.resolve()
    
    # Vérifier que le chemin retourné pointe vers un fichier existant
    assert cached_path.exists()
    assert cached_path.read_text() == "output content"


def test_is_cached_with_return_path_not_cached(temp_dir: Path) -> None:
    """Teste is_cached avec return_cached_path pour un fichier non en cache."""
    cache = ImageCache()
    test_file = temp_dir / "not_cached.jpg"
    
    # Le fichier n'est pas dans le cache
    is_cached, cached_path = cache.is_cached(test_file, return_cached_path=True)
    assert is_cached is False
    assert cached_path is None


def test_is_cached_with_return_path_and_params(temp_dir: Path) -> None:
    """Teste is_cached avec return_cached_path et des paramètres de traitement."""
    cache = ImageCache()
    test_file = temp_dir / "test_with_params.jpg"
    output_file = temp_dir / "output_with_params.jpg"
    params = {"scale": 2, "quality": 90}
    
    # Créer les fichiers nécessaires
    test_file.write_text("test content with params")
    output_file.write_text("output content with params")
    
    # Ajouter au cache avec des paramètres
    cache.add_to_cache(test_file, output_path=output_file, params=params)
    
    # Tester avec les mêmes paramètres
    is_cached, cached_path = cache.is_cached(
        test_file, 
        output_path=output_file,
        params=params,
        return_cached_path=True
    )
    assert is_cached is True
    assert cached_path == output_file.resolve()
    
    # Tester avec des paramètres différents (ne devrait pas correspondre)
    is_cached, cached_path = cache.is_cached(
        test_file,
        output_path=output_file,
        params={"scale": 1, "quality": 80},
        return_cached_path=True
    )
    assert is_cached is False
    assert cached_path is None


def test_is_cached_with_return_path_error_handling(temp_dir: Path) -> None:
    """Teste la gestion des erreurs avec return_cached_path."""
    cache = ImageCache()
    test_file = temp_dir / "error_test.jpg"
    output_file = temp_dir / "error_output.jpg"
    
    # Créer le fichier source mais pas le fichier de sortie
    test_file.write_text("test error handling")
    
    # Ajouter au cache avec un chemin de sortie qui n'existe pas
    cache.add_to_cache(test_file, output_path=output_file)
    
    # is_cached devrait retourner False car le fichier de sortie n'existe pas
    is_cached, cached_path = cache.is_cached(
        test_file, 
        output_path=output_file,
        return_cached_path=True
    )
    assert is_cached is False
    assert cached_path is None
