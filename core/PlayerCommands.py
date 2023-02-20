from core.storage.Types import Message

class PlayerCommands:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PlayerCommands, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        pass
    
    def injest_message(self,msg:Message) -> bool:
        return True
    
    def register_command(self,todo):
        pass
    
    def unregister_command(self,todo):
        pass