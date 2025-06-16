
import sys
import pandas as pd
from werkzeug.datastructures import MultiDict


sys.path.append(".")

from main import obtener_eventos_filtrados


# -------------------- Test 1 --------------------
print("\n🔎 TEST 1: Búsqueda simple — Gratuitos, mañana, temática 'Cultura'\n")


form_data_1 = MultiDict({
    'gratuito': 'Sí',
    'hora_min': '10',
    'hora_max': '14',
    'tematicas': ['Cultura'],
    'distritos': ['Centro', 'Retiro', 'Arganzuela', 'Latina', 'Carabanchel'],
    'modo_tematica': 'OR',
    'tipo_similitud': 'trapezoidal'
})

# -------------------- Test 2 --------------------
print("\n🔎 TEST 2: Eventos de pago — Tarde, múltiples temáticas, similitud gaussiana\n")

form_data_2 = MultiDict({
    'gratuito': 'No',
    'precio_min': '5',
    'precio_max': '50',
    'hora_min': '16',
    'hora_max': '21',
    'tematicas': ['Cultura', 'Música', 'Teatro'],
    'distritos': ['Centro', 'Salamanca', 'Chamberí', 'Tetuán'],
    'modo_tematica': 'OR',
    'tipo_similitud': 'gaussiana',
    'peso_precio': '0.4',
    'peso_hora': '0.6'
}) 


# -------------------- Test 3 --------------------
print("\n\n🔍 Test 3: Filtro estricto por múltiples temáticas (modo AND)")

form_data_3 = MultiDict({
    'gratuito': 'Sí',
    'hora_min': '10',
    'hora_max': '20',
    'tematicas': ['Cultura', 'Historia', 'Teatro'],
    'distritos': ['Centro', 'Salamanca', 'Retiro'],
    'modo_tematica': 'AND',
    'tipo_similitud': 'trapezoidal'
})

# -------------------- Test 4 --------------------
print("\n\n🔍 Test 4: Evento de pago con pesos personalizados (60% precio, 40% hora)")

form_data_4 = MultiDict({
    'gratuito': 'No',
    'precio_min': '10',
    'precio_max': '50',
    'hora_min': '16',
    'hora_max': '20',
    'peso_precio': '0.6',
    'peso_hora': '0.4',
    'tematicas': ['Música', 'Teatro'],
    'distritos': ['Chamartín', 'Salamanca'],
    'modo_tematica': 'OR',
    'tipo_similitud': 'gaussiana'
})

# -------------------- Test 5 --------------------
print("\n\n🌐 Test 5: Búsqueda generalista con múltiples distritos y temáticas (modo OR)")

form_data_5 = MultiDict({
    'gratuito': 'Sí',
    'hora_min': '10',
    'hora_max': '22',
    'tematicas': ['Música', 'Teatro', 'Arte', 'Cultura', 'Cine'],
    'distritos': ['Centro', 'Arganzuela', 'Latina', 'Retiro', 'Tetuán'],
    'modo_tematica': 'OR',
    'tipo_similitud': 'trapezoidal'  
})

# -------------------- Test 6 --------------------
print("\n\n🔎 Test 6: Filtro estricto con múltiples temáticas (modo AND)")

form_data_6 = MultiDict({
    'gratuito': 'Sí',
    'hora_min': '12',
    'hora_max': '20',
    'tematicas': ['Arte', 'Cultura', 'Historia'],
    'distritos': ['Centro', 'Salamanca', 'Retiro'],
    'modo_tematica': 'AND',
    'tipo_similitud': 'trapezoidal'
})

# -------------------- Test 7 --------------------
print("\n\n💸 Test 7: Eventos de pago con pesos personalizados y método gaussiano")

form_data_7 = MultiDict({
    'gratuito': 'No',
    'precio_min': '10',
    'precio_max': '50',
    'hora_min': '18',
    'hora_max': '22',
    'peso_precio': '0.7',
    'peso_hora': '0.3',
    'tematicas': ['Música'],
    'distritos': ['Arganzuela', 'Chamartín'],
    'modo_tematica': 'OR',
    'tipo_similitud': 'gaussiana'
})

# -------------------- Test 8 --------------------
print("\n\n🏙️ Test 8: Búsqueda en distritos con baja densidad de eventos")

form_data_8 = MultiDict({
    'gratuito': 'Sí',
    'precio_min': '0',
    'precio_max': '0',
    'hora_min': '10',
    'hora_max': '13',
    'tematicas': ['Educación', 'Tecnología'],
    'distritos': ['Barajas', 'Chamberí'],
    'modo_tematica': 'OR',
    'tipo_similitud': 'trapezoidal'
})

# -------------------- Test 9 --------------------
print("\n\n🔍 Test 9: Búsqueda sin temáticas seleccionadas")

form_data_9 = MultiDict({
    'gratuito': 'No',
    'precio_min': '5',
    'precio_max': '25',
    'hora_min': '16',
    'hora_max': '20',
    'tematicas': [],  
    'distritos': ['Centro', 'Retiro'],
    'modo_tematica': 'OR',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})

# -------------------- Test 10 --------------------
print("\n\n🔍 Test 10: Búsqueda sin distritos seleccionados")

form_data_10 = MultiDict({
    'gratuito': 'No',
    'precio_min': '10',
    'precio_max': '30',
    'hora_min': '17',
    'hora_max': '21',
    'tematicas': ['Teatro', 'Cultura'],
    'distritos': [],  # Sin distritos
    'modo_tematica': 'OR',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.3',
    'peso_hora': '0.7'
})

# -------------------- Test 11A: Comparativa algoritmo--------------------
print("\n\n⚖️ Test 11A: Similitud trapezoidal (Música, Centro/Retiro, 50/50)")

form_data_11a = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '40',
    'hora_min': '10',
    'hora_max': '14',
    'tematicas': ['Música'],
    'distritos': ['Centro', 'Retiro'],
    'modo_tematica': 'OR',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})

# -------------------- Test 11B: Comparativa algoritmo --------------------
print("\n\n⚖️ Test 11B: Similitud gaussiana (Música, Centro/Retiro, 50/50)")

form_data_11b = MultiDict(form_data_11a.copy())
form_data_11b['tipo_similitud'] = 'gaussiana'

# -------------------- Test 12A: Comparativa algoritmo --------------------

print("\n\n⚖️ Test 12A: Similitud trapezoidal (Teatro, 08h–22h, 50/50)")

form_data_12a = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '40',
    'hora_min': '8',
    'hora_max': '22',
    'tematicas': ['Teatro'],
    'distritos': [],
    'modo_tematica': 'OR',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})


# -------------------- Test 12B: Comparativa algoritmo --------------------
print("\n\n⚖️ Test 12B: Similitud gaussiana (Teatro, 08h–22h, 50/50)")

form_data_12b = MultiDict(form_data_12a.copy())
form_data_12b['tipo_similitud'] = 'gaussiana'


# -------------------- Test 13A: Comparativa algoritmo --------------------
print("\n\n⚖️ Test 13A: Similitud trapezoidal (Cultura, 18h–19h, 50/50)")

form_data_13a = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '40',
    'hora_min': '18',
    'hora_max': '19',
    'tematicas': ['Cultura'],
    'distritos': [],
    'modo_tematica': 'OR',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})

# -------------------- Test 13B: Comparativa algoritmo --------------------

print("\n\n⚖️ Test 13B: Similitud gaussiana (Cultura, 18h–19h, 50/50)")

form_data_13b = MultiDict(form_data_13a.copy())
form_data_13b['tipo_similitud'] = 'gaussiana'

# -------------------- Test 14A: Comparativa algoritmo --------------------
print("\n\n⚖️ Test 14A: Trapezoidal (hora 90%, precio 10%) — Música entre 20:00 y 22:00")

form_data_14a = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '40',
    'hora_min': '20',
    'hora_max': '22',
    'tematicas': ['Música'],
    'distritos': [],
    'modo_tematica': 'OR',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.1',
    'peso_hora': '0.9'
})

# -------------------- Test 14B: Comparativa algoritmo --------------------
print("\n\n⚖️ Test 14B: Gaussiana (hora 90%, precio 10%) — Música entre 20:00 y 22:00")

form_data_14b = MultiDict(form_data_14a.copy())
form_data_14b['tipo_similitud'] = 'gaussiana'

# -------------------- Test 15: Restrictivo  --------------------

print("\n\n🧪 Test 15: Filtro estricto — Gratuito, temática única 'Flamenco', solo a las 19:00")

form_data_15 = MultiDict({
    'gratuito': 'Sí',
    'precio_min': '0',
    'precio_max': '0',
    'hora_min': '19',
    'hora_max': '19',
    'tematicas': ['Flamenco'],
    'distritos': [],
    'modo_tematica': 'AND',
    'tipo_similitud': 'trapezoidal',
})

# -------------------- Test 16: Restrictivo --------------------
print("\n\n🎯 Test 16: Filtro muy restrictivo - Cine en Barajas, 21:00h, precio 0–5€")

form_data_16 = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '5',
    'hora_min': '21',
    'hora_max': '21',
    'tematicas': ['Cine'],
    'distritos': ['Barajas'],
    'modo_tematica': 'AND',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})

# -------------------- Test 17 --------------------
print("\n\n🎯 Test 17: Educación + Tecnología en Vicálvaro, 11h–13h, precio 0–5€")

form_data_17 = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '5',
    'hora_min': '11',
    'hora_max': '13',
    'tematicas': ['Educación', 'Tecnología'],
    'distritos': ['Vicálvaro'],
    'modo_tematica': 'AND',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})


# -------------------- Test 18 --------------------
print("\n\n🎯 Test 18: Sin hora mínima€")

form_data_18 = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '5',
    'hora_min': '',
    'hora_max': '13',
    'tematicas': ['Educación', 'Tecnología'],
    'distritos': ['Vicálvaro'],
    'modo_tematica': 'AND',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})

# -------------------- Test 19 --------------------
print("\n\n🎯 Test 19: Sin precio máximo y gratuito")

form_data_19 = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '',
    'hora_min': '11',
    'hora_max': '13',
    'tematicas': ['Educación', 'Tecnología'],
    'distritos': ['Vicálvaro'],
    'modo_tematica': 'AND',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})

# -------------------- Test 20 --------------------
print("\n\n🎯 Test 20: Sin modo temática")

form_data_20 = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '4',
    'hora_min': '11',
    'hora_max': '13',
    'tematicas': ['Educación', 'Tecnología'],
    'distritos': ['Vicálvaro'],
    'modo_tematica': '',
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})


# -------------------- Test 21 --------------------
print("\n\n🎯 Test 21: Sin tipo similitud")

form_data_21 = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '3',
    'hora_min': '10',
    'hora_max': '13',
    'tematicas': ['Educación', 'Tecnología'],
    'distritos': ['Vicálvaro'],
    'modo_tematica': 'AND',
    'tipo_similitud': '',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})

print("\n\n⚖️ Test 22: Comparativa entre modo temática AND vs OR")

form_data_22a = MultiDict({
    'gratuito': 'No',
    'precio_min': '0',
    'precio_max': '20',
    'hora_min': '16',
    'hora_max': '23',
    'tematicas': ['Cultura', 'Música', 'Conciertos'],
    'distritos': ['Centro', 'Retiro'],
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.5',
    'peso_hora': '0.5'
})

form_data_22b = MultiDict(form_data_22a.copy())
form_data_22b['modo_tematica'] = 'OR'

df_or = obtener_eventos_filtrados(form_data_22b)
print(f"🎯 Modo OR → Eventos encontrados: {len(df_or)}")
print(df_or[['TITULO', 'TEMATICA', 'similitud_total']].head().to_string(index=False))


form_data_and = MultiDict(form_data_22a.copy())
form_data_and['modo_tematica'] = 'AND'

df_and = obtener_eventos_filtrados(form_data_and)
print(f"\n🎯 Modo AND → Eventos encontrados: {len(df_and)}")
print(df_and[['TITULO', 'TEMATICA', 'similitud_total']].head().to_string(index=False))


print("\n📊 Diferencia de resultados:")
print(f"➕ OR encontró {len(df_or)} eventos")
print(f"➖ AND encontró {len(df_and)} eventos")


print("\n\n⚖️ Test 23: Comparativa modo temática AND vs OR (Educación, Tecnología)")

form_data_base = MultiDict({
    'gratuito': 'Sí',
    'hora_min': '10',
    'hora_max': '13',
    'tematicas': ['Educación', 'Tecnología'],
    'distritos': ['Chamartín', 'Vicálvaro', 'Centro'],
    'tipo_similitud': 'trapezoidal',
    'peso_precio': '0.0',   
    'peso_hora': '1.0'
})


form_data_or = MultiDict(form_data_base.copy())
form_data_or['modo_tematica'] = 'OR'

df_or = obtener_eventos_filtrados(form_data_or)
print(f"🎯 Modo OR → Eventos encontrados: {len(df_or)}")
print(df_or[['TITULO', 'TEMATICA', 'DISTRITO-INSTALACION', 'similitud_total']].head().to_string(index=False))


form_data_and = MultiDict(form_data_base.copy())
form_data_and['modo_tematica'] = 'AND'

df_and = obtener_eventos_filtrados(form_data_and)
print(f"\n🎯 Modo AND → Eventos encontrados: {len(df_and)}")
print(df_and[['TITULO', 'TEMATICA', 'DISTRITO-INSTALACION', 'similitud_total']].head().to_string(index=False))


print("\n📊 Comparación resumen:")
print(f"➕ OR encontró {len(df_or)} eventos")
print(f"➖ AND encontró {len(df_and)} eventos")

def run_test():
    try:
        df = obtener_eventos_filtrados(form_data_21)
        print(f"🎯 Eventos encontrados: {len(df)}")
        print(df[['TITULO', 'FECHA', 'HORA', 'TEMATICA', 'DISTRITO-INSTALACION']].head().to_string(index=False))
    except Exception as e:
        print(f"\n🚫 Error: {e}")

