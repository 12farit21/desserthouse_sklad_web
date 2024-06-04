from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Initialize Flask app
app = Flask(__name__)
CORS(app)


DATABASE_PATH = './scripts/DB/my_database.db'

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

scheduler = BackgroundScheduler()
scheduler.add_job(run_script_staff, 'interval', days=1)
scheduler.add_job(run_script_voronka, 'interval', days=1)
scheduler.add_job(run_script_products, 'interval', minutes=60)
scheduler.add_job(run_script_deals, 'interval', minutes=65)
#scheduler.add_job(run_script_test, 'interval', seconds=10)
scheduler.start()

#run_script_test()

def fetch_data_from_test():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return data

@app.route('/api/test_data', methods=['GET'])
def get_test_data():
    data = fetch_data_from_test()
    return jsonify(data)

@app.route('/api/run_test_script', methods=['POST'])
def run_test_script():
    run_script_test()
    return jsonify({"message": "Script test.py has been started."})

# Function to fetch data from the database
def fetch_data_from_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")  
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return data

@app.route('/api/data', methods=['GET'])
def get_data():
    data = fetch_data_from_db()
    return jsonify(data)

@app.route('/api/search', methods=['POST'])
def search_data_fromDB():
    search_params = request.json
    print(search_params)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query_conditions = []
    params = []

    for key, value in search_params.items():
        if value:
            if key == 'exactDate':
                query_conditions.append("DATE(timestampX) = ?")
                params.append(datetime.strptime(value, '%Y-%m-%d').date())
            elif key == 'startDate' or key == 'endDate':
                if 'startDate' in search_params and 'endDate' in search_params:
                    query_conditions.append("DATE(timestampX) BETWEEN ? AND ?")
                    params.append(datetime.strptime(search_params['startDate'], '%Y-%m-%d').date())
                    params.append(datetime.strptime(search_params['endDate'], '%Y-%m-%d').date())
                    break  
            elif key == 'iblockSectionId':
                for key2 in key:
                    placeholders = ', '.join(['?' for _ in value])  # Create placeholders for each id
                    query_conditions.append(f"{key} IN ({placeholders})")
                    params.extend(value)  # Add each id to the parameters list
            else:
                query_conditions.append(f"{key} = ?")
                params.append(value)

    where_clause = "WHERE " + " AND ".join(query_conditions) if query_conditions else ""
    cursor.execute(f"SELECT * FROM items {where_clause}", params)
    
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)

@app.route('/api/get_razdel_list', methods=['GET'])
def get_razdel_list():
    razdels = [
        {'id': 154, 'name': 'AIRBA FRESH'},
        {'id': 168, 'name': 'ÐÐ½Ð´Ð¸Ð²Ð¸Ð´ÑÐ°Ð»ÑÐ½Ð°Ñ Ð£Ð¿Ð°ÐºÐ¾Ð²ÐºÐ°'},
        {'id': 214, 'name': 'Ð¡ÑÑÑÐµ'},
        {'id': 234, 'name': 'ÐÐ¼Ð¿Ð¾ÑÑÐ¸ÑÐ¾Ð²Ð°Ð½Ð½ÑÐµ ÑÐ¾Ð²Ð°ÑÑ'},
        {'id': 238, 'name': 'Ð Ð°Ð·ÑÐ°Ð±Ð¾ÑÐºÐ°'},
        {'id': 254, 'name': 'Ð£Ð¿Ð°ÐºÐ¾Ð²ÐºÐ°'},
        {'id': 260, 'name': 'ÐÑÐ°Ðº'},
        {'id': 262, 'name': 'ÐÐ¾Ð¼Ð¿Ð¾Ð½ÐµÐ½ÑÑ'},
        {'id': 264, 'name': 'ÐÐ¾Ð»ÑÑÐ°Ð±ÑÐ¸ÐºÐ°ÑÑ'},
        {'id': 274, 'name': 'ÐÐ»Ð¼Ð°ÑÐ°'},
        {'id': 276, 'name': 'test'},
        {'id': 278, 'name': 'ÐÐµÑÑÐµÑÑÑ'},
        {'id': 280, 'name': 'ÐÐµ Ð½Ð°ÑÐµÐ·Ð°Ð½Ð½ÑÐµ Ð´ÐµÑÑÐµÑÑÑ'},
        {'id': 308, 'name': 'ÐÐµÑÐµÑÑÑ 1ÑÑ ÑÐ¿Ð¸ÑÐ°Ð½Ð¸Ðµ'}
    ]

    return jsonify(razdels)

def fetch_deals_from_db(filters):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query_conditions = []
    params = []

    for key, value in filters.items():
        if value:
            if key.endswith('Exact'):
                field = key[:-5]
                query_conditions.append(f"DATE({field}) = ?")
                params.append(datetime.strptime(value, '%Y-%m-%d').date())
            elif key.endswith('Start') or key.endswith('End'):
                field = key[:-5]
                if f"{field}Start" in filters and f"{field}End" in filters:
                    query_conditions.append(f"DATE({field}) BETWEEN ? AND ?")
                    params.append(datetime.strptime(filters[f"{field}Start"], '%Y-%m-%d').date())
                    params.append(datetime.strptime(filters[f"{field}End"], '%Y-%m-%d').date())
                    break  
            else:
                query_conditions.append(f"{key} = ?")
                params.append(value)

    where_clause = "WHERE " + " AND ".join(query_conditions) if query_conditions else ""
    cursor.execute(f"""
        SELECT 
            d.id_deal, 
            d.name AS deal_name, 
            vs.name AS stage_name, 
            d.client, 
            d.opportunity, 
            d.currency_id, 
            d.payment_method, 
            s.name || ' ' || s.last_name AS full_name, 
            d.date_create, 
            d.date_delivery, 
            d.date_payment, 
            d.city, 
            v.name AS voronka_name 
        FROM 
            deal d 
        LEFT JOIN 
            voronka_stage vs ON d.stage_id = vs.stage_id 
        LEFT JOIN 
            staff s ON d.responsible_id = s.staff_id 
        LEFT JOIN 
            voronka v ON d.voronka_id = v.voronka_id 
        {where_clause}
    """, params)

    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return data

@app.route('/api/deals', methods=['POST'])
def get_deals():
    filters = request.json
    data = fetch_deals_from_db(filters)
    return jsonify(data)

@app.route('/api/deal_products/<int:id_deal>', methods=['GET'])
def get_deal_products(id_deal):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deal_product WHERE id_deal = ?", (id_deal,))
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()

    store_name_list = [{1: 'ÐÑÐ¾Ð¸Ð·Ð²Ð¾Ð´ÑÑÐ²Ð¾'}, {2: 'ÐÑÑÐ°Ð½Ð°'}, {4: 'ÐÐ»Ð¼Ð°ÑÑ'}, {6: 'Ð¨ÑÐ¼ÐºÐµÐ½Ñ'}, {8: 'ÐÐ°ÑÐ°Ð³Ð°Ð½Ð´Ð°'}]
    for item in data:
        store_id = item['store_id']
        store_name = ''
        for item2 in store_name_list:
            if store_id in item2:
                store_name = item2[store_id]
                break
        item['store_id'] = store_name

    return jsonify(data)

@app.route('/api/deal_by_product/<int:product_id>', methods=['GET'])
def get_deal_by_product(product_id):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            d.id_deal, 
            d.name AS deal_name, 
            vs.name AS stage_name, 
            d.client, 
            d.opportunity, 
            d.currency_id, 
            d.payment_method, 
            s.name || ' ' || s.last_name AS full_name, 
            d.date_create, 
            d.date_delivery, 
            d.date_payment, 
            d.city, 
            v.name AS voronka_name 
        FROM 
            deal d 
        LEFT JOIN 
            voronka_stage vs ON d.stage_id = vs.stage_id 
        LEFT JOIN 
            staff s ON d.responsible_id = s.staff_id 
        LEFT JOIN 
            voronka v ON d.voronka_id = v.voronka_id 
        JOIN 
            deal_product dp ON d.id_deal = dp.id_deal 
        WHERE 
            dp.product_id = ?
    """, (product_id,))
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
