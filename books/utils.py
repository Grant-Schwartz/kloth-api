class APIException(Exception):

    def __init__(self, provider, message):
        self.provider = provider
        self.message = message
    
    def __str__(self):
        return str(f'{self.provider} APIExeption: {self.message}')
    
def to_dict(obj):
    if not  hasattr(obj,"__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        element = []
        if isinstance(val, list):
            for item in val:
                element.append(to_dict(item))
        else:
            element = to_dict(val)
        result[key] = element
    return result