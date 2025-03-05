from flask import Flask, render_template, redirect, request

app = Flask(__name__, static_url_path="/static")

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

app.run(debug=True)