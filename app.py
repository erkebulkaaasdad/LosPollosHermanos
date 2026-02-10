from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'lospollos_secret_key'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload configuration
UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user') 
    points = db.Column(db.Integer, default=0)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    reward_points = db.Column(db.Integer, default=300)
    status = db.Column(db.String(20), default='available') # 'available', 'completed'
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    report_photo = db.Column(db.String(200), nullable=True)
    proof_photo = db.Column(db.String(200), nullable=True)

class ShopItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))

# Initialize database and seed data
with app.app_context():
    db.create_all()
    if not ShopItem.query.first():
        items = [
            ShopItem(name="Фирменная кепка", price=5000, description="Кепка с логотипом LosPollos"),
            ShopItem(name="Футболка", price=10000, description="Стильная футболка для лучших работников"),
            ShopItem(name="Сертификат на обед", price=15000, description="Бесплатное комбо в нашем ресторане"),
            ShopItem(name="Инструменты", price=30000, description="Набор профессиональных инструментов")
        ]
        db.session.bulk_save_objects(items)
    db.session.commit()

@app.route('/')
def welcome():
    if 'user_id' in session:
        return redirect(url_for('client'))
    return render_template('welcome.html')

@app.route('/auth')
def auth():
    if 'user_id' in session:
        return redirect(url_for('client'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing data'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful'}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))

@app.route('/client')
def client():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    my_reports = Task.query.filter_by(reporter_id=user.id).all()
    return render_template('client.html', reports=my_reports, user=user)

@app.route('/submit_report', methods=['POST'])
def submit_report():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    title = request.form.get('type')
    location = request.form.get('location')
    file = request.files.get('photo')
    
    if not title or not location:
        return jsonify({'error': 'Title and location are required'}), 400
    
    filename = None
    if file:
        filename = secure_filename(f"report_{session['user_id']}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    new_task = Task(
        title=title,
        location=location,
        reporter_id=session['user_id'],
        report_photo=filename,
        reward_points=5000
    )
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({'message': 'Report submitted successfully'}), 201

@app.route('/worker')
def worker():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    tasks = Task.query.filter_by(status='available').all()
    return render_template('worker.html', user=user, tasks=tasks)

@app.route('/complete_task', methods=['POST'])
def complete_task():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    task_id = request.form.get('task_id')
    file = request.files.get('photo')
    
    if not file:
        return jsonify({'error': 'Photo proof is required'}), 400
    
    task = Task.query.get(task_id)
    if task and task.status == 'available':
        filename = secure_filename(f"proof_{task_id}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        task.status = 'completed'
        task.worker_id = user.id
        task.proof_photo = filename
        user.points += task.reward_points
        db.session.commit()
        return jsonify({'message': 'Task completed with proof', 'points': user.points}), 200
    
    return jsonify({'error': 'Task not found or already completed'}), 400

@app.route('/shop')
def shop():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    items = ShopItem.query.all()
    return render_template('shop.html', user=user, items=items)

@app.route('/buy_item', methods=['POST'])
def buy_item():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    item_id = data.get('item_id')
    item = ShopItem.query.get(item_id)
    user = User.query.get(session['user_id'])
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if item and user.points >= item.price:
        user.points -= item.price
        db.session.commit()
        return jsonify({'message': f'Purchased {item.name}', 'points': user.points}), 200
    
    return jsonify({'error': 'Not enough points or item not found'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
