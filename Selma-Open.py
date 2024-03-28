import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

def obtener_info_selma_digital(nombre_producto):
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

        # Crear una lista para almacenar los productos
        productos = []

        # Iterar sobre los elementos y obtener los títulos y precios
        for title, price in zip(titles, prices):
            # Obtener el título y el precio y agregarlos a la lista
            titulo = title.text.strip()
            precio = price.text.strip().replace('$', '').replace(',', '').replace('.','_')  # Eliminar caracteres no numéricos del precio
            productos.append({'Título': titulo, 'Precio': float(precio)})

        return productos

    return None

def obtener_info_openfarma(nombre_producto):
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

        # Buscar los elementos que contienen el precio con la clase "promo"
        prices = soup_openfarma.find_all('span', class_='regular')

        # Crear una lista para almacenar los productos
        productos = []

        # Iterar sobre los elementos y obtener los títulos y precios
        for title, price in zip(titles, prices):
            # Obtener el título y el precio y agregarlos a la lista
            titulo = title.text.strip()
            precio = price.text.strip().replace('$', '').replace('.', '').replace(',', '.')  # Formatear el precio
            productos.append({'Título': titulo, 'Precio': float(precio)})

        return productos

    return None

def comparar_precios(productos_selma_digital, productos_openfarma):
    precios_selma_digital = {producto['Título']: producto['Precio'] for producto in productos_selma_digital}
    precios_openfarma = {producto['Título']: producto['Precio'] for producto in productos_openfarma}

    for titulo_selma, precio_selma in precios_selma_digital.items():
        for titulo_openfarma, precio_openfarma in precios_openfarma.items():
            similitud = fuzz.token_sort_ratio(titulo_selma, titulo_openfarma)
            if similitud >= 80:  # Umbral de similitud
                if precio_selma < precio_openfarma:
                    print(f'Selma Digital tiene un precio más bajo para "{titulo_selma}": ${precio_selma}')
                elif precio_selma > precio_openfarma:
                    print(f'Openfarma tiene un precio más bajo para "{titulo_openfarma}": ${precio_openfarma}')
                else:
                    print(f'Ambos tienen el mismo precio para "{titulo_selma}": ${precio_selma}')

# Nombre del producto a buscar en ambas farmacias
nombre_producto = input("Ingrese el nombre del producto a buscar: ")

# Obtener e imprimir la información de los productos de Selma Digital
productos_selma_digital = obtener_info_selma_digital(nombre_producto)
if productos_selma_digital:
    print(f'Productos encontrados en Selma Digital para "{nombre_producto}":')
    for idx, producto in enumerate(productos_selma_digital, start=1):
        print(f'#{idx} - Títulfo: {producto["Título"]}, Precio: ${producto["Precio"]}')
else:
    print(f'No se pudo obtener la información de Selma Digital para "{nombre_producto}".')

# Obtener e imprimir la información de los productos de Openfarma
productos_openfarma = obtener_info_openfarma(nombre_producto)
if productos_openfarma:
    print(f'\nProductos encontrados en Openfarma para "{nombre_producto}":')
    for idx, producto in enumerate(productos_openfarma, start=1):
        print(f'#{idx} - Título: {producto["Título"]}, Precio: ${producto["Precio"]}')
else:
    print(f'No se pudo obtener la información de Openfarma para "{nombre_producto}".')

# Comparar precios
if productos_selma_digital and productos_openfarma:
    comparar_precios(productos_selma_digital, productos_openfarma)
