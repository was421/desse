from flask import Flask
from waitress import serve
from core.Config import Config
import threading,os

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
        self.flask_app = Flask(__name__,static_folder=os.path.abspath('web/static'),template_folder=os.path.abspath('web/templates'))
    
    def start_daemon(self,port):
        threading.Thread(target=lambda: serve(self.flask_app,host='0.0.0.0',port=port),daemon=True).start()
        
    def start_blocking(self,port):
        serve(self.flask_app,host='0.0.0.0',port=port)
        
    def start_dev(self,port):
        self.flask_app.run(host='0.0.0.0',port=port)