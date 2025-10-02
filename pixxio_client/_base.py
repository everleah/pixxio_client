import json

from types import SimpleNamespace
from json import JSONEncoder

from .exceptions import get_response_exception


class ReadOnlyResourceBase:
    
    def __init__(self, client, logger=None, response_fields=None):
        self.client = client
        self.response_fields=response_fields
        if logger:
            self.logger=logger
        else:
            self.logger = self.client.logger.getLogger(
                self.__class__.__name__)
        self.endpoint_base=f'{self.client.location_base}/{self.NAME}'
        return
    
    def set_response_fields(self, response_fields):
        self.response_fields = response_fields
        return
    
    def set_response_field(self, response_field):
        if self.response_fields and response_field not in self.response_fields:
            self.response_fields.append(response_field)
        elif not self.response_fields:
            self.response_fields = [response_field,]
        return len(self.response_fields)
    
    def _get(self, endpoint_base, **params):
        if self.response_fields:
            params.update({"responseFields":self.response_fields})
        try:
            response = self.client.session.get(
                endpoint_base,
                params = params
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
    
    def get(self, id=None, **params):
        if id is None:
            return self._get(
                endpoint_base=self.endpoint_base, **params)
        return self._get(
            endpoint_base=f"{self.endpoint_base}/{id}", 
            **params)
    
    def _parseResponse(self, response):
        if response is None:
            raise get_response_exception()
        content = response.text
        if content:
            try:
                response_object = Objectifier.from_json_str(content)
            except Exception as ex:
                raise get_response_exception(
                    message = f"ivalid response; maybe not json: {content}\r\n(err:{ex})")
        elif response.status_code==204: # No Content
            response_object = SimpleNamespace( 
                success=True
                )
        if not response.ok:
            raise get_response_exception(
                response_object=response_object, response=response)
        return response_object
    

class ResourceBase(ReadOnlyResourceBase):
    
    def _post(
            self, endpoint_base, json_data = None, 
            form_data=None, files=None, **params):
        try:
            response = self.client.session.post(
                endpoint_base,
                params = params,
                json = json_data,
                data = form_data,
                files = files
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
    
    def _put(self, endpoint_base, json_data = None, form_data=None, **params):
        try:
            response = self.client.session.put(
                endpoint_base,
                params = params,
                json = json_data,
                data = form_data
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
    
    def _delete(self, endpoint_base, **params):
        try:
            response = self.client.session.delete(
                endpoint_base,
                params = params
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
        
    def delete(self, **params):
        return self._delete(
            endpoint_base=self.endpoint_base, **params)
        
    def post(self, json_data = None, form_data=None, files=None, **params):
        return self._post(
            endpoint_base=self.endpoint_base,
            json_data = json_data,
            form_data = form_data,
            files = files,
            **params)

    def put(self, id, json_data = None, form_data=None, **params):
        return self._put(
            endpoint_base=f"{self.endpoint_base}/{id}",
            json_data = json_data,
            form_data = form_data,
            **params)

class ResourceUploadMixin:
    
    def upload(self, file_path, **form_data):
        with open(file_path,"rb") as f:
            files = { "file" : f }
            response_object = self.post(
                form_data=form_data, files=files)
        return response_object   
    
    
class _ResponseObject(SimpleNamespace):

    def __getattribute__(self, value):
        try:
            return super().__getattribute__(value)
        except AttributeError:
            return None

class _ObjectJSONEncoder(JSONEncoder):

    def default(self, obj):
        return obj.__dict__

class Objectifier:
    
    @staticmethod
    def from_json_str(json_data):
        return json.loads(json_data, object_hook = lambda d: _ResponseObject(**d))

    @staticmethod
    def to_json_str(obj, json_encoder_cls=None):
        if json_encoder_cls is None:
            json_encoder_cls = _ObjectJSONEncoder
        return json.dumps(obj, indent=4, cls=json_encoder_cls)    