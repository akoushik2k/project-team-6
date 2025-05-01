import os
import json
from types import SimpleNamespace
import pytest
from unittest.mock import patch

from config import config

# Pytest fixture that automatically resets the config object before and after every test
@pytest.fixture(autouse=True)
def reset_config():
    config._config = None  # Clear config before test
    yield
    config._config = None  # Clear config after test

# Test _init_config when config file doesn't exist
def test_init_config_file_does_not_exist():
    with patch('os.getcwd', return_value="/random"), patch('os.path.isfile', return_value=False), patch('config.config.logger') as test_logger:
        config._init_config()
        # Should log message about initializing an empty config
        test_logger.info.assert_called_with('Initializing empty config')

# Test _init_config when a valid config.json file is present
def test_init_config_file_exists(tmp_path):
    # Sample config to be written into file
    sample_json = {"code": "works", "reason": "unknown"}

    # Create mock config directory and file under pytest's tmp_path
    path_to_test_config_directory = tmp_path / 'config'
    path_to_test_config_directory.mkdir()
    config_json = path_to_test_config_directory / 'config.json'
    config_json.write_text(json.dumps(sample_json))

    # Patch current directory to the temporary one, logger is patched for silence
    with patch('os.getcwd', return_value=str(tmp_path)), \
         patch('config.config.logger'):
        config._init_config()
        assert config._config == sample_json

# Test get_parameter when key is not found (should return None)
def test_get_parameter_default():
    assert config.get_parameter("random") is None

# Test get_parameter when environment variable takes precedence over config
def test_get_parameter_evn_precedence(monkeypatch):
    monkeypatch.setenv('coffee', 'empty')  # Set env variable
    config._config = {"coffee": "full"}    # Conflicting config value
    assert config.get_parameter('coffee') == 'empty'

# Test get_parameter when no environment variable is set (falls back to config)
def test_get_parameter_no_env():
    config._config = {"coffee": "full"}
    assert config.get_parameter('coffee') == 'full'

# Test convert_to_typed_value with a non-numeric string (should stay string)
def test_convert_to_typed_value_string():
    assert config.convert_to_typed_value('randomIsNotSoRandom') == 'randomIsNotSoRandom'

# Test convert_to_typed_value with a numeric string (should become int)
def test_convert_to_typed_value_non_string():
    assert config.convert_to_typed_value('3513431') == 3513431

# Test setting a key/value pair into the environment via set_parameter
def test_set_parameter(monkeypatch):
    config.set_parameter('mood', 'debugging')
    assert os.environ['mood'] == 'debugging'

# Test overwrite_from_args sets only non-null arguments to the environment
def test_overwrite_from_args():
    args = SimpleNamespace(wifi='unstable', patience=None)  # Only one meaningful param
    with patch.dict(os.environ, {}, clear=True):  # Start with a clean environment
        config.overwrite_from_args(args)
        assert os.environ['wifi'] == 'unstable'
        assert 'patience' not in os.environ  # Should not be set
