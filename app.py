from flask import Flask, render_template, request, redirect, url_for, flash
from connectionmongo import get_mongo_connection
from connectiondb import get_connection
import pyodbc
app = Flask(__name__)
app.secret_key = 'clave_secreta_123'

####### READ (SQL) #######
@app.route('/')
def index():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC CatequesisData.ObtenerCatequizados")
        catequizados = cursor.fetchall()
        conn.close()
        return render_template('index.html', catequizados=catequizados)
    except pyodbc.Error as e:
        flash(f'Error al obtener los catequizados: {e.args[1]}', 'error')
        return render_template('index.html', catequizados=[])

####### CREATE (SQL) #######
@app.route('/create', methods=['GET', 'POST'])
def create():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT IdBautismo, ParroquiaBautismo FROM CatequesisData.Bautismo")
    bautismos = cursor.fetchall()

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        fecha_nac = request.form['fecha']
        id_bautismo = request.form['id_bautismo']

        try:
            cursor.execute("EXEC CatequesisData.CrearCatequizado ?,?,?,?,?",
                           (nombre, apellido, telefono, fecha_nac, id_bautismo))
            conn.commit()
            flash('Catequizado creado exitosamente.', 'success')
            return redirect(url_for('index'))
        except pyodbc.Error as e:
            flash(f'Error al crear catequizado: {e.args[1]}', 'error')

    conn.close()
    return render_template('create.html', bautismos=bautismos)

####### EDIT (SQL) #######
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT IdBautismo, ParroquiaBautismo FROM CatequesisData.Bautismo")
        bautismos = cursor.fetchall()

        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            telefono = request.form['telefono']
            fecha_nac = request.form['fecha']
            id_bautismo = request.form['id_bautismo']

            try:
                cursor.execute(
                    "EXEC CatequesisData.ActualizarCatequizado ?, ?, ?, ?, ?, ?",
                    (id, nombre, apellido, telefono, fecha_nac, id_bautismo)
                )
                conn.commit()
                flash('Catequizado actualizado correctamente.', 'success')
                return redirect(url_for('index'))
            except pyodbc.Error as e:
                flash(f'Error al actualizar: {e.args[1]}', 'error')

        cursor.execute("SELECT * FROM CatequesisData.Catequizado WHERE IdCatequizado=?", (id,))
        catequizado = cursor.fetchone()
        conn.close()

        if not catequizado:
            flash('Catequizado no encontrado.', 'error')
            return redirect(url_for('index'))

        return render_template('edit.html', catequizado=catequizado, bautismos=bautismos)

    except pyodbc.Error as e:
        flash(f'Error general: {e.args[1]}', 'error')
        return redirect(url_for('index'))

####### DELETE (SQL) #######
@app.route('/delete/<int:id>')
def delete(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC CatequesisData.EliminarCatequizado ?", (id,))
        conn.commit()
        conn.close()
        flash('Catequizado eliminado exitosamente.', 'success')
    except pyodbc.Error as e:
        flash(f'Error al eliminar: {e.args[1]}', 'error')

    return redirect(url_for('index'))

####### REPORTES (MONGODB) #######
@app.route('/reporte-general')
def reporte_general():
    try:
        db = get_mongo_connection()
        datos = {}

        # Recorre todas las colecciones y guarda sus documentos
        for nombre_coleccion in db.list_collection_names():
            coleccion = db[nombre_coleccion]
            documentos = list(coleccion.find())
            
            # Convertir _id (ObjectId) a string para evitar errores en Jinja2
            for doc in documentos:
                doc['_id'] = str(doc['_id'])
            datos[nombre_coleccion] = documentos

        return render_template('reporte_general.html', datos=datos)
    except Exception as e:
        flash(f"Error al obtener el reporte general: {e}", "danger")
        return render_template('reporte_general.html', datos={})

if __name__ == '__main__':
    app.run(debug=True)