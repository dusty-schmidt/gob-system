import yaml

class ConfigManager:
    def __init__(self, config_path='config/gob.yaml'):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # In a real application, you'd want to handle this more gracefully.
            # For now, we'll just return an empty dict.
            return {}

    def get(self, key, default=None):
        return self.config.get(key, default)

    def get_service_config(self, service_name):
        return self.get('services', {}).get(service_name, {})
