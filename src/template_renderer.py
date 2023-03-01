import chevron
import json


class PathParameterRenderer:
    def __init__(self, template):
        self.template = template

    def render(self, path_params):
        for key in path_params:
            if f"{{{{{key}}}}}" in self.template:
                path_params[key] = chevron.render(path_params[key])
        rendered_template = chevron.render(self.template, path_params)
        return json.loads(rendered_template)
