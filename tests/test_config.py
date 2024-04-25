import yaml

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def test_env_is_production():
    config = load_config('config.yaml')
    assert config['env'] == 'production', "Environment is not set to production!"