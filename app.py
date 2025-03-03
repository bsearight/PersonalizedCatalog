from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin


app = Flask(__name__, static_url_path="/static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final.db'
app.config['SECRET_KEY'] = 'superLongSecretKeyForCookieManagement'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

class LoginInfo(db.Model, UserMixin):
    __tablename__ = 'login_info'
    loginid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    user_profile = db.relationship("UserProfile", backref="login_info", uselist=False)


class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    UserID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    prefered_medium = db.Column(db.String(255))
    loginid = db.Column(db.Integer, db.ForeignKey('login_info.loginid'), unique=True)
    
    projects = db.relationship("Project", backref="user_profile")
    supplies = db.relationship("Supply", backref="user_profile")

class Project(db.Model):
    __tablename__ = 'project'
    ProjectID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    field = db.Column(db.String(255))
    date = db.Column(db.Date)
    notes = db.Column(db.Text)
    status = db.Column(db.String(255))
    UserID = db.Column(db.Integer, db.ForeignKey('user_profile.UserID'))
    
    project_notes = db.relationship("ProjectNotes", backref="project")

class Supply(db.Model):
    __tablename__ = 'supply'
    SupplyID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255))
    category = db.Column(db.String(255))
    purchase_link = db.Column(db.String(255))
    cost = db.Column(db.Numeric(10, 2))
    rating = db.Column(db.Numeric(3, 2))
    information = db.Column(db.Text)
    notes = db.Column(db.Text)
    description = db.Column(db.Text)
    UserID = db.Column(db.Integer, db.ForeignKey('user_profile.UserID'))
    
    supply_notes = db.relationship("SupplyNotes", backref="supply")

class SupplyNotes(db.Model):
    __tablename__ = 'supply_notes'
    snoteid = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date)
    importance = db.Column(db.Integer)
    SupplyID = db.Column(db.Integer, db.ForeignKey('supply.SupplyID'))

class ProjectNotes(db.Model):
    __tablename__ = 'project_notes'
    pnoteid = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date)
    importance = db.Column(db.Integer)
    ProjectID = db.Column(db.Integer, db.ForeignKey('project.ProjectID'))

@login_manager.user_loader
def load_user(user_id):
    return LoginInfo.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/items")
def items():
    return render_template("items.html")

with app.app_context():
    db.create_all()
app.run(debug=True)
