from flask import Flask, request, render_template_string

# Crear la app de Flask
app = Flask(__name__)

# Página principal
@app.route('/', methods=['GET'])
def home():
    return '''
    <h1>Inscripción de Mazos MTG</h1>
    <form action="/registrar" method="post">
        Nombre del Jugador: <input type="text" name="jugador"><br>
        Nombre del Mazo: <input type="text" name="mazo"><br>
        <input type="submit" value="Registrar">
    </form>
    '''

# Página que recibe los datos del formulario
@app.route('/registrar', methods=['POST'])
def registrar():
    jugador = request.form.get('jugador')
    mazo = request.form.get('mazo')
    return f'<h2>¡Mazo registrado!</h2><p>Jugador: {jugador}<br>Mazo: {mazo}</p>'

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)