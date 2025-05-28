from flask import Flask, render_template, request, redirect, url_for, flash
from connectiondb import get_connection
import pyodbc

app = Flask(__name__)
app.secret_key = 'clave_secreta_123'

@app.route('/bautismos')
def get_bautismos():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT IdBautismo, ParroquiaBautismo FROM CatequesisData.Bautismo")
        bautismos = cursor.fetchall()
        conn.close()
        return bautismos
    except:
        return []

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

if __name__ == '__main__':
    app.run(debug=True)