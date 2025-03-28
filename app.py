import os
import secrets
from flask import Flask,redirect,url_for,render_template,flash,request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_login import UserMixin,current_user,LoginManager,login_user,logout_user,login_required
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,TextAreaField,BooleanField,SelectField,DateField,PasswordField,TimeField
from wtforms.validators import DataRequired,ValidationError,Length,EqualTo,Email
from flask_wtf.file import FileField,FileAllowed
from datetime import datetime,timedelta
from flask_migrate import Migrate
from PIL import Image




# Create the Flask application object
app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Generate a secret key for the application
app.config['SECRET_KEY'] = secrets.token_hex(16)
# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://captain:captain@localhost:5432/taskmania'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)



class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    profile_picture = db.Column(db.String(20), nullable=False, default='image3.jpeg')
    tasks = db.relationship('Task', backref='users', lazy='dynamic')


# Define the Task model
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, default=False,nullable=False)
    date_created = db.Column(db.Date,default= datetime.now)
    date_due = db.Column(db.Date,default=datetime.now,nullable=False)
    time_due = db.Column(db.Time,default=datetime.now().time())
    date_completed = db.Column(db.Date,default= datetime.now) 
    category = db.Column(db.String(50),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    

    def _repr_(self):
        return f'{self.title} {self.description} {self.date_due} {self.category} {self.status} {self.time_due}'



# Create the database tables
app.app_context().push()
db.create_all()



class TaskForm(FlaskForm):
    title = StringField(validators=[DataRequired()],render_kw={'placeholder':'Name of the task'})
    description = TextAreaField(validators=[DataRequired()],render_kw={'placeholder':'More information about the task'})
    category = SelectField(choices=[
            ('general', 'General'), 
            ('work', 'Work'), 
            ('personal', 'Personal'), 
            ('other', 'Other')
        ],validators=[DataRequired()],render_kw={'placeholder':'General'})
    date_due = DateField(validators=[DataRequired()])
    time_due = TimeField(validators=[DataRequired()])
    submit = SubmitField('Create Task')

    def validate_time_due(form, field):
        time_due = field.data
        if time_due < datetime.now().time():
            raise ValidationError('Due time cannot be in the past.')
           
           
        def _init_(self,args,*kwargs):
            super(TaskForm, self)._init_(args,*kwargs)
            self.time_due.data = (datetime.now() + timedelta(hours=1)).strftime('%H:%M')

    def validate_date_due(form, field):
        date_due = field.data
        if date_due < datetime.now().date():
            raise ValidationError('Due date cannot be in the past.')
           
           
        def _init_(self,args,*kwargs):
            super(TaskForm, self)._init_(args,*kwargs)
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

# general_tasks={}
# def get_task_category(category):
#     task = Task.query.get(category)
#     if task.category == general:
#         general_tasks.update(task.category

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = TaskForm()
    if form.validate_on_submit():
        try:
            task = Task(title=form.title.data, description=form.description.data, category=form.category.data, date_due=form.date_due.data, user_id=current_user.id,time_due=form.time_due.data)
            db.session.add(task)
            db.session.commit()
            flash('Task created successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Failed to create task: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
    search_query = request.args.get('search')
    sort_by = request.args.get('sort_by', 'category')
    page = request.args.get('page',1,type=int)

    query = Task.query.filter_by(user_id=current_user.id)

    if search_query:
        query = query.filter(
            Task.title.ilike(f'%{search_query}%') | 
            Task.description.ilike(f'%{search_query}%') | 
            Task.category.ilike(f'%{search_query}%') 
        
        )
    
    if sort_by == 'category':
        query = query.order_by(Task.category)
    elif sort_by == 'title':
        query = query.order_by(Task.title)
    elif sort_by == 'description':
        query = query.order_by(Task.description)
   
    else:
        query = query.order_by(Task.id.desc())  # default sorting

    tasks = query.paginate(page=page, per_page=3)
    
    return render_template('index.html', form=form, tasks=tasks.items, sort_by=sort_by, pagination=tasks)
    # if sort_by == 'category':
    #     tasks = query.order_by(Task.category).paginate(page=page,per_page=4)
  
    # else:
    #     tasks = query.order_by(Task.id.desc()).paginate(page=page,per_page=4)
    
    # return render_template('index.html', form=form, tasks=tasks.items, sort_by=sort_by,pagination=tasks)


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


@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    # form = TaskForm()
    tasks = Task.query.order_by(Task.date_due).paginate(page=request.args.get('page', 1, type=int), per_page=4)
    task = Task.query.filter_by(id=task_id).first()
    form = TaskForm(obj=task)
    
    if form.validate_on_submit():
        task = Task.query.get(task_id)
        task.title = form.title.data
        task.description = form.description.data
        task.date_due = form.date_due.data
        db.session.commit()
        flash('Task has been updated!', 'success')
        return redirect(url_for('index'))
    
    # elif request.method == 'GET':
    #     task = Task.query.get(task_id)
    #     form.title.data = task.title
    #     form.description.data = task.description
    #     form.date_due.data = task.date_due
    
    return render_template('index.html', form=form, task_id=task_id, tasks=tasks.items,pagination=tasks)



@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
        return redirect(url_for('index'))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Failed to delete task!', 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred!', 'danger')
        return redirect(url_for('index'))
        
  
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
                                
    
    output_size = (100, 100)
    i = Image.open(form_picture)
    i = i.resize(output_size, Image.LANCZOS)
    i.save(picture_path)

    return picture_fn



@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        try:
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.profile_picture = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Your account has been updated!","success")
            return redirect(url_for('account'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Failed to update account, please choose another file.", "danger")
            return redirect(url_for('account'))
        except Exception as e:
            flash(f"An error occurred while updating account!", "danger")
            return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

     # Handle profile picture URL
    if current_user.profile_picture:
        profile_picture = url_for('static', filename='images/' + current_user.profile_picture)
    else:
        # Fallback to a default profile picture if none is set
        profile_picture = url_for('static', filename='images/image3.jpeg')
    
    return render_template('account.html', title='Account', form=form, profile_picture=profile_picture)
    # profile_picture = url_for('static',filename='images/' + current_user.profile_picture)
    # return render_template('account.html',title='Account',form=form,profile_picture=profile_picture)


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
        flash(f'Account created successfully.Please login.','success')
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)


# @app.route("/login",methods=["POST","GET"])   
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("index"))
    
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user and bcrypt.check_password_hash(user.password,form.password.data):
#             login_user(user,remember=form.remember.data)
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('index'))
      
 
#     return render_template("login.html", title="Login", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("Login successful!","success")
            return redirect(next_page or url_for('index'))
      
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5002)