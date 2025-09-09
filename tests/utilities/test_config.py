import json
import logging
from types import MappingProxyType
from unittest.mock import mock_open, patch

import pytest

from podcast.utilities.config import ConfigUtility


@pytest.fixture
def logger():
    return logging.getLogger("test_logger")


@pytest.fixture
def valid_config():
    return {"key1": "value1", "key2": "value2"}


@pytest.fixture
def invalid_json():
    return '{"key1": "value1", "key2": "value2"'  # Missing closing bracket


def test_config_initialization_with_valid_dict(logger, valid_config):
    config_util = ConfigUtility(logger=logger, config=valid_config)
    assert isinstance(config_util.get_config(), MappingProxyType)
    assert config_util.get_config()["key1"] == "value1"


def test_config_initialization_invalid_dict(logger):
    with pytest.raises(TypeError):
        ConfigUtility(logger=logger, config="not_a_dict")  # type: ignore


def test_config_loading_valid_json(logger, valid_config):
    m = mock_open(read_data=json.dumps(valid_config))
    with patch("builtins.open", m):
        config_util = ConfigUtility(logger=logger, config_path="test_config.json")
        assert isinstance(config_util.get_config(), MappingProxyType)
        assert config_util.get_config()["key1"] == "value1"


def test_config_loading_invalid_json(logger, invalid_json):
    m = mock_open(read_data=invalid_json)
    with patch("builtins.open", m):
        with pytest.raises(ValueError):
            ConfigUtility(logger=logger, config_path="invalid_config.json")


def test_config_file_not_found(logger):
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            ConfigUtility(logger=logger, config_path="non_existent_config.json")


def test_reload_config(logger, valid_config):
    m = mock_open(read_data=json.dumps(valid_config))
    with patch("builtins.open", m):
        config_util = ConfigUtility(logger=logger, config_path="test_config.json")
        initial_config = config_util.get_config()
        assert initial_config["key1"] == "value1"

        # Reload config should work
        config_util.reload_config()
        reloaded_config = config_util.get_config()
        assert reloaded_config["key1"] == "value1"


def test_get_with_default(logger, valid_config):
    config_util = ConfigUtility(logger=logger, config=valid_config)
    assert config_util.get_with_default("key1", "default_value") == "value1"
    assert config_util.get_with_default("non_existent_key", "default_value") == "default_value"


def test_get_with_default_no_key_no_default(logger, valid_config):
    config_util = ConfigUtility(logger=logger, config=valid_config)
    assert config_util.get_with_default("non_existent_key") is None
