import logging
from core.storage.StorageContainer import StorageContainer
from core.storage.volatile import InMemory
from core.storage.persistent import SQLite
from core.FlaskContainer import FlaskContainer
from core.Config import Config
from core.WebUI import WebUI
from core.Server import Server
from core.DNS import DNS

if __name__ == '__main__':

    level,filename = Config().get_logging_settings()
    
    logging.basicConfig(level=level,
                        format="[%(asctime)s][%(levelname)s] %(message)s",
                        filename=filename)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    logging.getLogger("").addHandler(stream_handler)
    
    StorageContainer().persistent = SQLite.SQLite()
    StorageContainer().volatile = InMemory.InMemory()
    
    if(Config().get_flag("local_dns_server")):
        local_dns = DNS()
    
    if(Config().get_flag("enable_webui")):
        webui = WebUI()
    
    server = Server()
    
    if(Config().get_flag("is_devmode")):
        FlaskContainer(GetInstance=True).start_dev(Config().get_server_port())
    else:
        FlaskContainer(GetInstance=True).start_blocking(Config().get_server_port())