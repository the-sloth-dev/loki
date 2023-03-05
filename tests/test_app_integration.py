import json
import os
import tempfile
import threading
import requests
from unittest import TestCase
from app import Server


class ServerTest(TestCase):
    def setUp(self):
        mock_endpoints = [
            {
                "method": "GET",
                "path": "/test",
                "response_body": {"message": "Hello, world!"}
            },
            {
                "method": "POST",
                "path": "/test/<name>/<id>",
                "response_body": {"message": "Hello, {{name}}! Your ID is {{id}}."}
            }
        ]

        # Create a temporary file
        file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        file.write(json.dumps(mock_endpoints).encode('utf-8'))
        file.flush()

        os.environ["MOCK_ENDPOINTS_JSON"] = file.name

        self.server = Server()
        thread = threading.Thread(target=self.server.run)
        thread.setName('loki')
        thread.start()

    def tearDown(self):
        threading.Thread(target=self.server.stop).start()
        os.remove(os.environ["MOCK_ENDPOINTS_JSON"])
        os.environ.pop('MOCK_ENDPOINTS_JSON', None)

    def test_load_config_file_valid(self):
        response = requests.get('http://127.0.0.1:5000/test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Hello, world!'})
