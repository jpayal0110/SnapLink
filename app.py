import string, random
from flask import Flask, render_template, request, redirect, url_for
from models import db, URL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_code = generate_short_code()

        # Ensure unique short_code
        while URL.query.filter_by(short_code=short_code).first():
            short_code = generate_short_code()

        new_url = URL(original_url=original_url, short_code=short_code)
        db.session.add(new_url)
        db.session.commit()
        # Build absolute URL that includes host and port
        short_url = url_for('redirect_url', short_code=short_code, _external=True)

    return render_template('index.html', short_url=short_url)

@app.route('/<short_code>')
def redirect_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        url.clicks += 1
        db.session.commit()
        return redirect(url.original_url)
    return render_template('not_found.html')

# @app.route('/stats')
# def stats():
#     urls = URL.query.all()
#     return render_template('stats.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
