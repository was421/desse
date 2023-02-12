from core.FlaskContainer import FlaskContainer as FC
from core.Server import Server

class WebUI:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebUI, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        pass
    
    @FC().route("/")
    def index():
        return "Hi",200