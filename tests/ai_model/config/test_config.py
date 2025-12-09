import pytest
from unittest.mock import patch, mock_open
from ai_model.config import Config

class TestConfig:
    def test_init(self, mock_config_dict):
        # We need to mock the file opening and yaml loading since we don't want to read a real file
        with patch('builtins.open', mock_open(read_data="key: value")):
            with patch('yaml.safe_load', return_value=mock_config_dict):
                config = Config()
                assert config._config == mock_config_dict

    def test_get(self, mock_config):
        assert mock_config.get('model.architecture') == 'lstm'
        assert mock_config.get('training.batch_size') == 4
        assert mock_config.get('non_existent', 'default') == 'default'
        assert mock_config.get('model.non_existent', 'default') == 'default'

    def test_property_access(self, mock_config):
        assert mock_config.model['architecture'] == 'lstm'
        assert mock_config.training['batch_size'] == 4
        assert mock_config.data['sequence_length'] == 10
        assert mock_config.api['port'] == 5000

    def test_set(self):
        # Create a real Config object but with mocked load
        with patch('builtins.open', mock_open()):
             with patch('yaml.safe_load', return_value={}):
                config = Config()
                config.set('model.hidden_size', 256)
                assert config.get('model.hidden_size') == 256

                config.set('new_section.key', 'value')
                assert config.get('new_section.key') == 'value'
