import pytest
from unittest.mock import patch, mock_open
from ai_model.config import Config
import os
from pathlib import Path

class TestConfig:
    def test_init(self, mock_config_dict):
        with patch('builtins.open', mock_open(read_data="key: value")):
            with patch('yaml.safe_load', return_value=mock_config_dict):
                config = Config()
                assert config._config == mock_config_dict

    def test_init_default_path(self):
        with patch('os.path.dirname', return_value='/app/ai_model/config'):
            with patch('builtins.open', mock_open(read_data="key: value")) as mock_file:
                with patch('yaml.safe_load', return_value={}):
                    config = Config()
                    expected_path = Path(os.path.join('/app/ai_model/config', 'config.yaml'))
                    mock_file.assert_called_with(expected_path, 'r')

    def test_get(self, mock_config):
        assert mock_config.get('model.architecture') == 'lstm'
        assert mock_config.get('training.batch_size') == 4
        assert mock_config.get('non_existent', 'default') == 'default'
        assert mock_config.get('model.non_existent', 'default') == 'default'

    def test_get_not_dict(self, mock_config):
        # Accessing nested key on non-dict value
        # e.g. model.architecture.something
        # model.architecture is string 'lstm'
        assert mock_config.get('model.architecture.something', 'default') == 'default'

    def test_get_key_not_in_dict_nested(self, mock_config):
        # Case: model exists, but model.unknown does not
        # loop: k='model'. value=dict. k in value? Yes. value=value['model']
        # loop: k='unknown'. value=dict. k in value? No. return default.
        assert mock_config.get('model.unknown', 'def') == 'def'

    def test_property_access(self, mock_config):
        assert mock_config.model['architecture'] == 'lstm'
        assert mock_config.training['batch_size'] == 4
        assert mock_config.data['sequence_length'] == 10
        assert mock_config.api['port'] == 5000

    def test_set(self):
        with patch('builtins.open', mock_open()):
             with patch('yaml.safe_load', return_value={}):
                config = Config()
                config.set('model.hidden_size', 256)
                assert config.get('model.hidden_size') == 256

                config.set('new_section.key', 'value')
                assert config.get('new_section.key') == 'value'

    def test_set_nested(self):
        with patch('builtins.open', mock_open()):
             with patch('yaml.safe_load', return_value={}):
                config = Config()
                config.set('a.b.c', 1)
                assert config.get('a.b.c') == 1
                assert isinstance(config.get('a'), dict)
                assert isinstance(config.get('a.b'), dict)
