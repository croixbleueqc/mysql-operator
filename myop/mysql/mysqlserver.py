"""
MySQL Server
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

import mysql.connector
from mysql.connector import MySQLConnection
from pwgen import pwgen
from ..instances import InternalInstance
from ..typing.apps import AppKind

class MySQLServer():
    """MySQL Server"""

    def __init__(self, instance: InternalInstance):
        self._instance = instance
        self._cnx = None

    @property
    def cnx(self) -> MySQLConnection:
        """MySQL Server Connection"""
        return self._cnx

    def __enter__(self):
        self._cnx = mysql.connector.connect(
            host=self._instance.host,
            port=self._instance.port,
            user=self._instance.user,
            password=self._instance.get_mysql_pwd(),
            ssl_disabled=not self._instance.ssl
        )
        return self

    def __exit__(self, type, value, traceback): # pylint: disable=redefined-builtin
        self._cnx.close()
        self._cnx = None

    @classmethod
    def _uid_as_a_user(cls, uid: str) -> str:
        return uid[:31] # limited to 32 chars in MySQL <=8.0

    def register_application(self, uid: str, kapp: AppKind) -> dict:
        """Register/Update an application"""

        user = self._uid_as_a_user(uid)
        database = f"{kapp.metadata.namespace}-db"
        pwd = pwgen(pw_length=32, num_pw=1, no_symbols=True)

        cursor = self.cnx.cursor()

        # Create DB
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8 COLLATE utf8_unicode_ci"
        )

        # Create USER
        cursor.execute(
            f"CREATE USER '{user}'@'%' IDENTIFIED BY '{pwd}'"
        )

        # GRANT
        cursor.execute(
            f"GRANT ALL ON `{database}`.* TO '{user}'@'%'"
        )
        cursor.execute("FLUSH PRIVILEGES")
        cursor.close()

        return {
            "username": user,
            "password": pwd,
            "url": "jdbc:mysql://{host}:{port}/{database}{options}".format( # pylint: disable=consider-using-f-string
                host=self._instance.host,
                port=self._instance.port,
                database=database,
                options="" if not self._instance.ssl else "?useSSL=true&requireSSL=true"
            )
        }

    def unregister_application(self, uid: str):
        """Unregister an application"""

        user = self._uid_as_a_user(uid)

        cursor = self.cnx.cursor()
        cursor.execute(
            f"DROP USER IF EXISTS '{user}'@'%'"
        )
        cursor.execute("FLUSH PRIVILEGES")
        cursor.close()
