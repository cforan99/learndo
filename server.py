"""Learndo: An assignment tracker/notification system"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Class


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "This_should_be_secret"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage with registration form and login link"""

    return render_template("homepage.html")

#### REGISTRATION ####

@app.route('/register', methods=['GET'])
def register_form():

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

#### LOGIN / LOGOUT ####

@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")

    if user.is_teacher:
        return redirect("/teacher/%s" % user.user_id)
    else:
        return redirect("/student/%s" % user.user_id)


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")


#### TEACHER VIEWS ####

@app.route('/teacher/<int:user_id>')
def show_teacher_dashboard(user_id):
    """Initially shows links to messages, tasks, classes, and create a new task"""

    if session['user_id'] == user_id:
        teacher = User.query.get(user_id)  ## Can I make this a global variable or store in session?
        return render_template("tdashboard.html", teacher=teacher)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


@app.route('/teacher/<int:user_id>/classes', methods=['GET'])
def manage_classes(user_id):
    """Shows class lists and student lists. Teacher can also add classes and students."""

    if session['user_id'] == user_id:
        teacher = User.query.get(user_id)  ## Can I make this a global variable or store in session?

        class_list = show_classes(teacher)

        return render_template("class_list.html", teacher=teacher, class_list=class_list)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


def show_classes(teacher):
    """Creates a dictionary of class name and list of student objects for each class_id
    associated with a teacher. Used for printing a list of all the classes for a teacher.

    Example: 
    {class_id: {'class_name': class_name, 'students': [<student object>, <student object>]}}
    """
    class_list = {}

    for each_class in teacher.classes:
        class_list[each_class.class_id] = {'class_name' : each_class.class_name }
        for student in each_class.users:
            if student.is_teacher == 0:
                if 'students' not in class_list[each_class.class_id]:
                    class_list[each_class.class_id]['students'] = []
                class_list[each_class.class_id]['students'].append(student)

    return class_list


@app.route('/new_class', methods=['POST'])
def create_class():
    """Adds new class to db"""

    #Get form variables
    user_id = request.form.get("teacher")
    class_name = request.form.get("class_name")

    teacher = User.query.get(user_id)

    new_class = Class(class_name=class_name)                
    new_class.users.append(teacher)
    db.session.add(new_class)
    db.session.commit()

    flash("{} has been added.".format(class_name))
    return redirect('/teacher/{}/classes'.format(user_id))

@app.route('/add_student', methods=['POST'])
def add_student():
    """Teacher can add existing student to class by username"""
    
    # Get variables from form
    username = request.form.get('username')
    class_id = request.form.get('class-id')
    teacher_id = request.form.get("teacher")

    new_class = Class.query.get(class_id)

    try:
        user = User.query.filter(User.username == username).one()
        exists = True
    except:
        exists = False
        flash("There is no student with that username.")
        return redirect('/teacher/{}/classes'.format(teacher_id))

    if exists:
        user.classes.append(new_class)

    db.session.commit()

    flash("{} has been added to {}".format(user.first_name, new_class.class_name))
    return redirect('/teacher/{}/classes'.format(teacher_id))
 

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
