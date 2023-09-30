import sqlite3
import datetime
import os
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask import Flask, render_template, request, g, flash, make_response, url_for, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from FlaskDB import FlaskDB
from UserLogin import UserLogin

#config
DATABASE = 'tmp/app.db'
DEBUG = True
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config['SECRET_KEY'] = '!@lime11033011emil@!'
app.permanent_session_lifetime = datetime.timedelta(days=10)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'app.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None
@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FlaskDB(db)

@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

@app.route("/")
def index():
    return render_template('index.html', menu = dbase.getMenu())

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile") or url_for("books"))
 
        flash("Неверная пара логин/пароль", "error")
 
    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")



@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
            and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")
 
    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")

@app.route('/profile')
@login_required
def profile():
    dbase.activateUser(current_user.get_id())
    books = dbase.bookCount(current_user.get_id())
    name = dbase.userBooks(current_user.get_id())
    groups = dbase.getGroups()
    liked = dbase.likedBooks(current_user.get_id())
    return render_template("profile.html", menu=dbase.getMenu(), title="Личный кабинет",  books = books,\
                            name=name, groups = groups, liked = liked)

@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""
 
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                    return redirect(url_for('profile'))
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")
 
    return redirect(url_for('profile'))

@app.route("/books")
@login_required
def books():
    return render_template("books.html", menu=dbase.getMenu(), books = dbase.getBookAnonce(), \
                           title="Книги")

@app.route("/books/<alias>", methods=["POST", "GET"])
@login_required
def showBook(alias):
    groups = dbase.getGroups()
    bookid, name, author, genre, preview, isbn, pages, phouse, year, edition, availibility = dbase.getBook(alias)
    if request.method == "POST":
        if request.form['object'] == 123:
            if availibility == 0:
                flash('Книги нет в наличии', category='error')
            else:
                res = dbase.takeBook(alias, current_user.get_id())
                if not res:
                    flash('Ошибка гандон книги', category='error')
                else:
                    flash('Книга успешно зарезервирована', category='success')
                    dbase.switchBook(alias)
                    availibility = 0
        else:
            if request.form['object'] !="123":
                dbase.addBookInGroup(current_user.get_id(), alias, request.form['object'])
                flash('Книга успешно добавлена в группу', category='success')
                res = dbase.takeBook(alias, current_user.get_id())
                dbase.switchBook(alias)
                availibility = 0
            else:
                flash('Нельзя добавить в пустую группу')
    return render_template("book.html", menu=dbase.getMenu(), name=name, author = author, genre=genre,\
                           preview = preview, isbn = isbn, pages = pages, phouse = phouse, year = year,\
                            edition = edition, availibility = availibility, groups = groups)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.errorhandler(404)
def PageNotFound(error):
    return render_template('page404.html', title="Страница не найдена", menu = dbase.getMenu())

if __name__ == "__main__":
        app.run(debug=True)