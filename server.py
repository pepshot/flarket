import os, shutil
from flask import Flask, render_template, url_for, redirect, abort
from flask import make_response, jsonify, request
from flask_login import current_user, login_user, LoginManager
from flask_login import login_required, logout_user
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.add_post import AddPostForm
from forms.edit_post import EditPostForm
from forms.edit_user import EditUserForm
from data import db_session, posts_api, users_api
from data.users import User
from data.posts import Posts
from data.categories import Category


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this_is_not_project_yandex'

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error(404)': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error(400)': 'Bad Request'}), 400)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/main', methods=['GET'])
def main():
    title = 'Главная страница'
    db_sess = db_session.create_session()
    list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
    posts = db_sess.query(Posts).filter(Posts.is_hidden == False).all()[::-1]
    if request.method == 'GET':
        search_text = request.args.get('search')
        if search_text is not None:
            posts = db_sess.query(Posts).filter(Posts.is_hidden == False,
                                                Posts.name_post.like(f'%{search_text}%'),
                                                Posts.content_post.like(f'%{search_text}%')).all()[::-1]
            title = search_text
            return render_template("main.html", title=title, list_of_categories=list_of_categories,
                                   posts=posts)
        return render_template("main.html", title=title, list_of_categories=list_of_categories,
                               posts=posts)
    return render_template("main.html", title=title, list_of_categories=list_of_categories, posts=posts)


@app.route('/<int:category_id>')
def main_category_id(category_id):
    title = 'Главная страница'
    db_sess = db_session.create_session()
    list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
    posts = db_sess.query(Posts).filter(Posts.is_hidden == False, Posts.category == category_id).all()[::-1]
    for item in db_sess.query(Category).all():
        if item.id == category_id:
            title = item.name_category
            break
    else:
        abort(404)

    if request.method == 'GET':
        search_text = request.args.get('search')
        if search_text is not None:
            posts = db_sess.query(Posts).filter(Posts.is_hidden == False,
                                                Posts.name_post.like(f'%{search_text}%',
                                                Posts.category == category_id)).all()[::-1]
            title = search_text
            return render_template("main.html", title=title, list_of_categories=list_of_categories,
                                   posts=posts)
        return render_template("main.html", title=title, list_of_categories=list_of_categories, posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not current_user.is_authenticated:
        form = RegisterForm()
        css = url_for('static', filename='css/register.css')
        db_sess = db_session.create_session()
        list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
        if request.method == 'POST':
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form, css=css, list_of_categories=list_of_categories,
                                       message="Пароли не совпадают")
            if db_sess.query(User).filter((User.email == form.email.data)).first():
                return render_template('register.html', title='Регистрация',
                                       form=form, css=css, list_of_categories=list_of_categories,
                                       message="Такой пользователь уже есть")
            user = User(
                email=form.email.data,
                number_phone=form.number_phone.data,
                name=form.name.data,
                surname=form.surname.data,
                city=form.city.data,
                address=form.address.data,
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            shutil.copy('static/img/users/default_avatar.png', f'static/img/users/user_{user.id}.png')
            user.url_photo = f'/static/img/users/user_{user.id}.png'
            db_sess.commit()
            print(f'Зарегистрирован новый пользователь с id {user.id}')
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form, css=css,
                               list_of_categories=list_of_categories)
    abort(404)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm()
        css = url_for('static', filename='css/login.css')
        db_sess = db_session.create_session()
        list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
        if request.method == 'POST':
            user = db_sess.query(User).filter((User.email == form.login.data) | (User.number_phone == form.login.data)).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                print(user, 'зашел в свой аккаунт.')
                return redirect(f"/profile/{user.id}")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form, css=css, list_of_categories=list_of_categories)
        return render_template('login.html', title='Авторизация', form=form, css=css, list_of_categories=list_of_categories)
    abort(404)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    print(current_user, 'вышел со своего аккаунта.')
    return redirect("/")


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = AddPostForm()
    db_sess = db_session.create_session()
    list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
    form.category.choices = list_of_categories
    css = url_for('static', filename='css/add_post.css')
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Posts()
        post.author = current_user.id
        post.name_post = form.name_post.data
        post.category = form.category.data
        post.content_post = form.content_post.data
        post.price = form.price.data
        post.is_hidden = form.is_hidden.data
        post.url_photo = 'None'
        db_sess.add(post)
        db_sess.commit()
        return redirect(f'/user_posts/{current_user.id}')
    return render_template('add_post.html', title='Размещение объявления',
                           form=form, css=css, list_of_categories=list_of_categories)


@app.route('/user_posts/<int:user_id>')
@login_required
def user_posts(user_id):
    db_sess = db_session.create_session()
    list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
    user_posts = db_sess.query(Posts).filter(Posts.author == user_id).all()[::-1]
    if user_id == current_user.id:
        title = 'Мои объявления'
    else:
        title = f'Объявления {user_posts[0].user.name} {user_posts[0].user.surname}'
    return render_template('user_posts.html', title=title,
                           list_of_categories=list_of_categories,
                           posts=user_posts)


@app.route('/post/<int:post_id>')
def post(post_id):
    db_sess = db_session.create_session()
    list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
    post = db_sess.query(Posts).filter(Posts.id == post_id).first()
    css = url_for('static', filename='css/post.css')
    if post.user != current_user:
        post.count_views += 1
        db_sess.commit()
    if post.is_hidden == False:
        return render_template('post.html', title=f'{post.name_post}',
                           list_of_categories=list_of_categories,
                           post=post, css=css)
    abort(404)


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    db_sess = db_session.create_session()
    list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
    css = url_for('static', filename='css/edit_post.css')
    form = EditPostForm()
    form.category.choices = list_of_categories

    if request.method == 'GET':
        post = db_sess.query(Posts).filter(Posts.id == post_id,
                                           Posts.user == current_user).first()
        url = post.url_photo
        if post:
            form.name_post.data = post.name_post
            form.content_post.data = post.content_post
            form.price.data = post.price
            form.category.data = post.category
            form.is_hidden.data = post.is_hidden
        else:
            abort(404)
    if form.validate_on_submit():
        post = db_sess.query(Posts).filter(Posts.id == post_id,
                                           Posts.user == current_user).first()
        url = post.url_photo

        if post:
            file = request.files['file']
            if file and file.filename.split('.')[-1] in ['png', 'jpg', 'jpeg']:
                file.save(os.path.join('static/img/posts', f'post_{post.id}.png'))
                post.url_photo = f'/static/img/posts/post_{post.id}.png'
            post.name_post = form.name_post.data
            post.content_post = form.content_post.data
            post.price = form.price.data
            post.category = form.category.data
            post.is_hidden = form.is_hidden.data
            db_sess.commit()
            return redirect(f'/user_posts/{post.user.id}')
        else:
            abort(404)
    return render_template('edit_post.html', title='Редактирование объявления',
                           list_of_categories=list_of_categories,
                           form=form, css=css, url=url, post=post)


@app.route('/delete_post/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_jobs(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id).first()
    if post.user == current_user:
        if post:
            print(os.getcwd())
            os.remove(post.url_photo[1::])
            db_sess.delete(post)
            db_sess.commit()
        else:
            abort(404)
        return redirect(f'/user_posts/{post.user.id}')


@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    db_sess = db_session.create_session()
    list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
    user = db_sess.query(User).filter(User.id == user_id).first()
    css = url_for('static', filename='css/profile.css')
    if user:
        return render_template(f'profile.html', title=f'{user.name} {user.surname}',
                               list_of_categories=list_of_categories, post=post, css=css,
                               user=user)
    abort(404)


@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    db_sess = db_session.create_session()
    list_of_categories = [(category.id, category.name_category) for category in db_sess.query(Category).all()]
    css = url_for('static', filename='css/edit_user.css')
    form = EditUserForm()
    if request.method == 'GET':
        user = db_sess.query(User).filter(User.id == user_id,
                                          user_id == current_user.id).first()
        if user:
            form.name.data = user.name
            form.surname.data = user.surname
            form.city.data = user.city
            form.address.data = user.address
            form.number_phone.data = user.number_phone
            form.is_hidden_contact_info.data = user.is_hidden_contact_info
            url = user.url_photo
        else:
            abort(404)

    if request.method == 'POST':
        user = db_sess.query(User).filter(User.id == user_id,
                                          user_id == current_user.id).first()
        url = user.url_photo
        if user:
            file = request.files['file']
            if file and file.filename.split('.')[-1] in ['png', 'jpg', 'jpeg']:
                file.save(os.path.join('static/img/users', f'user_{user.id}.png'))
            if form.number_phone.data != user.number_phone:
                if not db_sess.query(User).filter(User.number_phone == form.number_phone.data).all():
                    user.name = form.name.data
                    user.surname = form.surname.data
                    user.city = form.city.data
                    user.address = form.address.data
                    user.number_phone = form.number_phone.data
                    user.is_hidden_contact_info = form.is_hidden_contact_info.data

                    db_sess.commit()
                    print(f'Пользователь {user.id} изменил информацию о себе')
                    return redirect(f'/profile/{user.id}')
                else:
                    render_template('edit_profile.html', title='Редактирование профиля',
                                    list_of_categories=list_of_categories, url=url,
                                    form=form, css=css, message='Такой номер телефона уже зарегистрирован')
            else:
                user.name = form.name.data
                user.surname = form.surname.data
                user.city = form.city.data
                user.address = form.address.data
                user.number_phone = form.number_phone.data
                user.is_hidden_contact_info = form.is_hidden_contact_info.data

                db_sess.commit()
                print(f'Пользователь {user.id} изменил информацию о себе')
                return redirect(f'/profile/{user.id}')
        else:
            abort(404)
    return render_template('edit_profile.html', title='Редактирование профиля',
                           list_of_categories=list_of_categories,
                           form=form, css=css, url=url)


if __name__ == '__main__':
    db_session.global_init(f"db/flarket.db")
    #import funct
    #funct.add_categories()
    app.register_blueprint(posts_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
