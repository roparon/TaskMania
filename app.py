import os
import secrets
from flask import Flask
from flask import redirect,url_for,render_template,flash,request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_login import UserMixin,current_user,LoginManager,login_user,logout_user,login_required
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,TextAreaField,BooleanField,SelectField,DateField,PasswordField
from wtforms.validators import DataRequired,ValidationError,Length,EqualTo,Email
from flask_wtf.file import FileField,FileAllowed
from datetime import datetime,timedelta
from PIL import Image




# Create the Flask application object
app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Generate a secret key for the application
app.config['SECRET_KEY'] = secrets.token_hex(16)
# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://captain: @localhost:5432/taskmania'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize the database
db = SQLAlchemy(app)


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    profile_picture = db.Column(db.String(20), nullable=False, default = 'default.jpeg')
    tasks = db.relationship('Task', backref='users', lazy='dynamic')


# Define the Task model
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Boolean, default=False,nullable=False)
    date_created = db.Column(db.Date,default= datetime.now)
    date_due = db.Column(db.Date,nullable=False,default=datetime.now)
    date_completed = db.Column(db.Date,default= datetime.now) 
    category = db.Column(db.String(50),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    

    def __repr__(self):
        return f'{self.title} {self.description} {self.date_due} {self.category} {self.status}'



# Create the database tables
app.app_context().push()
db.create_all()



class TaskForm(FlaskForm):
    title = StringField(validators=[DataRequired()],render_kw={'placeholder':'Title'})
    description = TextAreaField(validators=[DataRequired()],render_kw={'placeholder':'Description'})
    category = SelectField(choices=[
            ('general', 'General'), 
            ('work', 'Work'), 
            ('personal', 'Personal'), 
            ('other', 'Other')
        ],validators=[DataRequired()],render_kw={'placeholder':'General'})
    date_due = DateField(validators=[DataRequired()],render_kw={'placeholder':datetime.strptime("21/11/06 ", "%d/%m/%y ")})
    submit = SubmitField('Create Task')

    def validate_date_due(form, field):
        date_due = field.data
        if date_due < datetime.now().date():
            raise ValidationError('Due date cannot be in the past.')
           
           
        def __init__(self,*args,**kwargs):
            super(TaskForm, self).__init__(*args,**kwargs)
            self.date_due.data = (datetime.now + timedelta(days=7)).strftime('%Y-%m-%d')
           


class RegistrationForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired(), Length(min=3, max=20)],render_kw={'placeholder':'Username'})
    email = StringField('Email:',validators=[DataRequired(), Email()],render_kw={'placeholder':' Email address'})
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=6, max=20)],render_kw={'placeholder':'Password (min of 8 characters)'})
    confirm_password = PasswordField('Confirm Password:', validators=[DataRequired(),EqualTo('password',message='The passwords you entered do not match.')],render_kw={'placeholder':'Confirm password'})
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please enter a different one.')
        
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email exists. Please enter a different one!")



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],render_kw={'placeholder':'Username'})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={'placeholder':'Password '})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=3, max=20)],render_kw={'placeholder':'Enter username '})
    email = StringField('Email',validators=[DataRequired(), Email()],render_kw={'placeholder':'Enter email address '})
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("That username is taken.Please choose a different one!")
            

    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("That email is taken.Please choose a different one!")     



@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))


@app.route('/',methods=['GET', 'POST'])
@login_required
def index():
    form = TaskForm()
    if form.validate_on_submit():
        try:    
            task = Task(title=form.title.data,description=form.description.data,category=form.category.data,date_due=form.date_due.data,user_id=current_user.id)
            db.session.add(task)
            db.session.commit()
            flash(f'Task created successfully!','success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Failed to create task:{str(e)}','danger')
        return redirect(url_for('index')) 
    else:
       tasks=Task.query.order_by(Task.id.desc())
    return render_template('index.html',form=form,tasks=tasks)
   
    

@app.route('/update_task_status/<int:task_id>',methods=['GET','POST'])
@login_required
def update_task_status(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.status = 'completed' in request.form
        db.session.commit()
        return redirect(url_for('index'))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Failed to update task status:{str(e)}",'danger')
        return redirect(url_for('index'))


@app.route('/edit_task/<int:task_id>',methods=['GET','POST'])
@login_required
def edit_task(task_id):
    # try:
    #     task = Task.query.get_or_404(task_id)
    #     task.status = 'completed' in request.form
    #     db.session.commit()
    #     return redirect(url_for('index'))
    # except SQLAlchemyError as e:
    #     db.session.rollback()
    #     flash(f"Failed to update task status:{str(e)}",'danger')
    pass
    return redirect(url_for('index'))



@app.route('/delete_task/<int:task_id>',methods=['GET','POST'])
@login_required
def delete_task(task_id):
    try:
        # task = Task.query.get_or_404(task_id)
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()  # add user_id to filter the task by the current user only  # secure this with a login decorator or similar
        db.session.delete(task)  # delete the task
        db.session.commit()
    # except NoResultFound:
    #     flash('Task not found!','danger')
    #     return redirect(url_for('index')
        return redirect(url_for('index'))
     
        
        flash('Task deleted successfully!','success')
        return redirect(url_for('index'))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Failed to delete task:{str(e)}",'danger')
        return redirect(url_for('index'))
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
                                
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

        
    return picture_fn



@app.route("/account",methods=['POST','GET'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_picture = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!","success")
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_picture = url_for('static',filename='profile_pics/' + current_user.profile_picture)
    return render_template('account.html',title='Account',profile_picture=profile_picture,form=form)


@app.route("/register",methods=["POST","GET"])   
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created successfully.Please login.','success')
        return redirect(url_for('login'))
    
    return render_template("register.html", title="Register", form=form)


@app.route("/login",methods=["POST","GET"])   
def login():
    form = LoginForm()
    user = User.query.filter_by(username=form.username.data).first()
    if user and bcrypt.check_password_hash(user.password,form.password.data):
        login_user(user,remember=form.remember.data)
        flash('You have logged in successfully!','success')
        return redirect(url_for('index'))
    else:
        flash('Login unsuccessful.Check username and password.','danger')
    return render_template("login.html", title="Login", form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
 