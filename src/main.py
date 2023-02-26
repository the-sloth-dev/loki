import json
import os
import sys
from flask import Flask, jsonify


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


def validate_config_file(path):
    if not os.path.isfile(path):
        return False

    name, extension = os.path.splitext(path)
    if extension != '.json':
        return False

    return True


def load_config_file(config_file):
    if not validate_config_file(config_file):
        raise InvalidJsonFile(f'{config_file}')

    with open(config_file) as file:
        return json.load(file)


def validate_environment_variables():
    if os.environ.get('MOCK_ENDPOINTS_JSON') is None:
        raise CouldNotFindEnvironmentVariable('MOCK_ENDPOINTS_JSON')


def create_endpoint(path, method, response_body, status_code=200, headers=None):
    def endpoint():
        return jsonify(response_body), status_code, headers
    endpoint.__name__ = f"{method}_{path.replace('/', '_')}"
    return endpoint


def register_mock_endpoints(app, mock_endpoints):
    for endpoint in mock_endpoints:
        method = endpoint['method']
        path = endpoint['path']
        status_code = endpoint.get('status_code', 200)
        headers = endpoint.get('headers', {})
        response_body = endpoint['response_body']

        endpoint_func = create_endpoint(path, method, response_body, status_code=status_code, headers=headers)
        app.add_url_rule(path, view_func=endpoint_func, methods=[method])


def main():
    validate_environment_variables()

    mock_endpoints = load_config_file(os.environ.get('MOCK_ENDPOINTS_JSON'))

    app = Flask(__name__)

    register_mock_endpoints(app, mock_endpoints)
    app.run(debug=os.environ.get('DEBUG'))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
