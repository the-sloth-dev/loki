import json
import os
import sys
from flask import Flask, jsonify
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
    def __init__(self):
        self.app = Flask(__name__)

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
        return f"{method}{path.replace('/', '_')}"

    def create_endpoint(self, path, method, response_body, status_code=200, headers=None):
        def endpoint(*args, **kwargs):
            params = kwargs.copy()
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

        endpoint.__name__ = self.generate_name(method, path)
        return endpoint

    def register_mock_endpoints(self, mock_endpoints):
        for endpoint in mock_endpoints:
            method = endpoint['method']
            path = endpoint['path']
            status_code = endpoint.get('status_code', 200)
            headers = endpoint.get('headers', {})
            response_body = endpoint['response_body']

            endpoint_func = self.create_endpoint(path, method, response_body, status_code=status_code, headers=headers)
            self.app.add_url_rule(path, view_func=endpoint_func, methods=[method])

    def run(self):
        self.validate_environment_variables()
        self.register_mock_endpoints(self.load_config_file(os.environ.get('MOCK_ENDPOINTS_JSON')))
        self.app.run(debug=os.environ.get('DEBUG'))


if __name__ == '__main__':
    try:
        server = Server()
        server.run()
    except KeyboardInterrupt:
        sys.exit(0)
