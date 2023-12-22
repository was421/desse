from flask import Blueprint,render_template,url_for,send_from_directory,redirect,request
from flask_login.login_manager import LoginManager
from flask_login import login_required,login_user,logout_user,current_user,UserMixin
from core.FlaskContainer import FlaskContainer
import os,uuid

class User(UserMixin):
  def __init__(self,uuid4:str) -> None:
     super().__init__()
     self.id = uuid4
  
  def get_id(self):
    return self.id


class Admin:
    blueprint = Blueprint("Admin",__name__,
                        static_folder=os.path.abspath('web/static'),
                        static_url_path='/',
                        template_folder=os.path.abspath('web/templates/admin'))
    _login_manager = LoginManager(FlaskContainer().flask_app)
    _users:dict[str,User] = {}#TODO: move to StorageModel
    
    def __new__(cls):
      if not hasattr(cls, 'instance'):
          cls.instance = super(Admin, cls).__new__(cls)
          cls.instance._setup()
      return cls.instance
    
    def _setup(self):
        pass
    
    @_login_manager.user_loader
    def _load_user(user_id):
        return Admin()._users.get(user_id)#TODO: move to StorageModel
    
    @_login_manager.unauthorized_handler
    def _unauthorized():
        return redirect("/login")
    
    @blueprint.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            request.form.get('username')
            request.form.get('password')
            usr = User(str(uuid.uuid4()))
            if login_user(usr):
                Admin()._users[usr.get_id()] = usr
                return redirect('/admin')
            return redirect('/login')
        return render_template('login.html')
    @blueprint.route("/logout",methods=['POST'])
    @login_required
    def logout():
        usr:User = current_user
        del Admin()._users[usr.get_id()] #TODO: move to StorageModel
        logout_user()
        return redirect('/')
  
    @blueprint.route("/admin")
    @login_required
    def admin_dashboard():
        ctx:dict = {}
        #All Players Table
        ctx['player_data_headers'] = ["To","Do"]
        ctx['players'] = [[0,0]]
        #
        return render_template('dashboard.html',**ctx),200