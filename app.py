from flask import Flask, render_template, request, redirect, url_for
from connectiondb import get_connection

app = Flask(__name__)

@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT IdCatequizado, Nombre, Apellido, Telefono, FechaNacimiento FROM CatequesisData.Catequizado")
    catequizados = cursor.fetchall()
    conn.close()
    return render_template('index.html', catequizados=catequizados)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        fecha_nac = request.form['fecha']
        id_bautismo = request.form['id_bautismo']

        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM CatequesisData.Bautismo WHERE IdBautismo = ?", (id_bautismo,))
        if cursor.fetchone() is None:
            conn.close()
            return render_template('create.html', error="El ID de Bautismo no existe. Ingréselo correctamente.")
        
        cursor.execute("""
            INSERT INTO CatequesisData.Catequizado (Nombre, Apellido, Telefono, FechaNacimiento, IdBautismo)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, apellido, telefono, fecha_nac, id_bautismo))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        fecha_nac = request.form['fecha']
        id_bautismo = request.form['id_bautismo']
        cursor.execute("""
            UPDATE CatequesisData.Catequizado
            SET Nombre=?, Apellido=?, Telefono=?, FechaNacimiento=?, IdBautismo=?
            WHERE IdCatequizado=?
        """, (nombre, apellido, telefono, fecha_nac, id_bautismo, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM CatequesisData.Catequizado WHERE IdCatequizado=?", (id,))
    catequizado = cursor.fetchone()
    conn.close()
    return render_template('edit.html', catequizado=catequizado)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CatequesisData.Catequizado WHERE IdCatequizado=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
