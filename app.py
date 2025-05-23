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
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directorio donde está app.py
    db_path = os.path.join(BASE_DIR, "liga_mtg.db")        # Ruta absoluta
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def html_head(title="MTG Torneo"):
    return f'''
    <head>
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
                background-color: #eef;
                margin: 0;
            }}

            h1, h2, h3 {{
                margin-bottom: 20px;
            }}

            table {{
                margin: auto;
                border-collapse: collapse;
                width: 95%;
                max-width: 800px;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                font-size: 16px;
            }}

            th {{
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
            }}

            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}

            img {{
                max-width: 100%;
                height: auto;
                margin: 10px 0;
            }}

            form {{
                margin: 20px 0;
            }}

            input[type="text"],
            input[type="number"],
            input[type="file"],
            textarea,
            select {{
                font-size: 18px;
                padding: 10px;
                width: 90%;
                max-width: 400px;
                margin-bottom: 15px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }}

            textarea {{
                resize: vertical;
            }}

            input[type="submit"],
            .boton {{
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                cursor: pointer;
                margin: 10px 0;
                display: inline-block;
                text-decoration: none;
            }}

            input[type="submit"]:hover,
            .boton:hover {{
                background-color: #45a049;
            }}

            @media (max-width: 600px) {{
                table, th, td {{
                    font-size: 14px;
                    padding: 8px;
                }}

                input[type="text"],
                input[type="number"],
                input[type="file"],
                textarea,
                select {{
                    font-size: 16px;
                }}

                input[type="submit"],
                .boton {{
                    font-size: 16px;
                    padding: 10px 20px;
                }}
            }}
            img.ranking-img {{
                max-width: 80px;
                height: auto;
                border-radius: 8px;
                }}
        </style>
    </head>
    '''




# Página principal: MENÚ
@app.route('/', methods=['GET'])
def home():
    return f'''
    <html>
    {html_head("LIGA MTG - HBK")}

    <body>
        <h1>Bienvenido a Liga MTG 2025 - LAS TRES PIERNAS</h1>
        <img src="https://static.wixstatic.com/media/73522c_eef87b5cad5c4f8ca41de702a9b268f8~mv2.jpg" alt="Portada">
        <br>
        <a class="boton" href="/registrar-mazo">Registrar nuevo mazo</a>
        <a class="boton" href="/ranking">Ver Ranking Mazos</a>
        <a class="boton" href="/ranking-filtrado">Ver Ranking Mazos con Filtro </a>
        <a class="boton" href="/registrar-partida-multiple">Registrar Nueva Partida</a>
        <a class="boton" href="/torneos">Ver Torneos</a>
        <a class="boton" href="/mazos">Ver y editar mazos registrados</a>
        <a class="boton" href="/historial-partidas">Historial de Partidas</a>
        <a class="boton" href="/ranking-global">Ver Ranking Jugadores </a>
        <a class="boton" href="/ranking-global-filtrado">Ver Ranking Jugadores con Filtro </a>


    </body>
    </html>
    '''

# Página para mostrar formulario de registrar mazo
@app.route('/registrar-mazo', methods=['GET'])
def registrar_mazo_form():
    return f'''
    <html>
    {html_head("LIGA-Registrar Mazo")}
    <body style="text-align:center; padding:50px;">
        <h1>Registrar Mazo Nuevo</h1>
        <form action="/registrar" method="post" enctype="multipart/form-data">
            <input type="text" name="jugador" placeholder="Nombre del Jugador" required><br><br>
            <input type="text" name="mazo" placeholder="Nombre del Mazo" required><br><br>
            <textarea name="o_id" placeholder="KeyWord (tipo de Mazo)" rows="3" cols="30"></textarea><br><br>
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

    return f'''
    <html>
    {html_head("Registrado")}
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
    {html_head("Mazos registrados")}
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
    {html_head("Editar Mazo")}
    <body style="text-align:center; padding:50px;">
        <h1>Editando Mazo: {mazo['nombre_mazo']}</h1>
        <form action="/editar-mazo/{mazo_id}" method="post" enctype="multipart/form-data">
            <br>Jugador: <br>
            <input type="text" name="jugador" value="{mazo['jugador']}" required><br><br>
            <br>Nombre del Mazo: <br>
            <input type="text" name="mazo" value="{mazo['nombre_mazo']}" required><br><br>
            <br>Keywords (tipo de Mazo): <br>
            <textarea name="o_id" rows="3" cols="30">{mazo['Open_id']}</textarea><br><br>
            <br>Listado de Cartas: <br>
            <textarea name="cartas" rows="10" cols="30">{mazo['cartas_lista']}</textarea><br><br>
            Imagen Actual:<br>
            {'<img src="' + mazo['imagen_url'] + '" style="max-width:150px;">' if mazo['imagen_url'] else 'Sin imagen'}<br><br>
            Subir nueva imagen (opcional):<br>
            <input type="file" name="imagen"><br><br>
            <div style="font-weight: bold; color: red; font-size: 18px;">
            REQUERIDO: ¿Cuántas cartas cambiaste?<br>
            (Puedes poner 0. Cada carta cambiada descuenta 2% del ELO)
            </div><br>
            <input type="number" name="cartas_cambiadas" min="0" placeholder="Cartas cambiadas (minimo 0) *REQUERIDO" required style="width: 300px; height: 40px;"><br><br>
            <input type="submit" value="Guardar Cambios">
        </form>
        <br><br>
        <form action="/borrar-mazo/{mazo_id}" method="post" onsubmit="return confirm('¿Seguro que quieres borrar este mazo?');">
            <input type="submit" value="❌ Borrar Mazo" style="background-color:red; color:white; padding:10px;">
        </form>
        <br>
        <a href="/mazos">Cancelar</a>
    </body>
    </html>
    '''

@app.route('/borrar-mazo/<int:mazo_id>', methods=['POST'])
def borrar_mazo(mazo_id):
    conn = get_db_connection()

    # Primero borrar partidas donde aparece el mazo (opcional pero recomendado)
    conn.execute('DELETE FROM partidas WHERE mazo_1_id = ? OR mazo_2_id = ?', (mazo_id, mazo_id))

    # Luego borrar el mazo mismo
    conn.execute('DELETE FROM mazos WHERE id = ?', (mazo_id,))

    conn.commit()
    conn.close()

    return redirect('/mazos')


@app.route('/editar-mazo/<int:mazo_id>', methods=['POST'])
def editar_mazo_guardar(mazo_id):
    jugador = request.form.get('jugador')
    nombre_mazo = request.form.get('mazo')
    open_id = request.form.get('o_id')  # <<--- Capturamos el nuevo Open_id
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
        SET jugador = ?, nombre_mazo = ?, Open_id = ?, cartas_lista = ?, imagen_url = ?, elo = ?
        WHERE id = ?
    ''', (jugador, nombre_mazo, open_id, cartas_lista, imagen_url, nuevo_elo, mazo_id))

    conn.commit()
    conn.close()

    return redirect('/mazos')

@app.route('/ranking', methods=['GET'])
def ver_ranking():
    conn = get_db_connection()
    mazos = conn.execute('SELECT * FROM mazos ORDER BY elo DESC').fetchall()

    activos = []
    sin_jugar = []

    for mazo in mazos:
        id = mazo['id']

        total = conn.execute('''
            SELECT COUNT(*) as total
            FROM partidas
            WHERE mazo_1_id = ? OR mazo_2_id = ?
        ''', (id, id)).fetchone()['total']

        ganadas = conn.execute('''
            SELECT
                (SELECT COUNT(*) FROM partidas WHERE mazo_1_id = ? AND resultado_mazo_1 = 1) +
                (SELECT COUNT(*) FROM partidas WHERE mazo_2_id = ? AND resultado_mazo_1 = 0)
                AS ganadas
        ''', (id, id)).fetchone()['ganadas']

        info = {
            'mazo': mazo,
            'jugadas': total,
            'ganadas': ganadas,
            'porcentaje': round((ganadas / total * 100), 1) if total > 0 else 0
        }

        if total > 0:
            activos.append(info)
        else:
            sin_jugar.append(info)

    conn.close()

    tabla = f'''
    <html>
    {html_head("Ranking")}

    <body>
        <h1>Ranking de Mazos</h1>
        <h2>Mazos con partidas jugadas</h2>
        <table>
            <tr>
                <th>Imagen</th>
                <th>Nombre del Mazo</th>
                <th>Jugador</th>
                <th>ELO</th>
                <th>Partidas Jugadas</th>
                <th>Victorias (%)</th>
            </tr>
    '''

    for info in activos:
        mazo = info['mazo']
        imagen_html = f"<img src='{mazo['imagen_url']}' class='ranking-img' alt='Sin imagen'>" if mazo['imagen_url'] else "Sin imagen"
        tabla += f'''
            <tr>
                <td>{imagen_html}</td>
                <td>{mazo['nombre_mazo']}</td>
                <td>{mazo['jugador']}</td>
                <td>{round(mazo['elo'], 2)}</td>
                <td>{info['jugadas']}</td>
                <td>{info['porcentaje']}%</td>
            </tr>
        '''

    tabla += '''
        </table>
        <br><br>
        <h2>Mazos aún sin partidas</h2>
        <table>
            <tr>
                <th>Imagen</th>
                <th>Nombre del Mazo</th>
                <th>Jugador</th>
                <th>ELO</th>
            </tr>
    '''

    for info in sin_jugar:
        mazo = info['mazo']
        imagen_html = f"<img src='{mazo['imagen_url']}' class='ranking-img' alt='Sin imagen'>" if mazo['imagen_url'] else "Sin imagen"
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


@app.route('/ranking-filtrado', methods=['GET'])
def ranking_filtrado_form():
    return f'''
    <html>
    {html_head("Ranking Filtrado")}
    <body>
        <h1>Ranking Filtrado por Palabra Clave</h1>
        <form action="/ranking-filtrado" method="post">
            <label>Ingresa palabras clave (separadas por coma):</label><br><br>
            <input type="text" name="filtro" placeholder="Ej: Monocolor, Bloomburrow" required><br><br>
            <input type="submit" value="Filtrar Ranking">
        </form>
        <br>
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''
@app.route('/ranking-filtrado', methods=['POST'])
def ranking_filtrado_resultado():
    filtros = request.form.get('filtro')
    filtros = [f.strip() for f in filtros.split(',') if f.strip() != '']

    if not filtros:
        return "<h1>No ingresaste filtros válidos</h1><a href='/ranking-filtrado'>Volver</a>"

    condiciones = " OR ".join(["Open_id LIKE ?" for _ in filtros])
    parametros = [f"%{filtro}%" for filtro in filtros]

    conn = get_db_connection()
    mazos = conn.execute(f'''
        SELECT * FROM mazos
        WHERE {condiciones}
        ORDER BY elo DESC
    ''', parametros).fetchall()

    partidas_info = {}
    for mazo in mazos:
        id = mazo['id']

        total = conn.execute('''
            SELECT COUNT(*) as total
            FROM partidas
            WHERE mazo_1_id = ? OR mazo_2_id = ?
        ''', (id, id)).fetchone()['total']

        ganadas = conn.execute('''
            SELECT
                (SELECT COUNT(*) FROM partidas WHERE mazo_1_id = ? AND resultado_mazo_1 = 1) +
                (SELECT COUNT(*) FROM partidas WHERE mazo_2_id = ? AND resultado_mazo_1 = 0)
                AS ganadas
        ''', (id, id)).fetchone()['ganadas']

        partidas_info[id] = {
            'jugadas': total,
            'ganadas': ganadas,
            'porcentaje': round((ganadas / total * 100), 1) if total > 0 else 0
        }

    conn.close()

    tabla = f'''
    <html>
    {html_head("Ranking Filtrado")}
    <body>
        <h1>Ranking de Mazos Filtrado</h1>
        <h3>Filtros aplicados: {", ".join(filtros)}</h3>
        <table>
            <tr>
                <th>Imagen</th>
                <th>Nombre del Mazo</th>
                <th>Jugador</th>
                <th>ELO</th>
                <th>Partidas Jugadas</th>
                <th>Victorias (%)</th>
            </tr>
    '''

    for mazo in mazos:
        imagen_html = f"<img src='{mazo['imagen_url']}' class='ranking-img' alt='Sin imagen'>" if mazo['imagen_url'] else "Sin imagen"
        info = partidas_info.get(mazo['id'], {'jugadas': 0, 'ganadas': 0, 'porcentaje': 0})
        tabla += f'''
            <tr>
                <td>{imagen_html}</td>
                <td>{mazo['nombre_mazo']}</td>
                <td>{mazo['jugador']}</td>
                <td>{round(mazo['elo'], 2)}</td>
                <td>{info['jugadas']}</td>
                <td>{info['porcentaje']}%</td>
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


@app.route('/registrar-partida', methods=['GET'])
def registrar_partida_form():
    conn = get_db_connection()
    mazos = conn.execute('SELECT * FROM mazos ORDER BY nombre_mazo ASC').fetchall()
    conn.close()

    opciones = ""
    for mazo in mazos:
        opciones += f"<option value='{mazo['id']}'>{mazo['nombre_mazo']} ({mazo['jugador']})</option>"

    return f'''
    <html>
    {html_head("Registrar partida")}
    <body style="text-align:center; padding:50px;">
        <h1>Registrar Resultado de Partida</h1>
        <form action="/registrar-partida" method="post">
            <label for="mazo1">Mazo 1:</label><br>
            <select name="mazo1" required>{opciones}</select><br><br>
            <label for="mazo2">Mazo 2:</label><br>
            <select name="mazo2" required>{opciones}</select><br><br>
            ¿Ganó Mazo 1?<br>
            <select name="resultado" required>
                <option value="1">Sí</option>
                <option value="0">No</option>
            </select><br><br>
            <label for="torneo">Torneo (opcional):</label><br>
            <input type="text" name="torneo" placeholder="Ej: T1"><br><br>
            <input type="submit" value="Registrar Partida">
        </form>
        <br>
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''

@app.route('/registrar-partida', methods=['POST'])
def registrar_partida_guardar():
    mazo1_id = int(request.form.get('mazo1'))
    mazo2_id = int(request.form.get('mazo2'))
    resultado_mazo1 = int(request.form.get('resultado'))  # 1 si gana Mazo 1, 0 si gana Mazo 2
    torneo = request.form.get('torneo') or None  # ← opcional, puede ser None

    conn = get_db_connection()
    mazo1 = conn.execute('SELECT * FROM mazos WHERE id = ?', (mazo1_id,)).fetchone()
    mazo2 = conn.execute('SELECT * FROM mazos WHERE id = ?', (mazo2_id,)).fetchone()

    if mazo1 is None or mazo2 is None:
        conn.close()
        return "<h1>Error: Mazos no encontrados</h1><a href='/'>Volver</a>"

    # Cálculo ELO
    k = 32  # Constante típica de ajuste de ELO
    expected1 = 1 / (1 + 10 ** ((mazo2['elo'] - mazo1['elo']) / 400))
    expected2 = 1 / (1 + 10 ** ((mazo1['elo'] - mazo2['elo']) / 400))

    resultado_mazo2 = 1 - resultado_mazo1

    nuevo_elo1 = mazo1['elo'] + k * (resultado_mazo1 - expected1)
    nuevo_elo2 = mazo2['elo'] + k * (resultado_mazo2 - expected2)

    # Guardar la partida
    conn.execute('''
        INSERT INTO partidas (mazo1_id, mazo2_id, resultado_mazo1, torneo)
        VALUES (?, ?, ?, ?)
    ''', (mazo1_id, mazo2_id, resultado_mazo1, torneo))

    # Actualizar ELOs
    conn.execute('''
        UPDATE mazos SET elo = ? WHERE id = ?
    ''', (nuevo_elo1, mazo1_id))
    conn.execute('''
        UPDATE mazos SET elo = ? WHERE id = ?
    ''', (nuevo_elo2, mazo2_id))

    conn.commit()
    conn.close()

    return f'''
    <html>
    {html_head("Partida registrada")}
    <body style="text-align:center; padding:50px;">
        <h2>¡Partida registrada correctamente!</h2>
        <a href="/">Volver al Menú Principal</a><br>
        <a href="/ranking">Ver Ranking Actualizado</a>
    </body>
    </html>
    '''

@app.route('/ranking-global', methods=['GET'])
def ranking_global():
    conn = get_db_connection()
    jugadores = conn.execute('''
        SELECT
            jugador,
            AVG(elo) as promedio_elo,
            COUNT(*) as cantidad_mazos
        FROM mazos
        GROUP BY jugador
        ORDER BY promedio_elo DESC
    ''').fetchall()
    conn.close()

    tabla = f'''
    <html>
    {html_head("Ranking Global")}
    <body>
        <h1>Ranking Global de Jugadores</h1>
        <table>
            <tr>
                <th>Jugador</th>
                <th>ELO Promedio</th>
                <th>Número de Mazos</th>
            </tr>
    '''

    for jugador in jugadores:
        tabla += f'''
            <tr>
                <td>{jugador['jugador']}</td>
                <td>{round(jugador['promedio_elo'], 2)}</td>
                <td>{jugador['cantidad_mazos']}</td>
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

@app.route('/registrar-partida-simulado', methods=['GET'])
def registrar_partida_simulado_form():
    conn = get_db_connection()
    mazos = conn.execute('SELECT * FROM mazos ORDER BY nombre_mazo ASC').fetchall()
    conn.close()

    opciones = ""
    for mazo in mazos:
        opciones += f"<option value='{mazo['id']}'>{mazo['nombre_mazo']} ({mazo['jugador']})</option>"

    return f'''
    <html>
    {html_head("Registrar Partida (simulado)")}
    <body style="text-align:center; padding:50px;">
        <h1>Partida contra Rival Simulado</h1>
        <form action="/registrar-partida-simulado" method="post">
            <label for="mazo">Tu Mazo:</label><br>
            <select name="mazo" required>{opciones}</select><br><br>

            <label for="elo_rival">Puntaje ELO del Rival Simulado:</label><br>
            <input type="number" name="elo_rival" min="1" required><br><br>

            <label for="resultado">¿Ganaste?</label><br>
            <select name="resultado" required>
                <option value="1">Sí</option>
                <option value="0">No</option>
            </select><br><br>

            <input type="submit" value="Registrar Resultado">
        </form>
        <br>
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''
@app.route('/registrar-partida-simulado', methods=['POST'])
def registrar_partida_simulado_guardar():
    mazo_id = int(request.form.get('mazo'))
    elo_rival = float(request.form.get('elo_rival'))
    resultado = int(request.form.get('resultado'))  # 1 si ganaste, 0 si perdiste

    conn = get_db_connection()
    mazo = conn.execute('SELECT * FROM mazos WHERE id = ?', (mazo_id,)).fetchone()

    if mazo is None:
        conn.close()
        return "<h1>Mazo no encontrado</h1><a href='/'>Volver</a>"

    elo_mazo = mazo['elo']
    k = 32
    expected = 1 / (1 + 10 ** ((elo_rival - elo_mazo) / 400))
    nuevo_elo = elo_mazo + k * (resultado - expected)

    # Actualizar el ELO del mazo
    conn.execute('''
        UPDATE mazos SET elo = ? WHERE id = ?
    ''', (nuevo_elo, mazo_id))

    # Insertar también una partida simulada para contabilizarla
    conn.execute('''
        INSERT INTO partidas (mazo_1_id, mazo_2_id, resultado_mazo_1)
        VALUES (?, ?, ?)
    ''', (mazo_id, -1, resultado))  # Usamos -1 como "rival simulado"

    conn.commit()
    conn.close()

    return f'''
    <html>
    {html_head("Registrar partida")}
    <body style="text-align:center; padding:50px;">
        <h2>¡Resultado registrado correctamente!</h2>
        <a href="/">Volver al Menú Principal</a><br>
        <a href="/ranking">Ver Ranking Actualizado</a>
    </body>
    </html>
    '''
@app.route('/historial-partidas', methods=['GET'])
def historial_partidas():
    conn = get_db_connection()

    partidas = conn.execute('''
        SELECT
            p.id,
            p.fecha,
            p.resultado_mazo_1,
            m1.nombre_mazo AS mazo1_nombre,
            m1.jugador AS mazo1_jugador,
            m2.nombre_mazo AS mazo2_nombre,
            m2.jugador AS mazo2_jugador
        FROM partidas p
        LEFT JOIN mazos m1 ON p.mazo_1_id = m1.id
        LEFT JOIN mazos m2 ON p.mazo_2_id = m2.id
        ORDER BY p.fecha DESC
    ''').fetchall()

    conn.close()

    tabla = f'''
    <html>
    {html_head("Historial de partidas")}

    <body>
        <h1>Historial de Partidas</h1>
        <table>
            <tr>
                <th>Fecha</th>
                <th>Mazo 1</th>
                <th>Mazo 2</th>
                <th>Resultado</th>
                <th>Acción</th>

            </tr>
    '''

    for partida in partidas:
        mazo1 = f"{partida['mazo1_nombre']} ({partida['mazo1_jugador']})" if partida['mazo1_nombre'] else "Desconocido"
        if partida['mazo2_nombre']:
            mazo2 = f"{partida['mazo2_nombre']} ({partida['mazo2_jugador']})"
        else:
            mazo2 = "Rival Simulado"

        if partida['resultado_mazo_1'] == 1:
            resultado = "Gana Mazo 1"
        else:
            resultado = "Gana Mazo 2"

        tabla += f'''
            <tr>
                <td>{partida['fecha']}</td>
                <td>{mazo1}</td>
                <td>{mazo2}</td>
                <td>{resultado}</td>
                <td>
                    <form action="/borrar-partida/{partida['id']}" method="post" onsubmit="return confirm('¿Seguro que quieres borrar esta partida?');">
                        <input type="submit" value="❌ Borrar" style="background-color:red; color:white; font-weight:bold;">
                    </form>
                </td>
            </tr>
        '''

    tabla += f'''
        </table>
        <br>
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''

    return tabla

@app.route('/borrar-partida/<int:partida_id>', methods=['POST'])
def borrar_partida(partida_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM partidas WHERE id = ?", (partida_id,))
    conn.commit()
    conn.close()

    return redirect('/historial-partidas')

@app.route('/ranking-global-filtrado', methods=['GET'])
def ranking_global_filtrado_form():
    return f'''
    <html>
    {html_head("Ranking")}
    <body style="text-align:center; padding:50px;">
        <h1>Ranking Global Filtrado por Palabra Clave</h1>
        <form action="/ranking-global-filtrado" method="post">
            <label for="filtro">Ingresa palabras clave (separadas por coma si son varias):</label><br><br>
            <input type="text" name="filtro" placeholder="Ej: Monocolor, Bloomburrow" size="50" required><br><br>
            <input type="submit" value="Ver Ranking Filtrado">
        </form>
        <br>
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''
@app.route('/ranking-global-filtrado', methods=['POST'])
def ranking_global_filtrado():
    filtros = request.form.get('filtro')
    filtros = [f.strip() for f in filtros.split(',') if f.strip() != '']

    if not filtros:
        return "<h1>No ingresaste filtros válidos</h1><a href='/ranking-global-filtrado'>Volver</a>"

    # Construimos parte dinámica del SQL
    condiciones = " OR ".join(["Open_id LIKE ?" for _ in filtros])
    parametros = [f"%{filtro}%" for filtro in filtros]

    conn = get_db_connection()
    jugadores = conn.execute(f'''
        SELECT
            jugador,
            AVG(elo) as promedio_elo,
            COUNT(*) as cantidad_mazos
        FROM mazos
        WHERE {condiciones}
        GROUP BY jugador
        ORDER BY promedio_elo DESC
    ''', parametros).fetchall()
    conn.close()

    tabla = f'''
    <html>
    {html_head("Ranking")}

    <body>
        <h1>Ranking Global Filtrado</h1>
        <h3>Filtros aplicados: ''' + ", ".join(filtros) + '''</h3>
        <table>
            <tr>
                <th>Jugador</th>
                <th>ELO Promedio</th>
                <th>Número de Mazos</th>
            </tr>
    '''

    if jugadores:
        for jugador in jugadores:
            tabla += f'''
                <tr>
                    <td>{jugador['jugador']}</td>
                    <td>{round(jugador['promedio_elo'], 2)}</td>
                    <td>{jugador['cantidad_mazos']}</td>
                </tr>
            '''
    else:
        tabla += '''
            <tr><td colspan="3">No se encontraron jugadores con esos filtros.</td></tr>
        '''

    tabla += '''
        </table>
        <br>
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''

    return tabla

# Modifica la vista del torneo para mostrar título y descripción
@app.route('/torneo/<nombre>', methods=['GET'])
def ver_torneo(nombre):
    conn = get_db_connection()

    torneo_meta = conn.execute("SELECT * FROM torneos WHERE codigo = ?", (nombre,)).fetchone()
    titulo = torneo_meta['titulo'] if torneo_meta else f"Torneo {nombre}"
    descripcion = torneo_meta['descripcion'] if torneo_meta else ""

    # Obtener mazos y partidas
    mazos = conn.execute("SELECT * FROM mazos WHERE Open_id LIKE ?", (f"%{nombre}%",)).fetchall()
    mazo_dict = {mazo['id']: mazo for mazo in mazos}
    partidas = conn.execute("SELECT * FROM partidas WHERE torneo = ?", (nombre,)).fetchall()

    resultados = {}
    puntos_clasico = {}
    puntos_individual = {}

    for mazo in mazos:
        puntos_clasico[mazo['id']] = {'puntos': 0, 'diferencia': 0, 'mazo': mazo}
        puntos_individual[mazo['id']] = {'puntos': 0, 'diferencia': 0, 'mazo': mazo}

    for partida in partidas:
        m1 = partida['mazo_1_id']
        m2 = partida['mazo_2_id']
        res = partida['resultado_mazo_1']

        if m1 not in mazo_dict or m2 not in mazo_dict:
            continue

        key = tuple(sorted([m1, m2]))
        if key not in resultados:
            resultados[key] = {m1: 0, m2: 0}

        if res == 1:
            resultados[key][m1] += 1
        else:
            resultados[key][m2] += 1

        puntos_individual[m1]['diferencia'] += (1 if res == 1 else 0) - (0 if res == 1 else 1)
        puntos_individual[m2]['diferencia'] += (1 if res == 0 else 0) - (0 if res == 0 else 1)
        if res == 1:
            puntos_individual[m1]['puntos'] += 1
        else:
            puntos_individual[m2]['puntos'] += 1

    for (m1, m2), res_dict in resultados.items():
        g1 = res_dict[m1]
        g2 = res_dict[m2]

        if g1 > g2:
            puntos_clasico[m1]['puntos'] += 3
        elif g2 > g1:
            puntos_clasico[m2]['puntos'] += 3
        else:
            puntos_clasico[m1]['puntos'] += 1
            puntos_clasico[m2]['puntos'] += 1

        puntos_clasico[m1]['diferencia'] += g1 - g2
        puntos_clasico[m2]['diferencia'] += g2 - g1

    conn.close()

    html = f'''<html>{html_head(titulo)}<body>
        <h1>{titulo}</h1>
        <h2>Grilla de Encuentros</h2>
        <table><tr><th></th>'''

    orden = list(puntos_clasico.keys())
    for id2 in orden:
        html += f"<th><img src='{puntos_clasico[id2]['mazo']['imagen_url']}' class='ranking-img'><br>{puntos_clasico[id2]['mazo']['nombre_mazo']}</th>"
    html += "</tr>"

    for id1 in orden:
        html += f"<tr><th><img src='{puntos_clasico[id1]['mazo']['imagen_url']}' class='ranking-img'><br>{puntos_clasico[id1]['mazo']['nombre_mazo']}</th>"
        for id2 in orden:
            if id1 == id2:
                html += "<td style='background-color:#ccc;'>—</td>"
            else:
                key = tuple(sorted([id1, id2]))
                if key in resultados:
                    r = resultados[key]
                    html += f"<td>{r.get(id1,0)} - {r.get(id2,0)}</td>"
                else:
                    html += "<td>-</td>"
        html += "</tr>"
    html += "</table><br><br>"

    html += "<h2>Ranking (Estilo clásico: 3 puntos por victoria de cruce, 1 por empate)</h2>"
    html += "<p>Los puntos se asignan por cada serie de partidas entre dos mazos. El ganador de más partidas obtiene 3 puntos. Si empatan, ambos reciben 1 punto. Desempates: diferencia de partidas ganadas, luego ELO.</p>"
    ranking1 = sorted(puntos_clasico.values(), key=lambda x: (-x['puntos'], -x['diferencia'], -x['mazo']['elo']))
    html += "<table><tr><th>Jugador</th><th>Mazo</th><th>Puntos</th><th>Diferencia</th><th>ELO</th></tr>"
    for r in ranking1:
        m = r['mazo']
        html += f"<tr><td>{m['jugador']}</td><td>{m['nombre_mazo']}</td><td>{r['puntos']}</td><td>{r['diferencia']}</td><td>{round(m['elo'], 2)}</td></tr>"
    html += "</table><br><br>"

    html += "<h2>Ranking (Por partidas individuales ganadas)</h2>"
    html += "<p>Se otorga 1 punto por cada partida ganada, sin importar al rival. Desempates: diferencia de partidas ganadas y perdidas, luego ELO.</p>"
    ranking2 = sorted(puntos_individual.values(), key=lambda x: (-x['puntos'], -x['diferencia'], -x['mazo']['elo']))
    html += "<table><tr><th>Jugador</th><th>Mazo</th><th>Puntos</th><th>Diferencia</th><th>ELO</th></tr>"
    for r in ranking2:
        m = r['mazo']
        html += f"<tr><td>{m['jugador']}</td><td>{m['nombre_mazo']}</td><td>{r['puntos']}</td><td>{r['diferencia']}</td><td>{round(m['elo'], 2)}</td></tr>"
    html += f"</table><br><br><h3>Descripción del torneo:</h3><p>{descripcion}</p><br><a href='/'>Volver al Menú Principal</a></body></html>"

    return html

# Reemplaza la vista existente de /torneos con esta versión actualizada
# Reemplaza la vista existente de /torneos con versión mejorada
@app.route('/torneos', methods=['GET'])
def lista_torneos():
    conn = get_db_connection()
    torneos = conn.execute("SELECT * FROM torneos ORDER BY rowid DESC").fetchall()
    conn.close()

    html = f'''
    <html>
    {html_head("Torneos Disponibles")}
    <body>
        <h1>Torneos Registrados</h1>
        <ul style="list-style-type:none; padding:0;">
    '''

    if not torneos:
        html += "<p>No hay torneos registrados aún.</p>"
    else:
        for torneo in torneos:
            html += f'''
                <li style="margin: 30px 0; border-top: 2px solid #ccc; padding-top: 20px;">
                    <form action="/borrar-torneo/{torneo['codigo']}" method="post" onsubmit="return confirm('¿Seguro que quieres borrar este torneo?');" style="float:right;">
                        <input type="submit" value="❌ Borrar" style="background-color:red; color:white; font-weight:bold;">
                    </form>
                    <a class="boton" href="/torneo/{torneo['codigo']}" style="display:block; font-size: 24px; margin-bottom: 10px;">{torneo['titulo']}</a>
                    <p><strong>Código:</strong> {torneo['codigo']}</p>
                    <p>{torneo['descripcion']}</p>
                </li>
            '''

    html += '''
        </ul>
        <br>
        <a href="/crear-torneo" class="boton">➕ Crear nuevo torneo</a>
        <br><a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''

    return html


# Ruta para borrar torneo
@app.route('/borrar-torneo/<codigo>', methods=['POST'])
def borrar_torneo(codigo):
    conn = get_db_connection()
    # Borra todas las partidas asociadas con el torneo
    conn.execute('DELETE FROM partidas WHERE torneo = ?', (codigo,))
    # No borra mazos; solo el torneo como concepto
    conn.execute('DELETE FROM torneos WHERE codigo = ?', (codigo,))
    conn.commit()
    conn.close()
    return redirect('/torneos')

# Nueva versión de registrar-partida-multiple con integración de torneos
# Nueva versión de registrar-partida-multiple con integración de torneos (corregida con {{ }})
@app.route('/registrar-partida-multiple', methods=['GET'])
def registrar_partida_multiple_form():
    conn = get_db_connection()
    torneos = conn.execute("SELECT * FROM torneos ORDER BY codigo").fetchall()
    mazos = conn.execute("SELECT * FROM mazos ORDER BY jugador, nombre_mazo").fetchall()
    conn.close()

    # Opciones de torneos
    opciones_torneo = "<option value='libre' selected>Partida libre (sin torneo)</option>"
    for torneo in torneos:
        opciones_torneo += f"<option value='{torneo['codigo']}'>{torneo['titulo']} ({torneo['codigo']})</option>"

    # Opciones de mazos (todos por defecto, serán filtrados por JS)
    opciones = ""
    for mazo in mazos:
        opciones += f"<option value='{mazo['id']}' data-keywords='{mazo['Open_id']}'>{mazo['nombre_mazo']} ({mazo['jugador']})</option>"

    return f'''
    <html>
    {html_head("Registrar Partida Múltiple")}
    <body>
        <h1>Registrar Partida Múltiple (4 a 7 jugadores)</h1>
        <form action="/registrar-partida-multiple" method="post">

            <label for="torneo">¿Esta partida pertenece a un torneo?</label><br>
            <select name="torneo" id="torneo-select" onchange="filtrarMazosPorTorneo()">
                {opciones_torneo}
            </select><br><br>

            <label>Ganadores (puedes seleccionar múltiples):</label><br>
            <select name="ganadores" id="mazos-ganadores" multiple size="7" required>
                {opciones}
            </select><br><br>

            <label>Perdedores (puedes seleccionar múltiples):</label><br>
            <select name="perdedores" id="mazos-perdedores" multiple size="7" required>
                {opciones}
            </select><br><br>

            <input type="submit" value="Registrar Partida Múltiple">
        </form>

        <br><a href="/">Volver al Menú Principal</a>

        <script>
            function filtrarMazosPorTorneo() {{
                var torneo = document.getElementById('torneo-select').value;
                var selectGanadores = document.getElementById('mazos-ganadores');
                var selectPerdedores = document.getElementById('mazos-perdedores');

                [selectGanadores, selectPerdedores].forEach(select => {{
                    for (let i = 0; i < select.options.length; i++) {{
                        let opt = select.options[i];
                        let keywords = opt.getAttribute('data-keywords') || "";
                        if (torneo === 'libre' || keywords.includes(torneo)) {{
                            opt.style.display = '';
                        }} else {{
                            opt.style.display = 'none';
                            opt.selected = false;
                        }}
                    }}
                }});
            }}
            window.addEventListener('DOMContentLoaded', (event) => {{
            filtrarMazosPorTorneo();
            }});
        </script>
    </body>
    </html>
    '''


@app.route('/registrar-partida-multiple', methods=['POST'])
def registrar_partida_multiple():
    ganadores = request.form.getlist('ganadores')
    perdedores = request.form.getlist('perdedores')
    torneo = request.form.get('torneo')
    if torneo == 'libre':
        torneo = None

    if not ganadores or not perdedores:
        return "<h1>Debe haber al menos un ganador y un perdedor.</h1><a href='/registrar-partida-multiple'>Volver</a>"

    conn = get_db_connection()

    for g in ganadores:
        for p in perdedores:
            conn.execute('''
                INSERT INTO partidas (mazo_1_id, mazo_2_id, resultado_mazo_1, torneo)
                VALUES (?, ?, ?, ?)
            ''', (int(g), int(p), 1, torneo))

            # Actualizar ELO como partida normal
            m1 = conn.execute('SELECT * FROM mazos WHERE id = ?', (int(g),)).fetchone()
            m2 = conn.execute('SELECT * FROM mazos WHERE id = ?', (int(p),)).fetchone()
            if m1 and m2:
                elo1 = m1['elo']
                elo2 = m2['elo']
                expected1 = 1 / (1 + 10 ** ((elo2 - elo1) / 400))
                expected2 = 1 / (1 + 10 ** ((elo1 - elo2) / 400))
                nuevo_elo1 = elo1 + 32 * (1 - expected1)
                nuevo_elo2 = elo2 + 32 * (0 - expected2)

                conn.execute('UPDATE mazos SET elo = ? WHERE id = ?', (nuevo_elo1, int(g)))
                conn.execute('UPDATE mazos SET elo = ? WHERE id = ?', (nuevo_elo2, int(p)))

    conn.commit()
    conn.close()

    return '''
    <html>
    <body style="text-align:center; padding:50px;">
        <h2>Partida múltiple registrada exitosamente</h2>
        <a href="/">Volver al Menú Principal</a><br>
        <a href="/torneos">Ver Torneos</a>
    </body>
    </html>
    '''
# Paso 1: Agrega esta ruta para crear el formulario de nuevo torneo
@app.route('/crear-torneo', methods=['GET', 'POST'])
def crear_torneo():
    if request.method == 'POST':
        codigo = request.form.get('codigo').strip()
        titulo = request.form.get('titulo').strip()
        descripcion = request.form.get('descripcion').strip()

        if not codigo or not titulo:
            return "<h1>Error: Código y Título son obligatorios.</h1><a href='/crear-torneo'>Volver</a>"

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO torneos (codigo, titulo, descripcion) VALUES (?, ?, ?)',
                         (codigo, titulo, descripcion))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return f"<h1>Error: Ya existe un torneo con código '{codigo}'.</h1><a href='/crear-torneo'>Volver</a>"

        conn.close()
        return redirect('/torneos')

    # Método GET: mostrar formulario
    return f'''
    <html>
    {html_head("Crear Torneo")}
    <body>
        <h1>Crear Nuevo Torneo</h1>
        <form method="post">
            <label for="codigo">Código del Torneo (ej: T2):</label><br>
            <input type="text" name="codigo" required><br><br>

            <label for="titulo">Título del Torneo:</label><br>
            <input type="text" name="titulo" required><br><br>

            <label for="descripcion">Descripción / Reglas:</label><br>
            <textarea name="descripcion" rows="6"></textarea><br><br>

            <input type="submit" value="Crear Torneo">
        </form>
        <br>
        <a href="/">Volver al Menú Principal</a>
    </body>
    </html>
    '''



# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
