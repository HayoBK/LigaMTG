from flask import Flask, request, redirect
import sqlite3
import os
from werkzeug.utils import secure_filename

# Crear app Flask
app = Flask(__name__)

# Configurar carpeta de subida de imágenes
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limitar tamaño: 2MB máximo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Función para conectar con la base de datos
def get_db_connection():
    conn = sqlite3.connect('liga_mtg.db')
    conn.row_factory = sqlite3.Row
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
            .boton { display: block; margin: 20px; padding: 10px; background: #4CAF50; color: white; text-decoration: none; width: 250px; margin-left: auto; margin-right: auto; border-radius: 5px; }
            img { max-width: 400px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Bienvenido a Liga MTG 2025 - LAS TRES PIERNAS</h1>
        <img src="https://static.wixstatic.com/media/73522c_eef87b5cad5c4f8ca41de702a9b268f8~mv2.jpg" alt="Portada">
        <br>
        <a class="boton" href="/registrar-mazo">Registrar nuevo mazo</a>
        <a class="boton" href="/ranking">Ver Ranking </a>
        <a class="boton" href="/mazos">Ver y editar mazos registrados</a>
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
        <form action="/registrar" method="post" enctype="multipart/form-data">
            <input type="text" name="jugador" placeholder="Nombre del Jugador" required><br><br>
            <input type="text" name="mazo" placeholder="Nombre del Mazo" required><br><br>
            <input type="text" name="o_id" placeholder="Código Identificación del Mazo" required><br><br>
            <textarea name="cartas" placeholder="Listado de cartas (una por línea)" rows="10" cols="30"></textarea><br><br>
            Subir Imagen del Mazo: <input type="file" name="imagen"><br><br>
            <input type="submit" value="Registrar Mazo">
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
    open_id = request.form.get('o_id')
    cartas_lista = request.form.get('cartas')
    file = request.files['imagen']

    imagen_url = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(imagen_path)
        imagen_url = '/' + imagen_path  # Guardamos ruta relativa

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO mazos (Open_id, jugador, nombre_mazo, cartas_lista, imagen_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (open_id, jugador, nombre_mazo, cartas_lista, imagen_url))
    conn.commit()
    conn.close()

    return '''
    <html>
    <head><title>Registrado</title></head>
    <body style="text-align:center; padding:50px;">
        <h2>¡Mazo registrado exitosamente!</h2>
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
        listado += f"<li><strong>{mazo['jugador']}</strong> - {mazo['nombre_mazo']} (ELO: {mazo['elo']})"
        if mazo['imagen_url']:
            listado += f"<br><img src='{mazo['imagen_url']}' style='max-width:150px;'>"
        listado += f"<br><a href='/editar-mazo/{mazo['id']}'>Editar este mazo</a>"
        listado += "</li><br>"
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

@app.route('/editar-mazo/<int:mazo_id>', methods=['GET'])
def editar_mazo_form(mazo_id):
    conn = get_db_connection()
    mazo = conn.execute('SELECT * FROM mazos WHERE id = ?', (mazo_id,)).fetchone()
    conn.close()

    if mazo is None:
        return "<h1>Mazo no encontrado</h1><a href='/'>Volver</a>"

    return f'''
    <html>
    <head><title>Editar Mazo</title></head>
    <body style="text-align:center; padding:50px;">
        <h1>Editando Mazo: {mazo['nombre_mazo']}</h1>
        <form action="/editar-mazo/{mazo_id}" method="post" enctype="multipart/form-data">
            <input type="text" name="jugador" value="{mazo['jugador']}" required><br><br>
            <input type="text" name="mazo" value="{mazo['nombre_mazo']}" required><br><br>
            <textarea name="cartas" rows="10" cols="30">{mazo['cartas_lista']}</textarea><br><br>
            Imagen Actual:<br>
            {'<img src="' + mazo['imagen_url'] + '" style="max-width:150px;">' if mazo['imagen_url'] else 'Sin imagen'}<br><br>
            Subir nueva imagen (opcional):<br>
            <input type="file" name="imagen"><br><br>
            <input type="number" name="cartas_cambiadas" placeholder="¿Cuántas cartas cambiaste?" min="0" required><br><br>
            <input type="submit" value="Guardar Cambios">
        </form>
        <br>
        <a href="/mazos">Cancelar</a>
    </body>
    </html>
    '''


@app.route('/editar-mazo/<int:mazo_id>', methods=['POST'])
def editar_mazo_guardar(mazo_id):
    jugador = request.form.get('jugador')
    nombre_mazo = request.form.get('mazo')
    cartas_lista = request.form.get('cartas')
    cartas_cambiadas = int(request.form.get('cartas_cambiadas'))
    file = request.files['imagen']

    # Castigo de ELO: 2% por carta cambiada
    castigo = 1 - (0.02 * cartas_cambiadas)

    conn = get_db_connection()
    mazo = conn.execute('SELECT * FROM mazos WHERE id = ?', (mazo_id,)).fetchone()

    if mazo is None:
        conn.close()
        return "<h1>Mazo no encontrado</h1><a href='/'>Volver</a>"

    nuevo_elo = float(mazo['elo']) * castigo

    imagen_url = mazo['imagen_url']  # por defecto, mantener imagen anterior

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(imagen_path)
        imagen_url = '/' + imagen_path  # actualizar imagen_url

    conn.execute('''
        UPDATE mazos
        SET jugador = ?, nombre_mazo = ?, cartas_lista = ?, imagen_url = ?, elo = ?
        WHERE id = ?
    ''', (jugador, nombre_mazo, cartas_lista, imagen_url, nuevo_elo, mazo_id))

    conn.commit()
    conn.close()

    return redirect('/mazos')

@app.route('/ranking', methods=['GET'])
def ver_ranking():
    conn = get_db_connection()
    mazos = conn.execute('SELECT * FROM mazos ORDER BY elo DESC').fetchall()
    conn.close()

    tabla = '''
    <html>
    <head>
        <title>Ranking de Mazos</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background-color: #f5f5f5; }
            table { margin: auto; border-collapse: collapse; width: 80%; }
            th, td { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #4CAF50; color: white; }
            img { max-width: 100px; }
            tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Ranking de Mazos</h1>
        <table>
            <tr>
                <th>Imagen</th>
                <th>Nombre del Mazo</th>
                <th>Jugador</th>
                <th>ELO</th>
            </tr>
    '''

    for mazo in mazos:
        imagen_html = f"<img src='{mazo['imagen_url']}' alt='Sin imagen'>" if mazo['imagen_url'] else "Sin imagen"
        tabla += f'''
            <tr>
                <td>{imagen_html}</td>
                <td>{mazo['nombre_mazo']}</td>
                <td>{mazo['jugador']}</td>
                <td>{round(mazo['elo'], 2)}</td>
            </tr>
        '''

    tabla += '''
        </table>
        <br>
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''

    return tabla


# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
