import os
from sqlalchemy import case, desc
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bcrypt import hashpw, checkpw, gensalt

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

class ProjectImage(db.Model):
    __tablename__ = 'project_images'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    sale_price = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)
    images = db.relationship('ProjectImage', backref='project', lazy=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    items = db.relationship("ProjectItem", backref="project")

class ProjectItem(db.Model):
    __tablename__ = 'project_item'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('supply.id'))

class SupplyImage(db.Model):
    __tablename__ = 'supply_images'
    id = db.Column(db.Integer, primary_key=True)
    supply_id = db.Column(db.Integer, db.ForeignKey('supply.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)

class Supply(db.Model):
    __tablename__ = 'supply'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    brand = db.Column(db.String(55))
    item_type = db.Column(db.String(55))
    color = db.Column(db.String(55))
    purchase_link = db.Column(db.String(255))
    cost = db.Column(db.Numeric(10, 2))
    rating = db.Column(db.Numeric(3, 2))
    notes = db.Column(db.Text)
    image = db.Column(db.String(255))
    project_items = db.relationship("ProjectItem", backref="supply")
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    images = db.relationship('SupplyImage', backref='supply', lazy=True)

def database_insert(data):
    if isinstance(data, User):
        db.session.add(data)
    elif isinstance(data, Project):
        db.session.add(data)
    elif isinstance(data, Supply):
        db.session.add(data)
    elif isinstance(data, SupplyImage):
        db.session.add(data)
    elif isinstance(data, ProjectImage):
        db.session.add(data)
    elif isinstance(data, ProjectItem):
        db.session.add(data)
    db.session.commit()
def database_update(data):
    if isinstance(data, User):
        user = User.query.filter_by(id=data.id).first()
        if user:
            user.username = data.username
            user.password = data.password
    elif isinstance(data, Project):
        project = Project.query.filter_by(id=data.id).first()
        if project:
            project.name = data.name
            project.description = data.description
            project.image = data.image
            project.sale_price = data.sale_price
            project.notes = data.notes
            project.owner = data.owner
    elif isinstance(data, Supply):
        item = Supply.query.filter_by(id=data.id).first()
        if item:
            item.name = data.name
            item.description = data.description
            item.brand = data.brand
            item.item_type = data.item_type
            item.color = data.color
            item.purchase_link = data.purchase_link
            item.cost = data.cost
            item.rating = data.rating
            item.notes = data.notes
            item.image = data.image
    db.session.commit()
def database_getProjects(id):
    projects = Project.query.filter(Project.owner == id).all()
    return projects if projects else []
def database_getSupplies():
    supplies = Supply.query.filter(Supply.owner == current_user.id).all()
    return supplies if supplies else []
def database_getProject(project_id):
    project = db.session.get(Project, project_id)
    if project and project.owner == current_user.id:
        return project
    return None
def database_getSupply(supply_id):
    supply = db.session.get(Supply, supply_id)
    if supply and supply.owner == current_user.id:
        return supply
    return None
def database_findSupply(supply_name):
    supplies = Supply.query.filter(Supply.name.like(f"%{supply_name}%"), Supply.owner == current_user.id).all()
    return supplies if supplies else []
def database_findProject(project_name):
    projects = Project.query.filter(Project.name.like(f"%{project_name}%"), Project.owner == current_user.id).all()
    return projects if projects else []
def database_deleteItem(item_id):
    supply = db.session.get(Supply, item_id)
    if supply:
        db.session.delete(supply)
        db.session.commit()
def database_deleteProject(project_id):
    project = db.session.get(Project, project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
def database_deleteSupplyImage(image_path):
    image = SupplyImage.query.filter(SupplyImage.image_path == image_path).first()
    if image and image.supply.owner == current_user.id:
        db.session.delete(image)
        db.session.commit()
def database_deleteProjectImage(image_path):
    image = ProjectImage.query.filter(ProjectImage.image_path == image_path).first()
    if image and image.project.owner == current_user.id:
        db.session.delete(image)
def database_deleteProjectItem(project_item_id):
    project_item = db.session.get(ProjectItem, project_item_id)
    if project_item:
        db.session.delete(project_item)
        db.session.commit()
def database_multiparameter_item_search(search_terms):
    terms = search_terms.split(' ')
    OWNER_CONDITION = Supply.owner == current_user.id
    score_expr = None
    for term in terms:
        conditions = [
            case((Supply.name.like(f"%{term}%"), 1), else_=0),
            case((Supply.item_type.like(f"%{term}%"), 1), else_=0),
            case((Supply.brand.like(f"%{term}%"), 1), else_=0),
            case((Supply.color.like(f"%{term}%"), 1), else_=0)
        ]
        for condition in conditions:
            score_expr = condition if score_expr is None else score_expr + condition

    query = Supply.query.add_columns(score_expr.label("score")).filter(OWNER_CONDITION).filter(score_expr > 0)
    query = query.order_by(desc("score")).limit(25)
    
    scored_results = query.all()
    search_results = [row[0] for row in scored_results]
    return search_results if search_results else []

@app.route("/search")
def search():
    search_terms = request.args.get('query', '')
    search_type = request.args.get('type', '')
    if search_type == "item":
        results = database_multiparameter_item_search(search_terms)
    elif search_type == "project":
        results = database_findProject(search_terms)
    else:
        results = []
    if not results:
        results = []
    return render_template("search_results.html", results=results, search_type=search_type)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/")
def home():
    return redirect("/projects") if current_user.is_authenticated else render_template("projects.html", projects=[])

@app.route("/projects")
@login_required
def projects():
    project_list = database_getProjects(current_user.id)
    return render_template("projects.html", projects=project_list)

@app.route("/view_project")
@login_required
def view_project():
    return redirect("/projects")

@app.route("/view_project/<project_id>")
@login_required
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
        "sale_price": project.sale_price,
        "images": [img.image_path for img in project.images],
        "items": [item for item in project.items],
    }
    return render_template("view_project.html", project_details=project_details)

@app.route("/create_project", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        name = request.form.get("project_name", "Unnamed Project")
        description = request.form.get("project_description", "No Description")
        notes = request.form.get("project_notes", "No Notes")
        sale_price = request.form.get("project_sale_price", "0")
        image = request.files['project_image']
        image_path = ""
        if image and image.filename:
            filename = secure_filename(image.filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(full_path)
            image_path = f"/static/images/{filename}"
        else:
            image_path = ""
        new_project = Project(name=name, description=description, image=image_path, notes=notes, owner=current_user.id, sale_price=sale_price)
        database_insert(new_project)
        image_files = request.files.getlist("project_images")
        for file in image_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                full_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(full_path)
                image_path = f"/static/images/{filename}"
                new_image = ProjectImage(project_id=new_project.id, image_path=image_path)
                database_insert(new_image)
        return redirect("/projects")
    else:
        return render_template("create_project.html")
    
@app.route("/edit_project/<project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    if request.method == "POST":
        name = request.form.get("project_name", "Unnamed Project")
        description = request.form.get("project_description", "No Description")
        sale_price = request.form.get("project_sale_price", "0")
        notes = request.form.get("project_notes", "No Notes")
        image_path_pre = request.form.get("project_image_path", "No Image")
        image_path = ""
        if image_path_pre and image_path_pre != "No Image":
            image_path = image_path_pre
        else:
            image = request.files['project_image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(full_path)
                image_path = f"/static/images/{filename}"
            else:
                image_path = ""
        database_update(Project(id=project_id, name=name, description=description, image=image_path, notes=notes, owner=current_user.id, sale_price=sale_price))

        image_files = request.files.getlist("project_images")
        for file in image_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                full_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(full_path)
                image_path = f"/static/images/{filename}"
                new_image = ProjectImage(project_id=project_id, image_path=image_path)
                database_insert(new_image)
        

        return redirect("/projects")
    else:
        project = database_getProject(project_id)
        if not project:
            return redirect("/projects")
        project_details = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "sale_price": project.sale_price,
            "image": project.image,
            "notes": project.notes,
            "images": [img.image_path for img in project.images]
        }
        return render_template("edit_project.html", project_details=project_details)

@app.route("/delete_project/<project_id>")
@login_required
def delete_project(project_id):
    project = database_getProject(project_id)
    if not project or project.owner != current_user.id:
        return redirect("/projects")
    database_deleteProject(project_id)
    return redirect("/projects")

@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    project = database_getProject(request.args.get("project", None))
    item = database_getSupply(request.args.get("item", None))
    if project and item:
        database_insert(ProjectItem(project_id=project.id, item_id=item.id))
        return redirect("/view_project/" + str(project.id))
    query = request.args.get("query", None)
    if project and query:
        results = database_multiparameter_item_search(query)
        return render_template("add_item.html", project=project, results=results)
    if project:
        return render_template("add_item.html", project=project, results=[])
    return redirect("/projects")

@app.route("/remove_item/<item_id>")
@login_required
def remove_item(item_id):
    project_item = db.session.get(ProjectItem, item_id)
    if project_item:
        database_deleteProjectItem(project_item.id)
    return redirect("/view_project/" + str(project_item.project_id))
        
@app.route("/items")
@login_required
def items():
    supplies = database_getSupplies()
    return render_template("items.html", items=supplies)

@app.route("/view_item")
@login_required
def view_item():
    return redirect("/items")

@app.route("/view_item/<item_id>")
@login_required
def view_item_id(item_id):
    supply = database_getSupply(item_id)
    if not supply:
        return redirect("/items")
    item_details = {
        "id": supply.id,
        "name": supply.name,
        "description": supply.description,
        "brand": supply.brand,
        "item_type": supply.item_type,
        "color": supply.color,
        "purchase_link": supply.purchase_link,
        "cost": supply.cost,
        "rating": int(supply.rating),
        "notes": supply.notes,
        "image": supply.image,
        "images": [img.image_path for img in supply.images]
    }
    return render_template("view_item.html", item_details=item_details)

@app.route("/create_item", methods=["GET", "POST"])
@login_required
def create_item():
    if request.method == "POST":
        name = request.form.get("item_name", "Unnamed Item")
        description = request.form.get("item_description", "No Description")
        brand = request.form.get("item_brand", "No Brand")
        item_type = request.form.get("item_type", "Unknown Type")
        color = request.form.get("item_color", "No Color")
        purchase_link = request.form.get("item_purchase_link", "No Purchase Link")
        cost_raw = request.form.get("item_cost", "0")
        rating_raw = request.form.get("item_rating", "0")
        cost = float(cost_raw) if cost_raw.strip() else 0.0
        rating = float(rating_raw) if rating_raw.strip() else 0.0
        notes = request.form.get("item_notes", "No Notes")
        
        primary_image = ""
        image = request.files.get('item_image')
        if image and image.filename:
            filename = secure_filename(image.filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(full_path)
            primary_image = f"/static/images/{filename}"
        
        new_supply = Supply(name=name, description=description, brand=brand, item_type=item_type, 
                            color=color, purchase_link=purchase_link, cost=cost, rating=rating, 
                            notes=notes, image=primary_image, owner=current_user.id)
        database_insert(new_supply)
        
        image_files = request.files.getlist("item_images")
        for file in image_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                full_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(full_path)
                image_path = f"/static/images/{filename}"
                new_image = SupplyImage(supply_id=new_supply.id, image_path=image_path)
                database_insert(new_image)
        return redirect("/items")
    else:
        return render_template("create_item.html")
     
@app.route("/edit_item/<item_id>", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    supply = database_getSupply(item_id)
    if not supply:
        return redirect("/items")
    if request.method == "POST":
        name = request.form.get("item_name", "Unnamed Item")
        description = request.form.get("item_description", "No Description")
        brand = request.form.get("item_brand", "No Brand")
        item_type = request.form.get("item_type", "Unknown Type")
        color = request.form.get("item_color", "No Color")
        purchase_link = request.form.get("item_purchase_link", "No Purchase Link")
        cost_raw = request.form.get("item_cost", "0")
        rating_raw = request.form.get("item_rating", "0")
        cost = float(cost_raw) if cost_raw.strip() else 0.0
        rating = float(rating_raw) if rating_raw.strip() else 0.0
        notes = request.form.get("item_notes", "No Notes")
        image_path_pre = request.form.get("item_image_path", "No Image")
        image_path = ""
        if image_path_pre and image_path_pre != "No Image":
            image_path = image_path_pre
        else:
            image = request.files['item_image']
            image_path = ""
            if image and image.filename:
                filename = secure_filename(image.filename)
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(full_path)
                image_path = f"/static/images/{filename}"
            else:
                image_path = ""
        database_update(Supply(id=item_id, name=name, description=description, brand=brand, item_type=item_type, color=color, purchase_link=purchase_link, cost=cost, rating=rating, notes=notes, image=image_path))

        image_files = request.files.getlist("item_images")
        for file in image_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                full_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(full_path)
                image_path = f"/static/images/{filename}"
                new_image = SupplyImage(supply_id=item_id, image_path=image_path)
                database_insert(new_image)
    else:
        item_details = {
            "id": supply.id,
            "name": supply.name,
            "description": supply.description,
            "brand": supply.brand,
            "item_type": supply.item_type,
            "color": supply.color,
            "purchase_link": supply.purchase_link,
            "cost": supply.cost,
            "rating": supply.rating,
            "notes": supply.notes,
            "image": supply.image,
            "images": [img.image_path for img in supply.images]
        }
        return render_template("edit_item.html", item_details=item_details)
    return redirect("/items")

@app.route("/delete_item/<item_id>")
@login_required
def delete_item(item_id):
    supply = database_getSupply(item_id)
    if not supply or supply.owner != current_user.id:
        return redirect("/items")
    database_deleteItem(item_id)
    return redirect("/items")

@app.route("/delete_item_image")
@login_required
def delete_item_image():
    image_path = request.args.get("path")
    if image_path:
        database_deleteSupplyImage(image_path)
    return redirect("/items")

@app.route("/delete_project_image")
@login_required
def delete_project_image():
    image_path = request.args.get("path")
    if image_path:
        database_deleteProjectImage(image_path)
    return redirect("/projects")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect("/")
        password = request.form["password"]
        cpassword = request.form["confirm"]
        if password != cpassword:
            return redirect("/")
        hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
        database_insert(User(username=username, password=hashed_password))
        return redirect("/")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            print("logged in user:", user.username)
        else:
            return redirect("/")
        return redirect("/projects")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

with app.app_context():
    db.create_all()
app.run(debug=True)
