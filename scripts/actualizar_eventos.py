import pandas as pd
from datetime import datetime
import os
from utils.clima import obtener_clima
import json
import numpy as np

HISTORIAL_PATH = 'data/actualizaciones.json'


DATA_PATH = 'data/Datos_codificados.xlsx'

def actualizar_eventos():
    if not os.path.exists(DATA_PATH):
        print("No existe el archivo de eventos.")
        return [], []

    df = pd.read_excel(DATA_PATH)
    hoy = datetime.now().date()

    eliminados_nuevo = []     
    eventos_clima_actualizado = []
    actualizados = False  #

    for i, row in df.iterrows():
        fecha_evento = pd.to_datetime(row['FECHA']).date()

        
        if 'NUEVO' in row and fecha_evento < hoy and row['NUEVO'] == 1:
            df.at[i, 'NUEVO'] = 0
            eliminados_nuevo.append(row['TITULO'])
            actualizados = True

  
        if 0 <= (fecha_evento - hoy).days <= 7:
            temp, clima = obtener_clima(str(fecha_evento), row['HORA'], row['DISTRITO-INSTALACION'])
            try:
                df.at[i, 'Temperatura'] = float(temp)
            except (ValueError, TypeError):
                df.at[i, 'Temperatura'] = np.nan  
            df.at[i, 'Descripción del tiempo'] = clima
            eventos_clima_actualizado.append((row['TITULO'], temp, clima))
            actualizados = True
            

    df.to_excel(DATA_PATH, index=False)
    return eliminados_nuevo, eventos_clima_actualizado, actualizados



def guardar_en_historial(eliminados_nuevo, eventos_clima_actualizado):
    historial = []

    
    if os.path.exists(HISTORIAL_PATH):
        with open(HISTORIAL_PATH, 'r', encoding='utf-8') as f:
            historial = json.load(f)

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
    for titulo in eliminados_nuevo:
        historial.append({
            'tipo': 'Quitar NUEVO',
            'titulo': titulo,
            'fecha': fecha
        })

    for titulo, temp, clima in eventos_clima_actualizado:
        historial.append({
            'tipo': 'Actualizar clima',
            'titulo': titulo,
            'temperatura': temp,
            'clima': clima,
            'fecha': fecha
        })

  
    historial = historial[-50:]

    with open(HISTORIAL_PATH, 'w', encoding='utf-8') as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)



if __name__ == '__main__':
    actualizar_eventos()
