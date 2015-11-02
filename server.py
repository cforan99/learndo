"""Learndo: An assignment tracker/notification system"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "This_should_be_secret"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage with registration form and login link"""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    first = request.form.get("first")
    last = request.form.get("last")
    preferred = request.form.get("preferred")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    school = request.form.get("school")
    teacher = request.form.get("teacher")

    print teacher

    if preferred == "":
        preferred = first + " " + last

    new_teacher = User(is_teacher=teacher,
                       username=username,
                       password=password,
                       email=email,
                       first_name=first,
                       last_name=last,
                       display_name=preferred,
                       school=school)

    db.session.add(new_teacher)
    db.session.commit()

    session["user_id"] = new_teacher.user_id

    flash("Your teacher account has been created with the username {} and password {}".format(username, password))
    
    return redirect("/")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
