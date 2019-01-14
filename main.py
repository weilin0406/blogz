from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123456@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'e32t2EFwrefwR#G#%(jfj'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.owner = owner 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/', methods=["POST", "GET"])
def auto_redirect():
    return redirect('/blog')

@app.route('/blog', methods=["POST", "GET"])
def show_blog():
    post_id = request.args.get('id')
    if post_id:
        blog = Blog.query.get(post_id)
        return render_template('single_post.html', blog=blog, title="Single Post")
    else:
        
        all_blog_posts = Blog.query.all()
        
        return render_template('blog.html', all_blog_posts=all_blog_posts, title="All Blog")

@app.route('/newpost', methods=['GET', 'POST'])
def add_entry():

    if request.method == 'POST':

        title_error = ""
        blog_entry_error = ""

        post_title = request.form['blog_title']
        post_entry = request.form['blog_post']
        owner = User.query.filter_by(username=session['username']).first()
        post_new = Blog(post_title, post_entry, owner)

        if post_title and post_entry:
            db.session.add(post_new)
            db.session.commit()
            post_link = "/?id=" + str(post_new.id)
            return redirect(post_link)
        else:
            if not post_title and not post_entry:
                title_error = "Please enter text for blog title"
                blog_entry_error = "Please enter text for blog entry"
                return render_template('new_post.html', blog_entry_error=blog_entry_error, title_error=title_error)
            elif not post_title:
                title_error = "Please enter text for blog title"
                return render_template('new_post.html', title_error=title_error, post_entry=post_entry)
            elif not post_entry:
                blog_entry_error = "Please enter text for blog entry"
                return render_template('new_post.html', blog_entry_error=blog_entry_error, post_title=post_title)

    # DISPLAYS NEW BLOG ENTRY FORM
    else:
        return render_template('new_post.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_form(): 
    no_spec_char = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    if request.method == 'GET': 
        return render_template('Sign_up.html')


    if request.method == 'POST':
        username_error = ''
        password_error = ''
        password_verify_error = ''

        username = request.form['username_name']
        password = request.form['password_name']
        password_verify = request.form['password_verify']

        if username:

            for i in username: 
                if i not in no_spec_char:
                    username_error = "Not Valid: Use only Alphabet and Numbers."

                    if len(username) < 3 or len(username) > 20:
                        username_error = 'Username needs to be 3-20 characters.'
                                    
        else:
            username_error = "Username field is Blank."

        if not len(password): 
            password_error = "Password field is Blank."  

        if len(password) < 3 or len(password) > 20: 
            password_error = 'Password must be 3-20 characters and not contain spaces.' 
        if " " in password:
            password_error = "Not Valid: Do not use space in Password."
        if " " in password_verify:
            password_verify_error = "Not Valid: Do not use space in Password."
            
        if password_verify != password: 
            password_verify_error = 'Passwords do not match.' 
    
        if not username_error and not password_error and not password_verify_error:
            session['username'] = username
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/newpost') 


        return render_template('sign_up.html', username_value=username, 
                            username_error=username_error, password_error=password_error, 
                            password_verify_error=password_verify_error)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            user = User.query.filter(User.username == username).first()
            if user:
                if  user.password == password:
                    session['username'] = user.id
                    return redirect("/newpost")
                else:
                    password_error = "Password is Incorrect"
                    render_template("login.html", password_error=password_error)
            else:
                username_error = "User Does Not Exist"
                render_template("login.html", username_error=username_error)
        username_error = "Username is Blank"
        if not password:
            password_error = "Password is Blank"
            return render_template("login.html", username_error=username_error, password_error=password_error)
        return render_template("login.html", username_error=username_error)
    return render_template("login.html")
        

@app.route("/logout", methods=['GET'])
def logout():
    if "username" in session:
        del session['username']
        return redirect("/blog")
    return redirect("/login")



if __name__ == '__main__':
    app.run()