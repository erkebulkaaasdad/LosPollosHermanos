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

# Location Data
ALL_COUNTRIES = [
    "Афганистан", "Албания", "Алжир", "Андорра", "Ангола", "Антигуа и Барбуда", "Аргентина", "Армения", "Австралия", "Австрия", "Азербайджан",
    "Багамы", "Бахрейн", "Бангладеш", "Барбадос", "Беларусь", "Бельгия", "Белиз", "Бенин", "Бутан", "Боливия", "Босния и Герцеговина", "Ботсвана", "Бразилия", "Бруней", "Болгария", "Буркина-Фасо", "Бурунди",
    "Кабо-Верде", "Камбоджа", "Камерун", "Канада", "Центральноафриканская Республика", "Чад", "Чили", "Китай", "Колумбия", "Коморы", "Конго", "Коста-Рика", "Хорватия", "Куба", "Кипр", "Чехия",
    "Дания", "Джибути", "Доминика", "Доминиканская Республика", "Эквадор", "Египет", "Сальвадор", "Экваториальная Гвинея", "Эритрея", "Эстония", "Эсватини", "Эфиопия",
    "Фиджи", "Финляндия", "Франция", "Габон", "Гамбия", "Грузия", "Германия", "Гана", "Греция", "Гренада", "Гватемала", "Гвинея", "Гвинея-Бисау", "Гайана",
    "Гаити", "Гондурас", "Венгрия", "Исландия", "Индия", "Индонезия", "Иран", "Ирак", "Ирландия", "Израиль", "Италия",
    "Ямайка", "Япония", "Иордания", "Казахстан", "Кения", "Кирибати", "Корея Северная", "Корея Южная", "Кувейт", "Кыргызстан",
    "Лаос", "Латвия", "Ливан", "Лесото", "Либерия", "Ливия", "Лихтенштейн", "Литва", "Люксембург",
    "Мадагаскар", "Малави", "Малайзия", "Мальдивы", "Мали", "Мальта", "Маршалловы Острова", "Мавритания", "Маврикий", "Мексика", "Микронезия", "Молдова", "Монако", "Монголия", "Черногория", "Марокко", "Мозамбик", "Мьянма",
    "Намибия", "Науру", "Непал", "Нидерланды", "Новая Зеландия", "Никарагуа", "Нигер", "Нигерия", "Северная Македония", "Норвегия",
    "Оман", "Пакистан", "Палау", "Панама", "Папуа-Новая Гвинея", "Парагвай", "Перу", "Филиппины", "Польша", "Португалия",
    "Катар", "Румыния", "Россия", "Руанда", "Сент-Китс и Невис", "Сент-Люсия", "Сент-Винсент и Гренадины", "Самоа", "Сан-Марино", "Сан-Томе и Принсипи", "Саудовская Аравия", "Сенегал", "Сербия", "Сейшелы", "Сьерра-Леоне", "Сингапур", "Словакия", "Словения", "Соломоновы Острова", "Сомали", "Южная Африка", "Южный Судан", "Испания", "Шри-Ланка", "Судан", "Суринам", "Швеция", "Швейцария", "Сирия",
    "Таджикистан", "Танзания", "Таиланд", "Тимор-Лешти", "Того", "Тонга", "Тринидад и Тобаго", "Тунис", "Турция", "Туркменистан", "Тувалу",
    "Уганда", "Украина", "Объединенные Арабские Эмираты", "Великобритания", "США", "Уругвай", "Узбекистан",
    "Вануату", "Венесуэла", "Вьетнам", "Йемен", "Замбия", "Зимбабве"
]

KZ_LOCATIONS = {
    "Алматинская область": ["Алматы", "Талдыкорган", "Каскелен"],
    "Астанинская область": ["Астана"],
    "Акмолинская область": ["Кокшетау", "Степногорск"],
    "Карагандинская область": ["Караганда", "Темиртау", "Балхаш"],
    "Шымкент": ["Шымкент"],
    "Абайская область": ["Семей", "Курчатов"],
    "Жетысуская область": ["Талдыкорган", "Текели"],
    "Улытауская область": ["Жезказган", "Сатпаев"],
    "Актюбинская область": ["Актобе", "Кандыагаш"],
    "Атырауская область": ["Атырау", "Кульсары"],
    "Восточно-Казахстанская область": ["Усть-Каменогорск", "Риддер"],
    "Жамбылская область": ["Тараз", "Шу"],
    "Западно-Казахстанская область": ["Уральск", "Аксай"],
    "Костанайская область": ["Костанай", "Рудный"],
    "Кызылординская область": ["Кызылорда", "Байконур"],
    "Мангистауская область": ["Актау", "Жанаозен"],
    "Павлодарская область": ["Павлодар", "Экибастуз"],
    "Северо-Казахстанская область": ["Петропавловск"],
    "Туркестанская область": ["Туркестан", "Кентау"]
}

# Translations
TRANSLATIONS = {
    'ru': {
        'welcome_title': 'Добро пожаловать в LosPollos',
        'tagline': 'Вместе мы сделаем наш город лучше',
        'how_it_works': 'Как это работает?',
        'description': 'Наш сервис объединяет активных жителей и трудолюбивых рабочих для решения городских проблем.',
        'for_citizens': 'Жителям',
        'citizen_desc': 'Видите яму на дороге или сломанный светофор? Просто сфотографируйте и отправьте заявку. Мы найдем того, кто это исправит.',
        'for_workers': 'Рабочим',
        'worker_desc': 'Выполняйте заявки от жителей, прикрепляйте фотоотчет и получайте выплаты в Тенге за каждое успешно завершенное дело.',
        'rewards': 'Награды',
        'rewards_desc': 'Тратьте заработанные средства в нашем магазине на фирменную одежду, инструменты или сертификаты на вкусную еду.',
        'start_button': 'Начать использовать',
        'trash_on_streets': 'Горы мусора на улицах',
        'potholes_on_roads': 'Опасные ямы на дорогах',
        'illegal_dumps': 'Несанкционированные свалки',
        'login': 'Войти',
        'register': 'Регистрация',
        'logout': 'Выйти',
        'switch_to_worker': 'Перейти в Рабочий',
        'switch_to_citizen': 'Перейти в Житель',
        'shop': 'Магазин',
        'balance': 'Ваш баланс',
        'my_reports': 'Мои заявки',
        'new_report': 'Новая заявка',
        'report_type': 'Тип проблемы',
        'location': 'Адрес / место',
        'country': 'Страна',
        'region': 'Область',
        'city': 'Город',
        'photo': 'Фото проблемы',
        'submit': 'Отправить',
        'available_tasks': 'Доступные задания',
        'complete_task': 'Завершить и получить баллы',
        'proof_photo': 'Прикрепите фото результата:',
        'status_in_progress': 'В работе',
        'status_fixed': 'Исправлено',
        'no_reports': 'Вы еще не отправляли заявок.',
        'no_tasks': 'Пока нет новых заданий.',
        'about_system': 'О системе',
        'system_desc': 'Для завершения задания необходимо загрузить фотографию выполненной работы. После загрузки средства будут начислены на ваш баланс автоматически.',
        'shop_title': 'Магазин',
        'shop_desc': 'Тратьте баллы на эксклюзивные товары',
        'available_items': 'Доступные товары',
        'buy': 'Купить',
        'back_home': 'На главную'
    },
    'kk': {
        'welcome_title': 'LosPollos-қа қош келдіңіз',
        'tagline': 'Бірге біз қаламызды жақсартамыз',
        'how_it_works': 'Бұл қалай жұмыс істейді?',
        'description': 'Біздің сервис қалалық мәселелерді шешу үшін белсенді тұрғындар мен еңбекқор жұмысшыларды біріктіреді.',
        'for_citizens': 'Тұрғындарға',
        'citizen_desc': 'Жолдағы шұңқырды немесе бұзылған бағдаршамды көрдіңіз бе? Фотоға түсіріп, өтінім жіберіңіз. Біз оны жөндейтін адамды табамыз.',
        'for_workers': 'Жұмысшыларға',
        'worker_desc': 'Тұрғындардың өтінімдерін орындаңыз, фотоесепті тіркеңіз және әрбір сәтті аяқталған іс үшін Теңгемен төлем алыңыз.',
        'rewards': 'Марапаттар',
        'rewards_desc': 'Тапқан қаражатыңызды біздің дүкенде фирмалық киімдерге, құралдарға немесе дәмді тағамға сертификаттарға жұмсаңыз.',
        'start_button': 'Бастау',
        'trash_on_streets': 'Көшедегі қоқыс үйінділері',
        'potholes_on_roads': 'Жолдағы қауіпті шұңқырлар',
        'illegal_dumps': 'Рұқсат етілмеген қоқыс орындары',
        'login': 'Кіру',
        'register': 'Тіркелу',
        'logout': 'Шығу',
        'switch_to_worker': 'Жұмысшыға ауысу',
        'switch_to_citizen': 'Тұрғынға ауысу',
        'shop': 'Дүкен',
        'balance': 'Сіздің балансыңыз',
        'my_reports': 'Менің өтінімдерім',
        'new_report': 'Жаңа өтінім',
        'report_type': 'Мәселе түрі',
        'location': 'Мекен-жайы / орны',
        'country': 'Ел',
        'region': 'Облыс',
        'city': 'Қала',
        'photo': 'Мәселенің фотосы',
        'submit': 'Жіберу',
        'available_tasks': 'Қолжетімді тапсырмалар',
        'complete_task': 'Аяқтау және теңге алу',
        'proof_photo': 'Нәтиженің фотосын тіркеңіз:',
        'status_in_progress': 'Жұмыста',
        'status_fixed': 'Жөнделді',
        'no_reports': 'Сіз әлі өтінім жіберген жоқсыз.',
        'no_tasks': 'Әзірге жаңа тапсырмалар жоқ.',
        'about_system': 'Жүйе туралы',
        'system_desc': 'Тапсырманы аяқтау үшін орындалған жұмыстың фотосуретін жүктеу қажет. Жүктегеннен кейін қаражат сіздің балансыңызға автоматты түрде аударылады.',
        'shop_title': 'Дүкен',
        'shop_desc': 'Теңгелерді эксклюзивті тауарларға жұмсаңыз',
        'available_items': 'Қолжетімді тауарлар',
        'buy': 'Сатып алу',
        'back_home': 'Басты бетке'
    }
}

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user') 
    points = db.Column(db.Integer, default=0)
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))
    reward_points = db.Column(db.Integer, default=5000)
    status = db.Column(db.String(20), default='available') 
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    report_photo = db.Column(db.String(200), nullable=True)
    proof_photo = db.Column(db.String(200), nullable=True)

class ShopItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))

# Context Processor for translations
@app.context_processor
def inject_translate():
    lang = session.get('lang', 'ru')
    def translate(key):
        return TRANSLATIONS.get(lang, TRANSLATIONS['ru']).get(key, key)
    return dict(_=translate, current_lang=lang)

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['ru', 'kk']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('welcome'))

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
    return render_template('index.html', countries=ALL_COUNTRIES, kz_locations=KZ_LOCATIONS)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    country = data.get('country')
    region = data.get('region')
    city = data.get('city')
    
    if not email or not password:
        return jsonify({'error': 'Missing data'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(
        email=email, 
        password=hashed_password,
        country=country,
        region=region,
        city=city
    )
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
    return render_template('client.html', reports=my_reports, user=user, countries=ALL_COUNTRIES, kz_locations=KZ_LOCATIONS)

@app.route('/submit_report', methods=['POST'])
def submit_report():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    title = request.form.get('type')
    location = request.form.get('location')
    country = request.form.get('country')
    region = request.form.get('region')
    city = request.form.get('city')
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
        country=country,
        region=region,
        city=city,
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
