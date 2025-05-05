from flask import Flask, render_template, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.loginform import LoginForm
from forms.registerform import RegisterForm
from forms.add_share import AddShareForm
from forms.add_currency import AddCurrencyForm
from forms.add_cryptocurrency import AddCryptocurrencyForm
from data import db_session
from data.get_prices import *
from data.users import User
from data.shares import Shares
from data.currency import Currency
from data.cryptocurrency import Cryptocurrency

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_very_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    photo = url_for('static', filename='image/education.jpg')
    styles_css = url_for('static', filename='css/index.css')
    return render_template("index.html", title="Управляйте своими финансами легко и эффективно", photo=photo,
                           styles_css=styles_css)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    styles_css = url_for('static', filename='css/register.css')
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, styles_css=styles_css,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', styles_css=styles_css, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    styles_css = url_for('static', filename='css/login.css')
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", styles_css=styles_css, form=form)
    return render_template('login.html', title='Авторизация', styles_css=styles_css, form=form)


@app.route('/information')
def information():
    styles_css = url_for('static', filename='css/information.css')
    return render_template('information.html', title='О сайте', styles_css=styles_css)


@app.route('/assets')
def assets():
    styles_css = url_for('static', filename='css/assets.css')
    db_sess = db_session.create_session()
    last_share = db_sess.query(Shares).filter(Shares.user_id == current_user.id).first()
    last_currency = db_sess.query(Currency).filter(Currency.user_id == current_user.id).first()
    last_cryptocurrency = db_sess.query(Cryptocurrency).filter(Cryptocurrency.user_id == current_user.id).first()
    return render_template('assets.html', title='Активы', styles_css=styles_css, last_share=last_share,
                           last_currency=last_currency, last_cryptocurrency=last_cryptocurrency)


@app.route('/assets/add/<asset_type>', methods=['GET', 'POST'])
def add(asset_type):
    styles_css = url_for('static', filename='css/add.css')
    if asset_type == "share":
        form = AddShareForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            share = Shares()
            share.company = form.company.data
            share.amount = form.amount.data
            share.original_price = float(form.amount.data) * float(round(get_stock_price(form.company.data), 2))
            current_user.shares.append(share)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
    elif asset_type == "currency":
        form = AddCurrencyForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            currency = Currency()
            currency.name = form.name.data
            currency.amount = form.amount.data
            currency.original_price = float(form.amount.data) * float(get_cbr_currency_rate(form.name.data.upper().strip()))
            current_user.currency.append(currency)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
    else:
        form = AddCryptocurrencyForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            cryptocurrency = Cryptocurrency()
            cryptocurrency.name = form.name.data
            cryptocurrency.amount = form.amount.data
            cryptocurrency.original_price = float(form.amount.data) * float(round(get_crypto_price(form.name.data), 2))
            current_user.cryptocurrency.append(cryptocurrency)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
    return render_template('add.html', title='Активы', styles_css=styles_css, asset_type=asset_type, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == "__main__":
    main()
