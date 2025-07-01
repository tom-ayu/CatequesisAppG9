from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from connectionmongo import get_mongo_connection
from connectiondb import get_connection
import pyodbc
from bson import ObjectId
from datetime import datetime

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

####### NUEVOS ENDPOINTS PARA VALIDACIONES E ÍNDICES #######

# Página principal de consultas específicas
@app.route('/validaciones')
def validaciones_index():
    return render_template('validaciones.html')

# Consulta 1: Listado de catequizandos por nivel y parroquia
@app.route('/consulta-catequizandos-nivel-parroquia')
def consulta_catequizandos_nivel_parroquia():
    try:
        db = get_mongo_connection()
        
        pipeline = [
            {
                "$lookup": {
                    "from": "grupoCatequesis",
                    "localField": "_id",
                    "foreignField": "inscripciones.catequizando_id",
                    "as": "grupo"
                }
            },
            {"$unwind": "$grupo"},
            {
                "$lookup": {
                    "from": "nivelCatecismo",
                    "localField": "grupo.nivelCatequesis_id",
                    "foreignField": "_id",
                    "as": "nivel"
                }
            },
            {
                "$lookup": {
                    "from": "sacramentos",
                    "localField": "sacramentos.sacramento_id",
                    "foreignField": "_id",
                    "as": "sacInfo"
                }
            },
            {
                "$lookup": {
                    "from": "parroquias",
                    "localField": "sacramentos.parroquia_id",
                    "foreignField": "_id",
                    "as": "parroquia"
                }
            },
            {
                "$project": {
                    "nombre": 1,
                    "apellido": 1,
                    "nivel": "$nivel.nombre",
                    "parroquia": "$parroquia.direccion.nombreParroquia"
                }
            }
        ]
        
        resultados = list(db.catequizandos.aggregate(pipeline))
        
        # Convertir ObjectId a string
        for resultado in resultados:
            resultado['_id'] = str(resultado['_id'])
        
        return render_template('consulta_catequizandos_nivel.html', resultados=resultados)
    except Exception as e:
        flash(f"Error en consulta: {e}", "error")
        return render_template('consulta_catequizandos_nivel.html', resultados=[])

# Consulta 2: Sacramentos pendientes
@app.route('/consulta-sacramentos-pendientes')
def consulta_sacramentos_pendientes():
    try:
        db = get_mongo_connection()
        
        query = {
            "$or": [
                {"sacramentos": {"$exists": False}},
                {
                    "$expr": {
                        "$lt": [
                            {"$size": {"$ifNull": ["$sacramentos", []]}},
                            3
                        ]
                    }
                }
            ]
        }
        
        projection = {
            "nombre": 1,
            "apellido": 1,
            "sacramentos": 1
        }
        
        resultados = list(db.catequizandos.find(query, projection))
        
        # Convertir ObjectId a string
        for resultado in resultados:
            resultado['_id'] = str(resultado['_id'])
        
        return render_template('consulta_sacramentos_pendientes.html', resultados=resultados)
    except Exception as e:
        flash(f"Error en consulta: {e}", "error")
        return render_template('consulta_sacramentos_pendientes.html', resultados=[])

# Consulta 3: Reporte de confirmandos para la Vicaría
@app.route('/consulta-confirmandos-vicaria')
def consulta_confirmandos_vicaria():
    try:
        db = get_mongo_connection()
        
        pipeline = [
            {
                "$match": {
                    "sacramentos": {
                        "$elemMatch": {
                            "sacramento_id": 3
                        }
                    }
                }
            },
            {
                "$project": {
                    "nombre": 1,
                    "apellido": 1,
                    "sacramentos": {
                        "$filter": {
                            "input": "$sacramentos",
                            "as": "sac",
                            "cond": {"$eq": ["$$sac.sacramento_id", 3]}
                        }
                    }
                }
            },
            {"$unwind": "$sacramentos"},
            {
                "$project": {
                    "nombre": 1,
                    "apellido": 1,
                    "fechaConfirmacion": "$sacramentos.FechaEmision",
                    "padrino": "$sacramentos.padrino"
                }
            }
        ]
        
        resultados = list(db.catequizandos.aggregate(pipeline))
        
        # Convertir ObjectId a string
        for resultado in resultados:
            resultado['_id'] = str(resultado['_id'])
        
        return render_template('consulta_confirmandos_vicaria.html', resultados=resultados)
    except Exception as e:
        flash(f"Error en consulta: {e}", "error")
        return render_template('consulta_confirmandos_vicaria.html', resultados=[])

if __name__ == '__main__':
    app.run(debug=True)