from datetime import datetime
from flask import Flask, render_template,request, redirect, session, url_for, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.context_processor
def inject_lists():
    if 'logged_in' in session:
        return dict(mylists='hello')
    else :
        return dict(mylists='bye')

@app.route('/')
def index():
    tracks = Track.query.all()
    return render_template('index.html', tracks=tracks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Login')
    else :
        email = request.form['email']
        passw = request.form['password']
        try:
            data = User.query.filter_by(password=passw, email=email).first()
            #print(data.username)
            if data is not None:
                session['logged_in'] = True
                session['current_user'] = data.username
                session['current_id'] = data.id
                return render_template('index.html')
            else :
                return '로그인 실패'
        except:
            return '로그인 실패'

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username = request.form['username'], password=request.form['password'], email=request.form['email'])
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html', title='register')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/playlist/<listid>')
def playlist(listid):
    list = List.query.filter_by(id=listid).first()
    tracks = Track.query.filter_by(list_id=listid).all()
    return render_template('playlist.html', list=list, tracks=tracks)

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    lists = List.query.filter_by(user_id=session['current_id']).all()
    return render_template('profile.html', user=user, lists=lists)

@app.route('/newlist', methods=['GET', 'POST'])
def newlist():
    if request.method == 'POST':
        new_list = List(title=request.form['listname'], description=request.form['description'], user_id=session['current_id'])
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('profile', username=session['current_user']))
    else:
        return redirect(url_for('profile', username=session['current_user']))

@app.route('/newTrack', methods=['GET', 'POST'])
def newTrack():
    if request.method == 'POST':
        belongList = request.form['listSelect']
        lists = List.query.filter_by(user_id=session['current_id']).all()
        new_id=1
        for i in lists:
            if belongList==i.title:
                new_id=i.id
        new_track = Track(title=request.form['inputTitle'], artist=request.form['inputArtist'], link=request.form['inputLink'], description=request.form['description'], list_id=new_id, creator_name=session['current_user'])
        db.session.add(new_track)
        db.session.commit()
        return render_template('index.html')
    else :
        return render_template('index.html')



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_image = db.Column(db.String(100), default='default.png')

    lists = db.relationship('List', backref='creator', lazy=True)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

class List(db.Model):
    __table_name__ = 'list'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    description = db.Column(db.String(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    #tracks = db.relationship('track', backref='parent', lazy=True)

    def __repr__(self):
        return f"<List('{self.id}', '{self.title}', '{self.description}', '{self.date_created}')>"

class Track(db.Model):
    __table_name__ = 'track'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    artist = db.Column(db.String(), nullable=False)
    link = db.Column(db.String())
    description = db.Column(db.String())
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    list_id = db.Column(db.Integer, nullable=False)
    creator_name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"<Track('{self.id}', '{self.title}')>"
if __name__ == '__main__':
    app.run()
