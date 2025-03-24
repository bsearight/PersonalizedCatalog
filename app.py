from sqlite3 import Date
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__, static_url_path="/static")
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
app.config['SECRET_KEY'] = 'superLongSecretKeyForCookieManagement'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

@app.context_processor
def inject_user():
    return dict(user=current_user)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    projects = db.relationship("Project", backref="user")
    supplies = db.relationship("Supply", backref="user")

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    notes = db.Column(db.Text)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

class Supply(db.Model):
    __tablename__ = 'supply'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    brand = db.Column(db.String(255))
    purchase_link = db.Column(db.String(255))
    cost = db.Column(db.Numeric(10, 2))
    rating = db.Column(db.Numeric(3, 2))
    notes = db.Column(db.Text)
    image = db.Column(db.String(255))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

def database_insert(data):
    if isinstance(data, User):
        db.session.add(data)
    elif isinstance(data, Project):
        db.session.add(data)
    elif isinstance(data, Supply):
        db.session.add(data)
    db.session.commit()
def database_update(data):
    if isinstance(data, User):
        db.session.merge(data)
    elif isinstance(data, Project):
        db.session.merge(data)
    elif isinstance(data, Supply):
        db.session.merge(data)
    db.session.commit()
def database_getProjects():
    projects = Project.query.all()
    return projects
def database_getSupplies():
    supplies = Supply.query.all()
    return supplies
def database_getProject(project_id):
    project = db.session.get(Project, project_id)
    if project:
        return project
    else:
        return None
def database_getSupply(supply_id):
    supply = db.session.get(Supply, supply_id)
    if supply:
        return supply
    else:
        return None

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("index.html")

@app.route("/view_project")
def view_project():
    return redirect("/projects")

@app.route("/view_project/<project_id>")
def view_project_id(project_id):
    project = database_getProject(project_id)
    if not project:
        return redirect("/projects")
    project_details = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "image": project.image,
        "notes": project.notes,
    }
    return render_template("view_project.html", project_details=project_details)

@app.route("/create_project")
def create_project():
    return render_template("create_project.html")

@app.route("/create_project_submit", methods=["POST"])
def create_project_submit():
    name = request.form["project_name"]
    description = request.form["project_description"]
    notes = request.form["project_notes"]
    image = request.files['project_image']
    image_path = ""
    if image and image.filename:
        filename = secure_filename(image.filename)
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(full_path)
        image_path = f"/static/images/{filename}"
    else:
        image_path = ""
    database_insert(Project(name=name, description=description, image=image_path, notes=notes, owner=current_user.id))
    return redirect("/projects")

@app.route("/items")
def items():
    supplies = database_getSupplies()
    return render_template("items.html", supplies=supplies)

@app.route("/view_item")
def view_item():
    return redirect("/items")

@app.route("/view_item/<item_id>")
def view_item_id(item_id):
    supply = database_getSupply(item_id)
    if not supply:
        return redirect("/items")
    item_details = {
        "id": supply.id,
        "name": supply.name,
        "description": supply.description,
        "brand": supply.brand,
        "purchase_link": supply.purchase_link,
        "cost": supply.cost,
        "rating": supply.rating,
        "notes": supply.notes,
        "image": supply.image
    }
    return render_template("view_item.html", item_details=item_details)

@app.route("/register", methods=["GET", "POST"])
def register():
    ## WARNING: THIS IS NOT SECURED. DO NOT USE IN PRODUCTION
    if request.method == "POST":
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template("register.html")
        else:
            password = request.form["password"]
            cpassword = request.form["confirm"]
            if password != cpassword:
                return redirect("/")
            database_insert(User(username=username, password=password))
            return redirect("/")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    ## WARNING: THIS IS NOT SECURED. DO NOT USE IN PRODUCTION
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
            print("logged in user:", user.username)
        else:
            return render_template("login.html")
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/create_item")
def create_item():
    return render_template("create_item.html")

@app.route("/create_item_submit", methods=["POST"])
def create_item_submit():
    name = request.form.get("item_name", "Unnamed Item")
    description = request.form.get("item_description", "No Description")
    brand = request.form.get("item_brand", "No Brand")
    purchase_link = request.form.get("item_purchase_link", "No Purchase Link")
    cost_raw = request.form.get("item_cost", "0")
    rating_raw = request.form.get("item_rating", "0")
    cost = float(cost_raw) if cost_raw.strip() else 0.0
    rating = float(rating_raw) if rating_raw.strip() else 0.0
    notes = request.form.get("item_notes", "No Notes")
    image = request.files['item_image']
    image_path = ""
    if image and image.filename:
        filename = secure_filename(image.filename)
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(full_path)
        # Save URL-friendly path in database:
        image_path = f"/static/images/{filename}"
    else:
        image_path = ""
    database_insert(Supply(name=name, description=description, brand=brand, purchase_link=purchase_link, cost=cost, rating=rating, notes=notes, image=image_path, owner=current_user.id))
    return redirect("/items")

with app.app_context():
    db.create_all()
app.run(debug=True)
