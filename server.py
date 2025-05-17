import os
from data.info.all_shares import ALL_SHARES
from data.info.all_currency import ALL_CURRENCY
from data.info.all_cryptocurrency import ALL_CRYPTOCURRENCY
from flask import Flask, render_template, url_for, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.loginform import LoginForm  # login form
from forms.registerform import RegisterForm  # register form
from forms.add_share import AddShareForm  # form for adding share
from forms.add_currency import AddCurrencyForm  # form for adding currency
from forms.add_cryptocurrency import AddCryptocurrencyForm  # form for adding cryptocurrency
from data import db_session
from data.get_prices import *  # funcs for get assets price
from data.create_filename import generate_unique_filename
from data.users import User  # user db
from data.shares import Shares  # share db
from data.currency import Currency  # currency db
from data.cryptocurrency import Cryptocurrency  # cryptocurrency db

app = Flask(__name__)  # init app
app.config['SECRET_KEY'] = 'my_very_secret_key'  # key for work
login_manager = LoginManager()  # add user
login_manager.init_app(app)  # init current user


@login_manager.user_loader
def load_user(user_id):  # load user form db
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():  # basic page
    styles_css = url_for('static', filename='css/index.css')
    all_assets, profile_image = [], None
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        profile_image = url_for("static", filename=f"profile_image/{current_user.image}")
        all_shares = {}
        for share in db_sess.query(Shares).filter(Shares.user_id == current_user.id).all():
            if share.company not in all_shares:
                all_shares[share.company] = {"amount": 0, "original_price": 0, "current_price": 0}
            all_shares[share.company]["amount"] += share.amount
            all_shares[share.company]["original_price"] += round(share.original_price, 2)
            all_shares[share.company]["current_price"] += round(get_stock_price(share.company)) * share.amount
        all_assets.append(all_shares)
        all_currencies = {}
        for currency in db_sess.query(Currency).filter(Currency.user_id == current_user.id).all():
            if currency.name not in all_currencies:
                all_currencies[currency.name] = {"amount": 0, "original_price": 0, "current_price": 0}
            all_currencies[currency.name]["amount"] += currency.amount
            all_currencies[currency.name]["original_price"] += round(currency.original_price, 2)
            all_currencies[currency.name]["current_price"] += round(
                get_cbr_currency_rate(currency.name) * currency.amount, 2)
        all_assets.append(all_currencies)
        all_cryptocurrencies = {}
        for cryptocurrency in db_sess.query(Cryptocurrency).filter(Cryptocurrency.user_id == current_user.id).all():
            if cryptocurrency.name not in all_cryptocurrencies:
                all_cryptocurrencies[cryptocurrency.name] = {"amount": 0, "original_price": 0, "current_price": 0}
            all_cryptocurrencies[cryptocurrency.name]["amount"] += cryptocurrency.amount
            all_cryptocurrencies[cryptocurrency.name]["original_price"] += round(cryptocurrency.original_price, 2)
            all_cryptocurrencies[cryptocurrency.name]["current_price"] += round(
                get_crypto_price(cryptocurrency.name) * cryptocurrency.amount, 2)
        all_assets.append(all_cryptocurrencies)
        # print(all_assets)
    photo = url_for('static', filename='image/education.jpg')
    return render_template("index.html", title="Управляйте своими финансами легко и эффективно", photo=photo,
                           profile_image=profile_image, styles_css=styles_css, all_assets=all_assets)


@app.route('/register', methods=['GET', 'POST'])
def register():  # register page
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
        f = request.files['image']
        extension = f.filename.split(".")[-1]
        new_filename = generate_unique_filename(extension=extension)
        with open(f"static/profile_image/{new_filename}", mode="wb") as file:
            file.write(f.read())
        user = User(
            name=form.name.data,
            email=form.email.data,
            image=new_filename
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', styles_css=styles_css, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():  # login page
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
def information():  # page with information
    styles_css = url_for('static', filename='css/information.css')
    return render_template('information.html', title='О сайте', styles_css=styles_css)


@app.route('/assets')
def assets():  # page for looking first asset
    styles_css = url_for('static', filename='css/assets.css')
    db_sess = db_session.create_session()

    if a := db_sess.query(Shares).filter(Shares.user_id == current_user.id).all():
        last_share = a[-1]
        price_for_one_share = float(get_stock_price(last_share.company))
        current_price_of_share = float(last_share.amount * price_for_one_share)
        share_profit = float(current_price_of_share / last_share.original_price)
    else:
        last_share, price_for_one_share, current_price_of_share, share_profit = [None] * 4

    if a := db_sess.query(Currency).filter(Currency.user_id == current_user.id).all():
        last_currency = a[-1]
        price_for_one_currency = float(get_cbr_currency_rate(last_currency.name))
        current_price_of_currency = float(last_currency.amount * price_for_one_currency)
        currency_profit = float(price_for_one_currency / last_currency.original_price)
    else:
        last_currency, price_for_one_currency, current_price_of_currency, currency_profit = [None] * 4

    if a := db_sess.query(Cryptocurrency).filter(Cryptocurrency.user_id == current_user.id).all():
        last_cryptocurrency = a[-1]
        price_for_one_cryptocurrency = float(get_crypto_price(last_cryptocurrency.name))
        current_price_of_cryptocurrency = float(last_cryptocurrency.amount * price_for_one_cryptocurrency)
        cryptocurrency_profit = float(current_price_of_cryptocurrency / last_cryptocurrency.original_price)
    else:
        last_cryptocurrency, price_for_one_cryptocurrency, current_price_of_cryptocurrency, cryptocurrency_profit = [None] * 4
    price_for_one_asset = [price_for_one_share, price_for_one_currency, price_for_one_cryptocurrency]
    current_price = [current_price_of_share, current_price_of_currency, current_price_of_cryptocurrency]
    profit = [share_profit, currency_profit, cryptocurrency_profit]
    return render_template('assets.html', title='Активы', styles_css=styles_css, last_share=last_share,
                           last_currency=last_currency, last_cryptocurrency=last_cryptocurrency,
                           price_for_one_asset=price_for_one_asset, current_price=current_price, profit=profit)


@app.route('/assets/shares')
def shares():  # page for looking all shares
    styles_css = url_for('static', filename='css/shares.css')
    db_sess = db_session.create_session()
    all_shares = db_sess.query(Shares).filter(Shares.user_id == current_user.id).all()
    extra_data = []
    for share in all_shares:
        price_for_one_share = float(get_stock_price(share.company))
        current_price_of_share = float(share.amount * price_for_one_share)
        share_profit = float(current_price_of_share / share.original_price - 1)
        extra_data.append((price_for_one_share, current_price_of_share, share_profit))
    return render_template('shares.html', title='Акции', styles_css=styles_css, all_shares=all_shares,
                           extra_data=extra_data)


@app.route('/assets/currencies')
def currencies():  # page for looking all currencies
    styles_css = url_for('static', filename='css/currencies.css')
    db_sess = db_session.create_session()
    all_currencies = db_sess.query(Currency).filter(Currency.user_id == current_user.id).all()
    extra_data = []
    for currency in all_currencies:
        price_for_one_currency = float(get_cbr_currency_rate(currency.name))
        current_price_of_currency = float(currency.amount * price_for_one_currency)
        currency_profit = float(current_price_of_currency / currency.original_price - 1)
        extra_data.append((price_for_one_currency, current_price_of_currency, currency_profit))
    return render_template('currencies.html', title='Акции', styles_css=styles_css, all_currencies=all_currencies,
                           extra_data=extra_data)


@app.route('/assets/cryptocurrencies')
def cryptocurrencies():  # page for looking all cryptocurrencies
    styles_css = url_for('static', filename='css/cryptocurrencies.css')
    db_sess = db_session.create_session()
    all_cryptocurrencies = db_sess.query(Cryptocurrency).filter(Cryptocurrency.user_id == current_user.id).all()
    extra_data = []
    for cryptocurrency in all_cryptocurrencies:
        price_for_one_cryptocurrency = float(get_crypto_price(cryptocurrency.name))
        current_price_of_cryptocurrency = float(cryptocurrency.amount * price_for_one_cryptocurrency)
        cryptocurrency_profit = float(current_price_of_cryptocurrency / cryptocurrency.original_price - 1)
        extra_data.append((price_for_one_cryptocurrency, current_price_of_cryptocurrency, cryptocurrency_profit))
    return render_template('cryptocurrencies.html', title='Акции', styles_css=styles_css,
                           all_cryptocurrencies=all_cryptocurrencies, extra_data=extra_data)


@app.route('/assets/add/<asset_type>', methods=['GET', 'POST'])
def add(asset_type):  # page for adding assets
    styles_css = url_for('static', filename='css/add.css')
    if asset_type == "share":
        form = AddShareForm()
        if form.validate_on_submit():
            original_price = get_stock_price(form.company.data.strip().upper())
            if original_price == -1:
                return render_template('add.html', title='Активы', styles_css=styles_css, form=form,
                                       asset_type=asset_type,
                                       message="Такой акции не существует или название неправильно написано")
            db_sess = db_session.create_session()
            share = Shares()
            share.company = form.company.data.upper()
            share.amount = form.amount.data
            share.original_price = float(form.amount.data) * float(original_price)
            current_user.shares.append(share)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/assets')
    elif asset_type == "currency":
        form = AddCurrencyForm()
        if form.validate_on_submit():
            original_price = get_cbr_currency_rate(form.name.data.upper().strip())
            if original_price == -1:
                return render_template('add.html', title='Активы', styles_css=styles_css, form=form,
                                       message="Такой валюты не существует или название неправильно написано",
                                       asset_type=asset_type)
            db_sess = db_session.create_session()
            currency = Currency()
            currency.name = form.name.data.upper()
            currency.amount = form.amount.data
            currency.original_price = float(form.amount.data) * float(original_price)
            current_user.currency.append(currency)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/assets')
    else:
        form = AddCryptocurrencyForm()
        if form.validate_on_submit():
            original_price = get_crypto_price(form.name.data.strip().lower())
            if original_price == -1:
                return render_template('add.html', title='Активы', styles_css=styles_css, form=form,
                                       message="Такой криптовалюты не существует или название неправильно написано",
                                       asset_type=asset_type)
            db_sess = db_session.create_session()
            cryptocurrency = Cryptocurrency()
            cryptocurrency.name = form.name.data.capitalize()
            cryptocurrency.amount = form.amount.data
            cryptocurrency.original_price = float(form.amount.data) * float(original_price)
            current_user.cryptocurrency.append(cryptocurrency)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/assets')
    return render_template('add.html', title='Активы', styles_css=styles_css, asset_type=asset_type, form=form,
                           data=[ALL_SHARES, ALL_CURRENCY, ALL_CURRENCY])


@app.route('/assets/share_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def share_delete(id):  # sell asset
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


@app.route('/tariff')
@login_required
def tariff():
    styles_css = url_for('static', filename='css/tariff.css')
    return render_template('tariff.html', title='Тарифы', styles_css=styles_css)


@app.route('/profile')
@login_required
def profile():
    styles_css = url_for('static', filename='css/profile.css')
    user_image = url_for('static', filename=f'profile_image/{current_user.image}')
    return render_template('profile.html', title='Профиль', styles_css=styles_css, user_image=user_image)


@app.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    db_sess = db_session.create_session()
    for elem in db_sess.query(Shares).filter(Shares.user_id == current_user.id).all():
        db_sess.delete(elem)
    for elem in db_sess.query(Currency).filter(Currency.user_id == current_user.id).all():
        db_sess.delete(elem)
    for elem in db_sess.query(Cryptocurrency).filter(Cryptocurrency.user_id == current_user.id).all():
        db_sess.delete(elem)
    os.remove(f"static/profile_image/{current_user.image}")
    db_sess.delete(db_sess.query(User).filter(User.id == current_user.id).first())
    db_sess.commit()
    return redirect('/')


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
