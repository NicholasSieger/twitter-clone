<<<<<<< HEAD
from flask import Flask, session, render_template,redirect, g,url_for, request
from flask_login import LoginManager, login_user,current_user,logout_user,login_required
import sqlite3

app = Flask(__name__,static_url_path="/static")
app.config.from_object('config')
login_manager = LoginManager()
login_manager.init_app(app)

def connect_db(db):
    """Connects to the specific database."""
    rv = sqlite3.connect(db)
    rv.row_factory = sqlite3.Row
    return rv
    
def get_users_db():
    # if not hasattr(g, 'users_db'):
    users_db = connect_db('users.db')    
    return users_db, users_db.cursor()     

db = {"bob":"whoop","leah":"legos"}    
    
class User(object):
    
    
    def __init__(self,username,pw):
        self.username = username
        self.pw = pw
        self.authenticated = False
        self.active = True
        self.anonymous = False
        
    def get_id(self):
        return self.username
        
    def is_authenticated(self):
        return self.authenticated
        
    def is_active(self):
        return True
        
    def is_anonymous(self):
        return False
    
    @classmethod
    def validate(cls,username,password):
        return password == db[username]
                
    @classmethod
    def find(cls,username):
        return User(username,db[username])

@login_manager.request_loader
def user_loader(request):
    return User('bob','whoop')
    
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       username= request.form['username']
       password = request.form['password']
       if User.validate(username,password):
            user = User.find(username)
            user.authenticated = True
            login_user(user,remember = True)
            return redirect(url_for('main',user=username))
       return redirect(url_for('login'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=text name=password>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/main/<user>',methods=['GET','POST'])
@login_required
def main(user):
    if request.method == 'POST':
        return redirect(url_for('logout'))
    return '''
        <p>my name is %s</p>
        <form action="" method="POST">
            <p><input type=submit>
        </form>''' % user    
    
@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect(url_for('login'))


  
# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'    
    
if __name__ == '__main__':
    app.debug = True
=======
from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name__)

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/adder/<int:x>/<int:y>')
def adder(x,y):
   return "Answer= %d" % (int(x) + int(y))     
    
# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'    
    
if __name__ == '__main__':
    app.debug = True
>>>>>>> 60767513bb270f3169a431286bd3d10a7c8985b5
    app.run()