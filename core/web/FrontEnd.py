from flask import Blueprint,render_template,url_for,send_from_directory,redirect,request


from core.storage.StorageContainer import StorageContainer as SC
from core.FlaskContainer import FlaskContainer
from core.Util import *
import os,uuid


class FrontEnd:
  blueprint = Blueprint("FrontEnd",__name__,
                        static_folder=os.path.abspath('web/static'),
                        static_url_path='/',
                        template_folder=os.path.abspath('web/templates'))
  _render_ctx:dict = {}
  
  def __new__(cls):
      if not hasattr(cls, 'instance'):
          cls.instance = super(FrontEnd, cls).__new__(cls)
          cls.instance._setup()
      return cls.instance
  
  def _setup(self):
    FlaskContainer().flask_app.secret_key = os.urandom(128)
    pass
  
  def _get_current_players(self, region:str = "ALL"):
        blocks = {}
        regiontotal = {}
        regiontotal[US_REGION] = 0
        regiontotal[EU_REGION] = 0
        regiontotal[JP_REGION] = 0
        
        for ghost in SC().volatile.ghost_fetch_all():
            if regiontotal.get(ghost.region) is None:
                regiontotal[ghost.region] = 0
            regiontotal[ghost.region] += 1
            
            if region == "ALL" or ghost.region == region:
                if ghost.ghostBlockID not in blocks:
                    blocks[ghost.ghostBlockID] = 0
                blocks[ghost.ghostBlockID] += 1
                
        blockslist = sorted((v, k) for (k, v) in blocks.items())
        return regiontotal, blockslist
  
  
    
  @blueprint.route('/favicon.ico')
  def favicon():
    return FrontEnd().blueprint.send_static_file('favicon.ico')
  
  @blueprint.route("/")
  def index():
    self = FrontEnd()
    #STATIC Data
    self._render_ctx['STATIC'] = {'BLOCK_NAMES':BLOCK_NAMES}
    
    #players Data
    #{serverport:count} [(block:count)]             
    regiontotal, blockslist = self._get_current_players()
    self._render_ctx['players'] = {'regiontotal':regiontotal,'blockslist':blockslist, 'total_players':sum(regiontotal.values())}
    
    
    return render_template('index.html',**self._render_ctx)
  
  
  