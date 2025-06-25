#Copyright (c) 2025 [Alex villen]

#Todos los derechos reservados.

#No se concede permiso para usar, copiar, modificar o distribuir este código sin autorización explícita y por escrito del autor.

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
from datetime import datetime, timedelta
import os
import easyocr

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'Junio2025'  
DB = 'baterias.db'

reader = easyocr.Reader(['es'])

# FUNCIONES EXTRAS




def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def estado_revision(fecha_str):
    """calcula la ultima revision del coche"""
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
    proxima = fecha + timedelta(days=30)
    hoy = datetime.today()
    diff = (proxima - hoy).days

    if diff < 0:
        return 'rojo'
    elif diff <= 2:
        return 'amarillo'
    else:
        return 'verde'

# Main FUNCTIONS

@app.route('/')
def index():
    """LISTADO"""
    conn = get_db_connection()
    coches = conn.execute('''
        SELECT c.id, c.bastidor, c.plaza,
               (SELECT MAX(fecha) FROM revisiones WHERE coche_id = c.id) as ultima_revision
        FROM coches c
    ''').fetchall()

    lista = []
    for c in coches:
        fecha = c['ultima_revision'] or '1970-01-01'
        lista.append({
            'id': c['id'],
            'bastidor': c['bastidor'],
            'plaza': c['plaza'],
            'ultima_revision': fecha,
            'estado': estado_revision(fecha)
        })

    conn.close()
    return render_template('index.html', coches=lista)

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo_coche():
    """Form para añadir coches"""
    if request.method == 'POST':
        bastidor = request.form.get('bastidor', '').strip()
        plaza = request.form.get('plaza', '').strip()
        foto_bastidor = request.files.get('foto_bastidor')

        #Intentar usar ocr
        if not bastidor and foto_bastidor and foto_bastidor.filename != '':
            filepath = os.path.join(UPLOAD_FOLDER, foto_bastidor.filename)
            foto_bastidor.save(filepath)

            try:
                result = reader.readtext(filepath)
                texto_ocr = ''.join([res[1] for res in result]).replace(' ', '').strip()
                bastidor = texto_ocr
            except Exception as e:
                flash(f'Error al procesar la imagen OCR: {e}', 'danger')
                return redirect(url_for('nuevo_coche'))

        if not bastidor:
            flash('Debe introducir el bastidor manualmente o subir una foto para OCR', 'danger')
            return redirect(url_for('nuevo_coche'))

        if not plaza:
            flash('La plaza es obligatoria', 'danger')
            return redirect(url_for('nuevo_coche'))

        conn = get_db_connection()
        conn.execute('INSERT INTO coches (bastidor, plaza) VALUES (?, ?)', (bastidor, plaza))
        conn.commit()
        conn.close()

        flash('Coche añadido correctamente', 'success')
        return redirect(url_for('index'))

    return render_template('nuevo_coche.html')

@app.route('/editar_coche/<int:coche_id>', methods=['GET', 'POST'])
def editar_coche(coche_id):
    """Cambiar datos coche"""
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        bastidor = request.form['bastidor']
        plaza = request.form['plaza']
        c.execute('UPDATE coches SET bastidor = ?, plaza = ? WHERE id = ?', (bastidor, plaza, coche_id))
        conn.commit()
        conn.close()
        flash('Datos del coche actualizados correctamente', 'success')
        return redirect(url_for('historial', coche_id=coche_id))

    c.execute('SELECT * FROM coches WHERE id = ?', (coche_id,))
    coche = c.fetchone()
    conn.close()

    if coche is None:
        flash('Coche no encontrado', 'danger')
        return redirect(url_for('index'))

    return render_template('editar_coche.html', coche=coche)

@app.route('/calendario')
def calendario():
    return render_template('calendario.html')

@app.route('/add_revision/<int:coche_id>', methods=['POST'])
def add_revision(coche_id):
    """Agregar revision ocche"""
    fecha = request.form['fecha']
    foto = request.files.get('foto')
    filename = None

    if foto:
        filename = foto.filename
        foto.save(f'static/uploads/{filename}')

    conn = get_db_connection()
    conn.execute('INSERT INTO revisiones (coche_id, fecha, foto) VALUES (?, ?, ?)',
                 (coche_id, fecha, filename))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/historial/<int:coche_id>')
def historial(coche_id):
    """Historial de revisionsiones"""
    conn = get_db_connection()
    coche = conn.execute('SELECT * FROM coches WHERE id = ?', (coche_id,)).fetchone()
    comprobaciones = conn.execute('SELECT * FROM revisiones WHERE coche_id = ? ORDER BY fecha DESC', (coche_id,)).fetchall()
    conn.close()

    if not coche:
        return 'Coche no encontrado', 404

    return render_template('historial.html', coche=coche, comprobaciones=comprobaciones)

@app.route('/borrar_historial/<int:coche_id>', methods=['POST'])
def borrar_historial(coche_id):
    """borrar revisiones"""
    conn = get_db_connection()
    conn.execute('DELETE FROM revisiones WHERE coche_id = ?', (coche_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('historial', coche_id=coche_id))

@app.route('/borrar_coche/<int:coche_id>', methods=['POST'])
def borrar_coche(coche_id):
    """borrar todo coche"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM revisiones WHERE coche_id = ?', (coche_id,))
    c.execute('DELETE FROM coches WHERE id = ?', (coche_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/api/revisiones')
def api_revisiones():
    """pasa las cosas del calendario"""
    hoy = datetime.today().date()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT c.bastidor, c.plaza, MAX(r.fecha) as ultima_revision
        FROM revisiones r
        JOIN coches c ON r.coche_id = c.id
        GROUP BY r.coche_id
    ''')
    datos = c.fetchall()
    conn.close()

    color_map = {
        'verde': '#4caf50',
        'amarillo': '#ffc107',
        'rojo': '#f44336'
    }

    eventos = []
    for row in datos:
        ultima_revision = row[2]
        if ultima_revision:
            fecha_ultima = datetime.strptime(ultima_revision, '%Y-%m-%d').date()
            fecha_proxima = fecha_ultima + timedelta(days=30)
            if fecha_proxima >= hoy:
                estado = estado_revision(ultima_revision)
                eventos.append({
                    'title': f"Bastidor: {row[0]} (Plaza {row[1]})",
                    'start': fecha_proxima.strftime('%Y-%m-%d'),
                    'color': color_map.get(estado, '#000000'),
                    'extendedProps': {
                        'estado': estado,
                        'plaza': row[1]
                    }
                })

    return jsonify(eventos)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
