from flask import Flask, render_template, request
import sqlite3, time, requests, json

db=sqlite3.connect("db.db", check_same_thread=False)
sql=db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS servers (
    server_name TEXT,
    server_ip TEXT,
    server_description TEXT,
    create_date BIGINT    
)""")
db.commit()

app=Flask(__name__)

@app.route('/')
def index():
    sql.execute("SELECT server_name, server_ip, server_description FROM servers")
    servers = sql.fetchall()
    return render_template("index.html", servers=servers)

@app.route('/add', methods=["GET"])
def add():
    return render_template("add.html")

@app.route('/new', methods=["GET"])
def new():
    sql.execute("SELECT server_name, server_ip, server_description FROM servers ORDER BY create_date DESC LIMIT 6")
    servers = sql.fetchall()
    return render_template("new.html", servers=servers)

@app.route('/add', methods=["POST"])
def add_post():
    
    serverip = request.form.get("ip")
    servername = request.form.get("nm")
    serverdesc = request.form.get("ds")

    # проверка
    if len(servername) >= 17:
        return render_template("add.html", title="ОШИБКА", message="В названии максимум 16 символов")
    elif len(servername) >= 33:
        return render_template("add.html", title="ОШИБКА", message="В кратком описании максимум 32 символова")
    r=requests.get(f"https://api.mcstatus.io/v2/status/java/{serverip}")
    j=json.loads(r.text)

    if j["online"] == False:
        return render_template("add.html", title="ОШИБКА", message="Сервер оффлайн, поддержка: Poteto#5393")


    sql.execute(f"SELECT * FROM servers WHERE server_ip = '{serverip}'")
    if sql.fetchone():
        return render_template("add.html", title="ОШИБКА", message="Сервер уже был выложен")
    else:
        sql.execute("INSERT INTO servers VALUES (?, ?, ?, ?)", (servername, serverip, serverdesc, time.time()))
        db.commit()
        return render_template("add.html", title="Успешно", message="Сервер успешно выложен")
        return    
if __name__ == "__main__":
    app.run(port=80)