from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__, static_url_path="/static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
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

@app.route("/view_project")
def view_project():
    return redirect("/projects")

@app.route("/view_project/<project_id>")
def view_project_id(project_id):
    project_details = {
        "id": project_id,
        "name": f"Project {project_id}",
        "description": f"This is the description for project {project_id}."
    }
    return render_template("view_project.html", project_details=project_details)

@app.route("/create_project")
def create_project():
    return render_template("create_project.html")

@app.route("/create_project_submit", methods=["POST"])
def create_project_submit():
    name = request.form["project_name"]
    description = request.form["project_description"]
    new_project = Project(title=name, description=description)
    db.session.add(new_project)
    db.session.commit()
    return redirect("/projects")

@app.route("/items")
def items():
    return render_template("items.html")

@app.route("/view_item")
def view_item():
    return redirect("/items")

@app.route("/view_item/<item_id>")
def view_item_id(item_id):
    item_details = {
        "id": item_id,
        "name": f"Item {item_id}",
        "description": f"This is the description for item {item_id}."
    }
    return render_template("view_item.html", item_details=item_details)

@app.route("/register", methods=["GET", "POST"])
def register():
    ## WARNING: THIS IS NOT SECURED. DO NOT USE IN PRODUCTION
    if request.method == "POST":
        username = request.form["username"]
        user = LoginInfo.query.filter_by(username=username).first()
        if user:
            return render_template("register.html")
        else:
            password = request.form["password"]
            cpassword = request.form["confirm"]
            if password != cpassword:
                return redirect("/")
            user = LoginInfo(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect("/")
    return render_template("register.html")

@app.route("/create_item")
def create_item():
    return render_template("create_item.html")

@app.route("/create_item_submit", methods=["POST"])
def create_item_submit():
    name = request.form["item_name"]
    description = request.form["item_description"]
    new_supply = Supply(name=name, description=description)
    db.session.add(new_supply)
    db.session.commit()
    return redirect("/items")

with app.app_context():
    db.create_all()
app.run(debug=True)
