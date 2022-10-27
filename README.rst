========================
Apache Kafka Connect API
========================

|PYPI_VERSION| |PYPI_LICENSE|

|CODE_STYLE| |TDD| |BDD|

|DOCS_BUILD|


Python Kafka Connect API client


* Free software: MPL2.0
* Documentation: https://kafka-connect-api.readthedocs.io.


Features
--------

Allows you to interact with the Kafka Connect API (`API Reference`_) in a simple way.

* Connection to cluster (supports Basic Auth)
* List all connectors in the cluster
* Describe the connector configuration
* Update the connector configuration
* Pause / Resume Connector
* Restart all tasks for the connector


.. _API Reference: https://docs.confluent.io/platform/current/connect/references/restapi.html

.. |DOCS_BUILD| image:: https://readthedocs.org/projects/kafka-connect-api/badge/?version=latest
        :target: https://kafka-connect-api.readthedocs.io/en/latest/
        :alt: Documentation Status

.. |PYPI_VERSION| image:: https://img.shields.io/pypi/v/kafka-connect-api.svg
        :target: https://pypi.python.org/pypi/kafka_connect_api

.. |PYPI_LICENSE| image:: https://img.shields.io/pypi/l/kafka-connect-api
    :alt: PyPI - License
    :target: https://github.com/compose-x/kafka-connect-api/blob/master/LICENSE

.. |PYPI_PYVERS| image:: https://img.shields.io/pypi/pyversions/kafka-connect-api
    :alt: PyPI - Python Version
    :target: https://pypi.python.org/pypi/kafka-connect-api

.. |PYPI_WHEEL| image:: https://img.shields.io/pypi/wheel/kafka-connect-api
    :alt: PyPI - Wheel
    :target: https://pypi.python.org/pypi/kafka-connect-api

.. |CODE_STYLE| image:: https://img.shields.io/badge/codestyle-black-black
    :alt: CodeStyle
    :target: https://pypi.org/project/black/

.. |TDD| image:: https://img.shields.io/badge/tdd-pytest-black
    :alt: TDD with pytest
    :target: https://docs.pytest.org/en/latest/contents.html

.. |BDD| image:: https://img.shields.io/badge/bdd-behave-black
    :alt: BDD with Behave
    :target: https://behave.readthedocs.io/en/latest/

.. |QUALITY| image:: https://sonarcloud.io/api/project_badges/measure?project=compose-x_kafka-connect-api&metric=alert_status
    :alt: Code scan with SonarCloud
    :target: https://sonarcloud.io/dashboard?id=compose-x_kafka-connect-api

.. |PY_DLS| image:: https://img.shields.io/pypi/dm/kafka-connect-api
    :target: https://pypi.org/project/kafka-connect-api/
