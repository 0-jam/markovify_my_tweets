import json
from pathlib import Path


def load_settings(params_json='settings/default.json'):
    with Path(params_json).open(encoding='utf-8') as params:
        parameters = json.load(params)

    return parameters


def load_test_settings():
    return load_settings('settings/test.json')
