import logging
from core.storage.StorageContainer import StorageContainer
from core.storage.volatile.InMemory import InMemory
from core.storage.persistent.SQLite import SQLite
from core.FlaskContainer import FlaskContainer
from core.Config import Config

from core.web.FrontEnd import FrontEnd
from core.web.Admin import Admin

from core.StatusServer import StatusServer
from core.Server import Server
from core.DNS import DNS

if __name__ == '__main__':
    conf = Config()
    
    level,filename = conf.get_logging_settings()
    
    print(level,filename)
    
    logging.basicConfig(level=level,
                        format="[%(asctime)s][%(levelname)s] %(message)s",
                        filename=filename)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    logging.getLogger("").addHandler(stream_handler)
    
    StorageContainer().persistent = SQLite()
    StorageContainer().volatile = InMemory()
    
    flask = FlaskContainer()
    
    flask.configure(conf.get_server_port(),"blocking")
    
    if(conf.get_flag("DNS_SERVER")):
        local_dns = DNS()
    
    if(conf.get_flag("STATUS_SERVER")):
        server_status = StatusServer()
        flask.flask_app.register_blueprint(server_status.blueprint)
        
    if(conf.get_flag("SERVER")):
        server = Server()
        flask.flask_app.register_blueprint(server.blueprint)
        
    if(conf.get_flag("WEBUI")):
        fe = FrontEnd()
        flask.flask_app.register_blueprint(fe.blueprint)
    
    if(conf.get_flag("ADMINUI")):
        ad = Admin()
        flask.flask_app.register_blueprint(ad.blueprint)
    
    
    if(Config().get_flag("IS_DEVMODE")):
        flask.start_dev()
    else:
        flask.start()