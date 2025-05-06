#!apt-get update -qq
#!apt-get install -y -qq chromium-browser chromium-chromedriver

#!apt-get update -qq > /dev/null
#!apt-get install -y wget unzip > /dev/null
#!wget -q https://storage.googleapis.com/chrome-for-testing-public/114.0.5735.90/linux64/chrome-linux64.zip
#!wget -q https://storage.googleapis.com/chrome-for-testing-public/114.0.5735.90/linux64/chromedriver-linux64.zip
#!unzip -q chrome-linux64.zip
#!unzip -q chromedriver-linux64.zip
#!mv chrome-linux64 /opt/chrome
#!mv chromedriver-linux64/chromedriver /usr/bin/chromedriver
#!chmod +x /usr/bin/chromedriver
#!pip install -q selenium webdriver-manager

#!cp /usr/lib/chromium-browser/chromedriver /usr/bin

#!pip install beautifulsoup4 pandas selenium webdriver_manager

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Setup Selenium WebDriver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()

options.binary_location = "/opt/chrome/chrome"
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=service, options=options)

# URL de la página a scrapear
driver.get("https://www.falabella.com/falabella-cl/category/cat70057/Notebooks")
# Tiempo para que cargue la página
time.sleep(10)

productos_data = []
productos_deseados = 1150
productos_capturados = 0
pagina_actual = 1

try:
    while productos_capturados < productos_deseados:
        print(f"Scrapeando la página {pagina_actual}...")
        
        # Esperar a que los productos se carguen
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'search-results-') and contains(@class, 'grid-pod')]"))
        )
        
        product_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'search-results-') and contains(@class, 'grid-pod')]")
        print(f"Encontrados {len(product_containers)} productos en la página {pagina_actual}")

        for container in product_containers:
            if productos_capturados >= productos_deseados:
                break
            try:
                nombre_elemento = container.find_element(By.XPATH, ".//b[contains(@class, 'pod-subTitle')]")
                nombre = nombre_elemento.text

                precio_descuento_elemento = container.find_elements(By.XPATH, ".//div[@id[contains(., 'prices-')]]/ol/li[1]/div/span[contains(@class, 'high')]")
                precio_descuento = precio_descuento_elemento[0].text if precio_descuento_elemento else "no encontrado"

                precio_internet_elemento = container.find_elements(By.XPATH, ".//div[@id[contains(., 'prices-')]]/ol/li[2]/div/span[contains(@class, 'medium')]")
                precio_internet = precio_internet_elemento[0].text if precio_internet_elemento else "no encontrado"

                precio_anterior_elemento = container.find_elements(By.XPATH, ".//div[@id[contains(., 'prices-')]]/ol/li[3]/div/span[contains(@class, 'septenary') or contains(@class, 'crossed')]")
                precio_anterior = precio_anterior_elemento[0].text if precio_anterior_elemento else "no encontrado"

                productos_data.append({
                    'Producto': nombre,
                    'Precio Descuento': precio_descuento,
                    'Precio Internet': precio_internet,
                    'Precio Anterior': precio_anterior
                })
                productos_capturados += 1
                print(f"Producto {productos_capturados}/{productos_deseados} capturado: {nombre[:30]}...")
            except Exception as e:
                print(f"Error al procesar un producto: {e}")

        if productos_capturados >= productos_deseados:
            break

        pagina_actual += 1
        
        # Intentamos múltiples formas de hacer clic en el botón de siguiente página
        try:
            print("Intentando hacer clic en el botón de siguiente página...")           # Método 4: JavaScript executor como último recurso
            try:
                driver.execute_script("document.getElementById('testId-pagination-top-arrow-right').click();")
                print("Método 4 (JavaScript) exitoso")
                time.sleep(5)
                continue
            except Exception as e:
                print(f"Método 4 falló: {e}")
                
            # Si llegamos aquí, no pudimos navegar a la siguiente página
            print("No se pudo navegar a la siguiente página después de varios intentos.")
            break
            
        except Exception as e:
            print(f"Error general al intentar navegar a la siguiente página: {e}")
            break

except Exception as e:
    print(f"Error general en el script: {e}")

finally:
    # Guardar los resultados incluso si hay errores
    df = pd.DataFrame(productos_data)
    print(f"Total de productos capturados: {len(productos_data)}")
    print(df.head(10).to_string())  # Muestra solo las primeras 10 filas para verificar
    
    # Guardar los datos en un CSV
    df.to_csv('productos_falabella.csv', index=False)
    print("Datos guardados en 'productos_falabella.csv'")
    
    # Cerrar el navegador
    driver.quit()