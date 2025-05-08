from flask import Flask, render_template, url_for, redirect, abort
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
            return render_template('register.html', title='Регистрация', form=form, styles_css=styles_css,
                                   message="Пароли не совпадают")
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
        return render_template('login.html', title='Авторизация',
                               message="Неправильный логин или пароль", styles_css=styles_css, form=form)
    return render_template('login.html', title='Авторизация', styles_css=styles_css, form=form)


@app.route('/information')
def information():
    styles_css = url_for('static', filename='css/information.css')
    return render_template('information.html', title='О сайте', styles_css=styles_css)


@app.route('/assets')
def assets():
    styles_css = url_for('static', filename='css/assets.css')
    db_sess = db_session.create_session()

    if a := db_sess.query(Shares).filter(Shares.user_id == current_user.id).all():
        last_share = a[-1]
        price_for_one_share = round(float(get_stock_price(last_share.company)), 2)
        current_price_of_share = round(float(last_share.amount * price_for_one_share), 2)
        share_profit = round(float(current_price_of_share / last_share.original_price), 2)
    else:
        last_share, price_for_one_share, current_price_of_share, share_profit = [None] * 4

    if a := db_sess.query(Currency).filter(Currency.user_id == current_user.id).all():
        last_currency = a[-1]
        price_for_one_currency = round(float(get_cbr_currency_rate(last_currency.name)), 2)
        current_price_of_currency = round(float(last_share.amount * price_for_one_currency), 2)
        currency_profit = round(float(price_for_one_currency / last_currency.original_price), 2)
    else:
        last_currency, price_for_one_currency, current_price_of_currency, currency_profit = [None] * 4

    if a := db_sess.query(Cryptocurrency).filter(Cryptocurrency.user_id == current_user.id).all():
        last_cryptocurrency = a[-1]
        price_for_one_cryptocurrency = round(float(get_crypto_price(last_cryptocurrency.name)), 2)
        current_price_of_cryptocurrency = round(float(last_cryptocurrency.amount * price_for_one_cryptocurrency), 2)
        cryptocurrency_profit = round(float(current_price_of_cryptocurrency / last_cryptocurrency.original_price), 2)
    else:
        last_cryptocurrency, price_for_one_cryptocurrency, current_price_of_cryptocurrency, cryptocurrency_profit = [None] * 4
    price_for_one_asset = [price_for_one_share, price_for_one_currency, price_for_one_cryptocurrency]
    current_price = [current_price_of_share, current_price_of_currency, current_price_of_cryptocurrency]
    profit = [share_profit, currency_profit, cryptocurrency_profit]
    # last_share = db_sess.query(Shares).filter(Shares.user_id == current_user.id).all()
    # last_currency = db_sess.query(Currency).filter(Currency.user_id == current_user.id).all()
    # last_cryptocurrency = db_sess.query(Cryptocurrency).filter(Cryptocurrency.user_id == current_user.id).all()
    # last_assets = [last_share, last_currency, last_cryptocurrency]
    # current_price = [round(a * b.amount, 2) for a, b in zip(price_for_one_asset, [last_share, last_currency, last_cryptocurrency])]
    # profit = [round(a / b.original_price - 1, 3) for a, b in zip(current_price, [last_share, last_currency, last_cryptocurrency])]
    return render_template('assets.html', title='Активы', styles_css=styles_css, last_share=last_share,
                           last_currency=last_currency, last_cryptocurrency=last_cryptocurrency,
                           price_for_one_asset=price_for_one_asset, current_price=current_price, profit=profit)


@app.route('/assets/shares')
def shares():
    styles_css = url_for('static', filename='css/shares.css')
    db_sess = db_session.create_session()
    all_shares = db_sess.query(Shares).filter(Shares.user_id == current_user.id).all()
    extra_data = []
    for share in all_shares:
        price_for_one_share = round(float(get_stock_price(share.company)), 2)
        current_price_of_share = round(float(share.amount * price_for_one_share), 2)
        share_profit = round(float(current_price_of_share / share.original_price), 2)
        extra_data.append((price_for_one_share, current_price_of_share, share_profit))
    return render_template('shares.html', title='Акции', styles_css=styles_css, all_shares=all_shares,
                           extra_data=extra_data)


@app.route('/assets/currencies')
def currencies():
    styles_css = url_for('static', filename='css/currencies.css')
    db_sess = db_session.create_session()
    all_currencies = db_sess.query(Currency).filter(Currency.user_id == current_user.id).all()
    extra_data = []
    for currency in all_currencies:
        price_for_one_currency = round(float(get_cbr_currency_rate(currency.name)), 2)
        current_price_of_currency = round(float(currency.amount * price_for_one_currency), 2)
        currency_profit = round(float(current_price_of_currency / currency.original_price), 2)
        extra_data.append((price_for_one_currency, current_price_of_currency, currency_profit))
    return render_template('currencies.html', title='Акции', styles_css=styles_css, all_currencies=all_currencies,
                           extra_data=extra_data)


@app.route('/assets/cryptocurrencies')
def cryptocurrencies():
    styles_css = url_for('static', filename='css/cryptocurrencies.css')
    db_sess = db_session.create_session()
    all_cryptocurrencies = db_sess.query(Cryptocurrency).filter(Cryptocurrency.user_id == current_user.id).all()
    extra_data = []
    for cryptocurrency in all_cryptocurrencies:
        price_for_one_cryptocurrency = round(float(get_crypto_price(cryptocurrency.name)), 2)
        current_price_of_cryptocurrency = round(float(cryptocurrency.amount * price_for_one_cryptocurrency), 2)
        cryptocurrency_profit = round(float(current_price_of_cryptocurrency / cryptocurrency.original_price), 2)
        extra_data.append((price_for_one_cryptocurrency, current_price_of_cryptocurrency, cryptocurrency_profit))
    return render_template('cryptocurrencies.html', title='Акции', styles_css=styles_css,
                           all_cryptocurrencies=all_cryptocurrencies, extra_data=extra_data)


@app.route('/assets/add/<asset_type>', methods=['GET', 'POST'])
def add(asset_type):
    styles_css = url_for('static', filename='css/add.css')
    if asset_type == "share":
        form = AddShareForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            share = Shares()
            share.company = form.company.data.upper()
            share.amount = form.amount.data
            share.original_price = round(float(form.amount.data) * float(get_stock_price(form.company.data)), 2)
            current_user.shares.append(share)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/assets')
    elif asset_type == "currency":
        form = AddCurrencyForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            currency = Currency()
            currency.name = form.name.data.upper()
            currency.amount = form.amount.data
            currency.original_price = round(float(form.amount.data) * float(
                get_cbr_currency_rate(form.name.data.upper().strip())), 2)
            current_user.currency.append(currency)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/assets')
    else:
        form = AddCryptocurrencyForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            cryptocurrency = Cryptocurrency()
            cryptocurrency.name = form.name.data.capitalize()
            cryptocurrency.amount = form.amount.data
            cryptocurrency.original_price = round(float(form.amount.data) * float(get_crypto_price(form.name.data)), 2)
            current_user.cryptocurrency.append(cryptocurrency)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/assets')
    return render_template('add.html', title='Активы', styles_css=styles_css, asset_type=asset_type, form=form)


@app.route('/assets/share_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Shares).filter(Shares.id == id, Shares.user_id == current_user.id).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/shares')


@app.route('/assets/currency_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def currency_delete(id):
    db_sess = db_session.create_session()
    currency = db_sess.query(Currency).filter(Currency.id == id, Currency.user_id == current_user.id).first()
    if currency:
        db_sess.delete(currency)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/currencies')


@app.route('/assets/cryptocurrency_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def cryptocurrency_delete(id):
    db_sess = db_session.create_session()
    cryptocurrency = db_sess.query(Cryptocurrency).filter(Cryptocurrency.id == id,
                                                          Cryptocurrency.user_id == current_user.id).first()
    if cryptocurrency:
        db_sess.delete(cryptocurrency)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/cryptocurrencies')


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
