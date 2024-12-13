from crypt import methods

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/proyecto/proyectos_gestor', methods=['GET'])
def obtener_proyectos_gestor_id():
    empleado_id = request.args.get('id')

    if not empleado_id:
        return jsonify({"error": "Falta el parámetro 'id' en la solicitud"}), 400

    query = f"""
        SELECT * FROM public."Proyecto" p
        INNER JOIN public."GestoresProyecto" gp ON p.id = gp.proyecto
        WHERE gp.gestor = {empleado_id};
    """

    return ejecutar_sql(query)


@app.route('/proyecto/proyectos_activos', methods=['GET'])
def obtener_proyectos_activos():
    return ejecutar_sql(
        'SELECT nombre, descripcion, fecha_creacion, fecha_inicio, cliente FROM public."Proyecto" WHERE fecha_finalizacion is null OR fecha_finalizacion >= CURRENT_TIMESTAMP;'
    )

@app.route('/proyecto/proyectos', methods=['GET'])
def obtener_proyectos():
    return ejecutar_sql(
        'SELECT * FROM public."Proyecto"'
    )

@app.route('/hola_mundo', methods=['GET'])
def hola_mundo():
    return jsonify({"msg":"Hola Mundo"})


@app.route('/empleado/empleados', methods = ['GET'])
def obtener_empleados():
    resultado1 = ejecutar_sql(
        'SELECT e.nombre AS "nombre", \'Gestor\' AS "empleado" FROM public."Empleado" e INNER JOIN public."Gestor" g ON e.id = g.empleado;'
    )
    resultado2 = ejecutar_sql(
        'SELECT e.nombre AS "nombre", \'Programador\' AS "empleado" FROM public."Empleado" e INNER JOIN public."Programador" p ON e.id = p.empleado;'
    )

    todos_los_empleados = resultado1.json + resultado2.json

    return jsonify(todos_los_empleados)

def ejecutar_sql(query = ""):

    host = "localhost" # Ejemplo: 'localhost'
    port = "5432" # Puerto por defecto de PostgreSQL
    dbname = "alexsoft" # Nombre de la base de datos
    user = "postgres" # Usuario de la base de datos
    password = "postgres" # Contraseña del usuario

    try:
        # Establecer la conexión
        connection = psycopg2.connect(
            host = host,
            port = port,
            dbname = dbname,
            user = user,
            password = password,
            options = "-c search_path=public"
        )

        cursor = connection.cursor()
        cursor.execute(query)

        # Obtener columnas para construit claves JSON
        columnas = [desc[0] for desc in cursor.description]

        # Convertir resultados a JSON
        resultados = cursor.fetchall()
        empleados = [dict(zip(columnas, fila)) for fila in resultados]

        # Cerrar el cursor y la conexión
        cursor.close()
        connection.close()

        return jsonify(empleados)

    except psycopg2.Error as e:
        print("Error: ", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug = True)