"""Settings module"""

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

DOMAIN='bleuelab.ca'
OPERATOR='myop'
GROUP=f'mysql.{DOMAIN}'

LATEST_VERSION='v1'
DEFAULT_ADMISSION_MANAGED=f'admission.{GROUP}'
DEFAULT_TIMEOUT=60*60
WATCHING_SERVER_TIMEOUT=1*60
WATCHING_CONNECT_TIMEOUT=1*60

STATUS_SUCCESS='lastOperationSuccess'

BINDING=\
"""
apiVersion: v1
kind: Secret
metadata:
  name: {name}
type: Opaque
data:
  username: '{username}'
  password: '{password}'
  url: '{url}'
"""

ENV_HOST='MYOP_HOST'
