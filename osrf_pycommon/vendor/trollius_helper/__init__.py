# Copyright 2016 Open Source Robotics Foundation, Inc.
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

"""
Try's to import trollius normally, but will also try to import a local copy.

Should be imported before calling ``import trollius``.
"""

import os
import sys

try:
    import trollius
except ImportError:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    trollius_dir = os.path.join(this_dir, 'trollius')
    if os.path.exists(trollius_dir):
        sys.path.insert(0, trollius_dir)
        import trollius


def get_trollius_module():
    return trollius
