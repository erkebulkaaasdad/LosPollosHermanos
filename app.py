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
        'state_funding_title': 'Государственная поддержка',
        'state_funding_desc': 'Проект финансируется государством Казахстан. Все выплаты рабочим производятся из государственного бюджета для поддержания чистоты и порядка в наших городах.',
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
        'back_home': 'На главную',
        'password': 'Пароль',
        'email_label': 'Email',
        'location_data': 'Данные о местоположении',
        'select_country': 'Выберите или введите страну',
        'select_region': 'Выберите область',
        'select_city': 'Выберите город',
        'enter_city': 'Введите ваш город',
        'fill_all': 'Заполните все данные',
        'success_reg': 'Регистрация успешна! Теперь вы можете войти.',
        'error': 'Ошибка',
        'search_hint': 'Введите название для поиска',
        'item_cap': 'Фирменная кепка',
        'item_cap_desc': 'Кепка с логотипом LosPollos',
        'item_shirt': 'Футболка',
        'item_shirt_desc': 'Стильная футболка для лучших работников',
        'item_lunch': 'Сертификат на обед',
        'item_lunch_desc': 'Бесплатное комбо в нашем ресторане',
        'item_tools': 'Инструменты',
        'item_tools_desc': 'Набор профессиональных инструментов',
        'type_pothole': 'Яма на дороге',
        'type_traffic_light': 'Сломанный светофор',
        'type_hatch': 'Открытый люк',
        'type_trash': 'Мусор',
        'type_other': 'Другое',
        'address_placeholder': 'Например: ул. Абая, дом 25'
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
        'state_funding_title': 'Мемлекеттік қолдау',
        'state_funding_desc': 'Жобаны Қазақстан мемлекеті қаржыландырады. Жұмысшыларға барлық төлемдер қалаларымыздағы тазалық пен тәртіпті сақтау үшін мемлекеттік бюджеттен жүзеге асырылады.',
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
        'back_home': 'Басты бетке',
        'password': 'Құпия сөз',
        'email_label': 'Email',
        'location_data': 'Орналасқан жері туралы деректер',
        'select_country': 'Елді таңдаңыз немесе енгізіңіз',
        'select_region': 'Облысты таңдаңыз',
        'select_city': 'Қаланы таңдаңыз',
        'enter_city': 'Қалаңызды енгізіңіз',
        'fill_all': 'Барлық деректерді толтырыңыз',
        'success_reg': 'Тіркелу сәтті аяқталды! Енді кіре аласыз.',
        'error': 'Қате',
        'search_hint': 'Іздеу үшін атауды енгізіңіз',
        'item_cap': 'Фирмалық кепка',
        'item_cap_desc': 'LosPollos логотипі бар кепка',
        'item_shirt': 'Футболка',
        'item_shirt_desc': 'Үздік жұмысшыларға арналған стильді футболка',
        'item_lunch': 'Түскі асқа сертификат',
        'item_lunch_desc': 'Біздің мейрамханада тегін комбо',
        'item_tools': 'Құралдар',
        'item_tools_desc': 'Кәсіби құралдар жиынтығы',
        'type_pothole': 'Жолдағы шұңқыр',
        'type_traffic_light': 'Бұзылған бағдаршам',
        'type_hatch': 'Ашық люк',
        'type_trash': 'Қоқыс',
        'type_other': 'Басқа',
        'address_placeholder': 'Мысалы: Абай к-сі, 25 үй'
    }
}

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
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
    status = db.Column(db.String(20), default='in_progress')
    reward_points = db.Column(db.Integer, default=5000)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    report_photo = db.Column(db.String(200))
    proof_photo = db.Column(db.String(200))

with app.app_context():
    db.create_all()

def _(key):
    lang = session.get('lang', 'ru')
    return TRANSLATIONS.get(lang, TRANSLATIONS['ru']).get(key, key)

@app.context_processor
def inject_translate():
    return dict(_=_, current_lang=session.get('lang', 'ru'))

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['ru', 'kk']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return redirect(url_for('client'))
        else:
            session.clear()
    return render_template('welcome.html')

@app.route('/auth')
def auth():
    if 'user_id' in session:
        return redirect(url_for('client'))
    return render_template('index.html', countries=ALL_COUNTRIES, kz_locations=KZ_LOCATIONS)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    country = data.get('country')
    region = data.get('region')
    city = data.get('city')
    
    if not email or not password or not country or not city:
        return jsonify({'error': _('fill_all')}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
        
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password, country=country, region=region, city=city)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': _('success_reg')})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({'message': 'Success'})
    
    return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/client')
def client():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    reports = Report.query.filter_by(reporter_id=user.id).all()
    return render_template('client.html', user=user, reports=reports, countries=ALL_COUNTRIES, kz_locations=KZ_LOCATIONS)

@app.route('/worker')
def worker():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    tasks = Report.query.filter_by(status='in_progress').all()
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
    
    if not task or task.status != 'in_progress':
        return jsonify({'error': 'Task not found or already completed'}), 404
        
    proof_photo = request.files.get('proof_photo')
    if not proof_photo:
        return jsonify({'error': 'Photo proof required'}), 400
        
    filename = secure_filename(proof_photo.filename)
    proof_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    task.status = 'fixed'
    task.proof_photo = filename
    user.points += task.reward_points
    db.session.commit()
    
    return jsonify({'message': 'Success'})

@app.route('/shop')
def shop():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    
    items = [
        {'id': 1, 'name': _('item_cap'), 'desc': _('item_cap_desc'), 'price': 10000},
        {'id': 2, 'name': _('item_shirt'), 'desc': _('item_shirt_desc'), 'price': 15000},
        {'id': 3, 'name': _('item_lunch'), 'desc': _('item_lunch_desc'), 'price': 5000},
        {'id': 4, 'name': _('item_tools'), 'desc': _('item_tools_desc'), 'price': 25000},
    ]
    return render_template('shop.html', user=user, items=items)

@app.route('/buy/<int:item_id>', methods=['POST'])
def buy(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user = User.query.get(session['user_id'])
    prices = {1: 10000, 2: 15000, 3: 5000, 4: 25000}
    price = prices.get(item_id)
    
    if not price:
        return jsonify({'error': 'Item not found'}), 404
        
    if user.points < price:
        return jsonify({'error': 'Not enough money'}), 400
        
    user.points -= price
    db.session.commit()
    return jsonify({'message': 'Success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
