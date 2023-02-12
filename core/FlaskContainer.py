from flask import Flask
from waitress import serve
import threading

class FlaskContainer:
    flask_app:Flask
    def __new__(cls,GetInstance:bool = False):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FlaskContainer, cls).__new__(cls)
            cls.instance._setup()
        #this is kinda cursed but it really does work so uh, yeah
        if(GetInstance):
            return cls.instance
        return cls.instance.flask_app
    
    def _setup(self):
        self.flask_app = Flask(__name__)
    
    def start_daemon(self,port):
        threading.Thread(target=lambda: serve(self.flask_app,host='0.0.0.0',port=port),daemon=True).start()
        
    def start_blocking(self,port):
        serve(self.flask_app,host='0.0.0.0',port=port)