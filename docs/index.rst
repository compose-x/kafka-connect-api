
.. meta::
    :description: Kafka Connect API
    :keywords: Kafka, Connect, Python, SDK

##########################################
Kafka Connect API Client for Python
##########################################

|PYPI_VERSION| |PYPI_LICENSE|

|CODE_STYLE| |TDD| |BDD|

Install
========

.. code-block::

    pip install kafka-connect-api

Usage
======

.. code-block:: python

    from kafka_connect_api.kafka_connect_api import Api, Cluster

    api = Api(connect.cluster, port=8083)
    cluster = Cluster(api)
    print(cluster.connectors)



.. |DOCS_BUILD| image:: https://readthedocs.org/projects/kafka-connect-api/badge/?version=latest
        :target: https://kafka-connect-api.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. |PYPI_VERSION| image:: https://img.shields.io/pypi/v/kafka-connect-api.svg
        :target: https://pypi.python.org/pypi/kafka_connect_api

.. |PYPI_DL| image:: https://img.shields.io/pypi/dm/kafka-connect-api
    :alt: PyPI - Downloads
    :target: https://pypi.python.org/pypi/ecs_composex

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


.. toctree::
    :titlesonly:
    :maxdepth: 1
    :caption: Modules and Source Code

    install
    contributing
    modules

.. toctree::
    :titlesonly:
    :caption: Additional content

    changelog

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _Blog: https://blog.compose-x.io/
.. _ECS Compose-X: https://github.com/compose-x/ecs_composex
