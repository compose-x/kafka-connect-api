#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2022 John Mille <john@compose-x.io>

from requests import exceptions as req_exceptions

from .tools import KEYISSET


class ConnectGenericException(Exception):
    """
    Generic class handling Exceptions
    """

    def __init__(self, msg, code, details):
        """

        :param msg:
        :param code:
        :param details:
        """
        super().__init__(msg, code, details)
        self.code = code
        self.details = details


class GenericNotFound(ConnectGenericException):
    """
    Generic option for 404 return code
    """

    def __init__(self, code, details):
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            super().__init__(details, code, details[1:])


class GenericConflict(ConnectGenericException):
    """
    Generic option for 409 return code
    """

    def __init__(self, code, details):
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            super().__init__(details, code, details[1:])


class GenericUnauthorized(ConnectGenericException):
    """
    Generic option for 401 return code
    """

    def __init__(self, code, details):
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            super().__init__(details, code, details[1:])


class GenericForbidden(ConnectGenericException):
    """
    Generic exception for a 403
    """

    def __init__(self, code, details):
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            super().__init__(details, code, details[1:])


class ConnectApiException(ConnectGenericException):
    """
    Top class for DatabaseUser exceptions
    """

    def __init__(self, code, details):
        if code == 409:
            raise GenericConflict(code, details)
        elif code == 404:
            raise GenericNotFound(code, details)
        elif code == 401:
            raise GenericUnauthorized(code, details)
        elif code == 403:
            raise GenericForbidden(code, details)
        super().__init__(details[0], code, details[1])


def evaluate_api_return(function):
    """
    Decorator to evaluate the requests payload returned
    """

    def wrapped_answer(*args, **kwargs):
        """
        Decorator wrapper
        """
        try:
            payload = function(*args, **kwargs)
            if payload.status_code not in [200, 201, 202, 204] and not KEYISSET(
                "ignore_failure", kwargs
            ):
                try:
                    details = (args[0:2], payload.json())
                except req_exceptions.JSONDecodeError:
                    details = (args[0:2], payload.text)
                raise ConnectApiException(payload.status_code, details)

            elif KEYISSET("ignore_failure", kwargs):
                return payload
            return payload
        except req_exceptions.RequestException as error:
            print(error)
            raise

    return wrapped_answer
