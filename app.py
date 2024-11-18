from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import hashlib
import json

app = Flask(__name__)

# Настройки базы данных
db_config = {
    'host': 'localhost',  # Укажите ваш хост
    'user': 'root',       # Укажите ваш юзер
    'password': 'password',  # Укажите ваш пароль
    'database': 'donate_db'  # Название вашей базы данных
}

# Подключение к базе данных
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Главная страница (форма для доната)
@app.route('/')
def home():
    return render_template('index.html')

# Обработчик формы (обработка доната)
@app.route('/donate', methods=['POST'])
def donate():
    username = request.form['username']
    amount = request.form['amount']
    
    # Проверяем, что сумма введена корректно
    try:
        amount = int(amount)
    except ValueError:
        return 'Invalid amount', 400

    # Подключаемся к базе данных
    conn = get_db_connection()
    cursor = conn.cursor()

    # Обновляем баланс игрока
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        # Если пользователь найден, обновляем баланс
        new_balance = user[2] + amount
        cursor.execute("UPDATE users SET money = %s WHERE username = %s", (new_balance, username))
    else:
        # Если пользователя нет, добавляем его в таблицу
        cursor.execute("INSERT INTO users (username, money) VALUES (%s, %s)", (username, amount))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('home'))

# Обработчик для вебхуков (например, от Enot.io или других платёжных систем)
@app.route('/webhook', methods=['POST'])
def webhook():
    # Получаем данные из вебхука
    data = request.get_json()

    # Проверка данных вебхука (например, проверка сигнатуры)
    signature = request.headers.get('X-Signature')
    if signature != "your_signature_check":  # Здесь проверка сигнатуры для безопасности
        return "Invalid signature", 400

    # Обработка данных из вебхука (например, обновление баланса)
    username = data['username']
    amount = data['amount']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Обновляем баланс игрока
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        new_balance = user[2] + amount
        cursor.execute("UPDATE users SET money = %s WHERE username = %s", (new_balance, username))
    else:
        cursor.execute("INSERT INTO users (username, money) VALUES (%s, %s)", (username, amount))

    conn.commit()
    cursor.close()
    conn.close()

    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
