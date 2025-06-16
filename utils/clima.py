from datetime import datetime, timedelta
import requests

def obtener_clima(fecha_str, hora_decimal, distrito):
    try:
        lat, lon = distrito_coords.get(distrito, (40.4168, -3.7038))  
        fecha = datetime.strptime(str(fecha_str), "%Y-%m-%d")
        ahora = datetime.now()
        if (fecha - ahora).days > 7:
            return "", ""  

        hora_int = int(hora_decimal)
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&hourly=temperature_2m,weathercode&timezone=Europe%2FMadrid"
        )
        response = requests.get(url)
        data = response.json()

        tiempos = data["hourly"]["time"]
        temperaturas = data["hourly"]["temperature_2m"]
        codigos = data["hourly"]["weathercode"]

        timestamp_buscado = f"{fecha_str}T{hora_int:02d}:00"

        for i, t in enumerate(tiempos):
            if t == timestamp_buscado:
                codigo = codigos[i]
                temp = temperaturas[i]
                descripcion = interpretar_codigo_clima(int(codigo))
                return temp, descripcion

        return "", "" 
    except Exception as e:
        print(f"[ERROR clima] {e}")
        return "", ""
    

distrito_coords = {
    'Arganzuela': (40.398, -3.694),
    'Barajas': (40.475, -3.577),
    'Carabanchel': (40.377, -3.745),
    'Centro': (40.416, -3.703),
    'Chamartín': (40.460, -3.678),
    'Chamberí': (40.434, -3.713),
    'Ciudad Lineal': (40.444, -3.648),
    'Fuencarral-El Pardo': (40.506, -3.713),
    'Hortaleza': (40.473, -3.637),
    'Latina': (40.393, -3.745),
    'Moncloa-Aravaca': (40.438, -3.753),
    'Moratalaz': (40.407, -3.651),
    'Puente de Vallecas': (40.388, -3.662),
    'Retiro': (40.411, -3.678),
    'Salamanca': (40.426, -3.678),
    'San Blas-Canillejas': (40.438, -3.616),
    'Tetuán': (40.458, -3.707),
    'Usera': (40.380, -3.707),
    'Vicálvaro': (40.400, -3.605),
    'Villa de Vallecas': (40.367, -3.618),
    'Villaverde': (40.346, -3.701)
}

    
def interpretar_codigo_clima(codigo):
    codigos = {
        0: "Despejado",
        1: "Mayormente despejado",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Niebla",
        48: "Niebla con escarcha",
        51: "Llovizna ligera",
        53: "Llovizna moderada",
        55: "Llovizna densa",
        56: "Llovizna helada ligera",
        57: "Llovizna helada densa",
        61: "Lluvia ligera",
        63: "Lluvia moderada",
        65: "Lluvia intensa",
        66: "Lluvia helada ligera",
        67: "Lluvia helada intensa",
        71: "Nevada ligera",
        73: "Nevada moderada",
        75: "Nevada intensa",
        77: "Granizo",
        80: "Chubascos ligeros",
        81: "Chubascos moderados",
        82: "Chubascos fuertes",
        85: "Chubascos de nieve ligeros",
        86: "Chubascos de nieve fuertes",
        95: "Tormenta eléctrica ligera",
        96: "Tormenta con granizo leve",
        99: "Tormenta con granizo fuerte"
    }
    return codigos.get(int(codigo), "Desconocido")
