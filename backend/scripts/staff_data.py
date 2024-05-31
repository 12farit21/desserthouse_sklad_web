import requests
import sqlite3


# Ваш вебхук URL
webhook_url = "https://desserthouse.bitrix24.kz/rest/292/mnhi213vu9ykx3s1/"

print('run staff_data.py')

DATABASE_PATH = './DB/my_database.db'

def get_staff_list():
    start = 0
    limit = 50
    all_deal_categories = []

    while True:
        params = {
            'start': start,
            'limit': limit
        }
        response = requests.post(webhook_url + 'user.get', json=params)
        
        if response.status_code == 200:
            data = response.json()
            print(data)
            deal_categories = data['result']
            if not deal_categories:
                break
            all_deal_categories.extend(deal_categories)
            start += limit
        else:
            return f"Failed to fetch data: {response.status_code}"

    return all_deal_categories


def save_staff_data(data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    staff_id = data['ID']
    name = data['NAME']
    last_name = data ['LAST_NAME']

    cursor.execute("SELECT COUNT(*) FROM staff WHERE staff_id = ?", (staff_id,))
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Если записи нет, вставляем новую
        cursor.execute("INSERT INTO staff (staff_id, name, last_name) VALUES (?, ?, ?)", (staff_id, name, last_name))

    else:
        # Если запись существует, обновляем ее
        cursor.execute("UPDATE staff SET name = ?, last_name = ? WHERE staff_id = ?", (name, last_name,staff_id))
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


staffs = get_staff_list()
for staff in staffs:
    save_staff_data(staff)
print('finished staff_data.py')