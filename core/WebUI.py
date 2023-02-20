from flask import render_template,url_for,send_from_directory
from core.FlaskContainer import FlaskContainer as FC
from core.Server import Server
import os


class WebUI:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebUI, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
      pass
      
    @FC().route('/favicon.ico')
    def favicon():
      return FC().send_static_file('favicon.ico')
    
    @FC().route("/")
    def index():
      ctx:dict = {}
      #All Players Table
      ctx['player_data_headers'] = ["To","Do"]
      ctx['players'] = [[0,0]]
      #
      
      
      return render_template('index.html',**ctx),200