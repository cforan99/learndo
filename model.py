"""Models and database functions for project"""

import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

##############################################################################
# Model definitions

class User(db.Model):
    """Information for students and teachers"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    is_teacher = db.Column(db.Boolean, nullable=False)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=True)
    display_name = db.Column(db.String(32), nullable=True)
    school = db.Column(db.String(64), nullable=True)

    classes = db.relationship("Class",
                             secondary='usersclasses',
                             backref="users")
    tasks = db.relationship('Task', backref='user')
    assignments = db.relationship('Assignment', backref='user')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%r username=%s>" % (self.user_id, self.username)


class Class(db.Model):
    """Names of classes by id"""

    __tablename__ = "classes"

    class_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    class_name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Class class_id=%r class_name=%s>" % (self.class_id, self.class_name)



class UserClass(db.Model):
    """Association table to connect many users to many classes"""

    __tablename__ = "usersclasses"

    ucid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)


class Task(db.Model):
    """A teacher can create many tasks"""

    __tablename__ = "tasks"

    task_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    title = db.Column(db.String(128), nullable=False)
    goal = db.Column(db.String(712), nullable=False)
    directions = db.Column(db.String(712), nullable=False)
    link = db.Column(db.String(256))
    due_date = db.Column(db.DateTime)
    assigned_to = db.Column(db.Integer, db.ForeignKey('classes.class_id'))

    assignments = db.relationship('Assignment', backref='task')
    assigned_class = db.relationship('Class', backref='tasks')

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Task task_id=%r title=%s created_by=%s>" % (self.task_id, self.title, self.created_by)

    @staticmethod
    def unassign(task_id):
        task = Task.query.get(task_id)
        for a in task.assignments:
            db.session.delete(a)
            db.session.commit()


class Assignment(db.Model):
    """How a task is assigned to many students"""

    __tablename__ = "assignments"

    assign_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    assigned = db.Column(db.DateTime)
    viewed = db.Column(db.DateTime)
    completed = db.Column(db.DateTime)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Assignment assign_id=%d task_id=%d student_id=%s>" % (self.assign_id, self.task_id, self.student_id)

    @staticmethod
    def unview(task_id, student_id):
        a = Assignment.query.filter(Assignment.task_id == task_id, Assignment.student_id == student_id).one()
        a.viewed = None
        a.completed = None
        db.session.commit()
        

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "postgresql:///learndo")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


def delete_assignments(task_id):
    """Deletes all assignments for a given task_id from db."""

    to_delete = Assignment.query.filter(Assignment.task_id == task_id).all()
    for assignment in to_delete:
        db.session.delete(assignment)
    db.session.commit()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."