import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

from email.message import EmailMessage
import smtplib

def obtener_imperdibles_openfarma():
    
    # URL de Openfarma
    url_openfarma = f'https://www.openfarma.com.ar/'
    
    # Realizar la solicitud HTTP
    response_openfarma = requests.get(url_openfarma)    
    
    # Verificar si la solicitud fue exitosa (código de estado 200)
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
            precio = price.text.strip().replace('$', '').replace('.', '').replace(',', '.')  # Formatear el precio
            productos.append({'Título': titulo, 'Precio': float(precio)})

        return productos

def obtener_mejores_promos_farmacity():
    
    # URL de Farmacity
    url_farmacity = f'https://www.farmacity.com/2330?map=productClusterIds&order=OrderByBestDiscountDESC'
    
    # Realizar la solicitud HTTP
    response_farmacity = requests.get(url_farmacity)
    
    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response_farmacity.status_code == 200:
        # Parsear el contenido HTML con BeautifulSoup
        soup_farmacity = BeautifulSoup(response_farmacity.content, 'html.parser')
        
        # Buscar los elementos que contienen el título con la clase "vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body"
        titles = soup_farmacity.find_all('span', attrs={'class':'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'})
        print(titles)
        # Buscar los elementos que contienen el precio con la clase "vtex-product-price-1-x-currencyContainer"
        prices = soup_farmacity.find_all('span', attrs={'class':'vtex-product-price-1-x-currencyContainer'})
        print(prices)
        
         # Crear una lista para almacenar los productos
        productos = []

        # Iterar sobre los elementos y obtener los títulos y precios
        for title, price in zip(titles, prices):
            # Obtener el título y el precio y agregarlos a la lista
            titulo = title.text.strip()
            precio = price.text.strip().replace('$', '').replace('.', '').replace(',', '.')  # Formatear el precio
            productos.append({'Título': titulo, 'Precio': float(precio)})

        return productos

def enviar_mail_openfarma():
    
    # Obtener y enviar la información de los productos de Openfarma
    productos_openfarma = obtener_imperdibles_openfarma()
    if productos_openfarma:
        message = ""
        for idx, producto in enumerate(productos_openfarma, start=1):
            message = message + f'#{idx} - Título: {producto["Título"]}, Precio: ${producto["Precio"]}\n'

    # Enviar mail con ofertas

    sender = "scanossini@mail.austral.edu.ar"
    recipient = "stefano_canossini@hotmail.com"

    email = EmailMessage()
    email["From"] = sender
    email["To"] = recipient
    email["Subject"] = "Precios imperdibles de Openfarma"
    email.set_content(message)

    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    smtp.login(sender, "Mcdgrupo3.")
    smtp.sendmail(sender, recipient, email.as_string())
    smtp.quit()

def enviar_mail_farmacity():
    
    # Obtener y enviar la información de los productos de Farmacity
    productos_farmacity = obtener_mejores_promos_farmacity()
    message = ""
    if productos_farmacity:       
        for idx, producto in enumerate(productos_farmacity, start=1):
            message = message + f'#{idx} - Título: {producto["Título"]}, Precio: ${producto["Precio"]}\n'

    # Enviar mail con ofertas

    sender = "scanossini@mail.austral.edu.ar"
    recipient = "stefano_canossini@hotmail.com"

    email = EmailMessage()
    email["From"] = sender
    email["To"] = recipient
    email["Subject"] = "Mejores 2x1 de Farmacity"
    email.set_content(message)

    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    smtp.login(sender, "Mcdgrupo3.")
    smtp.sendmail(sender, recipient, email.as_string())
    smtp.quit()

enviar_mail_farmacity()
enviar_mail_openfarma()