from flask import render_template, request, json, flash, abort, redirect, url_for
from .backend import Backend
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators
from .user import User
import flask_login
from flask_login import LoginManager
import base64
import io

'''This module takes care of rendering pages and page functions.

   Contains all functions in charge of rendering all pages. Calls backend 
   functions to store data in gcp buckets. Takes care of validating user information
   for login and signup. It logsin, signups and logs out users from session. Uploads
   pokemon wiki information to buckets. 
'''

login_manager = LoginManager() # Lets the app and Flask-Login work together for user loading, login, etc.
backend = Backend()

@login_manager.user_loader
def load_user(username):
    '''Flask function that takes care of loading user to session.
    
       Args:
        username: User username

       Returns:
        User object representing the loaded user.
    '''
    return backend.get_user(username)

def make_endpoints(app):

    class LoginForm(FlaskForm):
        '''Login form, takes two input fields: username and password, has a sumbit field that validates form.'''
        username = StringField('Username', [validators.InputRequired()], render_kw={"placeholder":"Username"})
        password = PasswordField('Password', [validators.InputRequired()], render_kw={"placeholder":"Password"})
        submit = SubmitField('Login')

    class SignupForm(FlaskForm):
        '''Signup form, takes two input fields: username and password, has a sumbit field that validates form.'''
        username = StringField([validators.InputRequired()], render_kw={"placeholder":"Username"})
        password = PasswordField('Password', [validators.InputRequired()], render_kw={"placeholder":"Password"})
        submit = SubmitField('Signup')

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        image = backend.get_image('pokemon/logo.jpg')
        return render_template('main.html', image=image)

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/about")
    def about():
        images = [backend.get_image('authors/javier.png'), backend.get_image('authors/edgar.png'), backend.get_image('authors/mark.png')]
        return render_template('about.html', images=images)

    @app.route("/pages")
    def pages(backend = Backend()):
        #backend = Backend()
        pages = backend.get_all_page_names()
        return render_template('pages.html', pages=pages)

    @app.route("/pages/<pokemon>")
    def wiki(pokemon="abra"):
        poke_string = backend.get_wiki_page(pokemon)
        # pokemon blob is returned as string, turn into json
        poke_json = json.loads(poke_string)
        return render_template("wiki.html", poke=poke_json)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        '''Creates login form and logs in user.

           Creates login form and validates inputs in the form. Calls the backend
           to login the user and checks if the user exists or information is correct.
           Renders login page and form, when logged in successfully it redirects to home page and
           flashes a welcome message. When inputs are not correct it flashes an error message.
           
           Returns:
                Render template function that renders the login page and form.
        '''
        form = LoginForm()

        # User validation
        if form.validate_on_submit(): # Checks if login form is validated

            login_ = backend.sign_in(form.username.data, form.password.data) # Calls backend to login in user

            if login_:
                user = User(form.username.data, form.password.data) # Creates user object to login user
                flask_login.login_user(user) # Takes care of login in the user
                flash(f'Welcome {flask_login.current_user.username}!')

                return redirect(url_for('home'))
            else:
                flash('Wrong username or password.')

        return render_template('login.html', form=form) # Renders login page

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        '''Creates sign up form and creates a user account.

           Creates sign up form and validates form inputs. Calls backend to sign up 
           the new user. If the user account already exists it flashes an error message.
           If the form is validates it creates the account, flashes a success message and
           redirects the user to login page. Renders signup page and form.

           Returns:
                Render template function that renders signup page and form.
        '''
        form = SignupForm()

        # User validation
        if form.validate_on_submit(): # Checks if signup form is validated

            register = backend.sign_up(form.username.data, form.password.data) # Calls backend to create user account

            if register:
                flash('Succesfully created an account.')

                return redirect(url_for('login')) # When register redirects to login page
            else:
                flash('Account already exists.') 
            
        return render_template('signup.html', form=form) # Renders signup page and form
    
    @app.route('/logout', methods=['GET', 'POST'])
    @flask_login.login_required # Requires the user to be signed in
    def signout():
        '''Signs out user from session and redirects to login page.'''
        flask_login.logout_user() # Takes care of login out the user
        flash('Logged out successfully.')
        return redirect(url_for('login')) # Redirects to login page

    @app.route("/upload")
    @flask_login.login_required
    def upload():
        return render_template("upload.html")
    
    @app.route("/upload",methods=["POST"])
    def upload_file():
        # dictionary that holds all values from the form, except for the file
        pokemon_dict = {
            "name":request.form["name"],
            "hit_points":request.form["hit_points"],
            "attack":request.form["attack"],
            "defense":request.form["defense"],
            "speed":request.form["speed"],
            "special_attack":request.form["special_attack"],
            "special_defense":request.form["special_defense"],
            "type":request.form["type"]
        }
        # json object to be uploaded
        file_to_upload = request.files['file']

        # call backend upload
        backend.upload(file_to_upload, pokemon_dict)

        # render pages list
        return pages()