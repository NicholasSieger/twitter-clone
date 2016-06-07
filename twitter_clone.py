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
def tweet():
    '''if the user is tweeting, enter tweet in db'''
    if  'tweet_text' in request.form:
        tweet = request.form['tweet_text']
        if tweet:
            username = session['username']
            (tcon,tcur) = get_tweets_db()
            tcur.execute('''INSERT INTO Tweets 
                            (likes,message,username)
                            VALUES (?,?,?)''',
                        (0,tweet,username))
            tcon.commit()
        return None
    else:
        return None

def like():
    if 'id_like' in request.form:
        id = request.form['id_like']
        (tcon,tcur) = get_tweets_db()    
        tcur.execute('''UPDATE Tweets
                        SET likes=likes + 1
                        WHERE id = '%s' ''' % id)
        tcon.commit()

def dislike():
    if 'id_dislike' in request.form:
        id = request.form['id_dislike']
        (tcon,tcur) = get_tweets_db()    
        tcur.execute('''UPDATE Tweets
                        SET likes=likes - 1
                        WHERE id = '%s' ''' % id)
        tcon.commit() 
 
def search():
    '''if there is a search request, go to search page'''
    if 'searchterm' in request.form:
        searchterm = request.form['searchterm']
        if searchterm !="":
           return redirect(url_for('search_results',
                                    searchterm=searchterm))
    else:
        return None         

def get_following(user):
    #get the databases
    (fconn,fcur) = get_follows_db()
    
    #get the people I am following
    fcur.execute('''SELECT tip
                    FROM Follows
                    WHERE root LIKE '%s' ''' % user)
        
    return fcur.fetchall()
    
def get_tweets(user):
    (tconn,tcur) = get_tweets_db()
    tcur.execute('''SELECT *
                        FROM Tweets
                        WHERE username LIKE '%s' ''' %
                        user)
    return tcur.fetchall()
    
def isfollowing(root,tip):
    (fconn,fcur) = get_follows_db()
    fcur.execute('''SELECT root,tip
                    FROM Follows
                    WHERE root = '%s' AND tip = '%s' ''' %
                    (root,tip))
    return fcur.fetchall()
  
def validate(username,password):
    (uconn,ucur) = get_users_db()
    ucur.execute('''SELECT password
                    FROM Users
                    WHERE username LIKE '%s' ''' % username)
    pw = ucur.fetchone()
    return password == pw[0]
    
#routes    
@app.route('/timeline/<user>',methods=['GET','POST'])
def timeline(user):
   if request.method == 'POST':
      tweet()
      like()
      dislike()
      next = search()
      if next: return next  
   
   following = get_following(user)
   tweets = get_tweets(user)
   for profile in following:
        tweets = tweets + get_tweets(profile[0])
        
   return render_template('timeline.html',
                           profile=user,
                           follows=following,
                           tweets=tweets)
       
@app.route('/search_results/<searchterm>')
def search_results(searchterm):
    if request.method == 'POST':
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
           
@app.route('/profile/<user>',methods=['GET','POST'])
def profile(user):
   tweet()
   like()
   dislike()
   next = search()
   if next: return next
   descripion = get_user(user) 
   isfollow = isfollowing(session['username'],user)
   following = get_following(user)
   tweets = get_tweets(user)
   return render_template('profile.html',
                           profile=user,
                           description=description,
                           tweets=tweets,
                           following=following,
                           isfollow=isfollow)
           
@app.route('/new_user',methods=['GET','POST'])
def new_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        (uconn,ucur) = get_users_db()
        try:
            ucur.execute('''INSERT INTO Users 
                        (username,email,password)
                        VALUES (?,?,?)''',
                        (username,email,password))
            uconn.commit()
            session['username'] = username
        except:
            uconn.rollback()
        return redirect(url_for('login'))
    else:      
      return render_template('new_user.html')
    
@app.route('/login',methods=['GET','POST'])                    
@app.route('/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate(username,password):
            session.logged_in = True
            session['username'] =username
            return redirect(url_for('timeline',user=username))
        
        return render_template('login.html',
                                msg="incorrect password:")
    return render_template('login.html',msg="")

@app.route('/logout')
def logout():
    session.logged_in = False
    session.pop('username')
    return redirect(url_for('login'))
      
@app.route('/unfollow/<root>/<tip>')
def unfollow(root,tip):
    (fconn,fcur) = get_follows_db()
    fcur.execute('''DELETE FROM Follows 
                    WHERE root LIKE '%s' AND tip LIKE '%s' ''' %
                    (root,tip))
    fconn.commit()
    return redirect(url_for('profile',user=tip))    
    
@app.route('/follow/<root>/<tip>')
def follow(root,tip):
    (fconn,fcur) = get_follows_db()
    fcur.execute('''INSERT INTO Follows 
                    (root,tip)
                    VALUES (?,?)''',(root,tip))
    fconn.commit()
    return redirect(url_for('profile',user=tip))
    
    
app.secret_key = 'the mac address is....'    
    
if __name__ == '__main__':
    
    app.run(debug = True)