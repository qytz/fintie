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
"""数据模块

从网上抓取数据

同步提供数据抓取并返回接口及抓取并存储接口
"""
from . import mkt_calendar
from . import announcement
from . import fundamentals
from . import fundamentals_xq
from . import list_quotes
from . import hist_quotes
from . import live_quotes
from . import fenhong
from . import zengfa
from . import guben
from . import gudong
from . import insider
from . import picker_xq

from .mkt_calendar import *         # noqa
from .announcement import *         # noqa
from .fundamentals import *         # noqa
from .fundamentals_xq import *      # noqa
from .list_quotes import *          # noqa
from .hist_quotes import *          # noqa
from .live_quotes import *          # noqa
from .fenhong import *              # noqa
from .zengfa import *               # noqa
from .guben import *                # noqa
from .gudong import *               # noqa
from .insider import *              # noqa
from .picker_xq import *            # noqa


__all__ = (
    mkt_calendar.__all__
    + announcement.__all__
    + fundamentals.__all__
    + fundamentals_xq.__all__
    + fenhong.__all__
    + zengfa.__all__
    + guben.__all__
    + gudong.__all__
    + insider.__all__
    + picker_xq.__all__
    + list_quotes.__all__
    + live_quotes.__all__
    + hist_quotes.__all__
)
