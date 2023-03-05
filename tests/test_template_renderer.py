import unittest
from json import JSONDecodeError
from app import PathParameterRenderer


class TestPathParameterRenderer(unittest.TestCase):
    def setUp(self):
        self.template = '{"message": "Hello, {{name}}! Your ID is {{id}}."}'
        self.path_params = {
            "name": "John Doe",
            "id": "12345"
        }
        self.renderer = PathParameterRenderer(self.template)

    def test_render_with_valid_params(self):
        expected_output = {'message': 'Hello, John Doe! Your ID is 12345.'}
        self.assertEqual(self.renderer.render(self.path_params), expected_output)

    def test_render_with_invalid_params(self):
        path_params = {"age": "23"}
        expected_output = {'message': 'Hello, {{name}}! Your ID is {{id}}.'}
        self.assertEqual(self.renderer.render(path_params), expected_output)

    def test_render_with_empty_template(self):
        renderer = PathParameterRenderer("")
        with self.assertRaises(JSONDecodeError):
            renderer.render(self.path_params)

    def test_render_with_missing_parameter(self):
        template = '{"message": "Hello, {{name}}! Your age is {{age}}."}'
        renderer = PathParameterRenderer(template)
        expected_output = {"message": "Hello, John Doe! Your age is {{age}}."}
        self.assertEqual(renderer.render(self.path_params), expected_output)
