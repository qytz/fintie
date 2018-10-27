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
from collections import defaultdict

import aiohttp

_http_session = None
_init_in_session = defaultdict()


def get_http_session(*init_urls):
    global _http_session
    if not _http_session:
        _http_session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
            }
        )
    # aws = []
    # for url in init_urls:
    #     aws.append(_http_session.get(url))
    # await asyncio.gather(*aws, return_exceptions=True)
    return _http_session
