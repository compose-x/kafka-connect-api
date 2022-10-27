
.. meta::
    :description: Kafka Connect API
    :keywords: Kafka, Connect, Python, SDK

##########################################
Kafka Connect API
##########################################

|PYPI_VERSION| |PYPI_LICENSE|

|CODE_STYLE| |TDD| |BDD|


Install
========

On your system
---------------

.. code-block::

    pip install kafka-connect-api

For your local user
--------------------

.. code-block::

    pip install kafka-connect-api --user

In a virtual environment
-------------------------

.. code-block::

    python3 -m venv venv
    source venv/bin/activate
    pip install pip -U;
    pip install kafka-conect-api



.. |DOCS_BUILD| image:: https://readthedocs.org/projects/ecs-composex/badge/?version=latest
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

    modules
    contributing

.. toctree::
    :titlesonly:
    :caption: Additional content

    changelog

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. meta::
    :description: ECS Compose-X
    :keywords: AWS, AWS ECS, Docker, Containers, Compose, docker-compose


Credits
=======

This package would not have been possible without the amazing job done by the AWS CloudFormation team!
This package would not have been possible without the amazing community around `Troposphere`_!
This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`Mark Peek`: https://github.com/markpeek
.. _`AWS ECS CLI`: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI.html
.. _Troposphere: https://github.com/cloudtools/troposphere
.. _Blog: https://blog.compose-x.io/
.. _Docker Compose: https://docs.docker.com/compose/
.. _ECS Compose-X: https://github.com/compose-x/ecs_composex
.. _YAML Specifications: https://yaml.org/spec/
.. _Extensions fields:  https://docs.docker.com/compose/compose-file/#extension-fields
.. _ECS Compose-X Project: https://github.com/orgs/lambda-my-aws/projects/3
.. _CICD Pipeline for multiple services on AWS ECS with ECS Compose-X: https://blog.ecs-composex.lambda-my-aws.io/posts/cicd-pipeline-for-multiple-services-on-aws-ecs-with-ecs-composex/
.. _the compatibilty matrix: https://nightly.docs.compose-x.io/compatibility/docker_compose.html
.. _Find out how to use ECS Compose-X in AWS here: https://blog.compose-x.io/posts/use-your-docker-compose-files-as-a-cloudformation-template/index.html
