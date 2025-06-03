from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    image_path = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        today = datetime.today()
        age = today.year - user.birthdate.year - ((today.month, today.day) < (user.birthdate.month, user.birthdate.day))
        return render_template('profile.html', user=user, age=age)
    else:
        flash('Invalid credentials')
        return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    current_year = datetime.now().year
    if request.method == 'POST':
        name = request.form.get('name')
        year = request.form.get('birth_year')
        month = request.form.get('birth_month')
        day = request.form.get('birth_day')
        address = request.form.get('address')
        username = request.form.get('username')
        password = request.form.get('password')
        file = request.files.get('image')
        image_path = None

        if not (year and month and day):
            flash('Please enter your complete birthdate.')
            return render_template('register.html', current_year=current_year)

        try:
            birthdate = date(int(year), int(month), int(day))
        except Exception as e:
            flash('Invalid birthdate.')
            return render_template('register.html', current_year=current_year)

        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        user = User(
            name=name,
            birthdate=birthdate,
            address=address,
            username=username,
            password=password,
            image_path=image_path
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('index'))
    return render_template('register.html', current_year=datetime.now().year)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    today = datetime.today()
    age = today.year - user.birthdate.year - ((today.month, today.day) < (user.birthdate.month, user.birthdate.day))
    return render_template('profile.html', user=user, age=age)

if __name__ == '__main__':
    app.run(debug=True)