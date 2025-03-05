from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__, static_url_path="/static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final.db'
app.config['SECRET_KEY'] = 'superLongSecretKeyForCookieManagement'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

class Thing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    color = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    creator = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    things = db.relationship("Thing", backref="creator_user")

@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid)

#####################################-| USER ROUTES |-##########################################

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
        else:
            return render_template("login.html", error="badc")
        return redirect("/read")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template("register.html", error="dupu")
        else:
            password = request.form["password"]
            cpassword = request.form["confirm"]
            if password != cpassword:
                return render_template("register.html", error="badp")
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return render_template("login.html", error="succ")
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect("/view")
    return redirect("/login")

#####################################-| THING ROUTES |-##########################################

@app.route("/view")
def view():
    things = Thing.query.all()
    return render_template("view.html", things=things)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        name = request.form["name"]
        color = request.form["color"]
        quantity_check = request.form["quantity"]
        error = inputValidation(quantity_check)
        if error != "":
            return render_template("error.html", error=error)
        quantity = int(quantity_check)
        thing = Thing(name=name, color=color, quantity=quantity, creator=current_user.id)
        db.session.add(thing)
        db.session.commit()
        return redirect("/read")
    return render_template("create.html")

@app.route("/read")
@login_required
def read():
    things = Thing.query.filter_by(creator=current_user.id).all()
    return render_template("read.html", things=things)

@app.route("/update", methods=["POST"])
@login_required
def update():
    if request.method == "POST":
        id = request.form["id"]
        thing = Thing.query.filter_by(id=id).first()
        name = thing.name
        color = thing.color
        quantity = thing.quantity
        return render_template("update.html", thing=thing)
    return render_template("error.html", error="noop")

@app.route("/update_object", methods=["POST"])
@login_required
def update_object():
    id = request.form["id"]
    name = request.form["name"]
    color = request.form["color"]
    quantity_check = request.form["quantity"]
    error = inputValidation(quantity_check)
    if error != "":
        return render_template("error.html", error=error)
    quantity = int(quantity_check)
    thing = Thing.query.filter_by(id=id).first()
    thing.name = name
    thing.color = color
    thing.quantity = quantity
    if thing.creator != current_user.id:
        return render_template("error.html", error="e401")
    db.session.commit()
    return redirect("/read")

@app.route("/delete", methods=["POST"])
@login_required
def delete():
    if request.method == "POST":
        id = request.form["id"]
        thing = Thing.query.filter_by(id=id).first()
        if thing.creator != current_user.id:
            return render_template("error.html", error="e401")
        db.session.delete(thing)
        db.session.commit()
        return redirect("/read")
    return render_template("error.html", error="noop")

#####################################-| OTHER FUNCTIONS |-##########################################

@app.route("/secret")
@login_required
def secret():
    return current_user.username

@app.route("/madlibs")
@login_required
def madlibs():
    things = Thing.query.all()
    if len(things) == 0:
        return render_template("madlibs.html", names=things[0].name)
    names = ""
    for thing in things:
        names += thing.name + " "
    return render_template("madlibs.html", names=names)

@app.errorhandler(404)
def err404(err):
    return render_template("error.html", error="e404")

@app.errorhandler(401)
def err401(err):
    return render_template("error.html", error="e401")

def inputValidation(check):
    try:
        int(check)
    except ValueError:
        return "noin"
    if int(check) == 0:
        return "not0"
    return ""

with app.app_context():
    db.create_all()
app.run(debug=True)