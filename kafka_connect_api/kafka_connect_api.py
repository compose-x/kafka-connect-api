# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2022 John Mille <john@compose-x.io>

"""Main module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

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
        hostname: str = None,
        port: int = None,
        url: str = None,
        protocol: str = None,
        ignore_ssl_errors: bool = False,
        username: str = None,
        password: str = None,
    ):
        """

        :param str hostname:
        :param int port: The endpoint port
        :param str protocol: http or https
        :param bool ignore_ssl_errors: Ignore SSL errors, for self-signed endpoints. Use at own risks
        :param str username: Username used for basic auth
        :param str password: Password used for basic auth
        """
        if (username and not password) or (password and not username):
            raise ValueError("You must specify both username and password")
        self.username = username
        self.password = password
        self.hostname = hostname

        self._url = None
        self._port = None
        self._protocol = "http"
        self._ignore_ssl_errors = ignore_ssl_errors

        self.protocol = protocol
        self.port = port
        self.url = url
        self.headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }

    def __repr__(self):
        return self.url

    @property
    def verify_ssl(self) -> bool:
        if not self._ignore_ssl_errors and self.protocol == "http":
            return False
        return not self._ignore_ssl_errors

    @property
    def basic_auth(self) -> Union[HTTPBasicAuth, None]:
        """Returns basic auth information. If both the username and password are not set, raises AttributeError"""
        if self.username and self.password:
            return HTTPBasicAuth(self.username, self.password)
        if (self.username and not self.password) or (
            self.password and not self.username
        ):
            raise AttributeError("You must specify both username and password")
        return None

    @property
    def url(self) -> str:
        if self._url:
            return self._url
        elif self.hostname:
            if (self.port == 80 and self.protocol == "http") or (
                self.port == 443 and self.protocol == "https"
            ):
                return f"{self.protocol}://{self.hostname}"
            else:
                return f"{self.protocol}://{self.hostname}:{self.port}"
        else:
            raise AttributeError(
                "Unable to form a URL", self._url, self.hostname, self.port
            )

    @url.setter
    def url(self, value: Union[str, None]):
        if value is None:
            return
        if re.match(r"^https://(.*)$", value):
            self.protocol = "https"
        elif not re.match(r"(http://|https://)", value):
            print(f"URL Does not contain a protocol. Using default {self.protocol}")
            value = f"{self.protocol}://{value}"
        self._url = value

    @property
    def protocol(self) -> str:
        if self._protocol:
            return self._protocol
        return "http"

    @protocol.setter
    def protocol(self, value: Union[str, None]) -> None:
        if value is None:
            return
        valid_values: list = ["http", "https", "HTTP", "HTTPS"]
        if value not in valid_values:
            raise ValueError("protocol must be one of", valid_values, "got", value)
        self._protocol = value.lower()

    @property
    def port(self) -> int:
        if self._port:
            return self._port
        return 80

    @port.setter
    def port(self, value: Union[int, None]) -> None:
        if value is None and self.protocol == "http":
            value = 80
        elif value is None and self.protocol == "https":
            value = 443
        elif isinstance(value, str):
            value = int(value)

        if (value < 0) or (value > (2**16)):
            raise ValueError(
                f"Port {self.port} is not valid. Must be between 0 and {((2 ** 16) - 1)}"
            )
        self._port = value

    @evaluate_api_return
    def get_raw(self, query_path, **kwargs) -> Response:
        if not query_path.startswith(r"/"):
            query_path = f"/{query_path}"
        url = f"{self.url}{query_path}"
        req = get(
            url,
            auth=self.basic_auth,
            headers=self.headers,
            verify=self.verify_ssl,
            **kwargs,
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
            auth=self.basic_auth,
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
            auth=self.basic_auth,
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
            url,
            auth=self.basic_auth,
            headers=self.headers,
            verify=self.verify_ssl,
            **kwargs,
        )
        return req

    def delete(self, query_path):
        req = self.delete_raw(query_path)
        return req.json()
