import json
import os
import tempfile
from parameterized import parameterized
from unittest import TestCase
from app import Server, CouldNotFindEnvironmentVariable, InvalidJsonFile


class ServerTest(TestCase):
    def setUp(self):
        self.server = Server()
        self.mock_endpoints = [
            {
                "method": "GET",
                "path": "/test",
                "response_body": {"message": "Hello, world!"}
            },
            {
                "method": "POST",
                "path": "/test/{name}/{id}",
                "response_body": {"message": "Hello, {{name}}! Your ID is {{id}}."}
            }
        ]

    def test_load_config_file_valid(self):
        # Create a temporary file and write the mock endpoints to it
        with tempfile.NamedTemporaryFile(mode="w", suffix='.json', delete=True) as config_file:
            json.dump(self.mock_endpoints, config_file)
            config_file.seek(0)
            result = self.server.load_config_file(config_file.name)
            self.assertEqual(result, self.mock_endpoints)

    def test_load_config_file_invalid_path(self):
        with self.assertRaises(InvalidJsonFile):
            self.server.load_config_file("invalid_path.json")

    def test_load_config_file_invalid_extension(self):
        with self.assertRaises(InvalidJsonFile):
            self.server.load_config_file("test.txt")

    def test_validate_environment_variables_valid(self):
        os.environ["MOCK_ENDPOINTS_JSON"] = "test.json"
        self.server.validate_environment_variables()

    def test_validate_environment_variables_invalid(self):
        with self.assertRaises(CouldNotFindEnvironmentVariable):
            self.server.validate_environment_variables()

    def test_create_endpoint(self):
        server = Server()
        path = "/test/{name}"
        endpoint = server.create_endpoint(path, "GET", {"message": "Hello, {{name}}!"})
        self.assertEqual(endpoint.__name__, "get_test_name")
        with server.app.test_request_context(path):
            response = endpoint(name="John")
            self.assertEqual(response[0].json, {"message": "Hello, John!"})
            self.assertEqual(response[1], 200)

    def test_register_mock_endpoints(self):
        self.server.register_mock_endpoints(self.mock_endpoints)
        for endpoint in self.mock_endpoints:
            path = endpoint["path"]
            method = endpoint["method"]
            response_body = endpoint["response_body"]
            status_code = endpoint.get("status_code", 200)
            headers = endpoint.get("headers", {})
            view_func = self.server.app.view_functions[f"{method.lower()}{path.replace('/', '_').replace('{', '').replace('}', '')}"]
            with self.server.app.test_request_context(path):
                response = view_func()
                self.assertEqual(response[0].json, response_body)
                self.assertEqual(response[1], status_code)
                self.assertEqual(response[2], headers)

    @parameterized.expand([
        ["GET", "/test", "get_test"],
        ["DELETE", "/test", "delete_test"],
        ["PATCH", "/test", "patch_test"],
        ["PUT", "/test", "put_test"],
        ["POST", "/test/{name}/{id}", "post_test_name_id"]
    ])
    def test_generate_name(self, method, path, expected):
        actual = self.server.generate_name(method, path)
        self.assertEqual(expected, actual)
