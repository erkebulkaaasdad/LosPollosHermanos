import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'lospollos_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lospollos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, default=0)
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))
    status = db.Column(db.String(20), default='available') # available, completed
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    report_photo = db.Column(db.String(200))
    proof_photo = db.Column(db.String(200))

# --- Translations ---
TRANSLATIONS = {
    'ru': {
        'welcome': 'Добро пожаловать в LosPollos',
        'tagline': 'Вместе мы сделаем наш город лучше',
        'get_started': 'Начать использовать',
        'how_it_works': 'Как это работает?',
        'citizen_title': 'Для жителей',
        'citizen_desc': 'Сообщайте о проблемах города (мусор, ямы, освещение) и следите за их решением.',
        'worker_title': 'Для рабочих',
        'worker_desc': 'Выполняйте заявки, делайте фотоотчет и получайте вознаграждение от государства.',
        'rewards_title': 'Награды и Магазин',
        'rewards_desc': 'За каждое выполненное задание вы получаете 5 000 ₸, которые можно потратить в магазине.',
        'state_funding': 'Государственная поддержка',
        'state_desc': 'Этот проект финансируется государством Казахстан. Все выплаты производятся из бюджета по программе благоустройства.',
        'login_reg': 'Войти / Регистрация',
        'username_label': 'Логин',
        'password': 'Пароль',
        'confirm_password': 'Повторите пароль',
        'login': 'Войти',
        'register': 'Регистрация',
        'for_citizens': 'Личный кабинет жителя',
        'for_workers': 'Личный кабинет рабочего',
        'switch_to_worker': 'Перейти в Рабочий',
        'switch_to_citizen': 'Перейти в Житель',
        'shop': 'Магазин',
        'logout': 'Выйти',
        'new_report': 'Сообщить о проблеме',
        'report_type': 'Тип проблемы',
        'type_pothole': 'Яма на дороге',
        'type_traffic_light': 'Не работает светофор',
        'type_hatch': 'Открытый люк',
        'type_trash': 'Мусор / Свалка',
        'type_other': 'Другое',
        'country': 'Страна',
        'region': 'Область',
        'city': 'Город',
        'location': 'Точный адрес / Описание',
        'address_placeholder': 'Например: ул. Абая 15, возле входа',
        'photo': 'Фото проблемы',
        'submit': 'Отправить',
        'my_reports': 'Мои заявки',
        'status': 'Статус',
        'available_tasks': 'Доступные задания',
        'complete_task': 'Завершить и получить тенге',
        'proof_photo': 'Прикрепите фото результата:',
        'status_in_progress': 'В работе',
        'status_fixed': 'Исправлено',
        'no_reports': 'Вы еще не отправляли заявок.',
        'no_tasks': 'Пока нет новых заданий.',
        'about_system': 'О системе',
        'system_desc': 'Для завершения задания необходимо загрузить фотографию выполненной работы. После загрузки средства автоматически зачислятся на ваш баланс.',
        'shop_title': 'Магазин',
        'shop_desc': 'Тратьте тенге на эксклюзивные товары',
        'available_items': 'Доступные товары',
        'buy': 'Купить',
        'back_home': 'На главную',
        'location_data': 'Данные о местоположении',
        'select_country': 'Выберите или введите страну',
        'select_region': 'Выберите область',
        'select_city': 'Выберите город',
        'enter_city': 'Введите ваш город',
        'fill_all': 'Заполните все данные',
        'password_mismatch': 'Пароли не совпадают',
        'success_reg': 'Регистрация успешна! Теперь вы можете войти.',
        'error': 'Ошибка',
        'search_hint': 'Введите название для поиска',
        'item_cap': 'Фирменная кепка',
        'item_cap_desc': 'Кепка с логотипом LosPollos',
        'item_shirt': 'Футболка',
        'item_shirt_desc': 'Стильная футболка для лучших работников',
        'item_lunch': 'Сертификат на обед',
        'item_lunch_desc': 'Бесплатное комбо в нашем ресторане',
        'item_tools': 'Набор инструментов',
        'item_tools_desc': 'Профессиональный набор инструментов',
        'item_powerbank': 'Повербанк',
        'item_powerbank_desc': 'Мощный аккумулятор для ваших гаджетов',
        'item_backpack': 'Рюкзак',
        'item_backpack_desc': 'Вместительный рюкзак для работы',
        'item_earphones': 'Наушники',
        'item_earphones_desc': 'Беспроводные наушники с чистым звуком',
        'item_bike': 'Велосипед',
        'item_bike_desc': 'Надежный городской велосипед',
        'item_scooter': 'Электросамокат',
        'item_scooter_desc': 'Быстрый способ передвижения по городу'
    },
    'kk': {
        'welcome': 'LosPollos-қа қош келдіңіз',
        'tagline': 'Бірге біз қаламызды жақсартамыз',
        'get_started': 'Бастау',
        'how_it_works': 'Бұл қалай жұмыс істейді?',
        'citizen_title': 'Тұрғындар үшін',
        'citizen_desc': 'Қала мәселелері (қоқыс, шұңқырлар, жарықтандыру) туралы хабарлаңыз және олардың шешілуін қадағалаңыз.',
        'worker_title': 'Жұмысшылар үшін',
        'worker_desc': 'Өтінімдерді орындаңыз, фотоесеп жасаңыз және мемлекеттен сыйақы алыңыз.',
        'rewards_title': 'Сыйақылар және Дүкен',
        'rewards_desc': 'Әрбір орындалған тапсырма үшін сіз 5 000 ₸ аласыз, оны дүкенде жұмсауға болады.',
        'state_funding': 'Мемлекеттік қолдау',
        'state_desc': 'Бұл жобаны Қазақстан мемлекеті қаржыландырады. Барлық төлемдер абаттандыру бағдарламасы бойынша бюджеттен жүзеге асырылады.',
        'login_reg': 'Кіру / Тіркелу',
        'username_label': 'Логин',
        'password': 'Құпия сөз',
        'confirm_password': 'Құпия сөзді қайталаңыз',
        'login': 'Кіру',
        'register': 'Тіркелу',
        'for_citizens': 'Тұрғынның жеке кабинеті',
        'for_workers': 'Жұмысшының жеке кабинеті',
        'switch_to_worker': 'Жұмысшыға өту',
        'switch_to_citizen': 'Тұрғынға өту',
        'shop': 'Дүкен',
        'logout': 'Шығу',
        'new_report': 'Мәселе туралы хабарлау',
        'report_type': 'Мәселе түрі',
        'type_pothole': 'Жолдағы шұңқыр',
        'type_traffic_light': 'Бағдаршам істемейді',
        'type_hatch': 'Ашық люк',
        'type_trash': 'Қоқыс / Үйінді',
        'type_other': 'Басқа',
        'country': 'Ел',
        'region': 'Облыс',
        'city': 'Қала',
        'location': 'Нақты мекенжай / Сипаттама',
        'address_placeholder': 'Мысалы: Абай к-сі 15, кіреберіс жанында',
        'photo': 'Мәселенің фотосы',
        'submit': 'Жіберу',
        'my_reports': 'Менің өтінімдерім',
        'status': 'Мәртебесі',
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
        'back_home': 'Басты бетке',
        'location_data': 'Орналасқан жері туралы деректер',
        'select_country': 'Елді таңдаңыз немесе енгізіңіз',
        'select_region': 'Облысты таңдаңыз',
        'select_city': 'Қаланы таңдаңыз',
        'enter_city': 'Қалаңызды енгізіңіз',
        'fill_all': 'Барлық деректерді толтырыңыз',
        'password_mismatch': 'Құпия сөздер сәйкес келмейді',
        'success_reg': 'Тіркелу сәтті аяқталды! Енді кіре аласыз.',
        'error': 'Қате',
        'search_hint': 'Іздеу үшін атауды енгізіңіз',
        'item_cap': 'Фирмалық кепка',
        'item_cap_desc': 'LosPollos логотипі бар кепка',
        'item_shirt': 'Футболка',
        'item_shirt_desc': 'Үздік жұмысшыларға арналған стильді футболка',
        'item_lunch': 'Түскі ас сертификаты',
        'item_lunch_desc': 'Біздің мейрамханада тегін комбо',
        'item_tools': 'Құралдар жиынтығы',
        'item_tools_desc': 'Кәсіби құралдар жиынтығы',
        'item_powerbank': 'Повербанк',
        'item_powerbank_desc': 'Гаджеттеріңізге арналған қуатты аккумулятор',
        'item_backpack': 'Рюкзак',
        'item_backpack_desc': 'Жұмысқа арналған сыйымды рюкзак',
        'item_earphones': 'Құлаққаптар',
        'item_earphones_desc': 'Таза дыбысы бар сымсыз құлаққаптар',
        'item_bike': 'Велосипед',
        'item_bike_desc': 'Сенімді қалалық велосипед',
        'item_scooter': 'Электросамокат',
        'item_scooter_desc': 'Қала бойынша жылдам қозғалу тәсілі'
    }
}

COUNTRIES = ["Казахстан", "Россия", "США", "Китай", "Германия", "Франция", "Великобритания", "Турция", "ОАЭ", "Япония", "Южная Корея", "Канада", "Италия", "Испания", "Бразилия", "Индия", "Австралия", "Египет", "Таиланд", "Узбекистан", "Кыргызстан"]

KZ_LOCATIONS = {
    "Алматы": ["Алматы"],
    "Астана": ["Астана"],
    "Шымкент": ["Шымкент"],
    "Абайская область": ["Семей", "Аягоз", "Курчатов"],
    "Акмолинская область": ["Кокшетау", "Степногорск", "Щучинск"],
    "Актюбинская область": ["Актобе", "Кандыагаш", "Хромтау"],
    "Алматинская область": ["Конаев", "Каскелен", "Талгар"],
    "Атырауская область": ["Атырау", "Кульсары"],
    "Западно-Казахстанская область": ["Уральск", "Аксай"],
    "Жамбылская область": ["Тараз", "Шу", "Каратау"],
    "Жетысуская область": ["Талдыкорган", "Текели", "Жаркент"],
    "Карагандинская область": ["Караганда", "Темиртау", "Балхаш", "Шахтинск"],
    "Костанайская область": ["Костанай", "Рудный", "Аркалык", "Лисаковск"],
    "Кызылординская область": ["Кызылорда", "Байконур"],
    "Мангистауская область": ["Актау", "Жанаозен"],
    "Павлодарская область": ["Павлодар", "Экибастуз", "Аксу"],
    "Северо-Казахстанская область": ["Петропавловск", "Тайынша"],
    "Туркестанская область": ["Туркестан", "Кентау", "Арыс", "Сарыагаш"],
    "Улытауская область": ["Жезказган", "Сатпаев", "Каражал"],
    "Восточно-Казахстанская область": ["Усть-Каменогорск", "Риддер", "Алтай"]
}

SHOP_ITEMS = [
    {'id': 1, 'name': 'item_cap', 'desc': 'item_cap_desc', 'price': 5000},
    {'id': 2, 'name': 'item_shirt', 'desc': 'item_shirt_desc', 'price': 8000},
    {'id': 3, 'name': 'item_lunch', 'desc': 'item_lunch_desc', 'price': 3000},
    {'id': 4, 'name': 'item_tools', 'desc': 'item_tools_desc', 'price': 15000},
    {'id': 5, 'name': 'item_powerbank', 'desc': 'item_powerbank_desc', 'price': 12000},
    {'id': 6, 'name': 'item_backpack', 'desc': 'item_backpack_desc', 'price': 10000},
    {'id': 7, 'name': 'item_earphones', 'desc': 'item_earphones_desc', 'price': 20000},
    {'id': 8, 'name': 'item_bike', 'desc': 'item_bike_desc', 'price': 50000},
    {'id': 9, 'name': 'item_scooter', 'desc': 'item_scooter_desc', 'price': 80000},
]

def _(key):
    lang = session.get('lang', 'ru')
    return TRANSLATIONS.get(lang, TRANSLATIONS['ru']).get(key, key)

@app.context_processor
def utility_processor():
    return dict(_=_, current_lang=session.get('lang', 'ru'))

# --- Routes ---
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/auth')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return redirect(url_for('client'))
        session.clear()
    return render_template('index.html', countries=COUNTRIES, kz_locations=KZ_LOCATIONS)

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['ru', 'kk']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    country = request.form.get('country')
    region = request.form.get('region')
    city = request.form.get('city')
    
    if not username or not password or not country or not city:
        return jsonify({'error': _('fill_all')}), 400
        
    if password != confirm_password:
        return jsonify({'error': _('password_mismatch')}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
        
    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, password=hashed_pw, country=country, region=region, city=city)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': _('success_reg')})
    except Exception as e:
        db.session.rollback()

        return jsonify({'error': 'Server error during registration'}), 500

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id
        return jsonify({"message": "Success"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))

@app.route('/client')
def client():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('index'))
    reports = Report.query.filter_by(reporter_id=user.id).all()
    return render_template('client.html', user=user, reports=reports, countries=COUNTRIES, kz_locations=KZ_LOCATIONS)

@app.route('/worker')
def worker():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('index'))
    tasks = Report.query.filter_by(status='available').all()
    return render_template('worker.html', user=user, tasks=tasks)

@app.route('/submit_report', methods=['POST'])
def submit_report():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    title = request.form.get('title')
    location = request.form.get('location')
    country = request.form.get('country')
    region = request.form.get('region')
    city = request.form.get('city')
    photo = request.files.get('photo')
    
    # Debug print
    print(f"DEBUG: title={title}, location={location}, country={country}, city={city}")
    
    if not title or not location or not country or not city:
        return jsonify({'error': _('fill_all')}), 400
        
    filename = None
    if photo:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    new_report = Report(
        title=title, 
        location=location, 
        country=country, 
        region=region, 
        city=city,
        reporter_id=session['user_id'],
        report_photo=filename
    )
    db.session.add(new_report)
    db.session.commit()
    
    return jsonify({'message': 'Success'})

@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    task = Report.query.get(task_id)
    photo = request.files.get('photo')
    
    if not photo:
        return jsonify({'error': 'Photo required'}), 400
        
    if task and task.status == 'available':
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        task.status = 'completed'
        task.proof_photo = filename
        user.points += 5000
        db.session.commit()
        return jsonify({'message': 'Success'})
    return jsonify({'error': 'Task not found'}), 404

@app.route('/shop')
def shop():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('index'))
    return render_template('shop.html', user=user, items=SHOP_ITEMS)

@app.route('/buy/<int:item_id>', methods=['POST'])
def buy(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    item = next((i for i in SHOP_ITEMS if i['id'] == item_id), None)
    
    if item and user.points >= item['price']:
        user.points -= item['price']
        db.session.commit()
        return jsonify({'message': 'Success'})
    return jsonify({'error': 'Not enough Tenge'}), 400

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
