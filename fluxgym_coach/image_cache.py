"""
Module pour la gestion du cache des images traitées.
Permet d'éviter de retraiter les images inchangées.
"""

import hashlib
import json
import logging
import os
import xxhash
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set, Tuple, Union

# Configuration du logger
logger = logging.getLogger(__name__)

# Version du format du cache
CACHE_VERSION = 1


class ImageCache:
    """
    Gestionnaire de cache pour les images traitées.
    
    Le cache stocke des informations sur les images déjà traitées pour éviter
    de les retraiter inutilement. Il utilise un fichier JSON pour la persistance.
    """
    
    def __init__(self, cache_file: Optional[Union[str, Path]] = None):
        """
        Initialise le gestionnaire de cache.
        
        Args:
            cache_file: Chemin vers le fichier de cache. Si None, utilise un cache en mémoire uniquement.
        """
        self.cache_file = Path(cache_file) if cache_file else None
        self.cache: Dict[str, Dict] = {
            'version': CACHE_VERSION,
            'entries': {}
        }
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Charge le cache depuis le fichier s'il existe."""
        if not self.cache_file or not self.cache_file.exists():
            return
            
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Vérifier la version du cache
            if cache_data.get('version') != CACHE_VERSION:
                logger.warning("Format de cache obsolète, création d'un nouveau cache")
                return
                
            self.cache = cache_data
            logger.debug(f"Cache chargé depuis {self.cache_file} avec {len(self.cache['entries'])} entrées")
            
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Impossible de charger le cache depuis {self.cache_file}: {e}")
    
    def _save_cache(self) -> None:
        """Sauvegarde le cache dans le fichier."""
        if not self.cache_file:
            return
            
        try:
            # Créer le répertoire parent si nécessaire
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
                
            logger.debug(f"Cache sauvegardé dans {self.cache_file}")
            
        except IOError as e:
            logger.error(f"Erreur lors de la sauvegarde du cache: {e}")
    
    @staticmethod
    def calculate_file_hash(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
        """
        Calcule une empreinte unique d'un fichier.
        
        Args:
            file_path: Chemin vers le fichier
            chunk_size: Taille des blocs à lire (en octets)
            
        Returns:
            Chaîne hexadécimale représentant l'empreinte du fichier
        """
        file_path = Path(file_path)
        hasher = xxhash.xxh64()
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            
            # Ajouter la taille et la date de modification pour détecter les changements
            stat = file_path.stat()
            hasher.update(str(stat.st_size).encode())
            hasher.update(str(stat.st_mtime).encode())
            
            return f"{hasher.hexdigest()}"
            
        except (IOError, OSError) as e:
            logger.error(f"Erreur lors du calcul de l'empreinte de {file_path}: {e}")
            raise
    
    def get_cache_key(self, file_path: Union[str, Path], params: Optional[Dict] = None) -> str:
        """
        Génère une clé de cache pour un fichier et des paramètres donnés.
        
        Args:
            file_path: Chemin vers le fichier
            params: Paramètres de traitement (optionnel)
            
        Returns:
            Clé de cache unique
        """
        file_path = str(Path(file_path).resolve())
        param_str = json.dumps(params, sort_keys=True) if params else ""
        return f"{file_path}:{param_str}"
    
    def is_cached(
        self, 
        source_path: Union[str, Path], 
        output_path: Optional[Union[str, Path]] = None,
        params: Optional[Dict] = None
    ) -> bool:
        """
        Vérifie si une image est déjà dans le cache et que le fichier de sortie existe.
        
        Args:
            source_path: Chemin vers le fichier source
            output_path: Chemin attendu du fichier de sortie (optionnel)
            params: Paramètres de traitement (optionnel)
            
        Returns:
            True si l'image est en cache et que le fichier de sortie existe, False sinon
        """
        try:
            source_path = Path(source_path).resolve()
            if not source_path.exists():
                return False
                
            cache_key = self.get_cache_key(source_path, params)
            cache_entry = self.cache['entries'].get(cache_key)
            
            if not cache_entry:
                return False
                
            # Vérifier que le fichier de sortie existe
            if output_path:
                output_path = Path(output_path).resolve()
                if not output_path.exists():
                    return False
                
                # Vérifier que le fichier de sortie correspond à celui en cache
                if 'output_path' in cache_entry and str(output_path) != cache_entry['output_path']:
                    return False
            
            # Vérifier que le fichier source n'a pas changé
            current_hash = self.calculate_file_hash(source_path)
            return cache_entry.get('hash') == current_hash
            
        except Exception as e:
            logger.warning(f"Erreur lors de la vérification du cache pour {source_path}: {e}")
            return False
    
    def add_to_cache(
        self, 
        source_path: Union[str, Path], 
        output_path: Optional[Union[str, Path]] = None,
        params: Optional[Dict] = None
    ) -> None:
        """
        Ajoute une entrée au cache.
        
        Args:
            source_path: Chemin vers le fichier source
            output_path: Chemin du fichier de sortie (optionnel)
            params: Paramètres de traitement (optionnel)
        """
        try:
            source_path = Path(source_path).resolve()
            if not source_path.exists():
                logger.warning(f"Impossible d'ajouter au cache: {source_path} n'existe pas")
                return
                
            cache_key = self.get_cache_key(source_path, params)
            
            self.cache['entries'][cache_key] = {
                'hash': self.calculate_file_hash(source_path),
                'timestamp': datetime.now().isoformat(),
                'source_path': str(source_path),
                'params': params
            }
            
            if output_path:
                output_path = Path(output_path).resolve()
                self.cache['entries'][cache_key]['output_path'] = str(output_path)
            
            self._save_cache()
            logger.debug(f"Entrée ajoutée au cache: {cache_key}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout au cache: {e}")
    
    def remove_from_cache(self, source_path: Union[str, Path], params: Optional[Dict] = None) -> None:
        """
        Supprime une entrée du cache.
        
        Args:
            source_path: Chemin vers le fichier source
            params: Paramètres de traitement (optionnel)
        """
        try:
            source_path = Path(source_path).resolve()
            cache_key = self.get_cache_key(source_path, params)
            
            if cache_key in self.cache['entries']:
                del self.cache['entries'][cache_key]
                self._save_cache()
                logger.debug(f"Entrée supprimée du cache: {cache_key}")
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache: {e}")
    
    def clear_cache(self) -> None:
        """Vide complètement le cache."""
        self.cache['entries'] = {}
        self._save_cache()
        logger.info("Cache vidé")
    
    def cleanup_cache(self, max_age_days: int = 30) -> None:
        """
        Nettoie le cache en supprimant les entrées trop anciennes.
        
        Args:
            max_age_days: Âge maximum en jours avant suppression
        """
        if not self.cache['entries']:
            return
            
        try:
            now = datetime.now()
            removed = 0
            
            for cache_key, entry in list(self.cache['entries'].items()):
                if 'timestamp' not in entry:
                    continue
                    
                entry_time = datetime.fromisoformat(entry['timestamp'])
                age = (now - entry_time).days
                
                if age > max_age_days:
                    # Vérifier si le fichier de sortie existe et le supprimer
                    if 'output_path' in entry:
                        try:
                            output_path = Path(entry['output_path'])
                            if output_path.exists():
                                output_path.unlink()
                                logger.debug(f"Fichier de sortie supprimé: {output_path}")
                        except Exception as e:
                            logger.warning(f"Erreur lors de la suppression du fichier {entry['output_path']}: {e}")
                    
                    del self.cache['entries'][cache_key]
                    removed += 1
            
            if removed > 0:
                self._save_cache()
                logger.info(f"Cache nettoyé: {removed} entrées supprimées")
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du cache: {e}")


# Instance globale du cache
_default_cache = None

def get_default_cache() -> ImageCache:
    """Retourne une instance par défaut du cache."""
    global _default_cache
    if _default_cache is None:
        # Par défaut, utilise un cache en mémoire uniquement
        _default_cache = ImageCache()
    return _default_cache
