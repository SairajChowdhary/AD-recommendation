from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, Ad, AdAnalytics, User
from nlp_utils import extract_keywords
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/yourdb'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    if User.query.filter_by(username=username).first():
        return "User exists", 400
    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for('index'))
    return "Invalid credentials", 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/recommend', methods=['POST'])
@login_required
def recommend():
    data = request.get_json()
    content = data.get('content', '')
    query = extract_keywords(content)
    ads = Ad.query.all()
    ad_texts = [ad.keywords for ad in ads]
    vectorizer = TfidfVectorizer()
    ad_vectors = vectorizer.fit_transform(ad_texts)
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, ad_vectors).flatten()
    scores = similarities * [ad.bid for ad in ads]
    top_indices = scores.argsort()[::-1][:2]
    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            ad = ads[idx]
            analytic = AdAnalytics.query.filter_by(ad_id=ad.id).first()
            if not analytic:
                analytic = AdAnalytics(ad_id=ad.id)
                db.session.add(analytic)
            analytic.impressions += 1
            db.session.commit()
            results.append({
                "id": ad.id,
                "title": ad.title,
                "category": ad.category,
                "bid": ad.bid
            })
    return jsonify(results)

@app.route('/ad_click', methods=['POST'])
@login_required
def ad_click():
    ad_id = request.json['ad_id']
    analytic = AdAnalytics.query.filter_by(ad_id=ad_id).first()
    if analytic:
        analytic.clicks += 1
        db.session.commit()
    return jsonify(success=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
