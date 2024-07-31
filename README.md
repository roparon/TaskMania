# TaskMania: A Task Management Application

TaskMania is a web application built using Python and the Flask framework. It allows users to create, manage, and track their tasks efficiently. The application features user registration, login, and task creation with various customization options.

## Features

- User Registration: Users can create an account by providing a username, email, and password.
- User Login: Registered users can log in to their accounts using their username and password.
- Task Creation: Logged-in users can create tasks by providing a title, description, category, and due date.
- Task Status: Users can mark tasks as completed or pending.
- Task Search: Users can search for tasks based on their title, description, or category.
- Task Sorting: Users can sort tasks based on their due date, title, or category.
- Task Editing: Users can edit the details of their tasks.
- Task Deletion: Users can delete tasks permanently.
- User Profile: Logged-in users can update their profile information, including their profile picture.

## How to Collaborate and Clone the Project

1. Install Python and Flask on your local machine.
2. Clone the project repository using Git: `git clone https://github.com/roparon/TaskMania.git`
3. Navigate to the project directory: `cd TaskMania`
4. Create a virtual environment: `python -m venv venv`
5. Activate the virtual environment:
   - For Windows: `venv\Scripts\activate`
   - For macOS/Linux: `source venv/bin/activate`
6. Install the required dependencies: `pip install -r requirements.txt`
7. Set up the database:
   - Create a PostgreSQL database named "taskmania".
   - Update the database connection string in the `app.config` dictionary in the `app.py` file.
   - Run the following commands to create the database tables:
     - `python`
     - `from app import db`
     - `db.create_all()`
     - `exit()`
8. Run the application: `python app.py`
9. Access the application in your web browser by visiting `http://localhost:5000`.

## About Africode Academy

Africode Academy is an organization dedicated to fostering digital skills and empowering young people in Africa. Our mission is to create a diverse and inclusive coding community that empowers individuals to build their careers and contribute to the global tech ecosystem.

We offer a variety of coding programs, including beginner-friendly courses, advanced workshops, and mentorship programs. Our curriculum is designed to be accessible and engaging for students of all ages and backgrounds. We believe that coding is a powerful tool for empowerment and social change, and we strive to create a supportive and inclusive learning environment for all students.

For more information about Africode Academy, please visit our website at [africodeacademy.com](https://africodeacademy.com).
