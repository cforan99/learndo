from model import *
from flask import session

def add_class(teacher, class_name):
    """Create a new class in db and add the teacher to the class"""

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


def json_classes(teacher):
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
                    class_list[each_class.class_id]['students'] = {}
                class_list[each_class.class_id]['students'][student.user_id] =  { 'first' : student.display_name,
                                                                                  'last' : student.last_name,
                                                                                  'username' : student.username }

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

def find_class_by_task(task_id):
    """Finds class name given the task id so it can be displayed on the task page"""

    task = Task.query.get(task_id)

    teacher_id = task.created_by
    teacher = User.query.get(teacher_id)
    list_of_classes = teacher.classes 

    class_dictionary = {}  # key = class_id, value1 = class_name, value2 = student_ids_list

    for c in list_of_classes:
        class_dictionary[c.class_id] = { 'name' : c.class_name, 'users' : [] }
        for user in c.users:
            class_dictionary[c.class_id]['users'].append(user.user_id)
        class_dictionary[c.class_id]['users'].sort()

    assignment_list = Assignment.query.filter(Assignment.task_id == task_id).all()

    assigned_users = []

    for assignment in assignment_list:
        assigned_users.append(assignment.student_id)

    assigned_users.sort()

    for c in class_dictionary:
        if class_dictionary[c]['users'] == assigned_users:
            assigned_class = class_dictionary[c]['name']

        return assigned_class

def report_student_progress(task, assignment_list):
    """Generates a dictionary of students associated with the task's assignment and
    their progress status. The student_id is the key and the values are first, last, 
    assigned, viewed, completed, overdue."""

    student_progress = {}
    now = datetime.now()

    for assignment in assignment_list:
        if not assignment.user.is_teacher:
            student_id = assignment.student_id
            first_name = assignment.user.first_name
            last_name = assignment.user.last_name
            assigned = assignment.assigned.strftime("%A %m/%d/%y %I:%M %p")
            if assignment.viewed:
                viewed = assignment.viewed.strftime("%A %m/%d/%y %I:%M %p")
            else:
                viewed = None
            if assignment.completed:
                completed = assignment.completed.strftime("%A %m/%d/%y %I:%M %p")
                overdue = False
            else:
                completed = None
                due_date = task.due_date
                if now > due_date:
                    overdue = True
                else:
                    overdue = False
            student_progress[student_id] = { 'first' : first_name,
                                             'last' : last_name,
                                             'assigned' : assigned,
                                             'viewed' : viewed,
                                             'completed' : completed,
                                             'overdue' : overdue }

    return student_progress

def create_assignment_list(assignments_list, sort):
    """Generates a dictionary with all the info needed for the assignment list feature."""

    assignments = {}

    if session['acct_type'] == 'student':

        for assignment in assignments_list:

            if sort == 'new':
                dt = assignment.assigned
                ut = (dt - datetime(1970,1,1)).total_seconds()
            if sort == 'due':
                dt = assignment.task.due_date
                ut = (dt - datetime(1970,1,1)).total_seconds()
                ut = ut + float("."+str(assignment.task_id))
            
            assignments[ut] = {}
            assignments[ut]['id'] = assignment.assign_id
            assignments[ut]['title'] = assignment.task.title
            assignments[ut]['goal'] = assignment.task.goal
            assignments[ut]['due_date'] = assignment.task.due_date.strftime("%A %m/%d/%y %I:%M %p")
            assignments[ut]['assigned_by'] = db.session.query(User.display_name).filter(
                                             User.user_id == (assignments_list[0].task.created_by)).first()
            assignments[ut]['assigned_on'] = assignment.assigned.strftime("%A %m/%d/%y %I:%M %p")
            assignments[ut]['status'] = check_student_status(assignment)

    if session['acct_type'] == 'teacher':

        for assignment in assignments_list:

            if sort == 'new':
                dt = assignment.assigned
                ut = (dt - datetime(1970,1,1)).total_seconds()
            if sort == 'due':
                dt = assignment.task.due_date
                ut = (dt - datetime(1970,1,1)).total_seconds()
                ut = ut + float("."+str(assignment.task_id))

            assignments[ut] = {}
            assignments[ut]['id'] = assignment.assign_id
            assignments[ut]['title'] = assignment.task.title
            assignments[ut]['goal'] = assignment.task.goal
            assignments[ut]['due_date'] = assignment.task.due_date.strftime("%A %m/%d/%y %I:%M %p")
            assignments[ut]['assigned_to'] = find_class_by_task(assignment.task.task_id)
            assignments[ut]['assigned_on'] = assignment.assigned.strftime("%A %m/%d/%y %I:%M %p")
            assignments[ut]['status'] = check_class_status(assignment)

    return assignments


def check_student_status(assignment):
    """Checks assignment object for status as viewed, completed, or overdue."""
    if assignment.viewed: 
        if assignment.completed:
            status = 'completed'
        elif datetime.now() > assignment.task.due_date:
            status = 'overdue'
        else: 
            status = 'viewed'
    else:
        status = 'inactive'
    return status


def check_class_status(assignment):
    """Checks assignment object for status as viewed, completed, or overdue."""

    if assignment.assigned: 
        student_assignments = Assignment.query.filter(Assignment.task_id == assignment.task_id).all()
        for assignment in student_assignments:
            if assignment.student_id != session['user_id']:
                if assignment.completed == None:
                    if datetime.now() > assignment.task.due_date:
                        status = 'overdue'
                        break
                    else:
                        status = 'viewed'
                        break
                elif assignment.completed:
                    status = 'completed'
    else:
        status = 'inactive'

    return status
