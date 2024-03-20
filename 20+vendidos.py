from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import requests
from lxml import etree

def obtener_info_mercadolibre(nombre_producto):
    try:
        # URL de MercadoLibre para la primera página
        url_mercadolibre = f'https://listado.mercadolibre.com.ar/{nombre_producto}_Desde_1_NoIndex_True'

        # Configurar el WebDriver (descargar el controlador adecuado para tu navegador)
        driver = webdriver.Chrome()

        # Realizar la solicitud HTTP con Selenium
        driver.get(url_mercadolibre)

        # Esperar a que la página cargue completamente (puedes ajustar el tiempo según sea necesario)
        driver.implicitly_wait(10)

        # Buscar el elemento <label> con la clase y texto específicos (MÁS VENDIDO)
        mas_vendido_label = driver.find_element(By.XPATH, '//label[@class="ui-search-styled-label ui-search-item__highlight-label__text" and text()="MÁS VENDIDO"]')

        # Obtener el enlace del producto "MÁS VENDIDO"
        enlace_mas_vendido = mas_vendido_label.find_element(By.XPATH, '../../..//a').get_attribute('href')
        titulo_mas_vendido = mas_vendido_label.find_element(By.XPATH, '../../..//h2[@class="ui-search-item__title"]').text.strip()

        # Simular el ingreso a la URL del producto "MÁS VENDIDO"
        driver.get(enlace_mas_vendido)

        # Buscar el enlace a la página de "Más Vendidos" en la página del producto "MÁS VENDIDO"
        enlace_mas_vendidos = driver.find_element(By.XPATH, '//a[@class="ui-pdp-promotions-pill-label__target"]').get_attribute('href')

        # Simular el ingreso a la página de "Más Vendidos"
        driver.get(enlace_mas_vendidos)
        
        # Buscar todos los elementos <a> que contienen información sobre productos más vendidos
        elementos_mas_vendidos = driver.find_elements(By.XPATH, '//a[@class="ui-recommendations-card ui-recommendations-card--vertical __item"]')
        
        # Crear una lista para almacenar los títulos y enlaces de los productos más vendidos
        productos_mas_vendidos = []
        
        # Iterar sobre los elementos más vendidos y obtener títulos y enlaces
        for elemento in elementos_mas_vendidos:
            titulo_mas_vendido = elemento.text.strip()
            enlace_mas_vendido = elemento.get_attribute('href')

            #precio_mas_vendido = elemento.find_element(By.XPATH, './div[@class="ui-search-result__content-columns"]/div[@class="ui-search-result__content-column ui-search-result__content-column--left"]/div[1]/div//div[@class="ui-search-price__second-line"]//span[@class="price-tag-amount"]/span[2]').text
            #precio_mas_vendido = elemento.find_element(By.XPATH, 'ui-recommendations-card__price-and-discount .andes-money-amount__fraction').text
            # La obtención del precio puede variar, dependiendo de la estructura HTML específica
          
            precio_mas_vendido = soup_mercadolibre.find_all('span', class_='andes-money-amount__fraction')
            
            #driver.find_element(By.CSS_SELECTOR, 'span.price-tag-fraction').text
            

            
            productos_mas_vendidos.append({'Título': titulo_mas_vendido, 'Enlace': enlace_mas_vendido, 'Precio': precio_mas_vendido})
        
        return {'Título Más Vendido': titulo_mas_vendido, 'Enlace Más Vendido': enlace_mas_vendido, 'Enlace Más Vendidos': enlace_mas_vendidos, 'Productos Más Vendidos': productos_mas_vendidos}
        
    except Exception as e:
        print(f'Error: {e}')
        return None

    finally:
        # Cerrar el navegador al finalizar
        driver.quit()

# Nombre del producto a buscar
nombre_producto = 'desodorante old spice'

# Obtener e imprimir el título, enlaces del producto "MÁS VENDIDO" y lista de productos más vendidos
info_mas_vendido = obtener_info_mercadolibre(nombre_producto)
if info_mas_vendido:
    print(f'Título del producto "MÁS VENDIDO" en MercadoLibre para {nombre_producto}: {info_mas_vendido["Título Más Vendido"]}')
    print(f'Enlace del producto "MÁS VENDIDO": {info_mas_vendido["Enlace Más Vendido"]}')
    print(f'Enlace a la página "Más Vendidos" en la página del producto: {info_mas_vendido["Enlace Más Vendidos"]}')
    
    print('\nProductos Más Vendidos:') 
    for idx, producto_mas_vendido in enumerate(info_mas_vendido['Productos Más Vendidos'], start=1):
        print(f'#{idx} - Título: {producto_mas_vendido["Título"]}, Enlace: {producto_mas_vendido["Enlace"]}, Precio: {producto_mas_vendido["Precio"]}')
        #print(f'#{idx} - Título: {producto_mas_vendido["Título"]}, Enlace: {producto_mas_vendido["Enlace"]}')
else:
    print(f'No se encontró el producto "MÁS VENDIDO" en MercadoLibre para {nombre_producto}.')
