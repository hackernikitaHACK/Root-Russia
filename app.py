from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import json

app = Flask(__name__)

# Настройки базы данных
db_config = {
    'host': '51.91.215.125',  # Хост базы данных
    'user': 'gs280226',       # Логин к базе данных
    'password': 'b7RApcoKgboJ',  # Пароль к базе данных
    'database': 'gs280226'    # Название базы данных
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
    name = request.form['username']  # Никнейм игрока
    amount = request.form['amount']  # Сумма доната
    
    # Проверяем, что сумма введена корректно
    try:
        amount = int(amount)
    except ValueError:
        return 'Invalid amount', 400

    # Подключаемся к базе данных
    conn = get_db_connection()
    cursor = conn.cursor()

    # Обновляем баланс игрока
    cursor.execute("SELECT * FROM accounts WHERE name = %s", (name,))
    user = cursor.fetchone()

    if user:
        # Если пользователь найден, обновляем баланс
        new_balance = user[2] + amount  # Проверяем, что правильный индекс для колонки 'money'
        cursor.execute("UPDATE accounts SET money = %s WHERE name = %s", (new_balance, name))  # Обновляем баланс
    else:
        # Если пользователя нет, добавляем его в таблицу
        cursor.execute("INSERT INTO accounts (name, money) VALUES (%s, %s)", (name, amount))  # Вставляем новые данные

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
    name = data['username']  # Имя пользователя
    amount = data['amount']  # Сумма доната

    conn = get_db_connection()
    cursor = conn.cursor()

    # Обновляем баланс игрока
    cursor.execute("SELECT * FROM accounts WHERE name = %s", (name,))
    user = cursor.fetchone()

    if user:
        new_balance = user[2] + amount
        cursor.execute("UPDATE accounts SET money = %s WHERE name = %s", (new_balance, name))  # Обновление баланса
    else:
        cursor.execute("INSERT INTO accounts (name, money) VALUES (%s, %s)", (name, amount))  # Вставка нового пользователя

    conn.commit()
    cursor.close()
    conn.close()

    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
