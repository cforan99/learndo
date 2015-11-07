"""Learndo: An assignment tracker/notification system"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime

from model import connect_to_db, db, User, Class
from helper import *


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

############### REGISTRATION ###############

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

    # Check to see if username is available
    if len(User.query.filter(User.username == username).all()) > 0:
        flash("That username is already in use. Please choose another.")
        return redirect('/register')

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
    session["acct_type"] = 'teacher'

    flash("Your teacher account has been created with the username {} and password {}".format(username, password))
    
    return redirect("/teacher/{}".format(new_teacher.user_id))


############### LOGIN / LOGOUT ###############

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

    if user.is_teacher:
        session["acct_type"] = 'teacher'
    else:
        session["acct_type"] = 'student'

    flash("You are now logged in!")

    if user.is_teacher:
        return redirect("/teacher/%s" % user.user_id)
    else:
        return redirect("/student/%s" % user.user_id)


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    del session["acct_type"]
    flash("You are logged out.")
    return redirect("/")


############### TEACHER VIEWS ###############

@app.route('/teacher/<int:user_id>')
def show_teacher_dashboard(user_id):
    """Initially shows links to messages, tasks, classes, and create a new task"""

    if session['user_id'] == user_id:
        teacher = User.query.get(user_id)  ## Can I make this a global variable or store in session?
        return render_template("tdashboard.html", teacher=teacher)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


@app.route('/teacher/<int:user_id>/assignments')
def show_teacher_assignments(user_id):
    """Lists assignments created by a teacher"""

    if session['user_id'] == user_id:
        teacher = User.query.get(user_id)  ## Can I make this a global variable or store in session?
        tasks = teacher.tasks

        return render_template("tassignments.html", teacher=teacher, tasks=tasks)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


############### CLASSES ###############
@app.route('/teacher/<int:user_id>/classes', methods=['GET'])
def manage_classes(user_id):
    """Shows class lists and student lists. Teacher can also add classes and students."""

    if session['user_id'] == user_id:
        teacher = User.query.get(user_id) ## Can I make this a global variable or store in session?
        class_list = show_classes(teacher)
        return render_template("class_list.html", teacher=teacher, class_list=class_list)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


@app.route('/new_class', methods=['POST'])
def create_class():
    """Adds new class to db"""

    #Get form variables
    user_id = request.form.get("teacher")
    class_name = request.form.get("class_name")

    teacher = User.query.get(user_id)

    add_class(teacher, class_name)

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


@app.route('/delete_class', methods=["POST"])
def delete_class():
    """Deletes class from db when teacher clicks link in manage classes dashboard."""

    class_id = request.form.get('class_id')
    this_class = Class.query.get(class_id)

    print class_id, "*****************"

    users = this_class.users

    authorized = False
    for user in users:
        if user.is_teacher and user.user_id == session['user_id']:
            authorized = True

    if authorized:
        db.session.delete(this_class)
        db.session.commit()
        # Why are the next two lines not being run?
        flash("The class, {}, has been deleted.".format(this_class.class_name))
        return redirect('/teacher/{}/classes'.format(session['user_id']))
    # This does run after the confirm popup.
    else:
        flash("You are not authorized to make this change.")
        return redirect("/")


@app.route('/remove_student', methods=["POST"])
def remove_student():
    """Deletes class from db when teacher clicks link in manage classes dashboard."""

    student_id = request.form.get('user_id')
    class_id = request.form.get('class_id')

    print student_id, class_id, "*****************"

    user_class = UserClass.query.filter(UserClass.user_id==student_id, 
                                        UserClass.class_id==class_id).one()

    this_student = User.query.get(student_id)

    user = User.query.get(session['user_id'])

    authorized = False
    if user.is_teacher:
        authorized = True

    if authorized:
        db.session.delete(user_class)
        db.session.commit()

        flash("{} has been removed from that class.".format(this_student.display_name))
        return redirect('/teacher/{}/classes'.format(session['user_id']))

    else:
        flash("You are not authorized to make this change.")
        return redirect("/")
    

@app.route('/new_student', methods=['POST'])
def create_student():
    """Teacher creates new student accounts and add them to classes simultaneously"""

    # Get form variables
    first = request.form.get("first")
    last = request.form.get("last")
    preferred = request.form.get("preferred")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    class_id = request.form.get("class-id")
    teacher_id = request.form.get("teacher")

    # Check to see if username is available
    if len(User.query.filter(User.username == username).all()) > 0:
        flash("That username is already in use. Please choose another.")
        return redirect('/teacher/{}/classes'.format(teacher_id))

    if email == "":
        email = None

    if preferred == "":
        preferred = first

    teacher = User.query.get(teacher_id)

    new_student = User(is_teacher=0,
                       username=username,
                       password=password,
                       email=email,
                       first_name=first,
                       last_name=last,
                       display_name=preferred,
                       school=teacher.school)

    print class_id

    new_student.classes.append(Class.query.get(class_id))
    db.session.add(new_student)
    db.session.commit()
    
    flash("A new account has been created for {} with the username {} and password {}.".format(preferred, username, password))
    return redirect('/teacher/{}/classes'.format(teacher_id))


############### PROFILES ###############
@app.route('/profile/<int:user_id>')
def load_profile(user_id):
    """Renders template for profile page for both students and teachers"""

    user = User.query.get(user_id)

    if user.is_teacher:
        acct_type = 'Teacher'
    else:
        acct_type = 'Student'

    my_classes = []
    for each_class in user.classes:
        my_classes.append(each_class.class_name)

    if access_profile(user_id) == True:
        return render_template("profile.html", user=user, my_classes=my_classes, acct_type=acct_type)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    """Users can change their profile information"""

    # Get form variables
    first = request.form.get("first")
    last = request.form.get("last")
    preferred = request.form.get("preferred")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    school = request.form.get("school")
    user_id = request.form.get("user_id")

    if email == "" or "None":
            email = None

    if preferred == "" or "None":
            preferred = first

    user = User.query.get(user_id)

    # Check to see if username is available
    if len(User.query.filter(User.username == username).all()) > 0 and username != user.username:
        flash("That username is already in use. Please choose another.")
        return redirect('/profile/{}'.format(user_id))
    else:
        user.first_name = first
        user.last_name = last
        user.display_name = preferred
        user.email = email
        user.username = username
        user.password = password
        user.school = school

        db.session.commit()
    
        flash("Your changes have been successfully saved!")
        return redirect('/profile/{}'.format(user_id))


############### STUDENT VIEWS ###############
@app.route('/student/<int:user_id>')
def show_student_dashboard(user_id):
    """Initially shows links to messages and tasks"""

    if session['user_id'] == user_id:
        student = User.query.get(user_id)  ## Can I make this a global variable or store in session?
        return render_template("sdashboard.html", student=student)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


@app.route('/student/<int:user_id>/assignments')
def show_student_assignments(user_id):
    """Lists assignments assigned to a student"""

    if session['user_id'] == user_id:
        student = User.query.get(user_id)  ## Can I make this a global variable or store in session?
        assignments = db.session.query(Assignment).filter(Assignment.student_id == 
            user_id).order_by(Assignment.assigned.desc()).all()

        return render_template("sassignments.html", student=student, assignments=assignments)

    else:
        flash("You do not have access to that page.")
        return redirect("/")


############### ASSIGNMENTS ###############

@app.route('/new_assignment')
def show_assignment_form():
    """Form for creating new assignments"""

    user = User.query.get(session['user_id'])

    if user.is_teacher:
        return render_template("new_assignment.html", user=user)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


@app.route('/create_assignment', methods=["POST"])
def create_assignment():
    """Adds info from assignment form into the tasks table in the db."""

    title = request.form.get("title")
    goal = request.form.get("goal")
    directions = request.form.get("directions")
    link = request.form.get("link")
    month = request.form.get("month")
    day = request.form.get("day")
    year = request.form.get("year")
    hour = request.form.get("hour")
    minute = request.form.get("minute")
    ampm = request.form.get("ampm")
    points = int(request.form.get("points"))
    teacher_id = request.form.get("teacher_id")

    if points == "":
        points = None

    date_string = "{}/{}/{} {}:{} {}".format(month, day, year, hour, minute, ampm)
    due_date = datetime.strptime(date_string, "%m/%d/%y %I:%M %p")

    user = User.query.get(session['user_id'])

    if user.is_teacher:

        new_task = Task(created_by=teacher_id,
                        title=title,
                        goal=goal,
                        directions=directions,
                        link=link,
                        points=points,
                        due_date=due_date)

        db.session.add(new_task)
        db.session.commit()

        task_id = new_task.task_id

        return redirect("/teacher/{}/assignments/{}".format(teacher_id, task_id))

    else:
        flash("You are not authorized to make this change.")
        return redirect("/")


@app.route('/teacher/<int:teacher_id>/assignments/<int:task_id>')
def view_assignment(teacher_id, task_id):
    """Shows assignment information, assign button or class assigned to, and list of students
    working on that assignment and their progress"""

    task = Task.query.get(task_id)
    date_obj = task.due_date
    due_date = date_obj.strftime("%m/%d/%y %I:%M %p")

    created_by = task.user

    class_list = show_classes(created_by)

    # assignment = task.assignments.filter(student_id == teacher_id)
    # Left off here 11/5 trying to id assigned status and class assigned to

    user_id = session['user_id']

    if user_id == task.created_by:
        return render_template("view_assignment.html", task=task, due_date=due_date, class_list=class_list)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


@app.route('/teacher/<int:teacher_id>/assignments/<int:task_id>/edit', methods=["GET"])
def edit_assignment_form(teacher_id, task_id):
    """Shows assignment information in an editable form"""

    print task_id

    teacher = User.query.get(teacher_id)
    task = Task.query.get(task_id)

    print task

    #Unpack due_date into month, day, year, hour, minute, ampm

    if session['user_id'] == teacher_id:
        return render_template("edit_assignment.html", teacher=teacher, task=task)
    else:
        flash("You do not have access to that page.")
        return redirect("/")


@app.route('/edit_assignment', methods=["POST"])
def edit_assignment():
    """Update the db with assignment edits from teacher"""

    # Get form variables
    title = request.form.get("title")
    goal = request.form.get("goal")
    directions = request.form.get("directions")
    link = request.form.get("link")
    month = request.form.get("month")
    day = request.form.get("day")
    year = request.form.get("year")
    hour = request.form.get("hour")
    minute = request.form.get("minute")
    ampm = request.form.get("ampm")
    points = int(request.form.get("points"))
    teacher_id = request.form.get("teacher_id")
    task_id = request.form.get("task_id")

    if points == "":
        points = None

    date_string = "{}/{}/{} {}:{} {}".format(month, day, year, hour, minute, ampm)
    due_date = datetime.strptime(date_string, "%m/%d/%y %I:%M %p")

    user = User.query.get(user_id)

    # Check to see if username is available
    if teacher_id == task.created_by:

        task.title = title
        task.goal = goal
        task.directions = directions
        task.link = link
        task.points = points
        task.due_date = due_date

        db.session.commit()
    
        flash("Your changes have been successfully saved!")
        return redirect('/profile/{}'.format(user_id))



@app.route('/assign', methods=["POST"])
def assign_to_class():
    """Assigns task to all users, students and teachers, associated with the selected class."""

    class_id = request.form.get("class-id")
    task_id = request.form.get("task_id")

    task = Task.query.get(task_id)
    this_class = Class.query.get(class_id)
    class_list = this_class.users

    if session['user_id'] == task.created_by:
        for user in class_list:
            new_assignment = Assignment(student_id=user.user_id,
                                        task_id=task_id,
                                        assigned=datetime.now())
            db.session.add(new_assignment)

        db.session.commit()

        flash("This has been successfully assigned to {}".format(this_class.class_name))
        return redirect("/teacher/{}/assignments/{}".format(task.created_by, task_id))
    
    else:
        flash("You are not authorized to make this change.")
        return redirect("/")



# #THIS WORKS BUT I WILL NOT USE IT UNTIL START ANGULAR
# @app.route('/profile/<int:user_id>.json')
# def view_profile(user_id):
#     """Returns JSON object of user info from db to display on profile page"""

#     user = User.query.get(user_id)

#     if user.is_teacher:
#         acct_type = 'teacher'
#     else:
#         acct_type = 'student'

#     my_classes = []
#     for each_class in user.classes:
#         my_classes.append(each_class.class_name)

#     profile_info = {
#         'first' : user.first_name,
#         'last' : user.last_name,
#         'preferred' : user.display_name,
#         'email' : user.email,
#         'username' : user.username,
#         'password' : user.password,
#         'school' : user.school,
#         'classes' : my_classes
#     }

#     if access_profile(user_id) == True:
#         return jsonify(profile_info)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
