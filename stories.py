

def create_class(teacher_id, class_name):
	"""Teacher creates a new class"""

	teacher = User.query.get(teacher_id)  ## Can I make this a global variable or store in session?

	new_class = Class(class_name=class_name)                
	new_class.users.append(teacher)
	db.session.add(new_class)
	db.session.commit()


def create_student(first, last, preferred, username, password, email, class_id):
	"""Teacher creates new student accounts and add them to classes simultaneously"""

	teacher = User.query.get(teacher_id)

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




"""Teacher views a list of her classes"""

"""Teacher views a list of the students in each class"""

"""Teacher registers for a teacher account"""