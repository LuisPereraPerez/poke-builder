from flask import Flask, render_template, request, jsonify
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

app = Flask(__name__)

# Conectar a Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('poke_builder')
session.row_factory = dict_factory  # Para obtener los resultados como diccionarios

# Matriz de efectividad de tipos en Pokémon (simplificada para el ejemplo)
type_chart = {
    'Acero': {'Acero': 0.5, 'Agua': 0.5, 'Eléctrico': 0.5, 'Fuego': 0.5, 'Hada': 2, 'Hielo': 2, 'Roca': 2},
    'Agua': {'Fuego': 2, 'Agua': 0.5, 'Planta': 0.5, 'Tierra': 2, 'Roca': 2, 'Dragón': 0.5},
    'Bicho': {'Acero': 0.5, 'Fantasma': 0.5, 'Fuego': 0.5, 'Hada': 0.5, 'Lucha': 0.5, 'Planta': 2, 'Psíquico': 2, 'Siniestro': 2, 'Veneno': 0.5},
    'Dragón': {'Acero': 0.5, 'Dragón': 2, 'Hada': 0},
    'Eléctrico': {'Agua': 2, 'Eléctrico': 0.5, 'Planta': 0.5, 'Tierra': 0, 'Volador': 2, 'Dragón': 0.5},
    'Fantasma': {'Fantasma': 2, 'Normal': 0, 'Psíquico': 2, 'Siniestro': 0.5},
    'Fuego': {'Fuego': 0.5, 'Agua': 0.5, 'Planta': 2, 'Hielo': 2, 'Bicho': 2, 'Roca': 0.5, 'Dragón': 0.5, 'Acero': 2},
    'Hada': {'Acero': 0.5, 'Dragón': 2, 'Fuego': 0.5, 'Lucha': 2, 'Siniestro': 2, 'Veneno': 0.5},
    'Hielo': {'Fuego': 0.5, 'Agua': 0.5, 'Planta': 2, 'Hielo': 0.5, 'Tierra': 2, 'Volador': 2, 'Dragón': 2, 'Acero': 0.5},
    'Lucha': {'Acero': 2, 'Bicho': 0.5, 'Fantasma': 0, 'Hada': 0.5, 'Hielo': 2,'Normal': 2, 'Psíquico': 0.5, 'Roca': 2, 'Siniestro': 2, 'Veneno': 0.5},
    'Normal': {'Roca': 0.5, 'Fantasma': 0, 'Acero': 0.5},
    'Planta': {'Fuego': 0.5, 'Agua': 2, 'Planta': 0.5, 'Veneno': 0.5, 'Tierra': 2, 'Volador': 0.5, 'Bicho': 0.5, 'Roca': 2, 'Dragón': 0.5, 'Acero': 0.5},
    'Psíquico': {'Acero': 0.5, 'Lucha': 2, 'Psíquico': 0.5, 'Siniestro': 0, 'Veneno': 2},
    'Roca': {'Acero': 0.5, 'Bicho': 2, 'Fuego': 2, 'Hielo': 2, 'Lucha': 0.5, 'Tierra': 0.5, 'Volador': 2},
    'Siniestro': {'Fantasma': 2, 'Hada': 0.5, 'Lucha': 0.5, 'Psíquico': 2, 'Siniestro': 0.5},
    'Tierra': {'Acero': 2, 'Bicho': 0.5, 'Eléctrico': 2, 'Fuego': 2, 'Planta': 0.5, 'Roca': 2, 'Veneno': 2, 'Volador': 0},
    'Veneno': {'Acero': 0, 'Hada': 2, 'Planta': 2, 'Roca': 0.5, 'Fantasma': 0.5, 'Veneno': 0.5, 'Tierra': 0.5},
    'Volador': {'Acero': 0.5, 'Bicho': 2, 'Eléctrico': 0.5, 'Lucha': 2, 'Planta': 2, 'Roca': 0.5}
}

def calcular_ofensiva(tipo_atacante, tipos_defensor):
    """Calcula la efectividad ofensiva del atacante contra el defensor."""
    multiplicador = 1
    if tipo_atacante not in type_chart:
        return multiplicador
    for tipo_defensor in tipos_defensor:
        multiplicador *= type_chart[tipo_atacante].get(tipo_defensor, 1)
    return multiplicador

def evaluar_combate(tipos_A, tipos_B):
    """Evalúa la ventaja de A sobre B considerando ataque y defensa."""
    if not tipos_A or not tipos_B:
        return 1
    ofensiva_A_vs_B = sum(calcular_ofensiva(tipo, tipos_B) for tipo in tipos_A) / max(len(tipos_A), 1)
    return ofensiva_A_vs_B

def obtener_pokemon():
    """Obtiene la lista de Pokémon desde Cassandra."""
    try:
        rows = session.execute("SELECT name, type1, type2 FROM pokemon")
        return [{"name": row["name"], "type1": row["type1"], "type2": row["type2"]} for row in rows]
    except Exception as e:
        print(f"Error al obtener Pokémon: {e}")
        return []

def recomendar_equipo(equipo_rival):
    """Recomienda un equipo basado en el equipo rival."""
    try:
        rows = session.execute("SELECT name, type1, type2 FROM pokemon")
        mejores_pokemon = []

        for pokemon in rows:
            tipos_rival = [[rival["type1"], rival["type2"]] for rival in equipo_rival if rival["type1"] and rival["type2"]]
            ventaja = sum(evaluar_combate([pokemon["type1"], pokemon["type2"]], tipos) for tipos in tipos_rival)
            mejores_pokemon.append((pokemon["name"], ventaja))

        mejores_pokemon.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in mejores_pokemon[:6]]
    except Exception as e:
        print(f"Error al recomendar equipo: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pokemon', methods=['GET'])
def get_pokemon():
    try:
        # Obtener todos los Pokémon desde Cassandra
        rows = session.execute("SELECT name FROM pokemon")
        # Devolver la lista de nombres de Pokémon como JSON
        return jsonify([row["name"] for row in rows])
    except Exception as e:
        print(f"Error al obtener Pokémon: {e}")
        return jsonify([])

@app.route('/recomendar', methods=['POST'])
def recomendar():
    try:
        equipo_rival = request.json.get('equipo', [])
        if len(equipo_rival) < 6:
            return jsonify({"error": "Selecciona 6 Pokémon antes de continuar."}), 400

        # Obtener los tipos de los Pokémon rivales
        equipo_rival_con_tipos = []
        for nombre_pokemon in equipo_rival:
            pokemon = session.execute(
                f"SELECT name, type1, type2 FROM pokemon WHERE name = '{nombre_pokemon}' ALLOW FILTERING"
            ).one()
            if pokemon:
                equipo_rival_con_tipos.append({
                    "name": pokemon["name"],
                    "type1": pokemon["type1"],
                    "type2": pokemon["type2"]
                })

        if len(equipo_rival_con_tipos) < 6:
            return jsonify({"error": "No se encontraron todos los Pokémon en la base de datos."}), 400

        # Obtener todos los Pokémon disponibles
        rows = session.execute("SELECT name, type1, type2 FROM pokemon")
        mejores_pokemon = []

        # Calcular la efectividad de cada Pokémon contra el equipo rival
        for pokemon in rows:
            tipos_rival = [
                [rival["type1"], rival["type2"]] 
                for rival in equipo_rival_con_tipos 
                if rival["type1"] and rival["type2"]
            ]
            ventaja = sum(
                evaluar_combate([pokemon["type1"], pokemon["type2"]], tipos) 
                for tipos in tipos_rival
            )
            mejores_pokemon.append({
                "name": pokemon["name"],
                "ventaja": ventaja
            })

        # Ordenar los Pokémon por ventaja (de mayor a menor)
        mejores_pokemon.sort(key=lambda x: x["ventaja"], reverse=True)

        # Seleccionar los 6 Pokémon más efectivos
        equipo_recomendado = [p["name"] for p in mejores_pokemon[:6]]

        return jsonify({"equipo_recomendado": equipo_recomendado})
    except Exception as e:
        print(f"Error al recomendar equipo: {e}")
        return jsonify({"error": "Error al procesar la solicitud."}), 500

if __name__ == '__main__':
    app.run(debug=True)