from flask import Flask
from waitress import serve
import threading

class FlaskContainer:
    f:Flask
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FlaskContainer, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        self.f = Flask(__name__)
    
    def start_daemon(self,port):
        threading.Thread(target=lambda: serve(self.f,host='0.0.0.0',port=port),daemon=True).start()
        
    def start_blocking(self,port):
        serve(self.f,host='0.0.0.0',port=port)