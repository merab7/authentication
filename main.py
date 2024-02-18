from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


#login_manager 
login_manager = LoginManager()
login_manager.init_app(app)

#load user function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# CREATE TABLE IN DB
class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
 
with app.app_context():
    db.create_all()


 


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods = ('GET', 'POST'))
def register():
    global name
    if request.method == "POST":
        new_user = User(
            name = request.form.get('name'),
            email = request.form.get('email'),
            password = generate_password_hash(request.form.get('password'), method='scrypt', salt_length=16)
        )
        db.session.add(new_user)
        db.session.commit()
        return render_template("secrets.html", name=request.form.get('name'))
    return render_template("register.html")


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        user = db.session.execute(db.select(User).where(User.email == request.form.get("email"))).scalar()
        if user :
            #check hash
            if check_password_hash(user.password, request.form.get('password')):
                login_user(user)
                flash("you entered successfully")
                return render_template("secrets.html", name=user.name)
            else:
                flash("password is incorrect try again")
                return redirect(url_for('login'))  
        else:
            flash("user does not exist")
            return redirect(url_for('login'))        
        

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')


@app.route('/download')
def download():
    return send_from_directory('static', path='files/cheat_sheet.pdf' )


if __name__ == "__main__":
    app.run(debug=True)
