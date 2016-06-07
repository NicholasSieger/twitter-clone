from flask import Flask, g, request, render_template,\
                  redirect, url_for,session                 
import sqlite3

app = Flask(__name__)
app.config.from_object('config')

#db connections
def get_users_db():
    if not hasattr(g, 'users_db'):
        g.users_db = connect_db(app.config['DATABASE_USERS'])    
    return g.users_db, g.users_db.cursor()  

def get_follows_db():
    if not hasattr(g, 'follows_db'):
        g.follows_db = connect_db(app.config['DATABASE_FOLLOWS'])
    return g.follows_db, g.follows_db.cursor()  

def get_tweets_db():
    if not hasattr(g, 'tweets_db'):
        g.tweets_db = connect_db(app.config['DATABASE_TWEETS'])
    return g.tweets_db, g.tweets_db.cursor()       
     
def connect_db(db):
    """Connects to the specific database."""
    rv = sqlite3.connect(db)
    rv.row_factory = sqlite3.Row
    return rv

@app.teardown_appcontext
def close_db(exception):
    for key in ['users_db','follows_db','tweets_db']:
        db = getattr(g,key,None)
        if db is not None:
            db.close()     
            
#helpers
def search():
    '''if there is a search request, go to search page'''
    if request.method == 'POST':
        searchterm = request.form['searchterm']
        if searchterm != "":
           return redirect(url_for('search_results',
                                    searchterm=searchterm))
    else:
        return None                               
    
def tweet():
    '''if the user is tweeting, enter tweet in db'''
    if request.method == 'POST':
        tweet = request.form['searchterm']
        if tweet:
            username = session['username']
            (tcon,tcur) = get_tweets_db()
            tcur.execute('''INSERT INTO Tweets 
                    (likes,dislikes,message,username)
                    VALUES (?,?,?,?)''',
                    (0,0,tweet,username))
            tcon.commit()
    else:
        return None
        
def is_following(profile):
    (fconn,fcur) = get_follows_db()
    fcur.execute('''SELECT root,tip
                    FROM Follows
                    WHERE root = '%s' AND tip = '%s' ''' %
                    (root,tip))
    return len(fcur.fetchall()) > 0
    
def get_following(username):
    #get the databases
    (fconn,fcur) = get_follows_db()
    
    #get the people I am following
    fcur.execute('''SELECT tip
                    FROM Follows
                    WHERE root LIKE '%s' ''' % username)
        
    return fcur.fetchall()

def get_tweets(username):
    (tconn,tcur) = get_tweets_db()
    tcur.execute('''SELECT message,username
                    FROM Tweets
                    WHERE username LIKE '%s' ''' % username)
    return tcur.fetchall()

def validate(username,password):
     (ucon,ucur) = get_users_db()
     ucur.execute('''select password
                     from Users
                     where username like '%s' ''' % username)
     pw = ucur.fetchone()
     return (pw[0] == password)
    
#routes
@app.route('/',methods=['GET','POST'])
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate(username,password):
            session['username'] =username
            return redirect(url_for('timeline',user=username))
        else:
            return render_template('login.html',
                                    msg="incorrect password") 
    return render_template('login.html',msg="")   

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('login'))
    
@app.route('/timeline/<user>',methods=['GET','POST'])
def timeline(user):        
    tweet()
    next= search()
    if next: 
       return next
            
    following = get_following(user)
    tweets = []
    for profile in following:
        tweets += get_tweets(profile)
        
    return render_template('timeline.html',
                            profile=user,
                            following=following,
                            tweets = tweets)
    
@app.route('/profile/<username>',methods=['GET','POST'])
def profile(username):
    search()
    tweet()
    following = get_following(username)
    tweets = get_tweets(username)
    return render_template('profile.html',
                            profile=username,
                            is_following= is_following(username),
                            following=username,
                            tweets=username)

@app.route('/new_user',methods=['GET','POST'])
def new_user():
    if request.method =='POST':
       username = request.form['username']
       email = request.form['email']
       password = request.form['password']

       (uconn,ucur) = get_users_db()
       ucur.execute('''INSERT INTO Users 
                    (username,email,password)
                    VALUES (?,?,?)''',
                    (username,email,password))
       uconn.commit()
       session['username'] = username
       return redirect(url_for('login'))
    return render_template('new_user.html')
    
@app.route('/search_results/<searchterm>',methods=['GET','POST'])
def search_results(searchterm):
    next = search()
    if next: return next
    (uconn,ucur) = get_users_db()
    ucur.execute('''SELECT username
                    FROM Users
                    WHERE username LIKE '%s' ''' % searchterm)
    results = ucur.fetchall()
    return render_template('search_results.html',
                            term=searchterm,
                            results=results)

@app.route('/follow/<root>/<tip>')
def follow(root,tip):
    (fconn,fcur) = get_follows_db()
    fcur.execute('''INSERT INTO Follows 
                    (root,tip)
                    VALUES (?,?)''',(root,tip))
    fconn.commit()
    return redirect(url_for('profile',username=tip))

@app.route('/unfollow/<root>/<tip>')    
def unfollow(root,tip):
    (fconn,fcur) = get_follows_db()
    fcur.execute('''DELETE FROM Follows 
                    (root,tip)
                    VALUES (?,?)''',(root,tip))
    fconn.commit()
    return redirect(url_for('profile',username=tip))

app.secret_key = 'the mac address is....'    
    
if __name__ == '__main__':
    
    app.run(debug = True)