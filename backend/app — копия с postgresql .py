from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://default:qQNTd6YtJK7j@ep-tiny-scene-a214kivr.eu-central-1.aws.neon.tech:5432/verceldb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models
class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.String, nullable=False)

#Instead of aplying app_context every where
def with_app_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with app.app_context():
            return func(*args, **kwargs)
    return wrapper


# Initialize thread pool executor
executor = ThreadPoolExecutor(max_workers=5)

# Scheduler tasks
def run_script(script_name):
    subprocess.run(['python', f'./scripts/{script_name}'])

def run_script_staff():
    executor.submit(run_script, 'staff_data.py')

def run_script_voronka():
    executor.submit(run_script, 'voronka_and_stage.py')

def run_script_products():
    executor.submit(run_script, 'product_data_bx.py')

def run_script_deals():
    executor.submit(run_script, 'deal_and_productrows.py')

def run_script_test():
    executor.submit(run_script, 'test.py')

@with_app_context
def insert_current_datetime():
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = Test(date_time=current_datetime)
    db.session.add(new_entry)
    db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(run_script_staff, 'interval', days=1)
scheduler.add_job(run_script_voronka, 'interval', days=1)
scheduler.add_job(run_script_products, 'interval', minutes=60)
scheduler.add_job(run_script_deals, 'interval', minutes=65)
scheduler.add_job(insert_current_datetime, 'interval', seconds=10)
scheduler.start()


insert_current_datetime()

def fetch_data_from_test():
    results = Test.query.all()
    return [{"id": result.id, "date_time": result.date_time} for result in results]

@app.route('/api/test_data', methods=['GET'])
def get_test_data():
    data = fetch_data_from_test()
    return jsonify(data)

@app.route('/api/run_test_script', methods=['POST'])
def run_test_script():
    run_script_test()
    return jsonify({"message": "Script test.py has been started."})

@app.route('/api/data', methods=['GET'])
def get_data():
    data = fetch_data_from_db()
    return jsonify(data)

@app.route('/api/search', methods=['POST'])
def search_data_fromDB():
    search_params = request.json
    query = db.session.query(Item)
    if 'exactDate' in search_params:
        exact_date = datetime.strptime(search_params['exactDate'], '%Y-%m-%d').date()
        query = query.filter(func.DATE(Item.timestampX) == exact_date)
    if 'startDate' in search_params and 'endDate' in search_params:
        start_date = datetime.strptime(search_params['startDate'], '%Y-%m-%d').date()
        end_date = datetime.strptime(search_params['endDate'], '%Y-%m-%d').date()
        query = query.filter(func.DATE(Item.timestampX).between(start_date, end_date))
    if 'iblockSectionId' in search_params:
        query = query.filter(Item.iblockSectionId.in_(search_params['iblockSectionId']))
    # Add other filters as needed
    data = [item.as_dict() for item in query.all()]
    return jsonify(data)

@app.route('/api/get_razdel_list', methods=['GET'])
def get_razdel_list():
    razdels = [
        {'id': 154, 'name': 'AIRBA FRESH'},
        {'id': 168, 'name': 'Индивидуальная Упаковка'},
        {'id': 214, 'name': 'Сырье'},
        {'id': 234, 'name': 'Импортированные товары'},
        {'id': 238, 'name': 'Разработка'},
        {'id': 254, 'name': 'Упаковка'},
        {'id': 260, 'name': 'Брак'},
        {'id': 262, 'name': 'Компоненты'},
        {'id': 264, 'name': 'Полуфабрикаты'},
        {'id': 274, 'name': 'Алмата'},
        {'id': 276, 'name': 'test'},
        {'id': 278, 'name': 'Дессерты'},
        {'id': 280, 'name': 'Не нарезанные дессерты'},
        {'id': 308, 'name': 'Десерты 1шт списание'}
    ]
    return jsonify(razdels)

def fetch_deals_from_db(filters):
    query = db.session.query(Deal).join(VoronkaStage, Deal.stage_id == VoronkaStage.stage_id) \
        .join(Staff, Deal.responsible_id == Staff.staff_id) \
        .join(Voronka, Deal.voronka_id == Voronka.voronka_id)
    
    if 'date_createExact' in filters:
        date_create = datetime.strptime(filters['date_createExact'], '%Y-%m-%d').date()
        query = query.filter(func.DATE(Deal.date_create) == date_create)
    
    if 'date_createStart' in filters and 'date_createEnd' in filters:
        date_create_start = datetime.strptime(filters['date_createStart'], '%Y-%m-%d').date()
        date_create_end = datetime.strptime(filters['date_createEnd'], '%Y-%m-%d').date()
        query = query.filter(func.DATE(Deal.date_create).between(date_create_start, date_create_end))
    
    # Add other filters as needed
    
    data = [deal.as_dict() for deal in query.all()]
    return data

@app.route('/api/deals', methods=['POST'])
def get_deals():
    filters = request.json
    data = fetch_deals_from_db(filters)
    return jsonify(data)

@app.route('/api/deal_products/<int:id_deal>', methods=['GET'])
def get_deal_products(id_deal):
    products = DealProduct.query.filter_by(id_deal=id_deal).all()
    data = [product.as_dict() for product in products]
    store_name_list = {1: 'Производство', 2: 'Астана', 4: 'Алматы', 6: 'Шымкент', 8: 'Караганда'}
    for item in data:
        store_id = item['store_id']
        item['store_id'] = store_name_list.get(store_id, '')
    return jsonify(data)

@app.route('/api/deal_by_product/<int:product_id>', methods=['GET'])
def get_deal_by_product(product_id):
    query = db.session.query(Deal).join(VoronkaStage, Deal.stage_id == VoronkaStage.stage_id) \
        .join(Staff, Deal.responsible_id == Staff.staff_id) \
        .join(Voronka, Deal.voronka_id == Voronka.voronka_id) \
        .join(DealProduct, Deal.id_deal == DealProduct.id_deal) \
        .filter(DealProduct.product_id == product_id)
    
    data = [deal.as_dict() for deal in query.all()]
    return jsonify(data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
