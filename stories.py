
teacher = User.query.get(teacher_id)  ## Can I make this a global variable or store in session?


def create_class(teacher, class_name):
    """Teacher creates a new class"""

    new_class = Class(class_name=class_name)                
    new_class.users.append(teacher)
    db.session.add(new_class)
    db.session.commit()


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
    """Teacher views a list of the students in each class"""

    class_list = show_classes(teacher)

for class_id in class_list.keys():
    print class_list[class_id]['class_name']
    for student in class_list[class_id]['students']:
        print "\t", student.first_name, student.last_name


"""Teacher registers for a teacher account"""