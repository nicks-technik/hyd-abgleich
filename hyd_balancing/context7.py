import os
from django.conf import settings

class Context7:
    """
    Context class for Context7 MCP Server.
    """
    _readonly = False
    _api_key = None

    @classmethod
    def initialize(cls, readonly: bool = False):
        cls._readonly = readonly
        cls._api_key = getattr(settings, 'CONTEXT7_API_KEY', os.getenv('CONTEXT7_API_KEY'))
        
        if not cls._api_key:
            print("Warning: CONTEXT7_API_KEY not found in settings or environment variables.")

    @classmethod
    def readonly_mode(cls) -> bool:
        return cls._readonly

    @classmethod
    def get_api_key(cls):
        return cls._api_key
