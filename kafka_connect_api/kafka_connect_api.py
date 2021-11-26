#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille <john@compose-x.io>

"""Main module."""
import re

import requests
from requests.auth import HTTPBasicAuth


class Task(object):
    """
    Class to represent a Connector Task
    """

    def __init__(self, api, connector, task_id, task_config):
        """

        :param Api api:
        :param Connector connector:
        :param int task_id:
        """
        self.id = task_id
        self._connector = connector
        self._api = api
        self.config = task_config

    def __repr__(self):
        return f"{self._connector.name}.{self.id}"

    @property
    def status(self):
        _query = self._api.get(
            f"/connectors/{self._connector.name}/tasks/{self.id}/status"
        )
        return _query

    @property
    def state(self):
        return self.status["state"]

    def is_running(self):
        if self.state == "RUNNING":
            return True
        return False

    def restart(self):
        _query = self._api.post_raw(
            f"/connectors/{self._connector.name}/tasks/{self.id}/restart"
        )


class Connector(object):
    """
    Class to represent a Connector
    """

    def __init__(self, api, name, config=None):
        """

        :param Api api:
        :param str name:
        :param dict config:
        """
        self._api = api
        self.name = name

    def __repr__(self):
        return self.name

    def exists(self):
        req = self._api.get_raw(f"/connectors/{self.name}/")
        if req.status_code == 404:
            return False
        return True

    def restart(self):
        self._api.post(f"/connectors/{self.name}/restart")

    def pause(self):
        self._api.put_raw(f"/connectors/{self.name}/pause")

    def resume(self):
        self._api.put_raw(f"/connectors/{self.name}/resume")

    def restart_all_tasks(self):
        for _task in self.tasks:
            _task.restart()

    def delete(self):
        self._api.delete_raw(f"/connectors/{self.name}")

    def cycle_connector(self):
        self.pause()
        self.restart_all_tasks()
        self.resume()

    @property
    def state(self):
        return self.status()["connector"]["state"]

    @property
    def config(self):
        _config = self._api.get(f"/connectors/{self.name}")
        return _config["config"]

    @config.setter
    def config(self, config):
        self._api.put(f"/connectors/{self.name}/config", data=config)

    @property
    def status(self):
        return self._api.get(f"/connectors/{self.name}/status")

    @property
    def tasks(self):
        _tasks = []
        _connector_tasks = self._api.get(f"/connectors/{self.name}/tasks")
        for _task in _connector_tasks:
            _tasks.append(
                Task(
                    self._api,
                    self,
                    task_id=int(_task["id"]["task"]),
                    task_config=_task["config"],
                )
            )
        return _tasks


class Cluster(object):
    def __init__(self, api):
        self._api = api

    def get(self):
        return self._api.get("/")

    @property
    def version(self):
        return self.get()["version"]

    @property
    def kafka_cluster(self):
        return self.get()["kafka_cluster_id"]

    @property
    def connectors(self):
        _connectors = self._api.get("/connectors")
        _cluster_connectors = {}
        for connector in _connectors:
            _cluster_connectors[connector] = Connector(self._api, connector)
        return _cluster_connectors

    def __repr__(self):
        return f"{self._api.url} - {self.version} - {self.kafka_cluster}"


class Api(object):
    """
    Class to represent the Connect cluster
    """

    def __init__(
        self,
        hostname,
        port=None,
        url=None,
        protocol=None,
        ignore_ssl_errors=False,
        username=None,
        password=None,
    ):
        """

        :param str hostname:
        :param int port:
        :param str protocol:
        :param bool ignore_ssl_errors:
        :param str username:
        :param str password:
        """
        self.hostname = hostname
        self.protocol = protocol if protocol else "http"
        self.verify_ssl = not ignore_ssl_errors
        self.port = port if port else 8083
        self.username = username
        self.password = password

        if self.protocol not in ["http", "https"]:
            raise ValueError("protocol must be one of", ["http", "https"])
        if (self.port < 0) or (self.port > (2 ** 16)):
            raise ValueError(
                f"Port {self.port} is not valid. Must be between 0 and {((2 ** 16) - 1)}"
            )
        if self.username and not self.password or self.password and not self.username:
            raise ValueError("You must specify both username and password")
        if self.verify_ssl is True and self.protocol == "http":
            print("No SSL needed for HTTP without TLS. Disabling")
            self.verify_ssl = False
        if url:
            self.url = url
            if not re.match(r"(http://|https://)", self.url):
                print(f"URL Does not contain a protocol. Using default {self.protocol}")
                self.url = f"{self.protocol}://{self.url}"
            print("URL Defined from parameter. Skipping hostname:port parameters")
        elif (self.port == 80 and protocol == "http") or (
            self.port == 443 and self.protocol == "https"
        ):
            self.url = f"{self.protocol}://{self.hostname}"
        else:
            self.url = f"{self.protocol}://{self.hostname}:{self.port}"

        self.auth = (
            HTTPBasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )

        self.headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }

    def __repr__(self):
        return self.url

    def get_raw(self, query_path, **kwargs):
        if not query_path.startswith(r"/"):
            query_path = f"/{query_path}"
        url = f"{self.url}{query_path}"
        req = requests.get(
            url, auth=self.auth, headers=self.headers, verify=self.verify_ssl, **kwargs
        )
        return req

    def get(self, query_path):
        req = self.get_raw(query_path)
        return req.json()

    def post_raw(self, query_path, data=None, **kwargs):
        if not query_path.startswith(r"/"):
            query_path = f"/{query_path}"
        url = f"{self.url}{query_path}"
        req = requests.post(
            url,
            auth=self.auth,
            headers=self.headers,
            data=data,
            verify=self.verify_ssl,
            **kwargs,
        )
        return req

    def post(self, query_path, data=None):
        req = self.post_raw(query_path, data)
        return req.json()

    def put_raw(self, query_path, data=None, **kwargs):
        if not query_path.startswith(r"/"):
            query_path = f"/{query_path}"
        url = f"{self.url}{query_path}"
        req = requests.put(
            url,
            auth=self.auth,
            headers=self.headers,
            data=data,
            verify=self.verify_ssl,
            **kwargs,
        )
        return req

    def put(self, query_path, data=None, **kwargs):
        req = self.put_raw(query_path, data)
        return req.json()

    def delete_raw(self, query_path, **kwargs):
        if not query_path.startswith(r"/"):
            query_path = f"/{query_path}"
        url = f"{self.url}{query_path}"
        req = requests.delete(
            url, auth=self.auth, headers=self.headers, verify=self.verify_ssl, **kwargs
        )
        return req

    def delete(self, query_path):
        req = self.delete_raw(query_path)
        return req.json()
