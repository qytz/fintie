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
"""数据模块命令行"""
import logging

import click

from .config import load_config, set_config, def_config_path


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option(
    "-c",
    "--conf",
    type=click.Path(),
    help="配置文件",
    default=def_config_path,
    show_default=True,
)
@click.option("-d", "--data-path", type=click.Path(), help="数据存储路径，会覆盖 conf 文件里的设置")
def cli(verbose, conf, data_path):
    """Console script for fintie

    Copyright (C) 2017-present qytz <hhhhhf@foxmail.com>

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Project url: https://github.com/qytz/fintie
    """
    log_levels = [
        logging.CRITICAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
    ]
    if verbose >= len(log_levels):
        verbose = len(log_levels) - 1
    log_fmt = (
        "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
    )
    logging.basicConfig(
        filename="fintie.log", level=log_levels[verbose], format=log_fmt
    )

    if conf:
        load_config(conf)

    if data_path:
        set_config("data_path", data_path)


if __name__ == "__main__":
    cli()
