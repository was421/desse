from flask import Flask
from waitress import serve
from core.Config import Config
import threading,os

class FlaskContainer:
    flask_app:Flask
    mode:str = "daemon"
    port:int = 18000
    def __new__(cls,name:str = "Default"):
        if not hasattr(cls, 'instance'):
            cls.instance = {}
        if cls.instance.get(name) is None:
            cls.instance[name] = super(FlaskContainer, cls).__new__(cls)
            cls.instance[name].flask_app = Flask(name)
        return cls.instance[name]
       
    def start_daemon(self):
        threading.Thread(target=lambda: serve(self.flask_app,host='0.0.0.0',port=self.port),daemon=True).start()
        
    def start_blocking(self):
        serve(self.flask_app,host='0.0.0.0',port=self.port)
        
    def start_dev(self):
        self.flask_app.debug = True
        self.flask_app.run(host='0.0.0.0',port=self.port)
        
    def configure(self,port,mode:str = "daemon"):
        self.port = port
        self.mode = mode
        
    def start(self):
        match self.mode:
            case 'daemon':
                self.start_daemon()
            case 'blocking':
                self.start_blocking()
            case _:
                self.start_dev()
                
        
        
        
        
        