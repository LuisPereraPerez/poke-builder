from cassandra.query import dict_factory
from cassandra.cluster import Cluster

# Configuración de Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('poke_builder')
session.row_factory = dict_factory

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

def calcular_ventaja(tipos_atacante, tipos_defensor):
    """
    Calcula la ventaja de tipos entre un Pokémon atacante y un defensor.
    
    Args:
        tipos_atacante (list): Lista de tipos del Pokémon atacante (ej. ['Fire', 'Flying']).
        tipos_defensor (list): Lista de tipos del Pokémon defensor (ej. ['Grass', 'Poison']).
    
    Returns:
        float: Multiplicador de daño total (ej. 4.0 significa 4x de daño).
    """
    ventaja_total = 1.0
    
    for tipo_atacante in tipos_atacante:
        for tipo_defensor in tipos_defensor:
            # Obtener la efectividad del tipo_atacante contra tipo_defensor
            efectividad = type_chart.get(tipo_atacante, {}).get(tipo_defensor, 1.0)
            ventaja_total *= efectividad
    
    return ventaja_total

def evaluar_combate(pokemon_mio, pokemon_rival):
    try:
        # Obtener información de ambos Pokémon
        def get_pokemon_info(name):
            result = session.execute(
                "SELECT name, type1, type2, total, attack, defense, sp_attack, sp_defense, hp, speed "
                "FROM pokemon WHERE name = %s ALLOW FILTERING",
                [name]
            ).one()
            if not result:
                raise ValueError(f"Pokémon {name} no encontrado en la base de datos")
            return result

        try:
            mi_pokemon = get_pokemon_info(pokemon_mio)
            rival_pokemon = get_pokemon_info(pokemon_rival)
        except ValueError as e:
            print(e)
            return

        # Procesar tipos (eliminar None si type2 es null)
        mis_tipos = [t for t in [mi_pokemon["type1"], mi_pokemon["type2"]] if t]
        rival_tipos = [t for t in [rival_pokemon["type1"], rival_pokemon["type2"]] if t]

        ventaja = calcular_ventaja(mis_tipos, rival_tipos)

        # Mostrar resumen del combate
        print(f"\n⚔️ COMBATE: {mi_pokemon['name']} ({'/'.join(mis_tipos)}) vs {rival_pokemon['name']} ({'/'.join(rival_tipos)})")
        print(f"📊 Ventaja de tipos: {ventaja:.2f}x")

        # Mostrar efectividades específicas
        print("\n🔍 Efectividades detalladas:")
        for mi_tipo in mis_tipos:
            for rival_tipo in rival_tipos:
                efect = type_chart.get(mi_tipo, {}).get(rival_tipo, 1)
                print(f"- {mi_tipo} → {rival_tipo}: {efect}x")

    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")

# Ejemplo de uso
if __name__ == "__main__":
    print("=== SIMULADOR DE COMBATES POKÉMON ===")
    pokemon_mio = input("Tu Pokémon: ").strip().title()
    pokemon_rival = input("Pokémon rival: ").strip().title()
    evaluar_combate(pokemon_mio, pokemon_rival)