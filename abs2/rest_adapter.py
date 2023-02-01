import logging
from json import JSONDecodeError
from typing import Dict

import requests
import requests.packages

from .exceptions import ABS2Exception
from .models import Result


class RestAdapter:
    def __init__(
        self,
        hostname: str = "qubosolver.cs.hiroshima-u.ac.jp",
        api_key: str = "",
        ver: str = "v1",
        ssl_verify: bool = True,
        logger: logging.Logger = None,
    ):
        """
        Constructor for RestAdapter
        :param hostname: URL without "https://"
        :param api_key: (optional) string used for authentication when using POST / DELETE
        :param ver: version number of the API, standard v1
        :param ssl_verify: Normally set to true, can be set to false when facing issues with SSL/TLS cert
        :param logger: (optional) accepts preexisting logger
        """

        self._logger = logger or logging.getLogger(__name__)
        self.url = "https://{}/{}/".format(hostname, ver)
        self._api_key = api_key
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()  # type: ignore

    def _do(
        self,
        http_method: str,
        endpoint: str,
        ep_params: Dict = None,
        data: Dict = None,
        additional_headers=None,
    ):
        """
        Generic method to send requests to the API
        :param http_method: POST / GET / DELETE
        :param endpoint: Endpoint of the API on which the http_method should be executed
        :param ep_params: (optional) Dictionary, list of tuples or bytes to send
        in the query string
        :param data: (optional) A JSON serializable Python object to send in the body
        :return:
        """
        if additional_headers is None:
            additional_headers = {}
        full_url = self.url + endpoint
        headers = {"x-api-key": self._api_key, "Content-Type": "application/json"}
        headers = {**headers, **additional_headers}
        log_line_pre = f"method={http_method}, url={full_url}, params={ep_params}"
        log_line_post = ", ".join(
            (log_line_pre, "success={}, status_code={}, message={}")
        )
        # Log HTTP params and perform an HTTP request, catching and re-raising any exceptions
        try:
            self._logger.debug(msg=log_line_pre)
            response = requests.request(
                method=http_method,
                url=full_url,
                verify=self._ssl_verify,
                headers=headers,
                params=ep_params,
                json=data,
            )
        except requests.exceptions.RequestException as e:
            self._logger.error(msg=(str(e)))
            raise ABS2Exception("Request failed") from e
        # Deserialize JSON output to Python object, or return failed Result on exception
        try:
            data_out = response.json()
        except (ValueError, JSONDecodeError) as e:
            self._logger.error(msg=log_line_post.format(False, None, e))
            raise ABS2Exception("Bad JSON in response") from e
        # Test for 299 before 200 because response codes > 299 are more common
        # If status_code in 200-299 range, return success Result with data, otherwise raise exception
        is_success = 299 >= response.status_code >= 200  # OK
        log_line = log_line_post.format(
            is_success, response.status_code, response.reason
        )
        if is_success:
            self._logger.debug(msg=log_line)
            return Result(response.status_code, message=response.reason, data=data_out)
        self._logger.error(msg=log_line)
        raise ABS2Exception(f"{response.status_code}: {response.reason}")

    def get(
        self, endpoint: str, ep_params: Dict = None, additional_headers: Dict = None
    ) -> Result:
        """
        Generic GET method for a given Endpoint
        :param additional_headers: additional headers for e.g. a bearer token
        :param endpoint: Endpoint of the API on which the GET should be executed
        :param ep_params: (optional) Dictionary, list of tuples or bytes to send
        in the query string
        :return:
        """
        return self._do(
            http_method="GET",
            endpoint=endpoint,
            ep_params=ep_params,
            additional_headers=additional_headers,
        )

    def post(
        self,
        endpoint: str,
        ep_params: Dict = None,
        data: Dict = None,
        additional_headers: Dict = None,
    ) -> Result:
        """
        Generic POST method for a given Endpoint
        :param additional_headers: additional headers for e.g. a bearer token
        :param endpoint: Endpoint of the API on which the POST should be executed
        :param ep_params: (optional) Dictionary, list of tuples or bytes to send
        in the query string
        :param data: (optional) A JSON serializable Python object to send in the body
        :return:
        """
        return self._do(
            http_method="POST",
            endpoint=endpoint,
            ep_params=ep_params,
            data=data,
            additional_headers=additional_headers,
        )

    def delete(
        self,
        endpoint: str,
        ep_params: Dict = None,
        data: Dict = None,
        additional_headers: Dict = None,
    ) -> Result:
        """
        Generic DELETE method for a given Endpoint
        :param additional_headers: additional headers for e.g. a bearer token
        :param endpoint: Endpoint of the API on which the DELETE should be executed
        :param ep_params: (optional) Dictionary, list of tuples or bytes to send
        in the query string
        :param data: (optional) A JSON serializable Python object to send in the body
        :return:
        """
        return self._do(
            http_method="DELETE",
            endpoint=endpoint,
            ep_params=ep_params,
            data=data,
            additional_headers=additional_headers,
        )

    def put(
        self,
        endpoint: str,
        ep_params: Dict = None,
        data: Dict = None,
        additional_headers: Dict = None,
    ) -> Result:
        """
        Generic PUT method for a given Endpoint
        :param additional_headers: additional headers for e.g. a bearer token
        :param endpoint: Endpoint of the API on which the PUT should be executed
        :param ep_params: (optional) Dictionary, list of tuples or bytes to send
        in the query string
        :param data: (optional) A JSON serializable Python object to send in the body
        :return:
        """
        return self._do(
            http_method="PUT",
            endpoint=endpoint,
            ep_params=ep_params,
            data=data,
            additional_headers=additional_headers,
        )
