from flask import Flask, render_template, request, redirect, url_for, flash
from connectionmongo import get_mongo_connection
from connectiondb import get_connection
import pyodbc

app = Flask(__name__)
app.secret_key = 'clave_secreta_123'

####### READ (SQL) #######
@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC sp_ReadCatequizando")
    rows = cursor.fetchall()
    conn.close()

    catequizandos = [{
        'Id': row[0],
        'Nombre': row[1],
        'Apellido': row[2],
        'FechaNacimiento': row[3],
        'FeBautismo': bool(row[4])
    } for row in rows]

    return render_template('index.html', catequizandos=catequizandos)

####### CREATE (SQL) #######
@app.route('/create', methods=['GET', 'POST'])
def create_catequizando():
    if request.method == 'POST':
        data = request.form
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_CreateCatequizando ?, ?, ?, ?",
                data['Nombre'],
                data['Apellido'],
                data['FechaNacimiento'],
                int(data['FeBautismo'])
            )
            conn.commit()
            conn.close()
            flash("Catequizando registrado con éxito", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error al registrar: {e}", "error")
            return redirect(url_for('create_catequizando'))
    return render_template('create.html')


####### EDIT (SQL) #######
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def update_catequizando(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.form
        cursor.execute(
            "EXEC sp_UpdateCatequizando ?, ?, ?, ?, ?",
            id, data['Nombre'], data['Apellido'],
            data['FechaNacimiento'], int(data['FeBautismo'])
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("EXEC sp_ReadCatequizandoPorId ?", id)
    row = cursor.fetchone()
    conn.close()

    if row:
        catequizando = {
            'Id': row[0],
            'Nombre': row[1],
            'Apellido': row[2],
            'FechaNacimiento': row[3],
            'FeBautismo': bool(row[4])
        }
        return render_template('edit.html', catequizando=catequizando)
    return 'No encontrado', 404

####### DELETE (SQL) #######
@app.route('/delete/<int:id>', methods=['GET'])
def delete_catequizando(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC sp_DeleteCatequizando ?", id)
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

####### REPORTES (MONGODB) #######
@app.route('/reporte-general')
def reporte_general():
    try:
        db = get_mongo_connection()
        datos = {}

        for nombre_coleccion in db.list_collection_names():
            coleccion = db[nombre_coleccion]
            documentos = list(coleccion.find())
            
            for doc in documentos:
                doc['_id'] = str(doc['_id'])
            datos[nombre_coleccion] = documentos

        return render_template('reporte_general.html', datos=datos)
    except Exception as e:
        flash(f"Error al obtener el reporte general: {e}", "danger")
        return render_template('reporte_general.html', datos={})

if __name__ == '__main__':
    app.run(debug=True)