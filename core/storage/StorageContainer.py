from core.storage.StorageModel import StorageModel
class StorageContainer:
    volatile:StorageModel
    persistent:StorageModel
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StorageContainer, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        pass