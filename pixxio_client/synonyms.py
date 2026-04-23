from .keywords import Keyword

class Synonym(Keyword):
    NAME = "synonyms"
    
    def get_columns(self, **params):
        with self._without_response_fields():
            return self._get(
                endpoint_base=f"{self.client.location_base}/synonymColumns",
                **params)
    