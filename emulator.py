import logging
from core.Config import Config
from core.Server import Server
from core.DNS import DNS

if __name__ == '__main__':
    log_conf = Config().get_conf_dict("LOGGING")
    level = logging.NOTSET

    match(log_conf.get("log_level")):
        case "DEBUG":
            level = logging.DEBUG
        case "INFO":
            level = logging.INFO
        case "WARNING":
            level = logging.WARNING
        case "ERROR":
            level = logging.ERROR
            
    logging.basicConfig(level=level,
                        format="[%(asctime)s][%(levelname)s] %(message)s",
                        filename=log_conf.get("log_file"))

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    logging.getLogger("").addHandler(stream_handler)

    if(Config().get_flag("local_dns_server")):
        local_dns = DNS()

    server = Server()
    server.start()