import os
import requests
import threading

class PixabayDownloader:
    """
    Clase para descargar imágenes de Pixabay usando la API.

    Atributos:
    ----------
    api_key : str
        Clave de API de Pixabay para autenticar solicitudes.
    directorio_imagenes : str
        Directorio donde se guardarán las imágenes descargadas.

    Métodos:
    --------
    __init__(api_key, directorio_imagenes="imagenes_descargadas")
        Inicializa la clase con la clave de API y el directorio de descarga.
    obtener_urls_imagenes(consulta, cantidad=50)
        Realiza una consulta a la API de Pixabay y devuelve una lista de URLs de imágenes.
    descargar_imagen(url, nombre_archivo)
        Descarga una imagen desde una URL específica.
    descargar_imagenes_concurrentes(consulta, cantidad=50)
        Realiza la descarga concurrente de imágenes basadas en la consulta dada.
    """

    def __init__(self, api_key, directorio_imagenes="imagenes_descargadas"):
        """
        Inicializa la clase con la clave de API y el directorio de descarga.

        Parámetros:
        -----------
        api_key : str
            Clave de API de Pixabay para autenticar las solicitudes.
        directorio_imagenes : str, opcional
            Nombre del directorio donde se guardarán las imágenes descargadas. (por defecto "imagenes_descargadas")
        """
        self.api_key = api_key
        self.directorio_imagenes = directorio_imagenes
        os.makedirs(directorio_imagenes, exist_ok=True)  # Crear el directorio si no existe

    def obtener_urls_imagenes(self, consulta, cantidad=5):
        """
        Realiza una consulta a la API de Pixabay y devuelve una lista de URLs de imágenes.

        Parámetros:
        -----------
        consulta : str
            Palabra clave para buscar imágenes en Pixabay.
        cantidad : int, opcional
            Número de imágenes a obtener. (por defecto 5)

        Retorna:
        --------
        list
            Una lista de URLs de imágenes obtenidas de Pixabay.

        Excepciones:
        ------------
        requests.exceptions.RequestException
            Si hay un problema en la solicitud a la API.
        """
        URL_BASE = "https://pixabay.com/api/"
        parametros = {
            'key': self.api_key,
            'q': consulta,
            'image_type': 'photo',
            'per_page': cantidad
        }

        try:
            respuesta = requests.get(URL_BASE, params=parametros)
            respuesta.raise_for_status()  # Lanza una excepción si la solicitud falla
            datos = respuesta.json()
            urls = [imagen['largeImageURL'] for imagen in datos['hits']]
            return urls
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud a la API: {e}")
            return []

    def descargar_imagen(self, url, nombre_archivo):
        """
        Descarga una imagen desde una URL específica y la guarda en el directorio configurado.

        Parámetros:
        -----------
        url : str
            URL de la imagen a descargar.
        nombre_archivo : str
            Nombre del archivo donde se guardará la imagen.

        Excepciones:
        ------------
        requests.exceptions.RequestException
            Si hay un problema en la solicitud de descarga.
        """
        try:
            respuesta = requests.get(url, stream=True)
            respuesta.raise_for_status()  # Verifica que la respuesta sea correcta

            ruta = os.path.join(self.directorio_imagenes, nombre_archivo)
            with open(ruta, 'wb') as archivo:
                for fragmento in respuesta.iter_content(chunk_size=8192):
                    archivo.write(fragmento)
            print(f"Descarga completada: {nombre_archivo}")
        except requests.exceptions.RequestException as e:
            print(f"Error descargando {nombre_archivo}: {e}")

    def descargar_imagenes_concurrentes(self, consulta, cantidad = 50):
        """
        Realiza la descarga concurrente de imágenes basadas en la consulta dada.

        Parámetros:
        -----------
        consulta : str
            Palabra clave para buscar imágenes en Pixabay.
        cantidad : int, opcional
            Número de imágenes a descargar. (por defecto 50)
        """
        urls = self.obtener_urls_imagenes(consulta, cantidad)
        
        if not urls:
            print("No se encontraron imágenes para descargar.")
            return

        # Crear y lanzar un hilo para cada imagen
        hilos = []
        for i, url in enumerate(urls):
            nombre_archivo = f"imagen_{i+1}.jpg"
            hilo = threading.Thread(target=self.descargar_imagen, args=(url, nombre_archivo))
            hilos.append(hilo)
            hilo.start()

        # Esperar a que todos los hilos terminen
        for hilo in hilos:
            hilo.join()

        print("Todas las imágenes han sido descargadas.")


# Reemplaza 'TU_API_KEY' con tu clave de API de Pixabay
descargador = PixabayDownloader(api_key="PON_AQUÍ_TU_API_KEY")
# descargador = PixabayDownloader(api_key="")
descargador.descargar_imagenes_concurrentes(consulta = "perros", cantidad = 50) # Indicamos la temática de las imágenes a descargar y el número de estas.
