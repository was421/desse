import logging,dnserver

from core.Config import Config

class DNS:
    conf:dict
    server:dnserver.DNSServer
    def __init__(self) -> None:
        self.conf:dict = Config().get_conf_dict("DNS_SERVER")
        self.server = dnserver.DNSServer(port=self.conf.get("PORT"),upstream=self.conf.get("FAILOVER"))
        
        auto_ip = Config().get_flag("AUTOMATIC_IP_CONFIG")
        
        rec_list:list[dict] = self.conf.get('RECORDS')
        for rec in rec_list:
            if auto_ip:
                rec['IP'] = Config().get_server_ip()
            zone = dnserver.Zone(rec.get("HOST"),rec.get("TYPE"),rec.get("IP"))
            logging.debug(f"DNS record created {zone}")
            self.server.add_record(zone)
        
        self.server.start()
        logging.info(f"DNS server started on port {self.server.port}") 