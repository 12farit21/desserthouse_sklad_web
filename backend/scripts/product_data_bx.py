import requests
import sqlite3

print('run product_data_bx')

# Ваш вебхук URL
webhook_url = "https://desserthouse.bitrix24.kz/rest/292/mnhi213vu9ykx3s1/"

DATABASE_PATH = './DB/my_database.db'

def get_all_products(iblock_id):
    # Initialize an empty list to hold all products
    all_products = []
    start = 0

    while True:
        # Set up parameters with pagination start position
        params = {
            'select': ['id', 'iblockId', 'iblockSectionId', 'name', 'quantity', 'timestampX'],
            'filter': {'iblockId': iblock_id},
            'start': start
        }

        # Make the API request
        response = requests.post(webhook_url + 'catalog.product.list', json=params)
        
        # Check for a successful response
        if response.status_code == 200:
            data = response.json()
            
            # If there are products in the result, add them to the list
            if 'result' in data and 'products' in data['result']:
                products = data['result']['products']
                all_products.extend(products)

                # If fewer than 50 products returned, no more pages left
                if len(products) < 50:
                    break

                # Otherwise, move to the next set of results
                start += len(products)
            else:
                # If no products found, break out of the loop
                break
        else:
            # Handle request failure
            print(f"Failed to fetch data: {response.status_code}")
            break

    return all_products



def get_product_data(productId): #Узнать сколько товара в каком складе
    # Параметры для запроса к API Bitrix24
    params = {
#        'select': ['id'],
        'filter': {'productId': productId}
    }
    
    # Отправляем POST-запрос на API Bitrix24 для получения данных о товарах
    response = requests.post(webhook_url + 'catalog.storeproduct.list', json=params)
    
    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data['result']
    else:
        return f"Failed to fetch data: {response.status_code}"


def save_to_database(data):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER NOT NULL UNIQUE,
            iblockId INTEGER,
            iblockSectionId INTEGER,
            name TEXT,
            quantity REAL,
            quantity_proizvodstvo_1 REAL,
            quantity_astana_2 REAL,
            quantity_almaty_4 REAL,
            quantity_shymkent_6 REAL,
            quantity_karaganda_8 REAL,
            timestampX TEXT,
            PRIMARY KEY(id)
        )
    ''')

    for item in data:
        cursor.execute('''
            INSERT INTO items (id, iblockId, iblockSectionId, name, quantity, timestampX)
            VALUES (:id, :iblockId, :iblockSectionId, :name, :quantity, :timestampX)
            ON CONFLICT(id) DO UPDATE SET
                iblockId=excluded.iblockId,
                iblockSectionId=excluded.iblockSectionId,
                name=excluded.name,
                quantity=excluded.quantity,
                timestampX=excluded.timestampX
        ''', {
            'id': item['id'],
            'iblockId': item['iblockId'],
            'iblockSectionId': item['iblockSectionId'],
            'name': item['name'],
            'quantity': item['quantity'],
            'timestampX': item['timestampX']
        })


    connection.commit()
    connection.close()

def save_quantity_in_warehouse(data):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    if data['storeId'] == 1:
        warehouse_name = 'quantity_proizvodstvo_1'
    elif data['storeId'] == 2:
        warehouse_name = 'quantity_astana_2'
    elif data['storeId'] == 4:
        warehouse_name = 'quantity_almaty_4'
    elif data['storeId'] == 6:
        warehouse_name = 'quantity_shymkent_6'
    elif data['storeId'] == 8:
        warehouse_name = 'quantity_karaganda_8'
    
    if data['amount'] != None:
        cursor.execute(f'UPDATE items SET {warehouse_name} = {data['amount']} WHERE id = {data['productId']}')

    # Сохраняем изменения в базе данных
    connection.commit()
    connection.close()              


catalog_id = 14
all_products = get_all_products(catalog_id)
all_products.extend(get_all_products(16))


all_productID=[] #Айди товаров где quantity not None
sum=0
for i in all_products:
    if i['quantity'] != None:
        all_productID.append(i['id'])
        sum+=i['quantity']

save_to_database(all_products)

for i in all_productID:
    storeProduct = get_product_data(i)
    storeProduct = storeProduct ['storeProducts']
    for j in storeProduct:
        save_quantity_in_warehouse(j)
print('finished product_data_bx')