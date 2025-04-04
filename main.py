from flask import *
from data import db_session
from data.users import User
from data.jobs import Jobs
from flask_login import *
from data.login import LoginForm
from data.register import RegisterForm
from data.job_form_module import JobForm
from datetime import *
from data import db_session, api


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/joblist')
def joblist():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    db_sess.commit()
    return render_template('all_jobs.html', jobs=jobs)


@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html')


@app.route('/test')
def test():
    return render_template("content.html")


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(api.blueprint)
    app.run(port=8080, host='127.0.0.1')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/cookie_test")
def cookie_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        db_sess = db_session.create_session()
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = form.age.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.add(user)
        try:
            db_sess.commit()
        except Exception as e:
            return render_template('register.html', title='Регистрация', form=form, message='Уже есть такой пользователь')
        return redirect("/login")
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
def work():
    form = JobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        job.team_leader = form.team_leader.data
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.work_done.data
        job.start_date = datetime.now()
        job.end_date = datetime.now() + timedelta(days=3)
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template('addjob.html', title="Работа", form=form)


if __name__ == '__main__':
    main()
