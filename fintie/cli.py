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
import os
from plumbum import cli
from .__version__ import __version__


class FinApp(cli.Application):
    """Base FinTie command"""
    VERSION = __version__

    _verbose = 0
    _debug = False
    _root_dir = os.path.expanduser("~/.local/fintie")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.parent:
            self._verbose = self.parent._verbose
            self._debug = self.parent._debug
            self._root_dir = self.parent._root_dir

    @cli.switch(['-v', '--verbose'], overridable=True, list=True, argtype=None)
    def set_verbose(self, val):
        """If given, I will be very talkative"""
        self._verbose += len(val)

    @cli.switch(['-d', '--debug'], overridable=True)
    def set_debug(self):
        """If given, I will give diagnosis infos"""
        self._debug = True

    @cli.switch(['-r', '--root'], argtype=str, overridable=True)
    def set_root(self, root):
        """The root directory to store data, default='~/.local/fintie'"""
        self._root_dir = os.path.abspath(os.path.expanduser(root))
        os.makedirs(self._root_dir, exist_ok=True)


class FinTie(FinApp):
    """FinTie command"""
    def main(self, *args):
        if args:
            print("Unknown command {0!r}".format(args[0]))
            return 1   # error exit code
        if not self.nested_command:           # will be ``None`` if no sub-command follows
            print("No command given")
            return 1   # error exit code
        return 0


if __name__ == "__main__":
    FinTie()
