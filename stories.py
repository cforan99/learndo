
teacher = User.query.get(teacher_id)  ## Can I make this a global variable or store in session?


def create_class(teacher, class_name):
    """Teacher creates a new class"""

    new_class = Class(class_name=class_name)                
    new_class.users.append(teacher)
    db.session.add(new_class)
    db.session.commit()

    return class_name, "has been added."


def create_student(first, last, preferred, username, password, email, class_id, teacher):
    """Teacher creates new student accounts and add them to classes simultaneously"""

    if email == "":
        email == None

    if preferred == "":
        preferred == first

    new_student = User(is_teacher=0,
                       username=username,
                       password=password,
                       email=email,
                       first_name=first,
                       last_name=last,
                       display_name=preferred,
                       school=teacher.school)

    new_student.classes.append(Class.query.get(class_id))
    db.session.add(new_student)
    db.session.commit()

    ##FIGURE OUT HOW TO GET CLASS ID FROM DROP DOWN MENU

    return "A new account has been created for {} with the username {} and password {}.".format(preferred, username, password)


def show_classes(teacher):
    """Creates a dictionary of class name and list of student objects for each class_id
    associated with a teacher. Used for printing a list of all the classes for a teacher.

    Example: 
    {class_id: {'class_name': class_name, 'students': [<student object>, <student object>]}}
    """
    class_list = {}

    for each_class in t.classes:
        class_list[each_class.class_id] = {'class_name' : each_class.class_name }
        for student in each_class.users:
            if student.is_teacher == 0:
                if 'students' not in class_list[each_class.class_id]:
                    class_list[each_class.class_id]['students'] = []
                class_list[each_class.class_id]['students'].append(student)

    return class_list


def show_students(teacher):
    """Teacher views a list of the students in each class. 
    This can be editted to list all student information from the class_list dictionary."""

    class_list = show_classes(teacher)

    for class_id in class_list.keys():
        print class_list[class_id]['class_name']
        for student in class_list[class_id]['students']:
            print "\t", student.first_name, student.last_name


def edit_student(student_id):
    """Teacher can edit student information displayed in a table.
    Add later with jQuery: when a field is clicked a textbox with the student's current
    information appears and can be editted and saved through a form.
    And easier solution would be to just give the teacher access to the student's profile,
    and give her permission to view and edit the info there."""
    pass


def list_teachers(student_id):
    """Returns a list of teachers associated with that student"""

    student = User.query.get(student_id)
    teachers = []

    if student.is_teacher == 0:
        for each_class in student.classes:
            for user in each_class.users:
                if user.is_teacher == 1:
                    teachers.append(user.user_id)

    return teachers


def access_profile(user_id):
    """Does the user_id in session match the user_id in the route?
    Or does the user_id belong to that student's teacher?"""

    user = User.query.get(user_id)

    teachers = list_teachers(user_id)

    if session['user_id'] == user_id:
        return true
    else:
        for teacher_id in teachers:
            if session['user_id'] == teacher_id
                return true
            else:
                return false


def edit_profile(user_id, first, last, preferred, username, password, email):
    """Teachers and students can view and edit their own account information"""

    if access_profile(user_id):

        user = User.query.get(user_id)

        user.username=username
        user.password=password
        user.email=email
        user.first_name=first
        user.last_name=last
        user.display_name=preferred

        db.session.commit()

    #With AJAX, update form to show new information

    return "Your profile has been updated."


def remove_student(student_id, class_id):
    """Teacher can remove a student from a class"""

    this_class = Class.query.get(class_id)

    for student in this_class.users:
        if student.user_id == student_id:
            index = this_class.users.index(student)
            del this_class.users[index]

    db.session.commit()

    #flash message
    return "This student has been removed from your class."


def add_student(username, class_id):
    """Teacher can add existing student to class by username"""
    
    new_class = Class.query.get(class_id)
    try:
        user = User.query.filter(User.username == username).one()
        exists = True
    except:
        exists = False
        print "There is no student with that username."

    if exists:
        user.classes.append(new_class)

    db.session.commit()

    return "{} has been added to {}".format(user.preferred, new_class.class_name)
    

def create_teacher(first, last, preferred, username, password, email, class_id, teacher):
    """Teacher registers for a teacher account"""

    if preferred == "":
        preferred == first + " " + last

    new_student = User(is_teacher=1,
                       username=username,
                       password=password,
                       email=email,
                       first_name=first,
                       last_name=last,
                       display_name=preferred,
                       school=teacher.school)







