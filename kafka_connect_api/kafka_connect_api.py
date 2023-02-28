# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2022 John Mille <john@compose-x.io>

"""Main module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests import Response

import re

from requests import delete, get, post, put
from requests.auth import HTTPBasicAuth

from .errors import evaluate_api_return

LOG_LEVELS = ["INFO", "DEBUG", "TRACE", "WARN", "ERROR", "CRITICAL"]


class Task:
    """
    Class to represent a Connector Task
    """

    def __init__(self, connector: Connector, task_id: int, task_config: dict):
        """
        Initializes the Task for a given connector
        """
        self.id = task_id
        self._connector = connector
        self.config = task_config

    def __repr__(self):
        return f"{self._connector.name}.{self.id}"

    @property
    def api(self) -> Api:
        return self._connector.api

    @property
    def connector(self) -> Connector:
        return self._connector

    @property
    def status(self):
        _query = self.api.get(
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
        _query = self.api.post_raw(
            f"/connectors/{self._connector.name}/tasks/{self.id}/restart"
        )


class Connector:
    """
    Class to represent a Connector.

    Configuration & Tasks are retrieved live from the connect cluster, never cached, to ensure there is no
    conflict or out of date settings.
    """

    def __init__(self, cluster: Cluster, name: str):
        self._cluster = cluster
        self.name = name

    @property
    def api(self) -> Api:
        return self._cluster.api

    @property
    def cluster(self) -> Cluster:
        return self._cluster

    @property
    def connector_class(self) -> str:
        return self.config["connector.class"]

    def __repr__(self):
        return self.name

    def exists(self) -> bool:
        req = self.api.get_raw(f"/connectors/{self.name}/")
        if req.status_code == 404:
            return False
        return True

    def restart(self) -> None:
        self.api.post(f"/connectors/{self.name}/restart")

    def pause(self) -> None:
        self.api.put_raw(f"/connectors/{self.name}/pause")

    def resume(self) -> None:
        self.api.put_raw(f"/connectors/{self.name}/resume")

    def restart_all_tasks(self) -> None:
        for _task in self.tasks:
            _task.restart()

    def delete(self) -> None:
        self.api.delete_raw(f"/connectors/{self.name}")

    def cycle_connector(self) -> None:
        self.pause()
        self.restart_all_tasks()
        self.resume()

    @property
    def status(self) -> dict:
        return self.api.get(f"/connectors/{self.name}/status")

    @property
    def state(self):
        return self.status["connector"]["state"]

    @property
    def config(self):
        _config = self.api.get(f"/connectors/{self.name}")
        return _config["config"]

    @config.setter
    def config(self, config: dict) -> None:
        if not isinstance(config, dict):
            raise TypeError(
                self.name,
                "connect configuration must be a dictionary/mapping. Got",
                type(config),
            )
        _req = self.api.put_raw(f"/connectors/{self.name}/config", json=config)
        if not (199 < _req.status_code < 300):
            print(_req.text)

    @property
    def tasks(self):
        _tasks = []
        _connector_tasks = self.api.get(f"/connectors/{self.name}/tasks")
        for _task in _connector_tasks:
            _tasks.append(
                Task(
                    self,
                    task_id=int(_task["id"]["task"]),
                    task_config=_task["config"],
                )
            )
        return _tasks


class Cluster:

    """
    Class to represent the cluster at the top level.

    Configurations & Connectors are retrieved "live" from the API, not stored in memory,
    to avoid conflicts/out of date settings.
    """

    def __init__(self, api: Api):
        self._api = api

    def get(self):
        return self._api.get("/")

    @property
    def api(self) -> Api:
        return self._api

    @property
    def version(self):
        return self.get()["version"]

    @property
    def kafka_cluster(self) -> str:
        return self.get()["kafka_cluster_id"]

    @property
    def connectors(self) -> dict:
        _connectors = self._api.get("/connectors")
        _cluster_connectors: dict = {}
        for connector in _connectors:
            _cluster_connectors[connector] = Connector(self, connector)
        return _cluster_connectors

    @property
    def loggers(self) -> dict:
        return self._api.get("/admin/loggers")

    @property
    def root_logger(self):
        return self.loggers["root"]

    @root_logger.setter
    def root_logger(self, log_level: str) -> None:
        if log_level not in LOG_LEVELS:
            raise ValueError(log_level, "not valid. Must be one of", LOG_LEVELS)
        self._api.put("/admin/loggers/root", json={"level": log_level})

    def set_logger_log_level(self, logger_name: str, log_level: str) -> dict:
        if log_level not in LOG_LEVELS:
            raise ValueError(log_level, "not valid. Must be one of", LOG_LEVELS)
        if logger_name not in self.loggers.keys():
            raise ValueError(
                logger_name,
                "Logger not found on the cluster. Valid loggers",
                list(self.loggers.keys()),
            )
        return self._api.put(f"/admin/loggers/{logger_name}", json={"level": log_level})

    def __repr__(self):
        return f"{self._api.url} - {self.version} - {self.kafka_cluster}"


class Api:
    """
    API Calls handler. Used by the Connect cluster to wrap connect API calls.
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
        if (self.port < 0) or (self.port > (2**16)):
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

    @evaluate_api_return
    def get_raw(self, query_path, **kwargs) -> Response:
        if not query_path.startswith(r"/"):
            query_path = f"/{query_path}"
        url = f"{self.url}{query_path}"
        req = get(
            url, auth=self.auth, headers=self.headers, verify=self.verify_ssl, **kwargs
        )
        return req

    def get(self, query_path):
        req = self.get_raw(query_path)
        return req.json()

    @evaluate_api_return
    def post_raw(self, query_path, **kwargs) -> Response:
        if not query_path.startswith(r"/"):
            query_path = f"/{query_path}"
        url = f"{self.url}{query_path}"
        req = post(
            url,
            auth=self.auth,
            headers=self.headers,
            verify=self.verify_ssl,
            **kwargs,
        )
        return req

    def post(self, query_path, **kwargs):
        req = self.post_raw(query_path, **kwargs)
        return req.json()

    @evaluate_api_return
    def put_raw(self, query_path, **kwargs) -> Response:
        if not query_path.startswith(r"/"):
            query_path = f"/{query_path}"
        url = f"{self.url}{query_path}"
        req = put(
            url,
            auth=self.auth,
            headers=self.headers,
            verify=self.verify_ssl,
            **kwargs,
        )
        return req

    def put(self, query_path, **kwargs):
        req = self.put_raw(query_path, **kwargs)
        return req.json()

    @evaluate_api_return
    def delete_raw(self, query_path, **kwargs) -> Response:
        if not query_path.startswith(r"/"):
            query_path = f"/{query_path}"
        url = f"{self.url}{query_path}"
        req = delete(
            url, auth=self.auth, headers=self.headers, verify=self.verify_ssl, **kwargs
        )
        return req

    def delete(self, query_path):
        req = self.delete_raw(query_path)
        return req.json()
