from flask import Flask, render_template, request, jsonify
from cassandra.query import dict_factory
from cassandra.cluster import Cluster
from cassandra.util import uuid
import json
import random
from flask import session as flask_session
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)  # Necesario para usar `session`

# Conectar a Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('poke_builder')
session.row_factory = dict_factory

# Matriz de efectividad de tipos en Pokémon
type_chart = {
    'Steel': {'Steel': 0.5, 'Water': 0.5, 'Electric': 0.5, 'Fire': 0.5, 'Fairy': 2, 'Ice': 2, 'Rock': 2},
    'Water': {'Fire': 2, 'Water': 0.5, 'Grass': 0.5, 'Ground': 2, 'Rock': 2, 'Dragon': 0.5},
    'Bug': {'Steel': 0.5, 'Ghost': 0.5, 'Fire': 0.5, 'Fairy': 0.5, 'Fighting': 0.5, 'Grass': 2, 'Psychic': 2, 'Dark': 2, 'Poison': 0.5},
    'Dragon': {'Steel': 0.5, 'Dragon': 2, 'Fairy': 0},
    'Electric': {'Water': 2, 'Electric': 0.5, 'Grass': 0.5, 'Ground': 0, 'Flying': 2, 'Dragon': 0.5},
    'Ghost': {'Ghost': 2, 'Normal': 0, 'Psychic': 2, 'Dark': 0.5},
    'Fire': {'Fire': 0.5, 'Water': 0.5, 'Grass': 2, 'Ice': 2, 'Bug': 2, 'Rock': 0.5, 'Dragon': 0.5, 'Steel': 2},
    'Fairy': {'Steel': 0.5, 'Dragon': 2, 'Fire': 0.5, 'Fighting': 2, 'Dark': 2, 'Poison': 0.5},
    'Ice': {'Fire': 0.5, 'Water': 0.5, 'Grass': 2, 'Ice': 0.5, 'Ground': 2, 'Flying': 2, 'Dragon': 2, 'Steel': 0.5},
    'Fighting': {'Steel': 2, 'Bug': 0.5, 'Ghost': 0, 'Fairy': 0.5, 'Ice': 2, 'Normal': 2, 'Psychic': 0.5, 'Rock': 2, 'Dark': 2, 'Poison': 0.5},
    'Normal': {'Rock': 0.5, 'Ghost': 0, 'Steel': 0.5},
    'Grass': {'Fire': 0.5, 'Water': 2, 'Grass': 0.5, 'Poison': 0.5, 'Ground': 2, 'Flying': 0.5, 'Bug': 0.5, 'Rock': 2, 'Dragon': 0.5, 'Steel': 0.5},
    'Psychic': {'Steel': 0.5, 'Fighting': 2, 'Dark': 0, 'Poison': 2},
    'Rock': {'Steel': 0.5, 'Bug': 2, 'Fire': 2, 'Ice': 2, 'Fighting': 0.5, 'Ground': 0.5, 'Flying': 2},
    'Dark': {'Ghost': 2, 'Fairy': 0.5, 'Fighting': 0.5, 'Psychic': 2, 'Dark': 0.5},
    'Ground': {'Steel': 2, 'Bug': 0.5, 'Electric': 2, 'Fire': 2, 'Grass': 0.5, 'Rock': 2, 'Poison': 2, 'Flying': 0},
    'Poison': {'Steel': 0, 'Fairy': 2, 'Grass': 2, 'Rock': 0.5, 'Ghost': 0.5, 'Poison': 0.5, 'Ground': 0.5},
    'Flying': {'Steel': 0.5, 'Bug': 2, 'Electric': 0.5, 'Fighting': 2, 'Grass': 2, 'Rock': 0.5}
}

def calcular_ofensiva(tipo_atacante, tipos_defensor):
    multiplicador = 1
    if tipo_atacante not in type_chart:
        return multiplicador
    for tipo_defensor in tipos_defensor:
        multiplicador *= type_chart[tipo_atacante].get(tipo_defensor, 1)
    return multiplicador

def calcular_defensiva(tipos_defensor, tipo_atacante):
    return calcular_ofensiva(tipo_atacante, tipos_defensor)

def evaluar_combate_con_bst(tipos_A, tipos_B, bst_A, bst_B):
    """Evalúa la ventaja de A sobre B considerando tipos y BST con peso reducido."""
    if not tipos_A or not tipos_B:
        return 1

    # Calcular ventaja de tipos (principal factor)
    ofensiva_A_vs_B = sum(calcular_ofensiva(tipo, tipos_B) for tipo in tipos_A) / max(len(tipos_A), 1)
    defensiva_A_vs_B = sum(calcular_defensiva(tipos_A, tipo) for tipo in tipos_B) / max(len(tipos_B), 1)
    ventaja_tipos = ofensiva_A_vs_B / defensiva_A_vs_B

    # Reducir el peso del BST
    diferencia_bst = bst_A - bst_B
    factor_bst = 1 + (diferencia_bst / 1000000) # Denominador mayor (1000) para menos influencia
    # Eliminamos el potenciador (factor_bst ** 1.5) para evitar amplificar demasiado

    # Combinar: tipos tienen más peso, BST es un ajuste menor
    return ventaja_tipos #* factor_bst

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/box')
def box():
    return render_template('box.html')

@app.route('/cajas')
def ver_cajas():
    return render_template('cajas.html')

@app.route('/poke-wordle')
def poke_wordle():
    return render_template('poke-wordle.html')

@app.route('/editar-caja')
def editar_caja():
    caja_id = request.args.get('id')
    return render_template('editar_caja.html', caja_id=caja_id)

@app.route('/pokemon', methods=['GET'])
def get_pokemon():
    try:
        rows = session.execute("SELECT name FROM pokemon")
        return jsonify([row["name"] for row in rows])
    except Exception as e:
        print(f"Error al obtener Pokémon: {e}")
        return jsonify([])

@app.route('/recomendar', methods=['POST'])
def recomendar():
    try:
        data = request.json
        equipo_rival_nombres = data.get('equipo', [])
        caja_id = data.get('caja_id')
        
        if len(equipo_rival_nombres) != 6:
            return jsonify({"error": "Debes seleccionar exactamente 6 Pokémon"}), 400

        # Obtener información completa de los Pokémon rivales
        equipo_rival = []
        for nombre_pokemon in equipo_rival_nombres:
            pokemon = session.execute(
                "SELECT name, type1, type2, total FROM pokemon WHERE name = %s ALLOW FILTERING",
                [nombre_pokemon]
            ).one()
            if not pokemon:
                return jsonify({"error": f"Pokémon {nombre_pokemon} no encontrado"}), 400
            equipo_rival.append({
                "name": pokemon["name"],
                "tipos": [t for t in [pokemon["type1"], pokemon["type2"]] if t],
                "bst": pokemon["total"]
            })

        # Determinar Pokémon disponibles
        if caja_id:
            caja = session.execute("SELECT pokemons FROM cajas WHERE id = %s", [uuid.UUID(caja_id)]).one()
            if not caja or not caja["pokemons"]:
                return jsonify({"error": "Caja no encontrada o vacía"}), 404
            pokemons_disponibles_nombres = caja["pokemons"]
        else:
            pokemons_disponibles_nombres = [row["name"] for row in session.execute("SELECT name FROM pokemon")]

        # Calcular ventajas para cada Pokémon disponible
        mejores_pokemon = []
        nombres_rivales = set(equipo_rival_nombres)
        for nombre in pokemons_disponibles_nombres:
            if nombre in nombres_rivales:
                continue
            pokemon = session.execute(
                "SELECT name, type1, type2, total FROM pokemon WHERE name = %s ALLOW FILTERING",
                [nombre]
            ).one()
            if not pokemon:
                continue

            tipos_A = [t for t in [pokemon["type1"], pokemon["type2"]] if t]
            bst_A = pokemon["total"]
            ventaja_total = 0

            # Calcular ventaja contra cada rival
            for rival in equipo_rival:
                ventaja = evaluar_combate_con_bst(tipos_A, rival["tipos"], bst_A, rival["bst"])
                ventaja_total += ventaja

            mejores_pokemon.append({
                "name": pokemon["name"],
                "ventaja": ventaja_total
            })

        # Ordenar y seleccionar los 6 mejores
        mejores_pokemon.sort(key=lambda x: x["ventaja"], reverse=True)
        equipo_recomendado = [p["name"] for p in mejores_pokemon[:6]]

        return jsonify({
            "equipo_recomendado": equipo_recomendado,
            "caja_usada": bool(caja_id),
            "pokemons_considerados": len(pokemons_disponibles_nombres)
        })

    except Exception as e:
        print(f"Error en endpoint /recomendar: {str(e)}")
        return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500

# Rutas para cajas (sin cambios)
@app.route('/crear-caja', methods=['POST'])
def crear_caja():
    try:
        data = request.json
        nombre = data.get('nombre')
        pokemons = data.get('pokemons', [])
        if not nombre or len(pokemons) != 30:
            return jsonify({"error": "El nombre de la caja y 30 Pokémon son requeridos."}), 400
        caja_id = uuid.uuid1()
        session.execute("INSERT INTO cajas (id, nombre, pokemons) VALUES (%s, %s, %s)", (caja_id, nombre, pokemons))
        return jsonify({"message": "Caja creada correctamente.", "id": str(caja_id)})
    except Exception as e:
        print(f"Error al crear la caja: {e}")
        return jsonify({"error": "Error al procesar la solicitud."}), 500

@app.route('/obtener-cajas', methods=['GET'])
def obtener_cajas():
    try:
        rows = session.execute("SELECT id, nombre, pokemons FROM cajas")
        cajas = [{"id": str(row["id"]), "nombre": row["nombre"], "pokemons": row["pokemons"]} for row in rows]
        return jsonify(cajas)
    except Exception as e:
        print(f"Error al obtener las cajas: {e}")
        return jsonify({"error": "Error al procesar la solicitud."}), 500

@app.route('/obtener-caja/<caja_id>', methods=['GET'])
def obtener_caja(caja_id):
    try:
        caja = session.execute("SELECT nombre, pokemons FROM cajas WHERE id = %s", (uuid.UUID(caja_id),)).one()
        if caja:
            return jsonify({"nombre": caja["nombre"], "pokemons": caja["pokemons"]})
        return jsonify({"error": "Caja no encontrada"}), 404
    except Exception as e:
        print(f"Error al obtener la caja: {e}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@app.route('/actualizar-caja/<caja_id>', methods=['PUT'])
def actualizar_caja(caja_id):
    try:
        data = request.json
        nombre = data.get('nombre')
        pokemons = data.get('pokemons', [])
        if not nombre:
            return jsonify({"error": "El nombre de la caja es requerido."}), 400
        session.execute("UPDATE cajas SET nombre = %s, pokemons = %s WHERE id = %s", (nombre, pokemons, uuid.UUID(caja_id)))
        return jsonify({"message": "Caja actualizada correctamente."})
    except Exception as e:
        print(f"Error al actualizar la caja: {e}")
        return jsonify({"error": "Error al procesar la solicitud."}), 500

@app.route('/eliminar-caja/<caja_id>', methods=['DELETE'])
def eliminar_caja(caja_id):
    try:
        session.execute("DELETE FROM cajas WHERE id = %s", (uuid.UUID(caja_id),))
        return jsonify({"message": "Caja eliminada correctamente."})
    except Exception as e:
        print(f"Error al eliminar la caja: {e}")
        return jsonify({"error": "Error al procesar la solicitud."}), 500
    
@app.route('/pokemon-caracteristicas', methods=['GET'])
def get_pokemon_caracteristicas():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Nombre del Pokémon requerido"}), 400
        
        pokemon = session.execute(
            "SELECT name, type1, type2, hp, attack, defense, sp_attack, sp_defense, speed, generation, lengendary "
            "FROM pokemon WHERE name = %s ALLOW FILTERING",
            [name]
        ).one()
        
        if not pokemon:
            return jsonify({"error": f"Pokémon {name} no encontrado"}), 404
        
        return jsonify({
            "name": pokemon["name"],
            "type1": pokemon["type1"],
            "type2": pokemon["type2"],
            "hp": pokemon["hp"],
            "attack": pokemon["attack"],
            "defense": pokemon["defense"],
            "sp_attack": pokemon["sp_attack"],
            "sp_defense": pokemon["sp_defense"],
            "speed": pokemon["speed"],
            "generation": pokemon["generation"],
            "lengendary": pokemon["lengendary"]
        })
    except Exception as e:
        print(f"Error al obtener características del Pokémon: {e}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@app.route('/pokemon-aleatorio', methods=['GET'])
def pokemon_aleatorio():
    try:
        # Obtener todos los nombres
        rows = session.execute("SELECT name FROM pokemon")
        nombres = [row["name"] for row in rows]

        if not nombres:
            return jsonify({"error": "No hay Pokémon disponibles."}), 404

        # Elegir uno al azar
        nombre_aleatorio = random.choice(nombres)

        # Obtener sus características
        pokemon = session.execute(
            "SELECT name, type1, type2, hp, attack, defense, sp_attack, sp_defense, speed, generation, lengendary "
            "FROM pokemon WHERE name = %s ALLOW FILTERING",
            [nombre_aleatorio]
        ).one()

        if not pokemon:
            return jsonify({"error": "No se pudo encontrar el Pokémon seleccionado"}), 404

        return jsonify({
            "name": pokemon["name"],
            "type1": pokemon["type1"],
            "type2": pokemon["type2"],
            "hp": pokemon["hp"],
            "attack": pokemon["attack"],
            "defense": pokemon["defense"],
            "sp_attack": pokemon["sp_attack"],
            "sp_defense": pokemon["sp_defense"],
            "speed": pokemon["speed"],
            "generation": pokemon["generation"],
            "lengendary": pokemon["lengendary"]
        })
    except Exception as e:
        print(f"Error al obtener Pokémon aleatorio: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    
@app.route('/generar-wordle', methods=['GET'])
def generar_wordle():
    try:
        rows = session.execute("SELECT name FROM pokemon")
        nombres = [row["name"] for row in rows]
        if not nombres:
            return jsonify({"error": "No hay Pokémon disponibles."}), 404

        nombre_aleatorio = random.choice(nombres)

        # Guardamos en la sesión
        flask_session['pokemon_wordle'] = nombre_aleatorio

        return jsonify({"message": "Pokémon generado para Wordle."})
    except Exception as e:
        print(f"Error al generar Pokémon Wordle: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/verificar-wordle', methods=['GET'])
def verificar_wordle():
    try:
        nombre_intento = request.args.get('nombre')
        objetivo_nombre = flask_session.get('pokemon_wordle')

        if not objetivo_nombre:
            return jsonify({"error": "No se ha generado un Pokémon Wordle aún."}), 400

        intento = session.execute("SELECT * FROM pokemon WHERE name = %s ALLOW FILTERING", [nombre_intento]).one()
        objetivo = session.execute("SELECT * FROM pokemon WHERE name = %s ALLOW FILTERING", [objetivo_nombre]).one()

        if not intento:
            return jsonify({"error": f"No se encontró el Pokémon '{nombre_intento}'"}), 404

        def comparar_stats(valor1, valor2):
            """Función solo para stats (hp, attack, etc.) que compara mayor/menor/igual"""
            if valor1 == valor2:
                return "correct"
            return "high" if valor1 > valor2 else "low"

        def comparar_igual(valor1, valor2):
            """Función para el resto de atributos que solo compara igual/diferente"""
            return "correct" if valor1 == valor2 else "incorrect"

        comparacion = {
            "name": {"value": intento["name"], "estado": comparar_igual(intento["name"], objetivo["name"])},
            "type1": {"value": intento["type1"], "estado": comparar_igual(intento["type1"], objetivo["type1"])},
            "type2": {"value": intento["type2"], "estado": comparar_igual(intento["type2"], objetivo["type2"])},
            "hp": {"value": intento["hp"], "estado": comparar_stats(intento["hp"], objetivo["hp"])},
            "attack": {"value": intento["attack"], "estado": comparar_stats(intento["attack"], objetivo["attack"])},
            "defense": {"value": intento["defense"], "estado": comparar_stats(intento["defense"], objetivo["defense"])},
            "sp_attack": {"value": intento["sp_attack"], "estado": comparar_stats(intento["sp_attack"], objetivo["sp_attack"])},
            "sp_defense": {"value": intento["sp_defense"], "estado": comparar_stats(intento["sp_defense"], objetivo["sp_defense"])},
            "speed": {"value": intento["speed"], "estado": comparar_stats(intento["speed"], objetivo["speed"])},
            "generation": {"value": intento["generation"], "estado": comparar_igual(intento["generation"], objetivo["generation"])},
            "legendary": {"value": intento["lengendary"], "estado": comparar_igual(intento["lengendary"], objetivo["lengendary"])}
        }

        return jsonify(comparacion)

    except Exception as e:
        print(f"Error en Wordle: {e}")
        return jsonify({"error": "Error al verificar intento"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)