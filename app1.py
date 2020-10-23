from flask import Flask, render_template
from flask import request
from country_list import countries_for_language
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.db'
db = SQLAlchemy(app)


class User(db.Model):
    """Model for Users"""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    country = db.Column(db.String)


db.create_all()


@app.route('/login', methods=['GET', 'POST'])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["pswd"]
        if not email:
            message = 'Please fill out this field.'
            return render_template('login.html', message=message)
        if not password:
            return render_template('login.html', message_p='Please fill out this field.')
        
        user = User.query.filter_by(email=email, password=password).first()
        if user is None:
            return render_template("login.html", message_failure="Wrong Credentials. Please Try Again.")
        else:
            return render_template('login.html', message_success="Successful login!!")

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    countries = dict(countries_for_language('en'))
    if request.method == "POST":
        req = request.form
        missing = []
        for field, input in req.items():
            if input == "":
                missing.append(field)

        if missing:
            feedback = " {}".format(', '.join(missing))
            return render_template('signup.html', countries=countries,
                                   feedback=feedback)
        if req["Email"] != req["Confirm email"]:
            return render_template('signup.html', countries=countries,
                                   dont_match="Emails don't match")
        if req["Password"] != req["Confirm password"]:
            return render_template('signup.html', countries=countries,
                                   dont_match="Passwords don't match")
        """adding data to database in SQLAlquemy"""
        new_user = User(first_name=req["First name"], last_name=req["Last name"],
                        email=req["Email"], password=req["Password"],
                        country=req["countries"])
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return render_template("signup.html", countries=countries,
                                   feedback="email already exists")
        finally:
            db.session.close()
            return render_template("signup.html", countries=countries,
                                   success="Successful Registration")    
    return render_template('signup.html', countries=countries)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
