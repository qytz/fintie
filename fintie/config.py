# -*- coding: utf-8 -*-
# This file is part of fintie.

# Copyright (C) 2018-present qytz <hhhhhf@foxmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import logging
from pathlib import Path


_config = None
def_config_path = Path("~/.config/fintie")
logger = logging.getLogger(__name__)


def load_config(config_file=def_config_path):
    global _config
    config_file = Path(config_file)
    if not config_file.exists():
        logger.warning('配置文件不存在，配置设置为空')
        _config = {}
        return

    with config_file.open() as f:
        _config = json.load(f)


def get_config(key, default=None):
    if _config is None:
        load_config()
    return _config.get(key, default)


def set_config(key, val):
    if _config is None:
        load_config()
    _config[key] = val
    return True
