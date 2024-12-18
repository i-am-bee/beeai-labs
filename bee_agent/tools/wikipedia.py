from .tool import Tool


class WikipediaTool(Tool):
    name = "Wikipedia"
    description = "Search factual and historical information, including biography, history, politics, geography, society, culture, science, technology, people, animal species, mathematics, and other subjects."

    def input_schema(self):
        # # TODO: remove hard code
        return '{"type":"object","properties":{"query":{"type":"string","format":"date","description":"Name of the wikipedia page, for example \'New York\'"}}}'

    def _run(self, input, options=None):
        pass
