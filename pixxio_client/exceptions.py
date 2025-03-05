

class ResponseExceptionBase(Exception):

    def __init__(self, message=None):
        if message is None:
            message = "no response message"
        self.response_object = None
        return super().__init__(message)

class ResponseException(ResponseExceptionBase):

    def __init__(self, response_object = None):
        self.response_object = response_object
        if response_object:
            try:
                message = response_object.errorMessage
            except Exception as ex: 
                message = f"??? invalid response object ??? ({ex})"
        else:
            message = "no response object"
        return super().__init__(message)
    
class InvalidResponseException(ResponseException):

    def __init__(self, invalid_response_object = None):
        self.response_object = invalid_response_object
        if self.response_object:
            message = f"invalid response"
        else:
            message = "no response object"
        return super().__init__(message)
    
class ResponseError(ResponseException):

    def __init__(self, exception, message = None):
        self.exception = exception
        if message is None:
            message = str(exception)
        return super().__init__(message)
    
    
def get_response_exception(response_object = None, message=None, exception=None):
       
    if response_object is None:
        if exception:
            response_exception = ResponseError(exception, message)
        else:
            response_exception = ResponseExceptionBase(message)
    elif hasattr(response_object, 'errorCode'):
        response_exception = ResponseException(response_object)
    else: # invalid response
        response_exception = InvalidResponseException(response_object)
    return response_exception