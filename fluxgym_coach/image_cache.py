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
from typing import Any, Dict, Optional, Set, Tuple, Union

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
        self.cache: Dict[str, Dict] = {"version": CACHE_VERSION, "entries": {}}
        self._load_cache()

    def _load_cache(self) -> None:
        """Charge le cache depuis le fichier s'il existe."""
        if not self.cache_file or not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Vérifier la version du cache
            if cache_data.get("version") != CACHE_VERSION:
                logger.warning("Format de cache obsolète, création d'un nouveau cache")
                return

            self.cache = cache_data
            logger.debug(
                f"Cache chargé depuis {self.cache_file} avec {len(self.cache['entries'])} entrées"
            )

        except (json.JSONDecodeError, IOError) as e:
            logger.warning(
                f"Impossible de charger le cache depuis {self.cache_file}: {e}"
            )

    def _save_cache(self) -> None:
        """Sauvegarde le cache dans le fichier."""
        if not self.cache_file:
            return

        try:
            # Créer le répertoire parent si nécessaire
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)

            logger.debug(f"Cache sauvegardé dans {self.cache_file}")

        except IOError as e:
            logger.error(f"Erreur lors de la sauvegarde du cache: {e}")

    def generate_key(
        self, source_path: Union[str, Path], params: Optional[Dict] = None
    ) -> str:
        """
        Génère une clé de cache unique pour une image et des paramètres donnés.

        Args:
            source_path: Chemin vers le fichier source
            params: Dictionnaire de paramètres de traitement (optionnel)

        Returns:
            Une chaîne de caractères représentant la clé de cache
        """
        import hashlib

        # Normaliser le chemin source
        source_path = str(Path(source_path).resolve())

        # Créer un hachage à partir du chemin source et des paramètres
        hasher = hashlib.sha256()
        hasher.update(source_path.encode("utf-8"))

        # Ajouter les paramètres au hachage s'ils sont fournis
        if params:
            # Trier les clés pour assurer un ordre cohérent
            for key in sorted(params.keys()):
                value = params[key]
                if value is not None:  # Ignorer les valeurs None
                    hasher.update(str(key).encode("utf-8"))
                    hasher.update(str(value).encode("utf-8"))

        return hasher.hexdigest()

    @staticmethod
    def calculate_file_hash(
        file_path: Union[str, Path], chunk_size: int = 65536
    ) -> str:
        """
        Calcule une empreinte unique d'un fichier.

        Args:
            file_path: Chemin vers le fichier
            chunk_size: Taille des blocs à lire (en octets)

        Returns:
            Chaîne hexadécimale représentant l'empreinte du fichier (64 caractères hexadécimaux)
        """
        import hashlib

        file_path = Path(file_path)
        hasher = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)

            # Ajouter la taille et la date de modification pour détecter les changements
            stat = file_path.stat()
            hasher.update(str(stat.st_size).encode())
            hasher.update(str(stat.st_mtime).encode())

            return hasher.hexdigest()

        except (IOError, OSError) as e:
            logger.error(f"Erreur lors du calcul de l'empreinte de {file_path}: {e}")
            raise

    def get_cache_key(
        self, file_path: Union[str, Path], params: Optional[Dict] = None
    ) -> str:
        """
        Génère une clé de cache pour un fichier et des paramètres donnés.

        Args:
            file_path: Chemin vers le fichier
            params: Paramètres de traitement (optionnel)

        Returns:
            Clé de cache unique
        """
        resolved_path = Path(file_path).resolve()
        file_path_str = str(resolved_path)

        # Créer une copie profonde des paramètres pour éviter de modifier l'original
        if params is not None:
            params = {k: v for k, v in params.items() if v is not None}
            # Trier les clés pour assurer une sérialisation cohérente
            params = dict(sorted(params.items()))
            # Convertir tous les paramètres en chaînes pour éviter les problèmes de type
            for k, v in params.items():
                if isinstance(v, (list, dict, bool)):
                    params[k] = json.dumps(v, sort_keys=True)
            param_str = json.dumps(params, sort_keys=True)
        else:
            param_str = ""

        # Ajout de logs pour le débogage
        logger.debug(f"[CACHE] Génération de la clé de cache pour: {file_path}")
        logger.debug(f"[CACHE] Chemin résolu: {file_path_str}")
        logger.debug(f"[CACHE] Paramètres: {params}")
        logger.debug(f"[CACHE] Paramètres sérialisés: {param_str}")

        cache_key = f"{file_path_str}:{param_str}"
        logger.debug(f"[CACHE] Clé de cache générée: {cache_key}")

        return cache_key

    def is_cached(
        self,
        source_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        params: Optional[Dict] = None,
        return_cached_path: bool = False,
    ) -> Union[bool, Tuple[bool, Optional[Path]]]:
        """
        Vérifie si une image est déjà dans le cache et que le fichier de sortie existe.

        Args:
            source_path: Chemin vers le fichier source
            output_path: Chemin attendu du fichier de sortie (optionnel)
            params: Paramètres de traitement (optionnel)
            return_cached_path: Si True, retourne un tuple (bool, Optional[Path]) contenant
                              le statut du cache et le chemin du fichier en cache

        Returns:
            Si return_cached_path est False (par défaut):
                bool: True si l'image est en cache et que le fichier de sortie existe, False sinon
            Si return_cached_path est True:
                Tuple[bool, Optional[Path]]: Un tuple contenant le statut du cache et le chemin du fichier en cache
        """
        try:
            # Normaliser les chemins pour éviter les problèmes de formatage
            source_path = Path(source_path).resolve()
            logger.debug(f"[CACHE] Vérification du cache pour: {source_path}")
            logger.debug(f"[CACHE] Chemin de sortie fourni: {output_path}")
            logger.debug(
                f"[CACHE] Paramètres fournis: {json.dumps(params, indent=2, default=str) if params else 'Aucun'}"
            )

            # Afficher toutes les clés de cache existantes pour le débogage
            logger.debug(
                f"[CACHE] Nombre d'entrées dans le cache: {len(self.cache['entries'])}"
            )
            if self.cache["entries"]:
                logger.debug("[CACHE] Clés de cache existantes:")
                for i, key in enumerate(
                    list(self.cache["entries"].keys())[:5]
                ):  # Limiter à 5 clés pour éviter les logs trop longs
                    entry = self.cache["entries"][key]
                    logger.debug(f"[CACHE]   {i+1}. {key}")
                    logger.debug(
                        f"[CACHE]     Entrée: {json.dumps(entry, indent=4, default=str)}"
                    )
                if len(self.cache["entries"]) > 5:
                    logger.debug(
                        f"[CACHE]   ... et {len(self.cache['entries']) - 5} autres entrées"
                    )

            # Vérifier que le fichier source existe
            if not source_path.exists():
                logger.warning(f"[CACHE] Le fichier source n'existe pas: {source_path}")
                if return_cached_path:
                    return False, None
                return False

            # Générer la clé de cache
            cache_key = self.get_cache_key(source_path, params)
            logger.debug(f"[CACHE] Clé de cache générée: {cache_key}")

            # Vérifier si la clé existe dans le cache
            cache_entry = self.cache["entries"].get(cache_key)
            if not cache_entry:
                logger.debug(
                    f"[CACHE] Aucune entrée de cache trouvée pour la clé: {cache_key}"
                )
                if return_cached_path:
                    return False, None
                return False

            logger.debug(
                f"[CACHE] Entrée de cache trouvée: {json.dumps(cache_entry, indent=2, default=str)}"
            )

            # Vérifier que le fichier source n'a pas changé
            current_hash = self.calculate_file_hash(source_path)
            cached_hash = cache_entry.get("hash")
            logger.debug(f"[CACHE] Hash actuel du fichier source: {current_hash}")
            logger.debug(f"[CACHE] Hash en cache: {cached_hash}")

            is_hash_match = cached_hash == current_hash
            logger.debug(f"[CACHE] Les hashs correspondent: {is_hash_match}")

            if not is_hash_match:
                logger.warning(
                    f"[CACHE] Le hash du fichier source a changé: {source_path}"
                )
                if return_cached_path:
                    return False, None
                return False

            # Vérifier le fichier de sortie si spécifié
            if output_path is not None:
                output_path = Path(output_path).resolve()

                # Vérifier si le fichier de sortie existe
                if not output_path.exists():
                    logger.warning(
                        f"[CACHE] Le fichier de sortie n'existe pas: {output_path}"
                    )
                    if return_cached_path:
                        return False, None
                    return False

                # Si un chemin de sortie est en cache, vérifier qu'il correspond
                if "output_path" in cache_entry and cache_entry["output_path"]:
                    cached_output = Path(cache_entry["output_path"]).resolve()
                    logger.debug(f"[CACHE] Chemin de sortie en cache: {cached_output}")
                    logger.debug(f"[CACHE] Chemin de sortie attendu: {output_path}")

                    # Comparaison des chemins normalisés
                    if str(cached_output) != str(output_path):
                        logger.warning(
                            f"[CACHE] Les chemins de sortie ne correspondent pas. "
                            f"Attendu: {output_path}, Trouvé: {cached_output}"
                        )
                        if return_cached_path:
                            return False, None
                        return False
                else:
                    logger.debug(
                        "[CACHE] Aucun chemin de sortie dans l'entrée de cache, utilisation du chemin fourni"
                    )

                    # Mettre à jour le cache avec le chemin de sortie fourni
                    self.cache["entries"][cache_key]["output_path"] = str(output_path)
                    self._save_cache()
                    logger.debug(
                        f"[CACHE] Cache mis à jour avec le chemin de sortie: {output_path}"
                    )

            logger.debug("[CACHE] Vérification du cache réussie")

            # Si on demande de retourner le chemin en cache
            if return_cached_path:
                cached_output = None
                if "output_path" in cache_entry and cache_entry["output_path"]:
                    cached_output = Path(cache_entry["output_path"])
                    if not cached_output.exists():
                        logger.warning(
                            f"[CACHE] Le fichier en cache n'existe pas: {cached_output}"
                        )
                        return False, None
                return True, cached_output

            return True

        except Exception as e:
            error_msg = f"[CACHE] Erreur lors de la vérification du cache pour {source_path}: {e}"
            logger.error(error_msg, exc_info=True)
            if return_cached_path:
                return False, None
            return False

    def add_to_cache(
        self,
        source_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        params: Optional[Dict] = None,
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
                logger.warning(
                    f"Impossible d'ajouter au cache: {source_path} n'existe pas"
                )
                return

            cache_key = self.get_cache_key(source_path, params)

            # Créer l'entrée de cache avec toutes les informations nécessaires
            cache_entry = {
                "hash": self.calculate_file_hash(source_path),
                "timestamp": datetime.now().isoformat(),
                "source_path": str(source_path),
                "params": params,
            }

            # Ajouter le chemin de sortie s'il est fourni
            if output_path:
                output_path = Path(output_path).resolve()
                cache_entry["output_path"] = str(output_path)

            # Mettre à jour le cache
            self.cache["entries"][cache_key] = cache_entry
            self._save_cache()
            logger.debug(f"Entrée ajoutée au cache: {cache_key}")

        except Exception as e:
            logger.error(f"Erreur lors de l'ajout au cache: {e}", exc_info=True)

    def remove_from_cache(
        self, source_path: Union[str, Path], params: Optional[Dict] = None
    ) -> None:
        """
        Supprime une entrée du cache.

        Args:
            source_path: Chemin vers le fichier source
            params: Paramètres de traitement (optionnel)
        """
        try:
            source_path = Path(source_path).resolve()
            cache_key = self.get_cache_key(source_path, params)

            if cache_key in self.cache["entries"]:
                del self.cache["entries"][cache_key]
                self._save_cache()
                logger.debug(f"Entrée supprimée du cache: {cache_key}")

        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache: {e}")

    def clear_cache(self) -> None:
        """Vide complètement le cache."""
        self.cache["entries"] = {}
        self._save_cache()
        logger.info("Cache vidé")

    def cleanup_cache(self, max_age_days: int = 30) -> None:
        """
        Nettoie le cache en supprimant les entrées trop anciennes.

        Args:
            max_age_days: Âge maximum en jours avant suppression
        """
        if not self.cache["entries"]:
            return

        try:
            now = datetime.now()
            removed = 0

            for cache_key, entry in list(self.cache["entries"].items()):
                if "timestamp" not in entry:
                    continue

                entry_time = datetime.fromisoformat(entry["timestamp"])
                age = (now - entry_time).days

                if age > max_age_days:
                    # Vérifier si le fichier de sortie existe et le supprimer
                    if "output_path" in entry:
                        try:
                            output_path = Path(entry["output_path"])
                            if output_path.exists():
                                output_path.unlink()
                                logger.debug(
                                    f"Fichier de sortie supprimé: {output_path}"
                                )
                        except Exception as e:
                            logger.warning(
                                f"Erreur lors de la suppression du fichier {entry['output_path']}: {e}"
                            )

                    del self.cache["entries"][cache_key]
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
