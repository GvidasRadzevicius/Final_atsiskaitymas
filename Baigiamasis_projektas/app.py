from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from werkzeug.utils import secure_filename
from flask import abort
from forms import EditCategoryForm, RegisterForm, LoginForm
import os







app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['UPLOAD_FOLDER'] = 'static/images'


    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False) 
    password = db.Column(db.String(100), nullable=False)
    categories = db.relationship('Category', backref='user', lazy=True)
    notes = db.relationship('Note', backref='notes_user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.relationship('Note', backref='category', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))







@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User(email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        
       
        if email == 'test@test.lt' and password == 'test':
            flash('Sėkmingai prisijungėte kaip test@test.lt', 'success')
            return redirect(url_for('dashboard'))

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):

            login_user(user)
            flash('Sėkmingai prisijungėte', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Prisijungimas nepavyko. Patikrinkite el. paštą ir slaptažodį.', 'danger')
    return render_template('login.html', title='Prisijungimas', form=form)


    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/new-category', methods=['GET', 'POST'])
@login_required
def new_category():
    if request.method == 'POST':
        category_name = request.form['name']
        category = Category(name=category_name, user_id=current_user.id)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_category.html')

@app.route('/edit-category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        abort(403)
    form = EditCategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.name.data = category.name
    return render_template('edit_category.html', category=category, form=form)


@app.route('/delete-category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        abort(403)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/new-note', methods=['GET', 'POST'])
@login_required
def new_note():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        note_title = request.form['title']
        note_content = request.form['content']
        note_category_id = request.form['category_id']
        note = Note(title=note_title, content=note_content, user_id=current_user.id, category_id=note_category_id)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_note.html', categories=categories)

@app.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    categories = Category.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        note.category_id = request.form['category_id']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_note.html', note=note, categories=categories)

@app.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/filter-notes/<int:category_id>', methods=['GET'])
@login_required
def filter_notes(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        abort(403)
    notes = Note.query.filter_by(category_id=category_id).all()
    return render_template('filtered_notes.html', notes=notes, category=category)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        notes = Note.query.filter(Note.user_id == current_user.id, Note.title.ilike(f'%{search_query}%')).all()
        return render_template('search_results.html', notes=notes)
    return render_template('search.html')



@app.route('/upload-image/<int:note_id>', methods=['GET', 'POST'])
@login_required
def upload_image(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nerasta nuotrauka')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Nepasirinkta nuotrauka')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            note.image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('upload_image.html', note=note)

@app.route('/')
def main_page():
    categories = Category.query.all()
    notes = Note.query.all()
    return render_template('index.html', categories=categories, notes=notes)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
