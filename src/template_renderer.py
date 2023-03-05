import chevron
import json
import re


class PathParameterRenderer:
    def __init__(self, template):
        self.template = template

    def render(self, path_params):
        template_params = re.findall(r'\{\{(.+?)\}\}', self.template)

        for key in path_params:
            if key in template_params:
                template_params.remove(key)

        for key in template_params:
            path_params[key] = f"{{{{{key}}}}}"

        rendered_template = chevron.render(self.template, path_params)
        return json.loads(rendered_template)
