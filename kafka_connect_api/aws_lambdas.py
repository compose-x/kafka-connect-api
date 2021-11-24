#   -*- coding: utf-8 -*-
#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2021 John Mille <john@compose-x.io>


"""
Module with functions that can be used as AWS Lambda Handlers to perform various tasks
"""

from os import environ

from jsonschema import validate

from .kafka_connect_api import Api, Cluster, Connector

KEYISSET = lambda x, y: isinstance(y, dict) and x in y.keys() and y[x]

CLUSTER_CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "kafka-connect-cluster-lambda-config",
    "type": "object",
    "title": "kafka-connect-cluster-lambda-config",
    "description": "Schema of the event payload expected to interact with the Lambda Function",
    "required": ["hostname"],
    "properties": {
        "hostname": {"type": "string", "format": "idn-hostname"},
        "port": {"type": "number", "default": 8083},
        "username": {"type": "string"},
        "password": {"type": "string"},
        "protocol": {"type": "string", "default": "http"},
        "ignore_ssl_errors": {"type": "bool", "default": False},
    },
}

CONNECTOR_CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "kafka-connect-connector-lambda-config",
    "type": "object",
    "title": "kafka-connect-connector-lambda-config",
    "description": "Schema of the event configuration required for a connector",
    "required": ["name"],
    "properties": {
        "name": {
            "type": "string",
        },
        "config": {"type": "object"},
    },
}


def config_from_env_vars():
    """
    Sets the config from environment variables
    :return: the cluster configuration
    :rtype: dict
    """
    if environ.get("CONNECT_CLUSTER_HOSTNAME", None) is None:
        raise LookupError("CONNECT_CLUSTER_HOSTNAME is not set.")
    return {
        "hostname": environ.get("CONNECT_CLUSTER_HOSTNAME", None),
        "port": int(environ.get("CONNECT_CLUSTER_PORT", 8083)),
        "username": environ.get("CONNECT_CLUSTER_BASIC_AUTH_USERNAME", None),
        "password": environ.get("CONNECT_CLUSTER_BASIC_AUTH_PASSWORD", None),
        "protocol": environ.get("CONNECT_CLUSTER_PROTOCOL", "http"),
        "ignore_ssl_errors": environ.get("CONNECT_CLUSTER_IGNORE_SSL_ERRORS", False),
    }


def config_from_event(event):
    """
    Validates the cluster configuration against schema if passed in event

    :param dict event:
    :return: The connect cluster configuration
    :rtype: dict
    """
    if not KEYISSET("cluster", event):
        return None
    cluster_config = event["cluster"]
    validate(cluster_config, CLUSTER_CONFIG_SCHEMA)
    return cluster_config


def set_cluster_config(event):
    """
    Function to set the connect cluster settings

    :param dict event:
    :return: The cluster config
    :rtype: dict
    """
    cluster_config = config_from_event(event)
    if not cluster_config:
        cluster_config = config_from_env_vars()
    if not cluster_config:
        raise ValueError("No connect cluster configuration was given.")
    return cluster_config


def get_connector(event):
    """
    Function to retrieve the one connector in the connect cluster from event

    :param dict event:
    :return: the connector
    :rtype: Connector
    """
    connector_config = event["connector"]
    validate(connector_config, CONNECTOR_CONFIG_SCHEMA)
    name = connector_config["name"]
    cluster_config = set_cluster_config(event)
    api = Api(**cluster_config)
    cluster = Cluster(api)
    if name not in cluster.connectors:
        raise KeyError(f"Connector {name} is not present in cluster {cluster}")
    return cluster.connectors[name]


def restart_all_connectors(event, context):
    """
    Function to restart all the connectors in a Connect cluster

    :param dict event:
    :param dict context:
    """
    cluster_config = set_cluster_config(event)
    api = Api(**cluster_config)
    cluster = Cluster(api)
    print(cluster)
    for connector in cluster.connectors.values():
        connector.cycle_connector()


def create_update_connector(event, context):
    """
    Function to create / update a new connector

    :param dict event:
    :param dict context:
    """
    if not KEYISSET("connector", event):
        raise KeyError("No configuration given for the connector to set/update")
    connector_config = event["connector"]
    validate(connector_config, CONNECTOR_CONFIG_SCHEMA)
    name = connector_config["name"]
    if not KEYISSET("config", connector_config):
        raise KeyError(
            f"The connector {name} has no configuration passed in event for create/update"
        )
    cluster_config = set_cluster_config(event)
    api = Api(**cluster_config)
    cluster = Cluster(api)
    connector = Connector(api, name)
    connector.config = connector_config["config"]
    if name not in cluster.connectors:
        raise Exception(f"Failed to create connector {name}")


def delete_connector(event, context):
    """
    Function to delete a connector. No need for config

    :param dict event:
    :param dict context:
    """
    connector = get_connector(event)
    connector.delete()


def restart_connector(event, context):
    """
    Function to delete a connector. No need for config

    :param dict event:
    :param dict context:
    """
    connector = get_connector(event)
    connector.cycle_connector()


def check_connector_health(event, context):
    """
    Function to evaluate the connector health

    :param dict event:
    :param dict context:
    :return:
    """
    connector = get_connector(event)
    tasks_health = [task.is_running() for task in connector.tasks]
    if all(tasks_health):
        return True
    return False
