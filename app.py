from flask import Flask, request
import sqlite3

# Crear app Flask
app = Flask(__name__)

# Función para conectar con la base de datos
def get_db_connection():
    conn = sqlite3.connect('liga_mtg.db')
    conn.row_factory = sqlite3.Row  # Esto permite leer los datos como si fueran diccionarios
    return conn

# Página principal: MENÚ
@app.route('/', methods=['GET'])
def home():
    return '''
    <html>
    <head>
        <title>MTG Torneo - Menú Principal</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background-color: #eef; }
            .boton { display: block; margin: 20px; padding: 10px; background: #4CAF50; color: white; text-decoration: none; width: 200px; margin-left: auto; margin-right: auto; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Bienvenido al Torneo MTG 2025</h1>
        <a class="boton" href="/registrar-mazo">Registrar nuevo mazo</a>
        <a class="boton" href="/mazos">Ver mazos registrados</a>
    </body>
    </html>
    '''

# Página para mostrar formulario de registrar mazo
@app.route('/registrar-mazo', methods=['GET'])
def registrar_mazo_form():
    return '''
    <html>
    <head><title>Registrar Mazo</title></head>
    <body style="text-align:center; padding:50px;">
        <h1>Registrar Mazo Nuevo</h1>
        <form action="/registrar" method="post">
            <input type="text" name="jugador" placeholder="Nombre del Jugador"><br><br>
            <input type="text" name="mazo" placeholder="Nombre del Mazo"><br><br>
            <input type="text" name="o_id" placeholder="Código Identifacion del Mazo"><br><br>
            <input type="submit" value="Registrar">
        </form>
        <br>
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''

# Procesar el registro del mazo y guardarlo en la base de datos
@app.route('/registrar', methods=['POST'])
def registrar():
    jugador = request.form.get('jugador')
    nombre_mazo = request.form.get('mazo')
    id = request.form.get('o_id')
    conn = get_db_connection()
    conn.execute('INSERT INTO mazos (jugador, nombre_mazo, Open_id) VALUES (?, ?, ?)', (jugador, nombre_mazo, id))
    conn.commit()
    conn.close()

    return f'''
    <html>
    <head><title>Registrado</title></head>
    <body style="text-align:center; padding:50px;">
        <h2>¡Mazo registrado en la base de datos!</h2>
        <p><strong>Jugador:</strong> {jugador}<br><strong>Mazo:</strong> {nombre_mazo}</p>
        <a href="/">Volver al Menú Principal</a><br>
        <a href="/mazos">Ver Mazos Registrados</a>
    </body>
    </html>
    '''

# Ver todos los mazos registrados desde la base de datos
@app.route('/mazos', methods=['GET'])
def ver_mazos():
    conn = get_db_connection()
    mazos = conn.execute('SELECT * FROM mazos').fetchall()
    conn.close()

    listado = "<ul>"
    for mazo in mazos:
        listado += f"<li><strong>{mazo['jugador']}</strong> - {mazo['nombre_mazo']} (ELO: {mazo['elo']})</li>"
    listado += "</ul>"

    return f'''
    <html>
    <head><title>Mazos Registrados</title></head>
    <body style="text-align:center; padding:50px;">
        <h1>Mazos Registrados</h1>
        {listado}
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
