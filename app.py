from flask import Flask, render_template, redirect, request

app = Flask(__name__, static_url_path="/static")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/items")
def items():
    return render_template("items.html")

app.run(debug=True)
