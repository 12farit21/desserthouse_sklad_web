import requests
import sqlite3


# Ваш вебхук URL
webhook_url = "https://desserthouse.bitrix24.kz/rest/292/mnhi213vu9ykx3s1/"

print("run voronka_and_stage.py")


DATABASE_PATH = './DB/my_database.db'

def get_dealcategory_list(): 

    response = requests.post(webhook_url + 'crm.dealcategory.list')

    if response.status_code == 200:
        data = response.json()
        return data['result']
    else:
        return f"Failed to fetch data: {response.status_code}"

def save_voronka_data(data):
    # Подключаемся к базе данных (если базы данных нет, то она будет создана)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    voronka_id = data['ID']
    name = data['NAME']
    
    # Проверяем, существует ли запись с данным voronka_id
    cursor.execute("SELECT COUNT(*) FROM voronka WHERE voronka_id = ?", (voronka_id,))
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Если записи нет, вставляем новую
        cursor.execute("INSERT INTO voronka (voronka_id, name) VALUES (?, ?)", (voronka_id, name))
    else:
        # Если запись существует, обновляем ее
        cursor.execute("UPDATE voronka SET name = ? WHERE voronka_id = ?", (name, voronka_id))
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def get_dealcategory_stage(dealcategory_id): 

    params = {
        'id': dealcategory_id
    }
    
    response = requests.post(webhook_url + 'crm.dealcategory.stage.list', json=params)
    
    if response.status_code == 200:
        data = response.json()
        return data['result']
    else:
        return f"Failed to fetch data: {response.status_code}"

def save_voronka_stage_data(voronka_id,data):
    # Подключаемся к базе данных (если базы данных нет, то она будет создана)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    for stage in data:
            stage_id = stage['STATUS_ID']
            name = stage['NAME']
            
            cursor.execute("SELECT COUNT(*) FROM voronka_stage WHERE stage_id = ?", (stage_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute("INSERT INTO voronka_stage (stage_id, voronka_id, name) VALUES (?, ?, ?)", (stage_id, voronka_id, name))
            else:
                cursor.execute("UPDATE voronka_stage SET name = ?, voronka_id = ? WHERE stage_id = ?", (name, voronka_id, stage_id))

        
    conn.commit()
    conn.close()


dealcategory_list = get_dealcategory_list()

for item in dealcategory_list:
    save_voronka_data(item)
    dealcategory_stage=get_dealcategory_stage(item['ID'])
    save_voronka_stage_data(item['ID'],dealcategory_stage)
print("finished voronka_and_stage.py")