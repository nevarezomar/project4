from flask import Flask, redirect, url_for, render_template

application = Flask(__name__)

@application.route("/")
@application.route("/home")
def home():
    return render_template("index.html", content=["HOME"])


@application.route("/<name>")
def name(name):
    return render_template("index.html", content=["tim", "omar", "bob"])

# EB looks for an 'application' callable by default.
application = Flask(__name__)

if __name__ == "__main__":
        application.run(debug=True)