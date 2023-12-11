# Instalar con pip install Flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
CORS(app)

class BibliotecaLibros:  # Cambié el nombre de la clase a BibliotecaLibros
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
            editorial VARCHAR(255) NOT NULL,
            imagen_url VARCHAR(255),
            enlace VARCHAR(255))''')
        self.conn.commit()

        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def agregar_libro(self, codigo, titulo, autor, editorial, imagen, enlace):
        self.cursor.execute(f"SELECT * FROM libros WHERE codigo = {codigo}")
        libro_existe = self.cursor.fetchone()
        if libro_existe:
            return False

        sql = "INSERT INTO libros (codigo, titulo, autor, editorial, imagen_url, enlace) VALUES (%s, %s, %s, %s, %s, %s)"
        valores = (codigo, titulo, autor, editorial, imagen, enlace)

        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True

    def consultar_libro(self, codigo):
        self.cursor.execute(f"SELECT * FROM libros WHERE codigo = {codigo}")
        return self.cursor.fetchone()

    def modificar_libro(self, codigo, nuevo_titulo, nuevo_autor, nueva_editorial, nueva_imagen, nuevo_enlace):
        sql = "UPDATE libros SET titulo = %s, autor = %s, editorial = %s, imagen_url = %s, enlace = %s WHERE codigo = %s"
        valores = (nuevo_titulo, nuevo_autor, nueva_editorial, nueva_imagen, nuevo_enlace, codigo)
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
            print(f"Editorial..: {libro['editorial']}")
            print(f"Imagen.....: {libro['imagen_url']}")
            print(f"Enlace.....: {libro['enlace']}")
            print("-" * 40)
        else:
            print("Libro no encontrado.")


biblioteca = BibliotecaLibros(host='acmdq.mysql.pythonanywhere-services.com', user='acmdq', password='comision23521', database='acmdq$miapp')

RUTA_DESTINO = '/home/acmdq/mysite/static/imagenes'

@app.route("/libros", methods=["GET"])
def listar_libros():
    libros = biblioteca.listar_libros()
    return jsonify(libros)


@app.route("/libros/<int:codigo>", methods=["GET"])
def mostrar_libro(codigo):
    libro = biblioteca.consultar_libro(codigo)
    if libro:
        return jsonify(libro), 201
    else:
        return "Libro no encontrado", 404


#--------------------------------------------------------------------
# Agregar un producto
#--------------------------------------------------------------------

@app.route("/libros", methods=["POST"])

#La ruta Flask `/productos` con el método HTTP POST está diseñada para permitir la adición de un nuevo producto a la base de datos.
#La función agregar_producto se asocia con esta URL y es llamada cuando se hace una solicitud POST a /productos.

def agregar_libro():
    codigo = request.form['codigo']
    titulo = request.form['titulo']
    autor = request.form['autor']
    editorial = request.form['editorial']
    imagen = request.files['imagen']
    enlace = request.form['enlace']
    nombre_imagen=""

    libro = biblioteca.consultar_libro(codigo)
    if not libro:
        nombre_imagen = secure_filename(imagen.filename)
        nombre_base, extension = os.path.splitext(nombre_imagen)
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
        
        if  biblioteca.agregar_libro(codigo, titulo, autor, editorial, nombre_imagen, enlace):
            imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
            return jsonify({"mensaje": "Libro agregado correctamente.", "imagen": nombre_imagen}), 201
        else:
            return jsonify({"mensaje": "Error al agregar el libro."}), 500
    else:
        return jsonify({"mensaje": "Libro ya existe."}), 400
    

@app.route("/libros/<int:codigo>", methods=["PUT"])
def modificar_libro(codigo):
    nuevo_titulo = request.form.get("titulo")
    nuevo_autor = request.form.get("autor")
    nueva_editorial = request.form.get("editorial")
    imagen = request.files['imagen']
    nuevo_enlace = request.form.get("enlace")

    # Procesamiento de la imagen
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"

    # Busco el producto guardado
    libro = biblioteca.consultar_libro(codigo)
    if libro:
        imagen_vieja = libro["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe la borro.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    # Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
    if biblioteca.modificar_libro(codigo, nuevo_titulo, nuevo_autor, nueva_editorial, nombre_imagen, nuevo_enlace):
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        
        #Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Libro modificado"}), 200
    else:
        #Si el producto no se encuentra (por ejemplo, si no hay ningún producto con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Libro no encontrado"}), 403





#--------------------------------------------------------------------
# Eliminar un producto según su código
#--------------------------------------------------------------------

@app.route("/libros/<int:codigo>", methods=["DELETE"])
#La ruta Flask /productos/<int:codigo> con el método HTTP DELETE está diseñada para eliminar un producto específico de la base de datos, utilizando su código como identificador.
#La función eliminar_producto se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /productos/ seguido de un número (el código del producto).

def eliminar_libro(codigo):
    # Busco el producto en la base de datos
    libro = biblioteca.consultar_libro(codigo)
    if libro:  # Si el producto existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = libro["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe, la elimina del sistema de archivos.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el producto del catálogo
        if biblioteca.eliminar_libro(codigo):
            return jsonify({"mensaje": "Libro eliminado"}), 200
        else:
            #Si ocurre un error durante la eliminación (por ejemplo, si el producto no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        return jsonify({"mensaje": "Libro no encontrado"}), 404

#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)