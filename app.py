from flask import Flask, render_template, request, redirect, url_for, flash
from connection_mongo import get_mongo_connection

app = Flask(__name__)
app.secret_key = 'clave_secreta_123'

# READ
@app.route('/')
def index():
    try:
        db = get_mongo_connection()
        catequizandos = list(db.catequizandos.find())
        return render_template('index.html', catequizandos=catequizandos)
    except Exception as e:
        flash(f'Error al obtener catequizandos: {e}', 'danger')
        return render_template('index.html', catequizandos=[])

# CREATE
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        try:
            db = get_mongo_connection()

            last = db.catequizandos.find_one({"_id": {"$type": "int"}}, sort=[("_id", -1)])
            next_id = last["_id"] + 1 if last else 1

            nuevo = {
                "_id": next_id,
                "nombre": request.form['nombre'],
                "apellido": request.form['apellido'],
                "dob": request.form['dob'],
                "fe_bautismo": True if request.form.get('fe_bautismo') == 'on' else False,
                "tutores": [],
                "sacramentos": None,
                "certificados": None
            }

            db.catequizandos.insert_one(nuevo)
            flash("Catequizando creado exitosamente", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error al crear catequizando: {e}", "danger")
    return render_template('create.html')

# UPDATE
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    db = get_mongo_connection()
    if request.method == 'POST':
        try:
            update_data = {
                "nombre": request.form['nombre'],
                "apellido": request.form['apellido'],
                "dob": request.form['dob'],
                "fe_bautismo": True if request.form.get('fe_bautismo') == 'on' else False
            }
            db.catequizandos.update_one({"_id": int(id)}, {"$set": update_data})
            flash("Catequizando actualizado exitosamente", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error al actualizar: {e}", "danger")
    catequizado = db.catequizandos.find_one({"_id": int(id)})
    return render_template('edit.html', catequizado=catequizado)

# DELETE
@app.route('/delete/<id>')
def delete(id):
    try:
        db = get_mongo_connection()
        db.catequizandos.delete_one({"_id": int(id)})
        flash("Catequizando eliminado exitosamente", "success")
    except Exception as e:
        flash(f"Error al eliminar catequizando: {e}", "danger")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)