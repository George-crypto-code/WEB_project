from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def index():
    photo = url_for('static', filename='image/back_ground.jpg')
    styles_css = url_for('static', filename='css/index.css')
    return render_template("index.html", title="Управляйте своими финансами легко и эффективно!", backgorund=photo,
                           styles_css=styles_css)


def main():
    app.run()


if __name__ == "__main__":
    main()
