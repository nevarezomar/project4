from flask import Flask, redirect, url_for, render_template

application = Flask(__name__)

@application.route("/")
@application.route("/home")
def home():
    return 'Hello man.'


@application.route("/<name>")
def name(name):
    return render_template("index.html", content=["tim", "omar", "bob"])

if __name__ == "__main__":
        application.run(debug=True)