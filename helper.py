from model import *
from flask import session

def add_class(teacher, class_name):
    """Teacher creates a new class"""

    new_class = Class(class_name=class_name)                
    new_class.users.append(teacher)
    db.session.add(new_class)
    db.session.commit()


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
        return True
    else:
        for teacher_id in teachers:
            if session['user_id'] == teacher_id:
                return True
            else:
                return False

