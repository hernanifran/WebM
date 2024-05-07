import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

from selenium import webdriver
from selenium.webdriver.common.by import By
from operator import itemgetter

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#funcion para consultar en la pagina de farmacity
def obtener_info_farmacity(nombre_producto, umbral_similitud=60):
    # Inicializa el navegador Chrome
    driver = webdriver.Chrome()

    # Abre la URL de Farmacity usando un f-string para insertar el nombre del producto
    url = f"https://www.farmacity.com/{nombre_producto}?_q={nombre_producto}&map=ft"
    driver.get(url)
    
    # Encuentra los elementos que contienen el título de los productos
    titles = driver.find_elements(By.XPATH, '//span[@class="vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body"]')

    # Encuentra los elementos que contienen el precio de los productos
    prices = driver.find_elements(By.XPATH, '//span[@class="vtex-product-price-1-x-currencyContainer"]')
       
    # Crear un conjunto para almacenar los títulos y precios únicos
    productos_set = set()
    
    # Iterar sobre los elementos y obtener los títulos y precios
    for title, price in zip(titles, prices):
        # Obtener el título y el precio y agregarlos a la lista
        titulo = title.text.strip()
        precio = price.text.strip().replace('$', '').replace('.', '').replace(',', '.')  # Formatear el precio
        productos_set.add((titulo, float(precio)))

    
    # Cierra el navegador
    driver.quit()
    
    # Convertir el conjunto a una lista y ordenarla por título
    productos = [{'Título': titulo, 'Precio': precio} for titulo, precio in sorted(productos_set, key=lambda x: x[0])]
    
    # Calcular la similitud entre el nombre del producto consultado y los nombres de los productos encontrados
    productos_similares = []
    for producto in productos:
        similitud = fuzz.token_sort_ratio(nombre_producto.lower(), producto['Título'].lower())
        if similitud >= umbral_similitud:
            producto['Similitud'] = similitud
            productos_similares.append(producto)
    
    return productos_similares


# Función para obtener la información de un producto en la página de Selma Digital
def obtener_info_selma_digital(nombre_producto, umbral_similitud=60):
    # URL de Selma Digital
    url_selma_digital = f'https://selmadigital.com/shop?search={nombre_producto}'

    # Realizar la solicitud HTTP
    response_selma_digital = requests.get(url_selma_digital)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response_selma_digital.status_code == 200:
        # Parsear el contenido HTML con BeautifulSoup
        soup_selma_digital = BeautifulSoup(response_selma_digital.content, 'html.parser')

        # Buscar los elementos que contienen el título con la clase "product-card-design8-vertical__name"
        titles = soup_selma_digital.find_all('div', class_='product-card-design8-vertical__name')

        # Buscar los elementos que contienen el precio con la clase "product-card-design8-vertical__price"
        prices = soup_selma_digital.find_all('div', class_='product-card-design8-vertical__price')
        
        # Crear un conjunto para almacenar los títulos y precios únicos
        productos_set = set()

        # Iterar sobre los elementos y obtener los títulos y precios
        for title, price in zip(titles, prices):
            # Obtener el título y el precio y agregarlos a la lista
            titulo = title.text.strip()
            precio = price.text.strip().replace('$', '').replace('.', '').replace(',', '.')#price.text.strip().replace('$', '').replace(',', '')  # Eliminar caracteres no numéricos del precio
            productos_set.add((titulo, float(precio)))

        # Convertir el conjunto a una lista y ordenarla por título
        productos = [{'Título': titulo, 'Precio': precio} for titulo, precio in sorted(productos_set, key=lambda x: x[0])]
        
        # Calcular la similitud entre el nombre del producto consultado y los nombres de los productos encontrados
        productos_similares = []
        for producto in productos:
            similitud = fuzz.token_sort_ratio(nombre_producto.lower(), producto['Título'].lower())
            if similitud >= umbral_similitud:
                producto['Similitud'] = similitud
                productos_similares.append(producto)
        
        return productos_similares

    return None


#funcion para consultar en la pagina de openfarma
def obtener_info_openfarma(nombre_producto, umbral_similitud=60):
    # URL de Openfarma
    url_openfarma = f'https://www.openfarma.com.ar/products?utf8=%E2%9C%93&keywords={nombre_producto}'

    # Realizar la solicitud HTTP
    response_openfarma = requests.get(url_openfarma)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response_openfarma.status_code == 200:
        # Parsear el contenido HTML con BeautifulSoup
        soup_openfarma = BeautifulSoup(response_openfarma.content, 'html.parser')

        # Buscar los elementos que contienen el título con la clase "card-title"
        titles = soup_openfarma.find_all('h2', class_='card-title')

        # Buscar los elementos que contienen el precio con la clase "regular"
        prices_regular = soup_openfarma.find_all('span', class_='regular')
        
        # Buscar los elementos que contienen el precio con la clase "promo"
        prices_promo = soup_openfarma.find_all('span', class_='promo')
        
        prices = prices_regular
        
        if len(prices_promo) > 0:
            prices = prices_promo
    

         # Crear una lista para almacenar los productos
        productos_set = set()

        # Iterar sobre los elementos y obtener los títulos y precios
        for title, price in zip(titles, prices):
            # Obtener el título y el precio y agregarlos a la lista
            titulo = title.text.strip()
            precio = price.text.strip().replace('$', '').replace('.', '').replace(',', '.')  # Formatear el precio
            productos_set.add((titulo, float(precio)))

        # Convertir el conjunto a una lista y ordenarla por título
        productos = [{'Título': titulo, 'Precio': precio} for titulo, precio in sorted(productos_set, key=lambda x: x[0])]
        
        # Calcular la similitud entre el nombre del producto consultado y los nombres de los productos encontrados
        productos_similares = []
        for producto in productos:
            similitud = fuzz.token_sort_ratio(nombre_producto.lower(), producto['Título'].lower())
            if similitud >= umbral_similitud:
                producto['Similitud'] = similitud
                productos_similares.append(producto)
        
        return productos_similares

    return None

# funcion comparacion 3 paginas
def comparar_precios_3_paginas_4(productos_selma_digital, productos_openfarma, productos_farmacity, umbral=60):
    todos_productos = []

    # Agregar productos de Selma Digital
    for producto in productos_selma_digital:
        todos_productos.append({'pagina': 'Selma Digital', 'titulo': producto['Título'], 'precio': producto['Precio']})

    # Agregar productos de Openfarma
    for producto in productos_openfarma:
        todos_productos.append({'pagina': 'Openfarma', 'titulo': producto['Título'], 'precio': producto['Precio']})

    # Agregar productos de Farmacity
    for producto in productos_farmacity:
        todos_productos.append({'pagina': 'Farmacity', 'titulo': producto['Título'], 'precio': producto['Precio']})

    # Ordenar productos por precio de forma ascendente
    todos_productos.sort(key=itemgetter('precio'))

    # Tomar los primeros 10 productos
    top_10_productos = todos_productos[:10]

    # Crear la lista de resultados
    resultados = ["Comparación de precios entre las tres páginas (Selma Digital, Openfarma y Farmacity):"]
    
    for i, producto in enumerate(top_10_productos, start=1):
        resultados.append(f"{i}. {producto['pagina']} tiene el producto '{producto['titulo']}' a ${producto['precio']}")

    return resultados

def enviar_correo(productos, destinatario):
    # Cargar las variables de entorno desde el archivo .env
    load_dotenv()

    # Configurar los detalles del servidor SMTP
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    ## Realizar la comparación de precios
    #resultados = comparar_precios_3_paginas_4(productos)

    # Crear el mensaje de correo electrónico
    mensaje = MIMEMultipart()
    mensaje['From'] = smtp_username
    mensaje['To'] = destinatario
    mensaje['Subject'] = 'Consulta de producto'

    # Cuerpo del correo electrónico
    cuerpo = """
    Hola,

    Estoy interesado en obtener más información sobre el producto que ofrecen. ¿Podrían proporcionarme detalles adicionales?

    A continuación, te presento una comparación de precios entre varias tiendas:

    {}
    ¡Gracias!
    """.format('\n'.join(productos))

    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Conectar al servidor SMTP y enviar el correo electrónico
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Iniciar conexión TLS (segura)
        server.login(smtp_username, smtp_password)
        texto_completo = mensaje.as_string()
        server.sendmail(smtp_username, destinatario, texto_completo)
        print('Correo electrónico enviado correctamente.')
        
        
# Función para realizar una consulta de web scraping y recopilar datos
def ejecutar_consulta(nombre_producto):
    
    
    # Obtener e imprimir la información de los productos de Selma Digital
    productos_selma_digital = obtener_info_selma_digital(nombre_producto)
    
    # Obtener e imprimir la información de los productos de Openfarma
    productos_openfarma = obtener_info_openfarma(nombre_producto)
    
    # Obtener e imprimir la información de los productos de Farmacity
    productos_farmacity = obtener_info_farmacity(nombre_producto)
    
    # Realizar la consulta de web scraping y recopilar datos
    resultados = comparar_precios_3_paginas_4(productos_selma_digital, productos_openfarma, productos_farmacity)
    return resultados


# Lista para almacenar los resultados acumulados de todas las consultas realizadas durante el día
resultados_acumulados = []
resultados2_acumulados = []


# Bucle principal para ejecutar el proceso diariamente
while True:
    # Obtener la hora actual del sistema
    hora_actual = datetime.now().time()
    
    print('inicio',hora_actual)
    
    # Realizar la consulta y recopilar datos
    resultados = ejecutar_consulta('Shampoo Aclarante Jalea Real')

    # Agregar los resultados de la consulta actual a la lista de resultados acumulados
    resultados_acumulados.append(resultados)
    
    # Realizar la consulta y recopilar datos
    resultados2 = ejecutar_consulta('Crema De Manos Antimanchas Eucerin Anti Pigment X 75 Ml')

    # Agregar los resultados de la consulta actual a la lista de resultados acumulados
    resultados2_acumulados.append(resultados2)

    # Esperar un período de tiempo antes de la próxima consulta (por ejemplo, cada hora)
    time.sleep(60*60)  # Esperar 1 hora antes de la próxima consulta 60*60, por prueba se hace cada 2 minuto
    
    # Obtener la hora de envío del correo electrónico (por ejemplo, 8:00 PM)
    hora_envio_correo = datetime.strptime("20:00", "%H:%M").time()
    
    print('hora de envio corre electronico', hora_envio_correo)

    # Verificar si es hora de enviar el correo electrónico diario (por ejemplo, al final del día)
    if hora_actual >= hora_envio_correo:
                
        # Convertir la lista de listas en una lista plana de cadenas
        productos = [item for sublist in resultados_acumulados for item in sublist]

        # Llamar a la función enviar_correo con la lista de productos combinada
        enviar_correo(productos, 'jose-5k4766@hotmail.com')

        # Reiniciar la lista de resultados acumulados para el próximo día
        resultados_acumulados = []
        resultados2_acumulados = []