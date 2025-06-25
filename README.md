# 🔋 Gestor de Revisiones de Baterías

Este proyecto es una aplicación web sencilla para gestionar revisiones de baterías de coches. Permite subir imágenes de comprobantes o lecturas, procesarlas mediante OCR y almacenarlas junto a los datos relevantes en una base de datos local.

## 🚀 Características

- 📷 Subida de imágenes de informes o lecturas de batería.
- 🔎 Reconocimiento automático de texto en las imágenes (OCR con EasyOCR).
- 🗂 Almacenamiento de los datos extraídos en una base de datos SQLite.
- 📅 Registro automático con fecha y hora.
- 🖥 Compatible con ordenadores y móviles.
- ✅ Interfaz clara y funcional para técnicos o usuarios individuales.

## 🛠 Requisitos

- Python 3.8 o superior
- pip

### Dependencias (se instalan automáticamente con `pip install -r requirements.txt`):

- Flask
- easyocr
- opencv-python
- numpy

## 📦 Instalación

```bash
git clone https://github.com/tu-usuario/gestor-baterias.git
cd gestor-baterias
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
