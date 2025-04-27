from flask import Flask, render_template, url_for, redirect
from forms.loginform import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_very_secret_key'


@app.route('/')
def index():
    photo = url_for('static', filename='image/education.jpg')
    styles_css = url_for('static', filename='css/index.css')
    return render_template("index.html", title="Управляйте своими финансами легко и эффективно", photo=photo,
                           styles_css=styles_css)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    styles_css = url_for('static', filename='css/login.css')
    if form.validate_on_submit():
        return redirect('/success')
    return render_template("login.html", title='Авторизация', styles_css=styles_css, form=form)


def main():
    app.run()


if __name__ == "__main__":
    main()
