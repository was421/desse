import logging,dnserver

from core.Config import Config

class DNS:
    conf:dict
    server:dnserver.DNSServer
    def __init__(self) -> None:
        self.conf:dict = Config().get_conf_dict("DNS")
        self.server = dnserver.DNSServer(port=self.conf.get("port"),upstream=self.conf.get("failover"))
        
        auto_ip = Config().get_flag("automatic_ip_config")
        
        rec_list:list[dict] = self.conf.get('records')
        for rec in rec_list:
            if auto_ip:
                rec['ip'] = Config().get_server_public_ip()
            zone = dnserver.Zone(rec.get("host"),rec.get("type"),rec.get("ip"))
            logging.debug(f"DNS record created {zone}")
            self.server.add_record(zone)
        
        self.server.start()
        logging.info(f"DNS server started on port {self.server.port}") 