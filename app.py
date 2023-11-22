from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response, session 
from flask_mysqldb import MySQL, MySQLdb
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename 
import secrets
import hashlib
import os
import base64
import requests
from telegram import Bot

app = Flask(__name__)
bot = Bot(token='6497427311:AAF7sCO_70BqsA5wMME44EUP7OzyfGLsyz8')
app.config.from_object('config')
app.secret_key = 'af48c649fa0a89cbf58f0c62b225db28'
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\aleja\\OneDrive\\Desktop\\Camion\\Camion\\static\\imagenes'
# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'camion'

mysql = MySQL(app)

# Directorio de destino para las imágenes
upload_directory = 'static/uploads'

if not os.path.exists(upload_directory):
    os.makedirs(upload_directory)

# Configuración de correo electrónico
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'alejandrorosalesperez030@gmail.com'  # Usa tu correo electrónico de Gmail
app.config['MAIL_PASSWORD'] = 'bvgj kief vcik uonp'  # Usa tu contraseña de Gmail
mail = Mail(app)

def generar_token_unico(correo):
    # Genera una cadena aleatoria segura
    cadena_aleatoria = secrets.token_urlsafe(16)

    # Combina el correo del usuario con la cadena aleatoria
    cadena_a_hashear = f'{correo}{cadena_aleatoria}'

    # Aplica una función hash (SHA-256 en este ejemplo) a la cadena combinada
    token = hashlib.sha256(cadena_a_hashear.encode()).hexdigest()

    return token

@app.route('/calcular_ruta', methods=['POST'])
def calcular_ruta():
    try:
        # Obtener datos de la solicitud (puedes ajustar esto según tus necesidades)
        data = request.get_json()

        # Extraer datos relevantes para el cálculo de la ruta
        user_coords = data['user_coords']
        parada_coords = data['parada_coords']
        duracion = data['duracion']

        # Tu lógica para calcular la ruta aquí

        # Enviar notificación a Telegram si la duración es menor o igual a 5 minutos
        if duracion <= 5:
            chat_id = '1718131524'  # Reemplaza 'ID_DEL_CHAT' con el ID del chat de Telegram
            mensaje = f'¡El camión está cerca de la parada! El tiempo estimado es de {duracion} minutos.'
            bot.send_message(chat_id, mensaje)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/confirmar_registro/<token>')
def confirmar_registro(token):
    # Aquí debes agregar la lógica para confirmar el registro
    # Usar el token para verificar y activar la cuenta del usuario, etc.
    return "Registro confirmado correctamente"


@app.route('/enviar_correo', methods=['POST'])
def enviar_correo():
    # Lógica para enviar el correo aquí

    # Si la operación fue exitosa, devuelve una respuesta JSON
    response = {'mensaje': 'Correos enviados con éxito'}
    return jsonify(response), 200


# Resto de tu código

def obtener_datos_de_base_de_datos():
    # Simulamos obtener datos de la base de datos
    datos = [
        {"nombre": "Parada 1", "hora_salida": "08:00:00", "imagen": "imagen1.jpg"},
        {"nombre": "Parada 2", "hora_salida": "09:15:00", "imagen": "imagen2.jpg"},
        # Agrega más datos de paradas según sea necesario
    ]
    return datos

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    # Ejecuta una consulta para obtener datos de la base de datos
    cursor.execute("SELECT NOMBRE, horasalida, imagen FROM paradas")
    paradas = cursor.fetchall()
    cursor.close()  # Cierra el cursor

    return render_template('index.html', paradas=paradas)


@app.route('/mapa')
def mapa():
    # Usar la extensión MySQL para interactuar con la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre, latitud, longitud,horasalida FROM paradas")
    paradas = cursor.fetchall()
    cursor.close()
    return render_template('mapa.html', paradas=paradas)


@app.route('/mapa_usu')
def mapa_usu():
    # Usar la extensión MySQL para interactuar con la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre, latitud, longitud,horasalida FROM paradas")
    paradas = cursor.fetchall()
    cursor.close()
    return render_template('mapa.html', paradas=paradas)


# Resto del código...
@app.route('/obtener_hora_salida')
def obtener_hora_salida():
    parada = request.args.get('parada')
    
    # Consulta la hora de salida desde la base de datos
    cursor = db.cursor()
    cursor.execute("SELECT horasalida FROM paradas WHERE nombre = %s", (parada,))
    hora_salida = cursor.fetchone()
    cursor.close()

    if hora_salida:
        return hora_salida[0]
    else:
        return "Hora de salida no encontrada para la parada seleccionada."


@app.route('/index_admin')
def index_admin():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT NOMBRE, horasalida, imagen FROM paradas")
    paradas = cursor.fetchall()
    return render_template('index_admin.html', paradas=paradas)


@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/formulario_camion')
def formulario_camion():
    return render_template('formulario_camion.html')


@app.route('/formulario_ciudad')
def formulario_ciudad():
    # Obtener los datos de la tabla 'login'
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT IdLogin, Nombre FROM login")
    login_data = cursor.fetchall()
    cursor.close()
    return render_template('formulario_ciudad.html', login_data=login_data)



@app.route('/formulario_ruta')
def formulario_ruta():
    return render_template('formulario_ruta.html')


@app.route('/ruta')
def ruta():
    return render_template('ruta.html')

@app.route('/guardar_ruta', methods=['POST'])
def guardar_ruta():
    if request.method == 'POST':
        # Obtén los datos del formulario
        id_ruta = request.form['id_ruta']
        nombre = request.form['nombre']
        precio = request.form['precio']
        fecha_creacion = request.form['fecha_creacion']
        fecha_modificacion = request.form['fecha_modificacion']
        id_login = request.form['id_login']

        # Crea un objeto Ruta con los datos del formulario
        nueva_ruta = Ruta(
            id_ruta=id_ruta,
            nombre=nombre,
            precio=precio,
            fecha_creacion=fecha_creacion,
            fecha_modificacion=fecha_modificacion,
            id_login=id_login
        )

        # Agrega la nueva ruta a la base de datos
        db.session.add(nueva_ruta)
        db.session.commit()

        flash('Ruta agregada exitosamente', 'success')

        return redirect(url_for('index'))  # Redirige a la página que prefieras después de agregar la ruta

    # En caso de que no sea una solicitud POST, simplemente renderiza el formulario nuevamente
    return render_template('formulario_ruta.html', usuarios=Usuario.query.all())


@app.route('/vista_camiones')
def vista_camiones():
    return render_template('vista_camiones.html')


@app.route('/vista_ciudad')
def vista_ciudad():
    # Obtener los datos de la tabla 'ciudad'
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM ciudad")
    ciudades = cursor.fetchall()
    cursor.close()
    return render_template('vista_ciudad.html', ciudades=ciudades)


@app.route('/ruta_camion')
def ruta_camion():
    return render_template('ruta_camion.html')

@app.route('/index_usu')
def index_usu():
    cursor = mysql.connection.cursor()
    # Ejecuta una consulta para obtener datos de la base de datos
    cursor.execute("SELECT NOMBRE, horasalida, imagen FROM paradas")
    paradas = cursor.fetchall()
    return render_template('index_usu.html', paradas=paradas)



#base de datos insertar
@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    if request.method == 'POST':
        # Obtener los datos del formulario
        id_login = request.form['id_login']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        rol = request.form['rol']

        # Validar si la matrícula existe en la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT IdLogin FROM login WHERE IdLogin = %s", (id_login,))
        matricula_existente = cursor.fetchone()
        cursor.close()

        if matricula_existente:
            flash('La matrícula ya está registrada en la base de datos.', 'danger')
            return redirect(url_for('formulario'))

        # Insertar los datos en la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO login (IdLogin, Nombre, Apellidos, Correo, Contraseña, Rol) VALUES (%s, %s, %s, %s, %s, %s)",
                       (id_login, nombre, apellidos, correo, contraseña, rol))
        mysql.connection.commit()

        # Enviar correo de confirmación
        token = generar_token_unico(correo)
        msg = Message('Confirmación de registro', sender='alejandrorosalesperez030@gmail.com', recipients=[correo])
        msg.body = f'Gracias por registrarte en nuestra aplicación. Por favor, confirma tu registro haciendo clic en el siguiente enlace: {url_for("confirmar_registro", token=token, _external=True)}'
        mail.send(msg)
        cursor.close()

        # Establecer un mensaje de éxito
        flash('Registro exitoso. Se ha enviado un correo de confirmación.', 'success')

        # Redirigir al usuario al index
        return redirect(url_for('formulario'))

    return "Error en la solicitud."


@app.route('/guardar_ciudad', methods=['POST'])
def guardar_ciudad():
    if request.method == 'POST':
        # Obtener los datos del formulario
        id_ciudad = request.form['id_ciudad']
        nombre = request.form['nombre']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        zoom = request.form['zoom']
        fecha_creacion = request.form['fecha_creacion']
        fecha_modificacion = request.form['fecha_modificacion']
        id_login = request.form['id_login']

        # Insertar los datos en la tabla 'ciudad' de la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO ciudad (IdCiudad, Nombre, Latitud, Longitud, Zoom, FechaCreacion, FechaModificacion, IdLogin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (id_ciudad, nombre, latitud, longitud, zoom, fecha_creacion, fecha_modificacion, id_login))
        mysql.connection.commit()
        cursor.close()

        # Establecer un mensaje de éxito
        flash('Los datos de la ciudad se han guardado correctamente.', 'success')

        # Redirigir al usuario a la página deseada (por ejemplo, la página de inicio)
        return redirect(url_for('formulario_ciudad'))

    return "Error en la solicitud."


#para insertar paradas
@app.route('/agregar_parada', methods=['GET', 'POST'])
def agregar_parada():
    if request.method == 'POST':
        # Obtén los datos del formulario
        nombre = request.form['nombre']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        horasalida = request.form['horasalida']

        # Obtén el archivo de imagen
        imagen = request.files['imagen']
        if imagen and imagen.filename != '':
            # Asegura el nombre del archivo y guarda la imagen en el sistema de archivos
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Inserta los datos en la base de datos, incluyendo la ruta de la imagen
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO paradas (NOMBRE, latitud, longitud, horasalida, imagen) VALUES (%s, %s, %s, %s, %s)",
               (nombre, latitud, longitud, horasalida, filename))

            mysql.connection.commit()
            cursor.close()

            flash('Parada agregada exitosamente', 'success')

    return render_template('formulario_parada.html')

@app.route('/vista_eparada/<nombre>')
def vista_eparada(nombre):
    # Conecta a la base de datos
    cur = mysql.connection.cursor()

    # Ejecuta una consulta para obtener los datos de la parada con el nombre proporcionado
    cur.execute("SELECT * FROM paradas WHERE nombre = %s", (nombre,))

    # Obtiene los datos de la parada
    parada = cur.fetchone()

    # Cierra la conexión a la base de datos
    cur.close()

    return render_template('editar_parada.html', parada=parada)


# Ruta para manejar la actualización de la parada
@app.route('/editar_parada/<int:id>', methods=['POST'])
def editar_parada(id):
    if request.method == 'POST':
        # Obtén los datos del formulario
        nombre = request.form['nombre']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        horasalida = request.form['horasalida']

        # Puedes agregar más campos según sea necesario

        # Actualiza los datos en la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE paradas SET NOMBRE = %s, latitud = %s, longitud = %s, horasalida = %s WHERE id = %s",
                       (nombre, latitud, longitud, horasalida, id))

        mysql.connection.commit()
        cursor.close()

        flash('Parada actualizada exitosamente', 'success')

    # Redirige a la página principal o a donde prefieras después de editar
    return redirect(url_for('index_admin'))

@app.route('/eliminar_parada/<nombre>')
def eliminar_parada(nombre):
    # Elimina físicamente la parada
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM paradas WHERE NOMBRE = %s", (nombre,))
    mysql.connection.commit()
    cursor.close()

    flash('Parada eliminada exitosamente', 'success')

    # Redirige a la página principal o a donde prefieras después de eliminar
    return redirect(url_for('index_admin'))

# Para ingrear al login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_login = request.form['id_login']
        contra = request.form['contra']

        # Consultar la base de datos para obtener el usuario y su rol
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT IdLogin, Rol FROM login WHERE IdLogin = %s AND Contraseña = %s", (id_login, contra))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Almacena el rol del usuario en la sesión
            session['rol'] = user[1]

            # Redirige a la página correspondiente según el rol
            if user[1] == 1:
                return redirect(url_for('index_admin'))
            elif user[1] == 2:
                return redirect(url_for('index_usu'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


#funciones extra 
def matricula_existe(matricula):
    try:
        conn = MySQLdb.connect(
            host='localhost',
            user='root',
            password='',
            db='camion'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT Matricula FROM matriculasvalidas WHERE Matricula = %s", (matricula,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result is not None:
            return True
        else:
            return False  # Matrícula no encontrada
    except Exception as e:
        print("Error al verificar la matrícula:", str(e))
        return False  # En caso de error, también considera que la matrícula no existe




@app.route('/verificar_matricula', methods=['GET'])
def verificar_matricula():
    matricula = request.args.get('matricula')

    if matricula_existe(matricula):
        return jsonify({"exists": True, "message": "La matrícula existe"})
    else:
        return jsonify({"exists": False, "message": "La matrícula no existe"})
    





if __name__ == '__main__':
    app.secret_key = 'af48c649fa0a89cbf58f0c62b225db28'
    app.run(debug=True)
