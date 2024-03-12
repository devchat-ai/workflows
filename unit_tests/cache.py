import json
import os


class LocalCache:
    """
    A file-based cache for storing and retrieving simple data in JSON format.
    """

    DIR = "local_cache"

    def __init__(self, name: str, base_path: str):
        self._name = name
        self._cache = {}
        self._base_path = base_path

        cache_dir = os.path.join(base_path, self.DIR)
        os.makedirs(cache_dir, exist_ok=True)

        self._cache_file = os.path.join(cache_dir, f"{name}.json")
        self.load()

    @property
    def name(self):
        return self._name

    def load(self):
        try:
            with open(self._cache_file, "r") as f:
                self._cache = json.load(f)
        except FileNotFoundError:
            pass

    def save(self):
        with open(self._cache_file, "w") as f:
            json.dump(self._cache, f)

    def get(self, key: str):
        return self._cache.get(key)

    def set(self, key: str, value):
        if self._cache.get(key) != value:
            self._cache[key] = value
            self.save()
