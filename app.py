import secrets
from flask import Flask, render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,TextAreaField,BooleanField,DateField
from wtforms.validators import DataRequired,ValidationError,Length,EqualTo
from datetime import datetime,timedelta
from flask_login import UserMixin




# Create the Flask application object
app = Flask(__name__)

# Generate a secret key for the application
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://Captain: @localhost:5432/taskmaniadb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize the database
db = SQLAlchemy(app)

# Define the Task model
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(200), unique=False, nullable=False)
    status = db.Column(db.String(20), default='Incomplete')
    date_created = db.Column(db.Date)
    date_due = db.Column(db.Date)
    date_completed = db.Column(db.Date) 

    def __repr__(self):
        return f' {self.title} {self.description} {self.date_created} {self.date_due} {self.status} {self.date_completed}'


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    #tasks = db.relationship('Task', backref='user', lazy=True)

# Create the database tables
# app.app_context().push()
# db.create_all()

#Define TaskForm class
class TaskForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_due_date(form, field):
        due_date = field.data
        if due_date < datetime().date():
            raise ValidationError('Due date cannot be in the past.')
    def __init__(self):
        super(TaskForm, self).__init__()
        self.due_date.data = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    rememberMe = BooleanField('Remember Me')
    submit = SubmitField('Login')
    # def __init__(self):
    #     super(LoginForm, self).__init__()
    #     self.rememberMe.data = True


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)],render_kw={'placeholder':'username'})
    password = StringField('Password', validators=[DataRequired(), Length(min=6, max=20)],render_kw={'placeholder':'password'})
    confirm_password = StringField('Confirm Password', validators=[DataRequired(),EqualTo(password)],render_kw={'placeholder':'confirm password'})
    submit = SubmitField('Register')

    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username already exists.')
        


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            # Login successful
            return redirect(url_for('index'))
        else:
            # Login failed
            return 'Login failed. Please check your username and password.'
    return render_template('login.html', form=form)     




@app.route('/',methods=['GET', 'POST'])
def index():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(title=form.title.data, description=form.description.data, date_due=form.due_date.data)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('index.html',form=form)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 