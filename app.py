from flask import Flask, render_template, redirect, request

app = Flask(__name__, static_url_path="/static")
app.config['SECRET_KEY'] = 'superLongSecretKeyForCookieManagement'

@app.route("/")
def home():
    return render_template("template.html")

app.run(debug=True)