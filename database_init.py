import sqlite3

def init_users():
    conn = sqlite3.connect('users.db')
    print "opened users db"
    conn.execute('''DROP TABLE IF EXISTS Users;''')
    conn.execute('''CREATE TABLE Users (
                    username TEXT PRIMARY KEY,
                    email TEXT,
                    password TEXT
                    description TEXT
                    )''')
    print "database formed"
    conn.close()                            
    
def init_follows():
    conn = sqlite3.connect('follows.db')
    print "opened follows db"
    conn.execute('''DROP TABLE IF EXISTS Follows''')
    conn.execute('''CREATE TABLE Follows (
                root TEXT,
                tip TEXT,
                FOREIGN KEY(root) REFERENCES Users(username),
                FOREIGN Key(tip) REFERENCES Users(username)
                )''')
    print "database formed"
    conn.close()  
    
def init_tweets():
    conn = sqlite3.connect('tweets.db')
    print "opened tweets db"
    conn.execute('''DROP TABLE IF EXISTS tweets''')
    conn.execute('''CREATE TABLE Tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    likes INTEGER,
                    message TEXT not null,
                    username TEXT,
                    FOREIGN KEY(username) REFERENCES Users(username)
                    )''')
    print "database formed"
    conn.close()     
    
def fill_users():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.executemany('''INSERT INTO Users 
                    (username,email,password)
                    VALUES (?,?,?)''',[("bob","bob@gmail.com","whoop"),("charlie","charlie@me.com","password")])
                    
    conn.commit()
    conn.close()
    
def fill_tweets():
    conn = sqlite3.connect('tweets.db')
    cur = conn.cursor()
    cur.execute('''INSERT INTO Tweets 
                    (likes,message,username)
                    VALUES (?,?,?)''',(5,"my second tweet","bob"))
    conn.commit()
    conn.close()   
    
def find_users(term='''%%'''):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    # cur.execute('''select password 
                   # FROM Users
                   # WHERE username LIKE '%s' ''' % 'bob')
    cur.execute('''SELECT * 
                   FROM Users
                   WHERE username LIKE '%s' ''' % term)
    result = cur.fetchall()
    print result
    conn.close()
    
def find_tweets():
    conn = sqlite3.connect('tweets.db')
    cur = conn.cursor()
    cur.execute('select * from Tweets')
    result = cur.fetchall()
    conn.close()    
    return result
    
def main():
   init_users()
   init_tweets()
   init_follows()
   # fill_users()
   # fill_tweets()
   # find_users()
   # find_tweets()