# 📍 Recomendador de Eventos Culturales en Madrid basado en Clima y Preferencias

Este proyecto consiste en el desarrollo de un sistema de recomendación de eventos culturales en Madrid, que integra filtros personalizados del usuario y condiciones climáticas en tiempo real para ofrecer resultados relevantes y contextualmente adecuados.

## 🧠 ¿Qué hace este sistema?

- Permite a los usuarios buscar eventos culturales filtrando por precio, hora, temáticas, distritos y tipo de similitud.
- Incorpora datos climáticos para ajustar los resultados al contexto (ej. evitar actividades al aire libre en caso de lluvia).
- Clasifica automáticamente los eventos por temáticas utilizando un modelo de clasificación zero-shot.
- Ofrece un panel exclusivo para administradores, con funcionalidades de revisión y gestión de eventos.
- Implementado con una arquitectura ligera Flask + HTML/CSS + Python + Pandas.

## 🚀 Requisitos y puesta en marcha

### 1. Clonar el repositorio


git clone https://github.com/ranchal88/TFG-AlejandroRanchal.git



### 2. Crear entorno virtual (opcional pero recomendable)


python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate


### 3. Instalar dependencias

Asegúrate de tener Python ≥ 3.8 instalado. Luego ejecuta:


pip install -r requirements.txt


Esto instalará todas las librerías necesarias como Flask, pandas, numpy, scikit-learn, sentence-transformers, etc.

## 🧪 Ejecutar el sistema

Una vez instaladas las dependencias, ejecuta:


python main.py


Esto levantará el servidor en modo local. Por defecto estará accesible en:

```
http://127.0.0.1:5000/
```


## 📘 Dataset

El sistema trabaja con un conjunto de datos en formato Excel (`Datos_codificados.xlsx`) que incluye:
- Información de eventos culturales proporcionados por la Comunidad de Madrid.
- Enriquecimiento con datos meteorológicos para cada evento.
- Campos codificados como precio, hora, temáticas, localización, etc.

## 🔐 Roles y acceso

El sistema incluye dos tipos de usuario:
- **Básico**: puede buscar eventos personalizados desde la interfaz.
- **Administrador**: tiene acceso al panel de control, revisión de eventos y actualización del dataset.

## ✅ Pruebas y validación

El archivo `test.py` contiene más de 20 escenarios de prueba con distintos perfiles de búsqueda y configuraciones. Esto permite validar:

- La coherencia del sistema de recomendación.
- El comportamiento ante entradas incompletas o conflictivas.
- El rendimiento del filtrado y la similitud.
- La diferencia entre funciones de similitud trapezoidal y gaussiana.

## 📄 Licencia y datos

Este proyecto reutiliza datos públicos de la Comunidad de Madrid y OpenWeather, cumpliendo sus condiciones de uso. No almacena datos personales de usuarios. Para más información, consulta el apartado “Marco regulador” de la memoria técnica.

## 💼 Autoría

> Proyecto desarrollado como Trabajo Fin de Grado en Ingeniería Informática – Curso 2024/2025  
> Autor: [Alejandro Ranchal Samaniego]  
> Email: [100432239@alumnos.uc3m.es]
