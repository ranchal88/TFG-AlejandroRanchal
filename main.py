from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session
import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import requests
from datetime import datetime
from scripts.actualizar_eventos import actualizar_eventos as ejecutar_actualizacion, guardar_en_historial
from utils.clima import obtener_clima
import json
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from transformers import pipeline
from dotenv import load_dotenv
load_dotenv()


HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")


HISTORIAL_PATH = 'data/actualizaciones.json'


app = Flask(__name__)
app.secret_key = 'clave' 




def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'usuario' not in session:
            flash("Debes iniciar sesión para acceder", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorada



modelo_embeddings = SentenceTransformer('all-MiniLM-L6-v2')


clasificador_zero_shot = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-3",
    token=HF_TOKEN
)

tematicas_zero_shot = [
    "Aire libre", "Arte", "Aventura", "Callejero", "Celebraciones", "Ciclismo",
    "Cine", "Competencia", "Conciertos", "Creatividad", "Cultura", "Danza",
    "Deportes", "Educación", "Entretenimiento", "Escénico", "Familia", "Feminismo",
    "Flamenco", "Formación", "Historia", "Idiomas", "Infantil", "Libros",
    "Literatura", "Magia", "Medio ambiente", "Música", "Naturaleza", "Navidad",
    "Online", "Poesía", "Religioso", "Rock/Pop", "Salud", "Sociedad", "Talento",
    "Teatro", "Tecnología", "Tercera edad", "Turismo"
]



distritos_coords = {
    "Centro": {"lat": 40.4168, "lon": -3.7038},
    "Arganzuela": {"lat": 40.3973, "lon": -3.6943},
    "Retiro": {"lat": 40.4114, "lon": -3.6793},
    "Salamanca": {"lat": 40.4301, "lon": -3.6783},
    "Chamartín": {"lat": 40.4602, "lon": -3.6778},
    "Tetuán": {"lat": 40.4563, "lon": -3.7045},
    "Chamberí": {"lat": 40.4350, "lon": -3.7035},
    "Fuencarral-El Pardo": {"lat": 40.5066, "lon": -3.7135},
    "Moncloa-Aravaca": {"lat": 40.4406, "lon": -3.7459},
    "Latina": {"lat": 40.3933, "lon": -3.7450},
    "Carabanchel": {"lat": 40.3810, "lon": -3.7396},
    "Usera": {"lat": 40.3824, "lon": -3.7094},
    "Puente De Vallecas": {"lat": 40.3914, "lon": -3.6625},
    "Moratalaz": {"lat": 40.4077, "lon": -3.6512},
    "Ciudad Lineal": {"lat": 40.4440, "lon": -3.6541},
    "Hortaleza": {"lat": 40.4761, "lon": -3.6414},
    "Villaverde": {"lat": 40.3428, "lon": -3.7122},
    "Villa De Vallecas": {"lat": 40.3756, "lon": -3.6218},
    "Vicálvaro": {"lat": 40.4013, "lon": -3.6014},
    "San Blas-Canillejas": {"lat": 40.4389, "lon": -3.6097},
    "Barajas": {"lat": 40.4721, "lon": -3.5800}
}



tematica_descripciones = {
    "Aire libre": "aire libre, naturaleza, parque, campo, excursión, senderismo, picnic, rutas al aire libre, paseo natural, actividades fuera, entorno abierto, caminatas",
    "Arte": "arte, pintura, escultura, arte moderno, artistas visuales, museos, exposiciones, arte digital, dibujo, instalaciones, galerías, expresión visual, arte contemporáneo",
    "Aventura": "aventura, explorar, adrenalina, escalada, kayak, rafting, tirolina, supervivencia, actividades extremas, riesgo controlado, emoción intensa",
    "Callejero": "callejero, eventos urbanos, actuaciones callejeras, arte callejero, graffiti, música callejera, danza urbana, espectáculos al aire libre, cultura popular, flashmobs",
    "Celebraciones": "celebraciones, fiestas, celebraciones populares, festividades, conmemoraciones, encuentros culturales, verbenas, carnaval, aniversarios, eventos comunitarios",
    "Ciclismo": "ciclismo, bicicletas, ciclismo urbano, mountain bike, ciclismo de carretera, rutas ciclistas, pedalear, bicis, carreras ciclistas, movilidad sostenible, ciclovías",
    "Cine": "cine, películas, cine, cortometrajes, largometrajes, proyecciones, documentales, cineclubs, cine al aire libre, estrenos, crítica cinematográfica, festivales de cine",
    "Competencia": "competencia, torneos, retos, concursos, campeonatos, duelos, pruebas, clasificación, competición individual, olimpiadas, habilidades, desafíos",
    "Conciertos": "concierto, música en vivo, recitales, bandas, cantantes, escenarios, festivales, sonido en directo, espectáculos musicales, público, entradas, acústico",
    "Creatividad": "creatividad, imaginación, diseño, dibujo, creación, talleres creativos, expresión personal, inventiva, actividades artísticas, manualidades, inspiración, innovación visual",
    "Crecimiento personal": "crecimiento personal, motivación, autoconocimiento, bienestar, mindfulness, desarrollo interior, autoestima, coaching, inteligencia emocional, superación personal, resiliencia",
    "Cultura": "cultura, historia, patrimonio, arte, tradiciones, costumbres, expresiones culturales, herencia, civilización, identidad cultural, museos, diversidad cultural",
    "Danza": "danza, baile, coreografías, danza contemporánea, ballet, folclore, expresión corporal, estilos de danza, clases de baile, danza moderna, flamenco, improvisación",
    "Debate": "debate, discusión, ideas, tertulias, política, temas sociales, argumentación, pensamiento crítico, confrontación de ideas, panel de expertos, diálogo público",
    "Deportes": "deportes, fútbol, baloncesto, atletismo, natación, entrenamiento, ejercicio físico, deporte colectivo, campeonatos, ligas deportivas, gimnasia, bienestar físico",
    "Discapacidad": "discapacidad, inclusión, accesibilidad, diversidad funcional, eventos adaptados, integración, participación plena, autonomía, sensibilización, capacidades distintas",
    "Ecología": "ecología, medio ambiente, sostenibilidad, reciclaje, cambio climático, naturaleza, educación ambiental, consumo responsable, energía verde, biodiversidad",
    "Educación": "educación, enseñanza, aprendizaje, clases, escuela, formación, conocimiento, alfabetización, pedagogía, estudiantes, profesorado, métodos educativos",
    "Entretenimiento": "entretenimiento, ocio, diversión, pasatiempos, espectáculos, entretenimiento familiar, juegos, animación, eventos lúdicos, entretenimiento digital",
    "Equitación": "equitación, caballos, montar a caballo, hípica, doma, salto ecuestre, equinos, centros ecuestres, concursos de hípica, paseo a caballo",
    "Escénico": "escénico, teatro, monólogos, escena, dramaturgia, actuación en vivo, comedia, drama, artes escénicas, performance, grupo teatral, puesta en escena",
    "Fiestas": "fiesta, celebraciones, fiesta, diversión, música, baile, reunión social, evento nocturno, festividad, discoteca, verbena, evento especial",
    "Familia": "familia, padres, hijos, actividades familiares, tiempo en familia, juegos familiares, educación infantil, crianza, dinámicas familiares, entretenimiento familiar",
    "Feminismo": "feminismo, igualdad, género, mujeres, empoderamiento, derechos, sororidad, lucha social, visibilidad femenina, movimientos sociales, justicia de género",
    "Flamenco": "flamenco, cante jondo, guitarra española, zapateado, baile flamenco, compás, tablao, cultura andaluza, palmas, arte flamenco, tradición",
    "Formación": "formación, educación, talleres, capacitación, cursos, conocimientos, habilidades, clases, certificados, sesiones formativas, actualización profesional",
    "Historia": "historia, pasado, patrimonio histórico, personajes históricos, cronología, épocas, arqueología, eventos históricos, visitas culturales, divulgación histórica",
    "Idiomas": "idioma, lenguas, aprendizaje lingüístico, intercambio de idiomas, clases de inglés, francés, español para extranjeros, inmersión lingüística, gramática, conversación",
    "Infantil": "infantil, niños, niñas, juegos, cuentos, actividades lúdicas, animación infantil, espectáculos para peques, títeres, talleres para menores, manualidades",
    "Libros": "libro, libros, literatura, novela, autores, bibliotecas, librerías, lectura, ensayo, ferias del libro, clubes de lectura, narrativa",
    "Literatura": "literatura, poesía, novela, relatos, ensayo literario, escritura creativa, narrativa, autoría, expresión escrita, textos, análisis literario",
    "Magia": "magia, magos, ilusionismo, trucos, espectáculo mágico, mentalismo, cartas, show de magia, misterio, entretenimiento mágico",
    "Medio ambiente": "medio ambiente, ecología, conservación, sostenibilidad, reciclaje, biodiversidad, cambio climático, campañas verdes, naturaleza, educación ambiental",
    "Música": "música, melodías, instrumentos, armonía, ensayos musicales, bandas, géneros musicales, letras de canciones, producción musical, conciertos",
    "Naturaleza": "naturaleza, flora, fauna, bosque, parque natural, excursiones, aire puro, rutas verdes, actividades ecológicas, senderos, biodiversidad",
    "Navidad": "navidad, fiestas navideñas, mercadillo, árbol de navidad, luces, Papá Noel, Reyes Magos, belén, regalos, villancicos, espíritu navideño",
    "Online": "online, virtual, por internet, plataforma digital, streaming, videollamada, webinar, actividad remota, formación online, evento digital",
    "Poesía": "poesía, versos, recitales, poesía contemporánea, escritura poética, poetas, metáforas, lírica, poesía visual, encuentro poético",
    "Religioso": "religioso, misa, iglesia, procesiones, espiritualidad, celebración litúrgica, fe, creencias, tradición religiosa, comunidad creyente",
    "Rock/Pop": "rock, pop, bandas de rock, pop alternativo, música popular, festivales, conciertos, guitarras eléctricas, cultura pop, hits musicales",
    "Running": "running, correr, maratón, entrenamiento, carreras populares, running urbano, cardio, zapatillas deportivas, ruta de running, salud física",
    "Salud": "salud, bienestar, medicina, alimentación sana, ejercicio físico, salud mental, prevención, terapias, vida saludable, hábitos saludables",
    "Sociedad": "sociedad, colectivo, convivencia, inclusión social, justicia, civismo, temas comunitarios, integración, actividades ciudadanas",
    "Talento": "talento, show de talentos, jóvenes promesas, creatividad, habilidades únicas, expresión artística, concurso de habilidades, nuevos artistas",
    "Teatro": "teatro, obra teatral, comedia, drama, espectáculo escénico, actores, actrices, guión, escenario, dirección escénica, compañía teatral",
    "Tecnología": "tecnología, innovación, programación, IA, robótica, apps, software, hardware, startups, transformación digital, impresión 3D",
    "Tercera edad": "tercera edad, mayores, actividades para jubilados, envejecimiento activo, salud senior, talleres para la tercera edad, acompañamiento, memoria",
    "Turismo": "turismo, visitas guiadas, rutas, cultura local, monumentos, excursiones, guías turísticos, experiencias culturales, descubrimiento urbano"
}

def asignar_tematicas_zero_shot(texto, max_etiquetas=5, umbral=0.3):
    if not texto or not texto.strip():
        return ""

    resultado = clasificador_zero_shot(
        texto,
        candidate_labels=tematicas_zero_shot,
        multi_label=True
    )

    etiquetas = []
    for label, score in zip(resultado['labels'], resultado['scores']):
        if score >= umbral:
            etiquetas.append((label, score))

    etiquetas.sort(key=lambda x: x[1], reverse=True)
    top_etiquetas = [etq for etq, _ in etiquetas[:max_etiquetas]]
    return ", ".join(top_etiquetas)



    
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

def registrar_usuario(username, password, rol):
    with open("data/usuarios.json", "r") as f:
        usuarios = json.load(f)

    if any(u["username"] == username for u in usuarios):
        return False  

    nuevo = {
        "username": username,
        "password": generate_password_hash(password),
        "rol": rol
    }

    usuarios.append(nuevo)

    with open("data/usuarios.json", "w") as f:
        json.dump(usuarios, f, indent=2)

    return True

def validar_usuario(username, password):
    with open("data/usuarios.json", "r") as f:
        usuarios = json.load(f)

    for u in usuarios:
        if u["username"] == username and check_password_hash(u["password"], password):
            return u["rol"]
    return None

def cargar_usuarios():
    with open("data/usuarios.json", "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open("data/usuarios.json", "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=2)



def obtener_eventos_filtrados(form_data):
       
    if not form_data.get('gratuito'):
        raise ValueError("Faltan parámetros: gratuito")

    if form_data.get('gratuito') == 'No':
        if not form_data.get('precio_min') or not form_data.get('precio_max'):
            raise ValueError("Faltan parámetros: precio_min o precio_max")

    if not form_data.get('hora_min') or not form_data.get('hora_max'):
        raise ValueError("Faltan parámetros: hora_min o hora_max")

    if not form_data.getlist('tematicas'):
        raise ValueError("Faltan parámetros: tematicas")

    if not form_data.getlist('distritos'):
        raise ValueError("Faltan parámetros: distritos")
    
    if not form_data.get('modo_tematica'):
        raise ValueError("Faltan parámetros: modo_tematica")
    
    if not form_data.get('tipo_similitud'):
        raise ValueError("Faltan parámetros: tipo_similitud")
    df_copy = df.copy()


    gratuito = form_data.get('gratuito') == 'Sí'
    precio_min = float(form_data.get('precio_min', 0))
    precio_max = float(form_data.get('precio_max', 100))
    hora_min = int(form_data.get('hora_min', 0))
    hora_max = int(form_data.get('hora_max', 23))
    tematicas = form_data.getlist('tematicas')
    distritos = form_data.getlist('distritos')
    modo_tematica = form_data.get('modo_tematica', 'OR')
    tipo_similitud = form_data.get('tipo_similitud', 'trapezoidal') 

    if not gratuito:
        peso_precio = float(form_data.get('peso_precio', 0.5))
        peso_hora = float(form_data.get('peso_hora', 0.5))
        total = peso_precio + peso_hora
        if total > 0:
            peso_precio /= total
            peso_hora /= total
        else:
            peso_precio = peso_hora = 0.5
    else:
        peso_precio = 0
        peso_hora = 1

    
    if gratuito:
        df_copy = df_copy[df_copy['GRATUITO'] == 1]
        df_copy['similitud_precio'] = 1
    else:
        if tipo_similitud == 'gaussiana':
            mu = (precio_min + precio_max) / 2
            sigma = (precio_max - precio_min) / 3 or 1  
            df_copy['similitud_precio'] = df_copy['PRECIO'].apply(lambda x: gaussian_similarity(x, mu, sigma))
        else:
            a, b = precio_min, precio_min + (precio_max - precio_min) / 3
            c, d = precio_max - (precio_max - precio_min) / 3, precio_max
            df_copy['similitud_precio'] = df_copy['PRECIO'].apply(lambda x: trapezoidal(x, a, b, c, d))

        df_copy = df_copy[df_copy['similitud_precio'] > 0]

    if tipo_similitud == 'gaussiana':
        mu = (hora_min + hora_max) / 2
        sigma = (hora_max - hora_min) / 3 or 1
        df_copy['similitud_hora'] = df_copy['HORA'].apply(lambda x: gaussian_similarity(x, mu, sigma))
    else:
        a, b = hora_min, hora_min + (hora_max - hora_min) / 3
        c, d = hora_max - (hora_max - hora_min) / 3, hora_max
        df_copy['similitud_hora'] = df_copy['HORA'].apply(lambda x: trapezoidal(x, a, b, c, d))

    
    if tematicas:
        tematicas = [t.strip() for t in ', '.join(tematicas).split(',')]
        if modo_tematica == 'AND':
            df_copy = df_copy[df_copy['TEMATICA'].apply(lambda x: all(t in x.split(', ') for t in tematicas))]
        else:
            df_copy = df_copy[df_copy['TEMATICA'].apply(lambda x: any(t in x.split(', ') for t in tematicas))]

    if distritos:
        distritos = [d.strip() for d in ', '.join(distritos).split(',')]
        df_copy = df_copy[df_copy['DISTRITO-INSTALACION'].isin(distritos)]

  
    df_copy['similitud_total'] = (
        peso_precio * df_copy['similitud_precio'] +
        peso_hora * df_copy['similitud_hora']
    )

    df_copy['FECHA'] = pd.to_datetime(df_copy['FECHA']).dt.date
    df_copy['HORA'] = df_copy['HORA'].astype(int)
    df_copy['Temperatura'] = pd.to_numeric(df_copy['Temperatura'], errors='coerce')
    df_copy['Descripción del tiempo'] = df_copy['Descripción del tiempo'].replace(["nan", "NaN", ""], np.nan)

    return df_copy.sort_values(by='similitud_total', ascending=False)


def asignar_tematicas(descripcion, umbral=0.48, minimo=3):
    descripcion_emb = modelo_embeddings.encode(descripcion, convert_to_tensor=True)
    
    etiquetas_similares = []
    
    for tema, contexto in tematica_descripciones.items():
        tema_emb = modelo_embeddings.encode(contexto, convert_to_tensor=True)
        similitud = util.cos_sim(descripcion_emb, tema_emb).item()
        if similitud >= umbral:
            etiquetas_similares.append((tema, similitud))
    
    if len(etiquetas_similares) < minimo:
   
        todas = []
        for tema, contexto in tematica_descripciones.items():
            tema_emb = modelo_embeddings.encode(contexto, convert_to_tensor=True)
            sim = util.cos_sim(descripcion_emb, tema_emb).item()
            todas.append((tema, sim))
        todas.sort(key=lambda x: x[1], reverse=True)
        etiquetas_similares = todas[:minimo]

    etiquetas_finales = [tema for tema, _ in etiquetas_similares]
    return ", ".join(etiquetas_finales)



def trapezoidal(x, a, b, c, d):
    try:
        x = float(x)
        if x <= a or x >= d:
            return 0
        elif a < x <= b:
            return (x - a) / (b - a)
        elif b < x <= c:
            return 1
        elif c < x < d:
            return (d - x) / (d - c)
    except Exception as e:
        print(f"Error en la función trapezoidal: {e}")
        return 0
    


def gaussian_similarity(x, mu, sigma):
    try:
        return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))
    except:
        return 0



df = pd.read_excel('data/Datos_codificados.xlsx')  

df['PRECIO'] = pd.to_numeric(df['PRECIO'], errors='coerce')
df['GRATUITO'] = pd.to_numeric(df['GRATUITO'], errors='coerce')
df['HORA'] = pd.to_numeric(df['HORA'], errors='coerce')

@app.route('/inicio')
@login_requerido
def inicio():
    return render_template('inicio.html')

from flask import flash, redirect, url_for

@app.route('/buscar', methods=['GET', 'POST'])
@login_requerido
def index():
    if request.method == 'POST':
        try:
            df_filtrado = obtener_eventos_filtrados(request.form)
            top_eventos = df_filtrado.head(10)
            hay_mas = len(df_filtrado) > 10 

            return render_template('resultados.html',
                eventos=top_eventos,
                hay_mas=hay_mas, 
                gratuito=request.form.get('gratuito') == 'Sí',
                precio_min=request.form.get('precio_min'),
                precio_max=request.form.get('precio_max'),
                hora_min=request.form.get('hora_min'),
                hora_max=request.form.get('hora_max'),
                tematicas=request.form.getlist('tematicas'),
                distritos=request.form.getlist('distritos'),
                modo_tematica=request.form.get('modo_tematica'),
                tipo_similitud=request.form.get('tipo_similitud'),
                peso_precio=request.form.get('peso_precio'),
                peso_hora=request.form.get('peso_hora')
            )

        except ValueError as e:
            flash(f"⚠️ {str(e)}", "warning")
            return redirect(url_for('index'))

    return render_template('index.html')


@app.route('/api/eventos', methods=['POST'])
@login_requerido
def api_eventos():
    offset = int(request.args.get('offset', 0))
    cantidad = int(request.args.get('cantidad', 10))

    print("\n📥 Petición API recibida")
    print("Offset:", offset)
    print("Cantidad:", cantidad)
    print("Form data recibido:", request.form.to_dict(flat=False))  

    df_filtrado = obtener_eventos_filtrados(request.form)
    total = len(df_filtrado)

    print("🎯 Eventos encontrados después de filtrar:", total)

    subset = df_filtrado.iloc[offset:offset+cantidad].copy()
    subset.replace({np.nan: None, pd.NA: None, pd.NaT: None}, inplace=True)
    eventos = subset.to_dict(orient='records')


    print("🚚 Eventos devueltos:", len(eventos))  

    return jsonify({
        "eventos": eventos,
        "hay_mas": offset + cantidad < total
    })

@app.route('/api/eventos_recientes')
@login_requerido
def eventos_recientes():
    df = pd.read_excel("data/Datos_codificados.xlsx")

  
    df = df.tail(15).iloc[::-1].copy()  

    df.replace({pd.NA: None, pd.NaT: None, float('nan'): None}, inplace=True)

    eventos = df.to_dict(orient="records")

    return jsonify({"eventos": eventos})



@app.route('/añadir', methods=['GET', 'POST'])
@login_requerido
def añadir_evento():
    ruta_pendientes = 'data/eventos_pendientes.xlsx'

    if request.method == 'POST':
        
        titulo = request.form.get('titulo')
        fecha = request.form.get('fecha')
        hora_str = request.form.get('hora') 
        hora = int(hora_str.split(":")[0])
        minuto = int(hora_str.split(":")[1])
        hora_decimal = hora + minuto / 60.0

        descripcion = request.form.get('descripcion')
        distrito = request.form.get('distrito')
        gratuito = request.form.get('gratuito')
        precio = request.form.get('precio')

       
        if gratuito == 'Sí':
            precio_valor = 0.0
            gratuito_valor = 1
        else:
            try:
                precio_valor = float(precio)
            except:
                precio_valor = 0.0
            gratuito_valor = 0

        print(f"Nuevo evento recibido: {titulo}, gratuito={gratuito_valor}, precio={precio_valor}")

      
        nuevo_evento = pd.DataFrame([{
            'TITULO': titulo,
            'FECHA': fecha,
            'HORA': hora_decimal,
            'DESCRIPCION': descripcion,
            'DISTRITO': distrito,
            'PRECIO': precio_valor,
            'GRATUITO': gratuito_valor,
            'ESTADO': 'pendiente',
            'Usuario': session.get("usuario", "")
        }])

        
        if os.path.exists(ruta_pendientes):
            df_pendientes = pd.read_excel(ruta_pendientes)
            df_actualizado = pd.concat([df_pendientes, nuevo_evento], ignore_index=True)
        else:
            df_actualizado = nuevo_evento

        df_actualizado.to_excel(ruta_pendientes, index=False)

        return render_template('confirmacion_envio.html', titulo=titulo)

    return render_template('añadir_evento.html')

@app.route('/admin/revisar', methods=['GET', 'POST'])
@login_requerido
def revisar_eventos():
    if session.get('rol') != 'Administrador':
        flash("Acceso restringido a administradores", "error")
        return redirect(url_for('inicio'))
    ruta_pendientes = 'data/eventos_pendientes.xlsx'
    ruta_final = 'data/Datos_codificados.xlsx'

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        accion = request.form.get('accion')

        if os.path.exists(ruta_pendientes):
            df_pendientes = pd.read_excel(ruta_pendientes)

        
            evento = df_pendientes[df_pendientes['TITULO'] == titulo]

            if not evento.empty:
                if accion == 'aprobar':
                    if os.path.exists(ruta_final):
                        df_final = pd.read_excel(ruta_final)
                    else:
                        df_final = pd.DataFrame()

                    row = evento.iloc[0]
                    temp, clima = obtener_clima(row['FECHA'], row['HORA'], row['DISTRITO'])
                    fecha_evento = pd.to_datetime(row['FECHA'])
                    es_futuro = fecha_evento > datetime.now()
                    nuevo_evento = pd.DataFrame([{
                        'ID-EVENTO': f"EVT-{str(uuid4())[:8]}",
                        'TITULO': row['TITULO'],
                        'PRECIO': row['PRECIO'],
                        'GRATUITO': row['GRATUITO'],
                        'FECHA': row['FECHA'],
                        'HORA': int(row['HORA']),
                        'DESCRIPCIÓN': row['DESCRIPCION'],
                        'DISTRITO-INSTALACION': row['DISTRITO'],
                        'TEMATICA': row['TEMATICA'],
                        'Temperatura': temp,
                        'Descripción del tiempo': clima,
                        'similitud_precio': 0,
                        'similitud_hora': 0,
                        'similitud_total': 0,
                        'NUEVO': 1 if es_futuro else 0,
                        'Usuario': row.get('Usuario', '')
                        
                    }])

                    df_final_actualizado = pd.concat([df_final, nuevo_evento], ignore_index=True)
                    df_final_actualizado.to_excel(ruta_final, index=False)
                    df_pendientes = df_pendientes[df_pendientes['TITULO'] != titulo]
                    df_pendientes.to_excel(ruta_pendientes, index=False)
                    flash("✅ Evento aprobado correctamente", "exito")
                    return redirect(url_for('revisar_eventos'))
                elif accion == 'actualizar_tematica':
                    nuevas = request.form.getlist('tematica_manual')
                    df_pendientes.loc[df_pendientes['TITULO'] == titulo, 'TEMATICA'] = ", ".join(nuevas)
                    df_pendientes.to_excel(ruta_pendientes, index=False)
                    return redirect(url_for('revisar_eventos'))
                
                elif accion == 'rechazar':
                  
                    df_pendientes = df_pendientes[df_pendientes['TITULO'] != titulo]
                    df_pendientes.to_excel(ruta_pendientes, index=False)
                    flash("❌ Evento rechazado correctamente", "exito")
                    return redirect(url_for('revisar_eventos'))
                    

                

                return redirect(url_for('revisar_eventos'))

  
    if os.path.exists(ruta_pendientes):
        df = pd.read_excel(ruta_pendientes)

  
        actualizados = False
        for i, row in df.iterrows():
            if pd.isna(row.get("TEMATICA", "")) or row["TEMATICA"] == "":
                descripcion = str(row["DESCRIPCION"])
                tematicas_detectadas = asignar_tematicas_zero_shot(descripcion)

                df.at[i, "TEMATICA"] = tematicas_detectadas
                actualizados = True

        if actualizados:
            df.to_excel(ruta_pendientes, index=False)
        
        tematicas_disponibles = list(tematica_descripciones.keys())
            
        return render_template('admin/revisar.html', eventos=df.to_dict("records"), asignar_tematicas=asignar_tematicas,tematicas_disponibles=tematicas_disponibles)


@app.route('/debug/ver_pendientes')
def ver_pendientes():
    df = pd.read_excel('data/eventos_pendientes.xlsx')
    return df.to_html()

@app.route('/debug/ver_datos_codificados')
def ver_eventos_actuales():
    df = pd.read_excel('data/Datos_codificados.xlsx')
    return df.to_html()

@app.route('/admin/actualizar_eventos', methods=['GET', 'POST'])
@login_requerido
def actualizar_eventos():
    if session.get('rol') != 'Administrador':
        flash("Acceso restringido a administradores", "error")
        return redirect(url_for('inicio'))
    historial = []
    if os.path.exists(HISTORIAL_PATH) and os.path.getsize(HISTORIAL_PATH) > 0:
            with open(HISTORIAL_PATH, 'r', encoding='utf-8') as f:
                historial = json.load(f)

    if request.method == 'POST':
        eliminados_nuevo, eventos_clima_actualizado, actualizados = ejecutar_actualizacion()
        guardar_en_historial(eliminados_nuevo, eventos_clima_actualizado)
        historial = []
        if os.path.exists(HISTORIAL_PATH) and os.path.getsize(HISTORIAL_PATH) > 0:
            with open(HISTORIAL_PATH, 'r', encoding='utf-8') as f:
                historial = json.load(f)
        return render_template(
            'admin/actualizar_eventos.html',
            eliminados_nuevo=eliminados_nuevo,
            eventos_clima_actualizado=eventos_clima_actualizado,
            actualizados=actualizados,
            historial=historial[::-1]  
        )
  


    return render_template('admin/actualizar_eventos.html', historial=historial[::-1])



@app.route('/admin/estadisticas')
@login_requerido
def panel_control_admin():
    if session.get('rol') != 'Administrador':
        flash("Acceso restringido a administradores", "error")
        return redirect(url_for('inicio'))
    try:
        df = pd.read_excel('data/Datos_codificados.xlsx')

      
        tematicas = df['TEMATICA'].dropna().str.split(', ')
        tematicas_flat = tematicas.explode()
        top_tematicas = tematicas_flat.value_counts().head(5)

        distritos = df['DISTRITO-INSTALACION'].dropna()
        top_distritos = distritos.value_counts()

        eventos = df.to_dict('records')[::-1]

        print(df[['TITULO', 'Descripción del tiempo']].tail(10))
        usuarios=cargar_usuarios()
 


        return render_template(
            'admin/panel_control.html',
            eventos=eventos,
            top_tematicas=top_tematicas.items(),
            top_distritos=top_distritos.items(),
            usuarios=usuarios
        )
    except Exception as e:
        print(f"[ERROR estadísticas] {e}")
        return "Error al cargar estadísticas"
    
@app.route('/admin/borrar_eventos', methods=['POST'])
@login_requerido
def borrar_eventos():
    ids_borrar = request.form.getlist('eventos_borrar')
    if ids_borrar:
        df = pd.read_excel('data/Datos_codificados.xlsx')
        df = df[~df['ID-EVENTO'].isin(ids_borrar)]
        df.to_excel('data/Datos_codificados.xlsx', index=False)
        flash("✅ Evento(s) eliminados correctamente", "exito")
    return redirect(url_for('panel_control_admin'))



@app.route("/mapa")
@login_requerido
def vista_mapa():
    df = pd.read_excel("data/Datos_codificados.xlsx")

  
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors='coerce')
    hoy = pd.Timestamp.now()
    eventos_futuros = df[df["FECHA"] >= hoy]


    eventos = eventos_futuros.to_dict("records")

    return render_template("mapa.html", distritos=distritos_coords, eventos=eventos)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']
        exito = registrar_usuario(username, password, rol)
        if exito:
            flash("Registro exitoso", "exito")
            return redirect(url_for('login'))
        else:
            flash("Usuario ya existe", "error")
    return render_template('registro.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rol = validar_usuario(username, password)
        if rol:
            session['usuario'] = username
            session['rol'] = rol
            
            return redirect(url_for('inicio'))
        else:
            flash("Credenciales inválidas", "error")
    return render_template('login.html')

@app.route('/logout')
@login_requerido
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for('login'))

@app.route('/perfil')
@login_requerido
def perfil():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return render_template('perfil.html')

@app.route('/cambiar_nombre', methods=['POST'])
@login_requerido
def cambiar_nombre():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    nuevo_nombre = request.form['nuevo_nombre'].strip()
    if not nuevo_nombre:
        flash("El nuevo nombre no puede estar vacío", "error")
        return redirect(url_for('perfil'))

    usuarios = cargar_usuarios()
    for u in usuarios:
        if u['username'] == session['usuario']:
           
            if any(other['username'] == nuevo_nombre for other in usuarios):
                flash("Ese nombre de usuario ya está en uso", "error")
                return redirect(url_for('perfil'))
            u['username'] = nuevo_nombre
            session['usuario'] = nuevo_nombre  
            guardar_usuarios(usuarios)
            flash("Nombre de usuario actualizado", "exito")
            return redirect(url_for('perfil'))

    flash("Usuario no encontrado", "error")
    return redirect(url_for('perfil'))

@app.route('/cambiar_contraseña', methods=['POST'])
@login_requerido
def cambiar_contraseña():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    actual = request.form['actual']
    nueva = request.form['nueva']

    usuarios = cargar_usuarios()
    for u in usuarios:
        if u['username'] == session['usuario']:
            if not check_password_hash(u['password'], actual):
                flash("Contraseña actual incorrecta", "error")
                return redirect(url_for('perfil'))

            u['password'] = generate_password_hash(nueva)
            guardar_usuarios(usuarios)
            flash("Contraseña actualizada correctamente", "exito")
            return redirect(url_for('perfil'))

    flash("Usuario no encontrado", "error")
    return redirect(url_for('perfil'))

@app.route('/eliminar_cuenta', methods=['POST'])
@login_requerido
def eliminar_cuenta():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario_actual = session['usuario']
    rol_actual = session.get('rol', 'Básico')
    usuario_objetivo = request.form.get('usuario') or usuario_actual


    if usuario_objetivo != usuario_actual and rol_actual != 'Administrador':
        flash("No tienes permisos para eliminar esta cuenta", "error")
        return redirect(url_for('inicio'))

    usuarios = cargar_usuarios()
    usuarios = [u for u in usuarios if u['username'] != usuario_objetivo]
    guardar_usuarios(usuarios)


    if usuario_objetivo == usuario_actual:
        session.clear()
        flash("Tu cuenta ha sido eliminada", "exito")
        return redirect(url_for('login'))
    else:
        flash(f"✅ Usuario '{usuario_objetivo}' eliminado correctamente", "exito")
        return redirect(url_for('panel_control_admin'))


@app.route('/admin/usuario/rol', methods=['POST'])
@login_requerido
def admin_usuario_rol():
    if session.get('rol') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('inicio'))

    usuario_objetivo = request.form.get("usuario")
    nuevo_rol = request.form.get("nuevo_rol")

    if not usuario_objetivo or not nuevo_rol:
        flash("Faltan datos del formulario", "error")
        return redirect(url_for('panel_control_admin'))

    try:
        with open("data/usuarios.json", "r", encoding="utf-8") as f:
            usuarios = json.load(f)  

        for user in usuarios:
            if user["username"] == usuario_objetivo:
                user["rol"] = nuevo_rol
                break
        else:
            flash("Usuario no encontrado", "error")
            return redirect(url_for('panel_control_admin'))

        with open("data/usuarios.json", "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=2, ensure_ascii=False)

        flash(f"Rol de '{usuario_objetivo}' actualizado a {nuevo_rol}", "exito")
    except Exception as e:
        print(f"[ERROR cambio de rol] {e}")
        flash("Error al actualizar el rol", "error")

    return redirect(url_for('panel_control_admin'))

@app.route("/etica")
@login_requerido 
def vista_etica():
    return render_template("etica.html")

@app.route("/sobre-nosotros")
@login_requerido 
def vista_sobre_nosotros():
    return render_template("sobre_nosotros.html")





if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"Error al arrancar Flask: {e}")