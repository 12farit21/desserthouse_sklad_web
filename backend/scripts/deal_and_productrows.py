#Заполнение таблиц deal и deal_product
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
import aiohttp
import asyncio
import aiosqlite

print("run deal_and_productrows.py")

webhook_url = "https://desserthouse.bitrix24.kz/rest/292/mnhi213vu9ykx3s1/"

DATABASE_PATH = './DB/my_database.db'

def get_deal_list(start=0, limit=50):
    all_deals = []
    params = {
        "filter": {"=CATEGORY_ID": ["22", "34", "48", "50", "76"]},
        "start": start,
        "limit": limit
    }

    while True:
        # Отправляем POST-запрос на API Bitrix24 для получения данных о сделках
        response = requests.post(webhook_url + 'crm.deal.list', json=params)
        
        # Проверяем статус ответа
        if response.status_code == 200:
            data = response.json()
            result = data.get('result', [])
            all_deals.extend(result)
            
            # Проверяем, есть ли еще данные для получения
            if 'next' in data and data['next'] is not None:
                params['start'] = data['next']
            else:
                break
        else:
            return f"Failed to fetch data: {response.status_code}"
    
    return all_deals


all_deals_list = get_deal_list()


all_deals_id = None
async def filter_dictionary(dictionary):
    """Функция для фильтрации одного словаря."""
    if 'ID' in dictionary:
        return dictionary['ID']
    return None

async def filter_dictionaries(all_deals_list):
    """Асинхронная функция для фильтрации списка словарей."""
    tasks = []
    for dictionary in all_deals_list:
        tasks.append(filter_dictionary(dictionary))
    
    filtered = await asyncio.gather(*tasks)
    # Убираем None значения
    return [item for item in filtered if item is not None]

# Основная программа
async def main_id_of_deals():
    all_deals_id = await filter_dictionaries(all_deals_list)
    return all_deals_id


all_deals_id =(asyncio.run(main_id_of_deals()))

'''
def get_client_by_id(client_id):
    params = {
        'ID': client_id
    }

    response = requests.post(webhook_url + 'crm.contact.get', json=params)
    
    if response.status_code == 200:
        data = response.json()
        keys_to_extract = [
            'NAME', 'SECOND_NAME', 'LAST_NAME'
        ]

        extracted_data = {key: data['result'].get(key) for key in keys_to_extract}
        client_data = ''
        for value in list(extracted_data.values()):
            if value is not None:
                client_data += " " + value
        return client_data.strip()
    else:
        return f"Failed to fetch data: {response.status_code}"

def get_deal_userfield_by_id(userfield_id, value_id):
    params = {
        'ID': userfield_id
    }

    response = requests.post(webhook_url + 'crm.deal.userfield.get', json=params)
    
    if response.status_code == 200:
        data = response.json()
        for item in data['result']['LIST']:
            if item['ID'] == value_id:
                return item['VALUE']
    else:
        return f"Failed to fetch data: {response.status_code}"'''

def get_deal_by_id(deal_id):
    params = {
        'ID': deal_id
    }

    response = requests.post(webhook_url + 'crm.deal.get', json=params)
    
    if response.status_code == 200:
        data = response.json()
        result = data['result']
        # без  keys_to_extract  [Finished in 267.2s]
        return result
    else:
        return response.status_code

def fetch_deals(deal_ids):
    all_deals = []
    error_ids = []

    def process_ids(ids):
        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {executor.submit(get_deal_by_id, deal_id): deal_id for deal_id in ids}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result == 503:
                        error_ids.append(futures[future])
                    elif isinstance(result, dict):
                        all_deals.append(result)
                    else:
                        print(f"Failed to fetch data for ID {futures[future]}: {result}")
                except Exception as e:
                    print(f"Failed to fetch data for ID {futures[future]}: {e}")
                time.sleep(1 / 14)  # Ограничение 7 запросов в секунду (0.14 секунды между запросами)

    process_ids(deal_ids)

    while error_ids:
        ids_to_retry = error_ids.copy()
        error_ids.clear()
        process_ids(ids_to_retry)
    
    return all_deals

all_deals = fetch_deals(all_deals_id)


def save_deal_data(data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Подготовка данных для вставки или обновления
    deal_data = []
    for item in data:
        deal_data.append((
            item['ID'],
            item['TITLE'],
            item['STAGE_ID'],
            item['CONTACT_ID'],  # client
            item['OPPORTUNITY'],
            item['CURRENCY_ID'],
            item['UF_CRM_1678870507288'],  # payment_method
            item['CREATED_BY_ID'],  # responsible_id
            item['DATE_CREATE'],
            item['UF_CRM_1684221847740'],  # date_delivery
            item['UF_CRM_1702647950651'],  # date_payment
            item['UF_CRM_1704702729411'],  # city
            item['CATEGORY_ID']  # voronka_id
        ))

    cursor.executemany('''
        INSERT OR REPLACE INTO deal (
            id_deal, name, stage_id, client, opportunity, currency_id,
            payment_method, responsible_id, date_create, date_delivery,
            date_payment, city, voronka_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', deal_data)
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


save_deal_data(all_deals)




def change_client_to_fio():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    query = "SELECT client FROM deal WHERE client not null "

    cursor.execute(query)
    results = cursor.fetchall()

    id_list = [row[0] for row in results]

    id_list = list(set(id_list))

    all_contacts = get_client_list(id_list)
    
    for item in all_contacts:
        fio = ""
        if item['NAME'] != None: fio+=item['NAME']
        if item['SECOND_NAME'] != None: fio+=' ' + item['SECOND_NAME']
        if item['LAST_NAME'] != None: fio+=' ' + item['LAST_NAME']
        cursor.execute('''UPDATE deal SET client = ? WHERE client = ?''', (fio,int(item['ID'])))
        connection.commit()

    cursor.close()
    connection.close()



def get_client_list(client_list, start=0, limit=50):
    
    all_deals = []
    params = {
        "filter": {"=ID": client_list},
        "select" : [ "ID", "NAME", "SECOND_NAME", "LAST_NAME"],
        "start": start,
        "limit": limit
    }

    while True:
        # Отправляем POST-запрос на API Bitrix24 для получения данных о сделках
        response = requests.post(webhook_url + 'crm.contact.list', json=params)
        
        # Проверяем статус ответа
        if response.status_code == 200:
            data = response.json()
            result = data.get('result', [])
            all_deals.extend(result)
            
            # Проверяем, есть ли еще данные для получения
            if 'next' in data and data['next'] is not None:
                params['start'] = data['next']
            else:
                break
        else:
            return f"Failed to fetch data: {response.status_code}"
    
    return all_deals


def change_userfield(column_name):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    query = f"SELECT {column_name} FROM deal WHERE {column_name} not null "

    cursor.execute(query)
    results = cursor.fetchall()

    field_list = [row[0] for row in results]

    field_list = list(set(field_list))

    for item in field_list:

        if column_name == 'payment_method':
            new_data = get_deal_userfield_by_id(214,item) #payment method
        elif column_name == 'city':
            new_data = get_deal_userfield_by_id(498, item) #field city
        try:
            cursor.execute(f'''UPDATE deal SET {column_name} = ? WHERE {column_name} = ?''', (new_data,int(item)))
        except:
            None

        connection.commit()

    cursor.close()
    connection.close()



def get_deal_userfield_by_id(userfield_id, value_id):
    params = {
        'ID': userfield_id
    }

    response = requests.post(webhook_url + 'crm.deal.userfield.get', json=params)
    
    if response.status_code == 200:
        data = response.json()
        for item in data['result']['LIST']:
            if item['ID'] == value_id:
                return item['VALUE']
    else:
        return f"Failed to fetch data: {response.status_code}"


change_client_to_fio()

change_userfield('payment_method')
change_userfield('city')



def get_product_of_deal(deal_id):
    params = {'ID': deal_id}
    response = requests.post(webhook_url + 'crm.deal.productrows.get', json=params)
    
    if response.status_code == 200:
        data = response.json()
        return data['result']
    else:
        return response.status_code

def fetch_productrows(deal_ids):
    all_products = []
    error_ids = []

    def process_ids(ids):
        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {executor.submit(get_product_of_deal, deal_id): deal_id for deal_id in ids}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result == 503:
                        error_ids.append(futures[future])
                    elif isinstance(result, list):
                        all_products.extend(result)
                    else:
                        print(f"Failed to fetch data for ID {futures[future]}: {result}")
                except Exception as e:
                    print(f"Failed to fetch data for ID {futures[future]}: {e}")
                time.sleep(1 / 7)  # Ограничение 7 запросов в секунду (0.14 секунды между запросами)

    process_ids(deal_ids)

    while error_ids:
        ids_to_retry = error_ids.copy()
        error_ids.clear()
        process_ids(ids_to_retry)
    
    return all_products

all_productrows_ofall_deals = fetch_productrows(all_deals_id)



def save_productrows_of_deal(all_productrows_ofall_deals):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Подготовка данных для вставки или обновления
    product_data = []
    for item in all_productrows_ofall_deals:
        product_data.append((
            item['ID'],
            item['OWNER_ID'],
            item['PRODUCT_ID'],
            item['PRODUCT_NAME'],
            item['PRICE'],
            item['QUANTITY'],
            item['MEASURE_NAME'],
            item['STORE_ID']
        ))

    cursor.executemany('''
        INSERT OR REPLACE INTO deal_product (
            id, id_deal, product_id, product_name, price, quantity,
            measure, store_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', product_data)
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

save_productrows_of_deal(all_productrows_ofall_deals)

def change_storeID_null(): # Почему то апи битрикса вместо айди склада производства иногда выдает null
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute('''UPDATE deal_product SET store_id = 1 WHERE store_id IS NULL''')
    connection.commit()

    cursor.close()
    connection.close()

change_storeID_null()

print("finished deal_and_productrows.py")

#~[Finished in 325.1s]