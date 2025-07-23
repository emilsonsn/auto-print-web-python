import os
import csv
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import schedule

def tirar_prints():
    hoje = datetime.now().strftime('%d-%m-%Y')  # Formato BR
    pasta_dia = os.path.join("prints", hoje)
    os.makedirs(pasta_dia, exist_ok=True)

    with open('sites.csv') as f:
        reader = csv.DictReader(f)
        sites = list(reader)

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)

    for site in sites:
        nome, url = site["name"], site["url"]
        print(f"-- Tirando print de {nome}")
        try:
            driver.get(url)
            time.sleep(5)
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(1920, total_height)
            time.sleep(2)
            path = os.path.join(pasta_dia, f"{nome}.png")
            driver.save_screenshot(path)
            print(f"-- Screenshot salva: {path}")

            if "atualizalitoral" in url:
                href = driver.execute_script("""
                    const el = document.querySelector('h1 a, h2 a');
                    return el ? el.href : null;
                """)
                if href:
                    driver.get(href)
                    time.sleep(5)
                    total_height = driver.execute_script("return document.body.scrollHeight")
                    driver.set_window_size(1920, total_height)
                    time.sleep(2)
                    internal_path = os.path.join(pasta_dia, f"{nome}-interno.png")
                    driver.save_screenshot(internal_path)
                    print(f"-- Screenshot interno salva: {internal_path}")
                else:
                    print(f"-- Nenhum link encontrado na home de {nome}")
        except Exception as e:
            print(f"Erro no site {url}: {e}")
    print("-- Execução concluída!")
    print("-- Próxima execução amanhã")
    driver.quit()

def agendar_disparo():
    with open('config.json') as f:
        config = json.load(f)
        hora = config.get('schedule_time', '08:00')
    schedule.every().day.at(hora).do(tirar_prints)
    print(f"-- Agendado para {hora} todos os dias")

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    agendar_disparo()
