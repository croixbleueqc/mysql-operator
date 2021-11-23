"""
App Kind
"""

from typing import Literal
from pydantic import BaseModel # pylint: disable=no-name-in-module
from .metadata import Metadata

# Copyright 2021 Croix Bleue du Québec

# This file is part of myop.

# myop is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# myop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with myop.  If not, see <https://www.gnu.org/licenses/>.

class AppSpec(BaseModel): # pylint: disable=too-few-public-methods
    """App Spec model"""
    instance: str

class AppKind(BaseModel): # pylint: disable=too-few-public-methods
    """App Kind model"""
    apiVersion: Literal['mysql.bleuelab.ca/v1']
    kind: Literal['App']
    metadata: Metadata
    spec: AppSpec
