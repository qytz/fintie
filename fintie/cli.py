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
from plumbum import cli
from .__version__ import __version__


class FinTie(cli.Application):
    """FinTie command"""
    VERSION = __version__

    verbose = cli.Flag(["v", "verbose"], help="If given, I will be very talkative")
    debug = cli.Flag(["d", "debug"], help="If given, I will give diagnosis infos")
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
