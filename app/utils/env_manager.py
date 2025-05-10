import os

class EnvManager:
    def __init__(self) -> None:
        pass

    def set_env_variable(self, key, value):
        os.environ[key] = value
    
    def get_env_variable(self, key, default=None):
        if key not in os.environ:
            if default is not None:
                return default
            raise KeyError(f"Enviroment variable {key} is not found")
        return os.environ[key] 