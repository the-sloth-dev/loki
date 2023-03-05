import json
import os
import sys
import logging
from urllib.parse import urlparse, parse_qs
from flask import Flask, request, jsonify
from template_renderer import PathParameterRenderer


class CouldNotFindEnvironmentVariable(Exception):
    """Exception raised when is not possible to find an environment variable

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InvalidJsonFile(Exception):
    """Exception raised a JSON file is invalid.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Server:
    def __init__(self, host='127.0.0.1', port=5000):
        self.app = Flask(__name__)
        self.mocked_endpoints = []
        self.host = host
        self.port = port

    @staticmethod
    def validate_config_file(path):
        if not os.path.isfile(path):
            return False

        name, extension = os.path.splitext(path)
        if extension != '.json':
            return False

        return True

    def load_config_file(self, config_file):
        if not self.validate_config_file(config_file):
            raise InvalidJsonFile(f'{config_file}')

        with open(config_file) as file:
            return json.load(file)

    @staticmethod
    def validate_environment_variables():
        if os.environ.get('MOCK_ENDPOINTS_JSON') is None:
            raise CouldNotFindEnvironmentVariable('MOCK_ENDPOINTS_JSON')

    @staticmethod
    def generate_name(method, path):
        return f"{method.lower()}{path.replace('/', '_').replace('<', '').replace('>', '')}"

    def create_endpoint(self, url, method, response_body, status_code=200, headers=None):
        def endpoint(*args, **kwargs):
            path_params = kwargs.copy()
            query_params = parse_qs(url.query)
            params = {**path_params, **query_params}
            stringify_response = json.dumps(response_body)
            if "{{" in stringify_response and "}}" in stringify_response:
                if len(params) > 0:
                    renderer = PathParameterRenderer(stringify_response)
                    body = renderer.render(params)
                    return jsonify(body), status_code, headers
                else:
                    return jsonify(response_body), status_code, headers
            else:
                return jsonify(response_body), status_code, headers

        endpoint.__name__ = self.generate_name(method, url.path)
        return endpoint

    def register_mock_endpoints(self, mock_endpoints):
        for endpoint in mock_endpoints:
            method = endpoint['method']
            url = urlparse(endpoint['path'])
            status_code = endpoint.get('status_code', 200)
            headers = endpoint.get('headers', {})
            response_body = endpoint['response_body']

            endpoint_func = self.create_endpoint(url, method, response_body, status_code=status_code, headers=headers)
            self.app.add_url_rule(url.path, view_func=endpoint_func, methods=[method])
            self.mocked_endpoints.append({"method": method, "path": endpoint['path']})

    def show_mocked_endpoints(self):
        for mocked_endpoint in self.mocked_endpoints:
            self.app.logger.info(f'mocking {mocked_endpoint["method"]} {mocked_endpoint["path"]}')

    def run(self):
        self.app.logger.setLevel(logging.INFO)
        self.validate_environment_variables()
        self.register_mock_endpoints(self.load_config_file(os.environ.get('MOCK_ENDPOINTS_JSON')))
        self.register_shutdown_function()
        self.app.before_first_request(self.show_mocked_endpoints)
        self.app.run(port=self.port, debug=os.environ.get('DEBUG'))

    @staticmethod
    def shutdown():
        shutdown_func = request.environ.get('werkzeug.server.shutdown')
        if shutdown_func is None:
            import os
            import signal

            sig = getattr(signal, "SIGKILL", signal.SIGTERM)
            os.kill(os.getpid(), sig)
        shutdown_func()
        return "shutting down..."

    def stop(self):
        import requests
        requests.get(f'http://{self.host}:{self.port}/shutdown')

    def register_shutdown_function(self):
        self.app.add_url_rule("/shutdown", view_func=self.shutdown, methods=['GET'])


if __name__ == '__main__':
    try:
        server = Server()
        server.run()
    except KeyboardInterrupt:
        sys.exit(0)
