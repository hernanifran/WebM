import requests
from bs4 import BeautifulSoup

def obtener_info_mercadolibre(nombre_producto):
    # URL de MercadoLibre
    url_mercadolibre = f'https://listado.mercadolibre.com.ar/{nombre_producto}'

    # Realizar la solicitud HTTP con headers simulando un navegador
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response_mercadolibre = requests.get(url_mercadolibre, headers=headers)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response_mercadolibre.status_code == 200:
        # Parsear el contenido HTML con BeautifulSoup
        soup_mercadolibre = BeautifulSoup(response_mercadolibre.content, 'html.parser')

        # Buscar los elementos que contienen el título con la clase "ui-search-item__title"
        titles = soup_mercadolibre.find_all('h2', class_='ui-search-item__title')

         # Buscar los elementos que contienen el precio con la clase "andes-money-amount__fraction"
        #prices = soup_mercadolibre.find_all('span', class_='andes-money-amount__fraction')
        prices = soup_mercadolibre.find_all('div', class_='ui-search-price__second-line')

        # Buscar los elementos que contienen el enlace con la clase "ui-search-link__title-card"
        links = soup_mercadolibre.find_all('a', class_='ui-search-link__title-card')

        # Crear una lista para almacenar los títulos de los productos
        productos = []

         # Iterar sobre los elementos y obtener los títulos, precios y enlaces
        for title, price, link in zip(titles, prices, links):
            # Obtener el título, el precio y el enlace y agregarlos a la lista
            titulo = title.text.strip()
            precio = price.text.strip()
            #precio = price.text.strip().replace('.', '').replace(',', '.')
            enlace = link['href']
            productos.append({'Título': titulo, 'Precio': precio, 'Enlace': enlace})
            
        return productos

    return None

# Nombre del producto a buscar
nombre_producto = 'cafe-molido'

# Obtener e imprimir la información de los títulos de MercadoLibre
titulos_mercadolibre = obtener_info_mercadolibre(nombre_producto)
if titulos_mercadolibre:
    print(f'Títulos de los productos encontrados en MercadoLibre para {nombre_producto}:')
    for idx, producto in enumerate(titulos_mercadolibre, start=1):
    #for idx, titulo in enumerate(titulos_mercadolibre, start=1):
        print(f'#{idx} - Título: {producto["Título"]}, Precio: {producto["Precio"]}, Enlace: {producto["Enlace"]}')
        #print(f'#{idx} - Título: {titulo}')
else:
    print('No se pudo obtener la información de MercadoLibre.')

