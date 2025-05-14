import json
from phonenumber_field.phonenumber import PhoneNumber

class PhoneNumberEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that can handle PhoneNumber objects.
    """
    def default(self, obj):
        if isinstance(obj, PhoneNumber):
            return str(obj)
        return super().default(obj)

def phone_number_json_dumps(data):
    """
    Serialize data to JSON, handling PhoneNumber objects.
    """
    return json.dumps(data, cls=PhoneNumberEncoder)
