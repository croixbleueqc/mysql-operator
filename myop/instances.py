"""
Manages Instances kind
"""

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

import kopf
from . import settings
from .typing.instances import InstancesKind
from .secrets.vault import HashiCorpVault

INSTANCES='instances'

class InternalInstance():
    """
    Internal Instance
    """
    def __init__(self, kinstance: InstancesKind):
        self._kinstance = kinstance
        self._mysql_pwd = None

    @property
    def host(self) -> str:
        """MySQL host"""
        return self._kinstance.spec.host

    @property
    def port(self) -> int:
        """MySQL port"""
        return self._kinstance.spec.port

    @property
    def ssl(self) -> bool:
        """MySQL ssl"""
        return self._kinstance.spec.ssl

    @property
    def user(self) -> str:
        """MySQL user"""
        return self._kinstance.spec.user

    def get_mysql_pwd(self) -> str:
        """
        Return the MySQL password associated with the instance
        """
        if self._mysql_pwd is not None:
            return self._mysql_pwd

        if self._kinstance.spec.pwd.hashicorpVault is not None:
            # get password from vault
            spec = self._kinstance.spec.pwd.hashicorpVault

            self._mysql_pwd = HashiCorpVault.get_one_secret(spec)
            return self._mysql_pwd

        raise ValueError("MySQL password is not available !")

@kopf.index(settings.GROUP, settings.LATEST_VERSION, INSTANCES)
def instances_idx(body: kopf.Body, **_):
    """
    Index all instances
    """
    kinstance: InstancesKind = InstancesKind.parse_obj(body)

    return {
        kinstance.metadata.name: InternalInstance(kinstance)
    }

def instance_from_index(index: kopf.Index, name: str) -> InternalInstance:
    """
    Get internal instance from Index or raise a temporary error
    """
    instances = index.get(name, [])

    if isinstance(instances, kopf.Store) and len(instances) > 0:
        instance = list(instances)[-1]
    else:
        instance = None

    if instance is None:
        raise kopf.TemporaryError(f"instance {name} is not available in index")

    return instance
