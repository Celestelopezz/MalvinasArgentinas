# Definir la clase Catalogo
class Catalogo:
    
    def __init__(self):
        # Definimos una lista para agregar los libros.
        self.libros = []
# metodo para agregar un nuevo libro    
    def agregar_libro(self, titulo, editorial, autor_a, imagen, enlace):
        if self.consultar_libro(titulo):
            print("Libro existente")
            return False
        else:
            nuevo_libro = {
                'titulo': titulo,
                'editorial': editorial,
                'autor_a': autor_a,
                'imagen': imagen,
                'enlace': enlace
            }
            self.libros.append(nuevo_libro)
            return True
# metodo para listar todos los libros del catalogo
    def listar_libros(self):
        print("-" * 50)
        for libro in self.libros:
            print(f"Titulo: {libro['titulo']}")
            print(f"Editorial: {libro['editorial']}")
            print(f"Autor/a: {libro['autor_a']}")
            print(f"Imagen: {libro['imagen']}")
            print(f"Enlace: {libro['enlace']}")
            print("-" * 50)

    def consultar_libro(self, titulo):
        for libro in self.libros:
            if libro['titulo'].lower() == titulo.lower():
                return libro
        return None
# metodo para modificar los detalles del libro
    def modificar_libros(self, titulo, nuevo_titulo, nueva_editorial, nuevo_autor_a, nueva_imagen, nuevo_enlace):
        libro_a_modificar = self.consultar_libro(titulo)
        if libro_a_modificar:
            libro_a_modificar['titulo'] = nuevo_titulo
            libro_a_modificar['editorial'] = nueva_editorial
            libro_a_modificar['autor_a'] = nuevo_autor_a
            libro_a_modificar['imagen'] = nueva_imagen
            libro_a_modificar['enlace'] = nuevo_enlace
            return True
        return False
# metodo para eliminar un libro poor su titulo
    def eliminar_libro(self, titulo):
        for libro in self.libros:
            if libro['titulo'].lower() == titulo.lower():
                self.libros.remove(libro)
                return True
        return False

# Programa principal
catalogo = Catalogo()
catalogo.agregar_libro('Si yo fuera un Monstruo', 'AZ Editora', 'Mónica López Valeria Dávila', 'img/img cuentos/tapa-040-0011-Monstruo.jpg', 'enlace')
catalogo.agregar_libro('Si yo fuera Ogro', 'AZ Editora', 'Mónica López Valeria Dávila', 'imagen', 'enlace')
catalogo.agregar_libro('Si yo fuera una Princesa', 'AZ Editora', 'Mónica López Valeria Dávila', 'imagen', 'enlace')
catalogo.agregar_libro('Si yo fuera un Mago', 'AZ Editora', 'Mónica López Valeria Dávila', 'imagen', 'enlace')
catalogo.agregar_libro('Si yo fuera un Superhéroe', 'AZ Editora', 'Mónica López Valeria Dávila', 'imagen', 'enlace')

# Lista los libros en pantalla
catalogo.listar_libros()

# Consulta un libro por título
titulo_a_buscar = "si yo fuera un superheroe"
libros_encontrados = catalogo.consultar_libro(titulo_a_buscar)

# Modifica un libro por su título
catalogo.modificar_libros('si yo fuera un monstruo', 'nuevo_titulo', 'nueva_editorial', 'nuevo_autor_a', 'nueva_imagen', 'nuevo_enlace')

# Elimina un libro por su título
catalogo.eliminar_libro('si yo fuera un mago')

# Lista los libros en pantalla después de modificar y eliminar
catalogo.listar_libros()


