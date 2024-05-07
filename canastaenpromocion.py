import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
import smtplib
from fuzzywuzzy import fuzz

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from selenium import webdriver
from selenium.webdriver.common.by import By
from operator import itemgetter

# Lista de productos de interés
productos_interesantes = ["kit serum", "suplmento dietario", "desodorante"]

def obtener_imperdibles_openfarma():
    # URL de Openfarma
    url_openfarma = f'https://www.openfarma.com.ar/'
    
    # Realizar la solicitud HTTP
    response_openfarma = requests.get(url_openfarma)    
    
    # Verificar si la solicitud fue exitosa (código de estado 200)'
    if response_openfarma.status_code == 200:
        # Parsear el contenido HTML con BeautifulSoup
        soup_openfarma = BeautifulSoup(response_openfarma.content, 'html.parser')
        
        # Buscar los elementos que contienen el título con la clase "card-title font-1-1 title-xsm black-65"
        titles = soup_openfarma.find_all('h2', attrs={'class':'card-title font-1-1 title-xsm black-65'})

        # Buscar los elementos que contienen el precio con la clase "promo dis-inblk"
        prices = soup_openfarma.find_all('span', attrs={'class':'promo dis-inblk'})
        
        # Crear una lista para almacenar los productos
        productos = []

        # Iterar sobre los elementos y obtener los títulos y precios
        for title, price in zip(titles, prices):
            # Obtener el título y el precio y agregarlos a la lista
            titulo = title.text.strip()
            precio = float(price.text.strip().replace('$', '').replace('.', '').replace(',', '.'))  # Formatear el precio
            productos.append({'Título': titulo, 'Precio': precio})

        return productos

def obtener_mejores_promos_farmacity():
    # URL de Farmacity
    url_farmacity = f'https://www.farmacity.com/2330?map=productClusterIds&order=OrderByBestDiscountDESC'

    # Inicializa el navegador Chrome
    driver = webdriver.Chrome()

    driver.get(url_farmacity)

    # Encuentra los elementos que contienen el título de los productos
    titles = driver.find_elements(By.XPATH, '//span[@class="vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body"]')

    # Encuentra los elementos que contienen el precio de los productos
    prices = driver.find_elements(By.XPATH, '//span[@class="vtex-product-price-1-x-currencyContainer"]')

    # Lista para almacenar los productos como diccionarios
    productos_list = []

    # Iterar sobre los elementos y obtener los títulos y precios
    for title, price in zip(titles, prices):
        # Obtener el título y el precio y agregarlos a la lista como un diccionario
        producto = {
            'Título': title.text.strip(),
            'Precio': float(price.text.strip().replace('$', '').replace('.', '').replace(',', ''))  # Formatear el precio
        }
        productos_list.append(producto)

    # Cierra el navegador
    driver.quit()

    return productos_list

# Función para obtener la información de un producto en la página de Selma Digital
def obtener_info_selma_digital():
    # URL de Selma
    url_selma = f'https://selmadigital.com/'
    
    # Realizar la solicitud HTTP
    response_selma_digital = requests.get(url_selma)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response_selma_digital.status_code == 200:
        # Parsear el contenido HTML con BeautifulSoup
        soup_selma_digital = BeautifulSoup(response_selma_digital.content, 'html.parser')

        # Buscar los elementos que contienen el título con la clase "product-card-design8-vertical__name"
        titles = soup_selma_digital.find_all('div', class_='product-card-design8-vertical__name')

        # Buscar los elementos que contienen el precio con la clase "product-card-design8-vertical__price"
        prices = soup_selma_digital.find_all('div', class_='product-card-design8-vertical__price')
        
        # Lista para almacenar los productos como diccionarios
        productos = []

        # Iterar sobre los elementos y obtener los títulos y precios
        for title, price in zip(titles, prices):
            # Obtener el título y el precio
            titulo = title.text.strip()
            precio = price.text.strip().replace('$', '').replace('.', '').replace(',', '')  # Eliminar caracteres no numéricos del precio
            
            # Agregar el producto como un diccionario a la lista de productos
            productos.append({'Título': titulo, 'Precio': float(precio)})

    return productos

def enviar_mail(productos, tienda):
    # Cargar las variables de entorno desde el archivo .env
    load_dotenv()
    
    # Configurar los detalles del servidor SMTP
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    sender = smtp_username
    recipient = "jevaldescastro@mail.austral.edu.ar"

    email = EmailMessage()
    email["From"] = sender
    email["To"] = recipient
    email["Subject"] = f"Productos en promoción de {tienda}"
    
    message = ""
    if productos:
        for idx, producto in enumerate(productos, start=1):
            message += f'#{idx} - Título: {producto["Título"]}, Precio: ${producto["Precio"]}\n'

        # Verificar si hay productos de interés que no estén en la lista de productos en promoción
        for producto_interesante in productos_interesantes:
            encontrado = False
            for producto in productos:
                if fuzz.ratio(producto_interesante.lower(), producto["Título"].lower()) > 60:
                    encontrado = True
                    break
            if not encontrado:
                message += f"No encontramos '{producto_interesante}' en promoción. Quizás la próxima tengas más suerte.\n"
    
    email.set_content(message)

    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(sender, smtp_password)
    smtp.sendmail(sender, recipient, email.as_string())
    smtp.quit()

def buscar_canasta_productos():
    productos_openfarma = obtener_imperdibles_openfarma()
    enviar_mail(productos_openfarma, "Openfarma")
    
    productos_farmacity = obtener_mejores_promos_farmacity()
    enviar_mail(productos_farmacity, "Farmacity")
    
    productos_selma = obtener_info_selma_digital()
    enviar_mail(productos_selma, "Selma")

buscar_canasta_productos()
