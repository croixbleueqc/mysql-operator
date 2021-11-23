"""
Manages App Kind
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

import base64
import kopf
import kubernetes
import yaml
from . import settings
from .typing.apps import AppKind
from .mysql.mysqlserver import MySQLServer
from .instances import instance_from_index
from .utils.checks import admission_error_immutable

APPS='apps'

def base64encode(value: str) -> str:
    """Encode string in base64"""
    return base64.b64encode(value.encode(encoding='UTF-8')).decode(encoding='UTF-8')

@kopf.on.create(settings.GROUP, settings.LATEST_VERSION, APPS, timeout=settings.DEFAULT_TIMEOUT)
def app_register(instances_idx: kopf.Index, body: kopf.Body, patch: kopf.Patch, **_):
    """
    Register an application
    """
    patch.status[settings.STATUS_SUCCESS] = False

    kapp: AppKind = AppKind.parse_obj(body)
    mysql_instance = instance_from_index(instances_idx, kapp.spec.instance)

    with MySQLServer(mysql_instance) as mysql:
        credentials = mysql.register_application(body.meta["uid"], kapp)

    # Create binding secret on the right namespace
    with kubernetes.client.ApiClient() as api_client:
        api: kubernetes.client.CoreV1Api = kubernetes.client.CoreV1Api(api_client)
        content = settings.BINDING.format(
            name=kapp.metadata.name,
            username=base64encode(credentials['username']),
            password=base64encode(credentials['password']),
            url=base64encode(credentials['url'])
        )
        data = yaml.safe_load(content)

        kopf.adopt(data) # Cascade deletion

        api.create_namespaced_secret(kapp.metadata.namespace, data)

    # Status
    patch.status[settings.STATUS_SUCCESS] = True

    return {"secretName": kapp.metadata.name}

@kopf.on.delete(settings.GROUP, settings.LATEST_VERSION, APPS, timeout=settings.DEFAULT_TIMEOUT)
def app_unregister(instances_idx: kopf.Index, body: kopf.Body, **_):
    """
    Unregister an application
    """
    kapp: AppKind = AppKind.parse_obj(body)
    mysql_instance = instance_from_index(instances_idx, kapp.spec.instance)

    with MySQLServer(mysql_instance) as mysql:
        mysql.unregister_application(body.meta["uid"])

@kopf.on.validate(settings.GROUP, settings.LATEST_VERSION, APPS)
def appadmission(body: kopf.Body, **_):
    """
    App Admission

    instance and description are immutables
    """
    if body.meta["generation"] == 1:
        return

    # previous version already exist. Checking immutable fields

    knew: AppKind = AppKind.parse_obj(body)

    with kubernetes.client.ApiClient() as api_client:
        api: kubernetes.client.CustomObjectsApi = kubernetes.client.CustomObjectsApi(api_client)
        response = api.get_namespaced_custom_object(
            settings.GROUP,
            settings.LATEST_VERSION,
            knew.metadata.namespace,
            APPS,
            knew.metadata.name
        )

    kcurrent: AppKind = AppKind.parse_obj(response)

    if kcurrent.spec.instance != knew.spec.instance:
        raise admission_error_immutable(".spec.instance")
