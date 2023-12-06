#--------------------------------------------------------------------
# Instalar con pip install Flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
import os
import time
#--------------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

#--------------------------------------------------------------------
class Biblioteca:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS libros (
            codigo INT,
            titulo VARCHAR(255) NOT NULL,
            autor VARCHAR(255) NOT NULL,
            imagen_url VARCHAR(255),
            genero VARCHAR(50) NOT NULL)''')
        self.conn.commit()

        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def agregar_libro(self, codigo, titulo, autor, imagen, genero):
        self.cursor.execute(f"SELECT * FROM libros WHERE codigo = {codigo}")
        libro_existe = self.cursor.fetchone()
        if libro_existe:
            return False

        sql = "INSERT INTO libros (codigo, titulo, autor, imagen_url, genero) VALUES (%s, %s, %s, %s, %s)"
        valores = (codigo, titulo, autor, imagen, genero)

        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True

    def consultar_libro(self, codigo):
        self.cursor.execute(f"SELECT * FROM libros WHERE codigo = {codigo}")
        return self.cursor.fetchone()

    def modificar_libro(self, codigo, nuevo_titulo, nuevo_autor, nueva_imagen, nuevo_genero):
        sql = "UPDATE libros SET titulo = %s, autor = %s, imagen_url = %s, genero = %s WHERE codigo = %s"
        valores = (nuevo_titulo, nuevo_autor, nueva_imagen, nuevo_genero, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def listar_libros(self):
        self.cursor.execute("SELECT * FROM libros")
        libros = self.cursor.fetchall()
        return libros

    def eliminar_libro(self, codigo):
        self.cursor.execute(f"DELETE FROM libros WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    def mostrar_libro(self, codigo):
        libro = self.consultar_libro(codigo)
        if libro:
            print("-" * 40)
            print(f"Código.....: {libro['codigo']}")
            print(f"Título.....: {libro['titulo']}")
            print(f"Autor......: {libro['autor']}")
            print(f"Imagen.....: {libro['imagen_url']}")
            print(f"Género.....: {libro['genero']}")
            print("-" * 40)
        else:
            print("Libro no encontrado.")


#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
biblioteca = Biblioteca(host='localhost', user='root', password='root', database='miapp')

RUTA_DESTINO = './static/imagenes/'

#--------------------------------------------------------------------
@app.route("/libros", methods=["GET"])
def listar_libros():
    libros = biblioteca.listar_libros()
    return jsonify(libros)


#--------------------------------------------------------------------
@app.route("/libros/<int:codigo>", methods=["GET"])
def mostrar_libro(codigo):
    libro = biblioteca.consultar_libro(codigo)
    if libro:
        return jsonify(libro), 201
    else:
        return "Libro no encontrado", 404


#--------------------------------------------------------------------
@app.route("/libros", methods=["POST"])
def agregar_libro():
    codigo = request.form['codigo']
    titulo = request.form['titulo']
    autor = request.form['autor']
    imagen = request.files['imagen']
    genero = request.form['genero']
    nombre_imagen = ""

    libro = biblioteca.consultar_libro(codigo)
    if not libro:
        nombre_imagen = secure_filename(imagen.filename)
        nombre_base, extension = os.path.splitext(nombre_imagen)
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"

        if biblioteca.agregar_libro(codigo, titulo, autor, nombre_imagen, genero):
            imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
            return jsonify({"mensaje": "Libro agregado correctamente.", "imagen": nombre_imagen}), 201
        else:
            return jsonify({"mensaje": "Error al agregar el libro."}), 500
    else:
        return jsonify({"mensaje": "Libro ya existe."}), 400


#--------------------------------------------------------------------
@app.route("/libros/<int:codigo>", methods=["PUT"])
def modificar_libro(codigo):
    nuevo_titulo = request.form.get("titulo")
    nuevo_autor = request.form.get("autor")
    nuevo_genero = request.form.get("genero")
    imagen = request.files['imagen']

    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"

    libro = biblioteca.consultar_libro(codigo)
    if libro:
        imagen_vieja = libro["imagen_url"]
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    if biblioteca.modificar_libro(codigo, nuevo_titulo, nuevo_autor, nombre_imagen, nuevo_genero):
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        return jsonify({"mensaje": "Libro modificado"}), 200
    else:
        return jsonify({"mensaje": "Libro no encontrado"}), 403


#--------------------------------------------------------------------
@app.route("/libros/<int:codigo>", methods=["DELETE"])
def eliminar_libro(codigo):
    libro = biblioteca.consultar_libro(codigo)
    if libro:
        imagen_vieja = libro["imagen_url"]
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    if biblioteca.eliminar_libro(codigo):
        return jsonify({"mensaje": "Libro eliminado"}), 200
    else:
        return jsonify({"mensaje": "Error al eliminar el libro"}), 500


#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
