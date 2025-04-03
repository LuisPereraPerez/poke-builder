from cassandra.query import dict_factory
from cassandra.cluster import Cluster
import statistics

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

def mostrar_estadisticas_pokemon(mi_pokemon, rival_pokemon, mis_tipos, rival_tipos):
    """Muestra las estadísticas de ambos Pokémon en formato legible."""

    stats_mio = [mi_pokemon.get('hp'), mi_pokemon.get('attack'), mi_pokemon.get('defense'), 
                 mi_pokemon.get('sp_attack'), mi_pokemon.get('sp_defense'), mi_pokemon.get('speed')]
    
    stats_rival = [rival_pokemon.get('hp'), rival_pokemon.get('attack'), rival_pokemon.get('defense'), 
                 rival_pokemon.get('sp_attack'), rival_pokemon.get('sp_defense'), rival_pokemon.get('speed')]

    print("\n--- Estadísticas ---")
    print(f"\n{mi_pokemon['name'].upper()}")
    print(f"  - Tipos: {mis_tipos}")
    print(f"  - HP: {mi_pokemon.get('hp', '?')}")
    print(f"  - Ataque: {mi_pokemon.get('attack', '?')}")
    print(f"  - Defensa: {mi_pokemon.get('defense', '?')}")
    print(f"  - Ataque Especial: {mi_pokemon.get('sp_attack', '?')}")
    print(f"  - Defensa Especial: {mi_pokemon.get('sp_defense', '?')}")
    print(f"  - Velocidad: {mi_pokemon.get('speed', '?')}")
    print(f"  - Total: {mi_pokemon.get('total', '?')}")
    print(f"  - Media: {statistics.mean(stats_mio):.2f}")
    print(f"  - Desviación estándar: {statistics.stdev(stats_mio):.2f}")

    print(f"\n{rival_pokemon['name'].upper()}")
    print(f"  - Tipos: {rival_tipos}")
    print(f"  - HP: {rival_pokemon.get('hp', '?')}")
    print(f"  - Ataque: {rival_pokemon.get('attack', '?')}")
    print(f"  - Defensa: {rival_pokemon.get('defense', '?')}")
    print(f"  - Ataque Especial: {rival_pokemon.get('sp_attack', '?')}")
    print(f"  - Defensa Especial: {rival_pokemon.get('sp_defense', '?')}")
    print(f"  - Velocidad: {rival_pokemon.get('speed', '?')}")
    print(f"  - Total: {rival_pokemon.get('total', '?')}")
    print(f"  - Media: {statistics.mean(stats_rival):.2f}")
    print(f"  - Desviación estándar: {statistics.stdev(stats_rival):.2f}")


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

        mostrar_estadisticas_pokemon(mi_pokemon, rival_pokemon, mis_tipos, rival_tipos)

        ventaja = calcular_ventaja(mis_tipos, rival_tipos)
        ventaja_rival = calcular_ventaja(rival_tipos, mis_tipos)

        # Mostrar resumen del combate
        print(f"\n⚔ COMBATE: {mi_pokemon['name']} ({'/'.join(mis_tipos)}) vs {rival_pokemon['name']} ({'/'.join(rival_tipos)})")
        print(f"📊 Ventaja de tipos: {ventaja:.2f}x")

        # Mostrar efectividades específicas
        print("\n🔍 Efectividades detalladas:")
        for mi_tipo in mis_tipos:
            for rival_tipo in rival_tipos:
                efect = type_chart.get(mi_tipo, {}).get(rival_tipo, 1)
                print(f"- {mi_tipo} → {rival_tipo}: {efect}x")

        # ---- NUEVA SECCIÓN: EVALUACIÓN DE ESTADÍSTICAS ----
        print("\n📈 EVALUACIÓN DE ESTADÍSTICAS:")
        
        # Calcular estadísticas ajustadas por ventaja de tipos
        ataque_ajustado_mio = mi_pokemon['attack'] * ventaja
        ataque_especial_ajustado_mio = mi_pokemon['sp_attack'] * ventaja
        
        # Comparar estadísticas clave
        def comparar_estadisticas(nombre_stat, stat_mio, stat_rival, ajuste_tipos=False):
            diferencia = stat_mio - stat_rival
            if ajuste_tipos:
                diferencia = diferencia * ventaja
            
            if diferencia > 0:
                return f"{nombre_stat}: A TU FAVOR (+{diferencia:.1f})"
            elif diferencia < 0:
                return f"{nombre_stat}: EN CONTRA ({diferencia:.1f})"
            else:
                return f"{nombre_stat}: EMPATE"
        
        # Comparar estadísticas básicas
        print("\n⚖ COMPARACIÓN DIRECTA:")
        print(comparar_estadisticas("ATAQUE", mi_pokemon['attack'], rival_pokemon['attack']))
        print(comparar_estadisticas("ATAQUE ESP.", mi_pokemon['sp_attack'], rival_pokemon['sp_attack']))
        print(comparar_estadisticas("DEFENSA", mi_pokemon['defense'], rival_pokemon['defense']))
        print(comparar_estadisticas("DEFENSA ESP.", mi_pokemon['sp_defense'], rival_pokemon['sp_defense']))
        print(comparar_estadisticas("VELOCIDAD", mi_pokemon['speed'], rival_pokemon['speed']))
        print(comparar_estadisticas("HP", mi_pokemon['hp'], rival_pokemon['hp']))
        
        # Comparar estadísticas ajustadas por tipos
        print("\n🎯 CONSIDERANDO VENTAJA DE TIPOS:")
        print(f"ATAQUE AJUSTADO: {ataque_ajustado_mio:.1f} vs {rival_pokemon['defense']}")
        print(f"ATAQUE ESP. AJUSTADO: {ataque_especial_ajustado_mio:.1f} vs {rival_pokemon['sp_defense']}")
        
        # Evaluación general
        print("\n🔮 PREDICCIÓN DEL COMBATE:")
        
        # Puntuación basada en estadísticas y tipos
        puntuacion = 0
        
        # Comparar velocidad (importante para atacar primero)
        if mi_pokemon['speed'] > rival_pokemon['speed']:
            puntuacion += 1
            print("- VENTAJA DE VELOCIDAD: Atacarás primero")
        else:
            puntuacion -= 1
            print("- DESVENTAJA DE VELOCIDAD: El rival atacará primero")
        
        # Comparar ataque físico
        if ataque_ajustado_mio > rival_pokemon['defense']:
            puntuacion += 1
            print("- ATAQUE FÍSICO: Puedes superar su defensa")
        else:
            puntuacion -= 0.5
            print("- ATAQUE FÍSICO: Dificultad para superar su defensa")
        
        # Comparar ataque especial
        if ataque_especial_ajustado_mio > rival_pokemon['sp_defense']:
            puntuacion += 1
            print("- ATAQUE ESPECIAL: Puedes superar su defensa especial")
        else:
            puntuacion -= 0.5
            print("- ATAQUE ESPECIAL: Dificultad para superar su defensa especial")
        
        # Comparar defensas
        if mi_pokemon['defense'] > rival_pokemon['attack']:
            puntuacion += 0.5
            print("- DEFENSA: Resistes bien sus ataques físicos")
        
        if mi_pokemon['sp_defense'] > rival_pokemon['sp_attack']:
            puntuacion += 0.5
            print("- DEFENSA ESPECIAL: Resistes bien sus ataques especiales")
        
        # Evaluar ventaja de tipos
        if ventaja > 1.5:
            puntuacion += 1.5
            print("- GRAN VENTAJA DE TIPOS: Tienes mucha efectividad contra el rival")
        elif ventaja > 1:
            puntuacion += 0.5
            print("- VENTAJA DE TIPOS: Eres efectivo contra el rival")
        elif ventaja < 0.5:
            puntuacion -= 1.5
            print("- GRAN DESVENTAJA DE TIPOS: El rival resiste mucho tus ataques")
        elif ventaja < 1:
            puntuacion -= 0.5
            print("- DESVENTAJA DE TIPOS: El rival resiste tus ataques")
        
        # Mostrar resultado final
        print("\n🏆 RESULTADO:")
        if puntuacion >= 2:
            print("¡COMBATE MUY FAVORABLE! Tienes grandes posibilidades de ganar")
        elif puntuacion >= 1:
            print("¡COMBATE FAVORABLE! Tienes ventaja sobre el rival")
        elif puntuacion >= -1:
            print("¡COMBATE EQUILIBRADO! El resultado es impredecible")
        else:
            print("¡COMBATE DESFAVORABLE! El rival tiene ventaja")

    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")

def evaluar_combates(mis_pokemons, pokemon_rival):
    try:
        # Obtener información del Pokémon rival una sola vez
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
            rival_pokemon = get_pokemon_info(pokemon_rival)
        except ValueError as e:
            print(e)
            return

        rival_tipos = [t for t in [rival_pokemon["type1"], rival_pokemon["type2"]] if t]
        
        resultados = []
        
        for pokemon_mio in mis_pokemons:
            try:
                mi_pokemon = get_pokemon_info(pokemon_mio)
                mis_tipos = [t for t in [mi_pokemon["type1"], mi_pokemon["type2"]] if t]
                
                ventaja = calcular_ventaja(mis_tipos, rival_tipos)
                ventaja_rival = calcular_ventaja(rival_tipos, mis_tipos)
                
                # Calcular puntuación (similar a la función anterior pero sin imprimir)
                puntuacion = 0
                
                # Velocidad
                if mi_pokemon['speed'] > rival_pokemon['speed']:
                    puntuacion += 1
                
                # Ataque físico
                ataque_ajustado_mio = mi_pokemon['attack'] * ventaja
                if ataque_ajustado_mio > rival_pokemon['defense']:
                    puntuacion += 1
                
                # Ataque especial
                ataque_especial_ajustado_mio = mi_pokemon['sp_attack'] * ventaja
                if ataque_especial_ajustado_mio > rival_pokemon['sp_defense']:
                    puntuacion += 1
                
                # Defensas
                if mi_pokemon['defense'] > rival_pokemon['attack']:
                    puntuacion += 0.5
                
                if mi_pokemon['sp_defense'] > rival_pokemon['sp_attack']:
                    puntuacion += 0.5
                
                # Ventaja de tipos
                if ventaja > 1.5:
                    puntuacion += 1.5
                elif ventaja > 1:
                    puntuacion += 0.5
                elif ventaja < 0.5:
                    puntuacion -= 1.5
                elif ventaja < 1:
                    puntuacion -= 0.5
                
                # Guardar resultados
                resultados.append({
                    'pokemon': pokemon_mio,
                    'puntuacion': puntuacion,
                    'ventaja_tipos': ventaja,
                    'stats': mi_pokemon
                })
                
            except Exception as e:
                print(f"Error al evaluar {pokemon_mio}: {str(e)}")
                continue
        
        # Ordenar resultados por puntuación (de mayor a menor)
        resultados.sort(key=lambda x: x['puntuacion'], reverse=True)
        
        # Mostrar ranking
        print(f"\n🏆 RANKING CONTRA {pokemon_rival.upper()} ({'/'.join(rival_tipos)})")
        print("="*50)
        for i, res in enumerate(resultados, 1):
            print(f"{i}. {res['pokemon'].upper()} ({'/'.join([t for t in [res['stats']['type1'], res['stats']['type2']] if t])})")
            print(f"   Puntuación: {res['puntuacion']:.2f}")
            print(f"   Ventaja de tipos: {res['ventaja_tipos']:.2f}x")
            print(f"   Total stats: {res['stats']['total']}")
            print("-"*50)
        
        # Mostrar el mejor
        if resultados:
            mejor = resultados[0]
            print(f"\n✨ MEJOR OPCIÓN: {mejor['pokemon'].upper()} con puntuación {mejor['puntuacion']:.2f}")
            print("🔍 Detalles del combate:")
            evaluar_combate(mejor['pokemon'], pokemon_rival)
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")

def evaluar_mejor_equipo(mis_pokemons, pokemons_rivales):
    try:
        # Obtener información de todos los Pokémon de una vez
        def get_pokemon_info(name):
            result = session.execute(
                "SELECT name, type1, type2, total, attack, defense, sp_attack, sp_defense, hp, speed "
                "FROM pokemon WHERE name = %s ALLOW FILTERING",
                [name]
            ).one()
            if not result:
                raise ValueError(f"Pokémon {name} no encontrado en la base de datos")
            return result

        # Primero verificar que todos los Pokémon existen
        try:
            mis_pokemons_info = {p: get_pokemon_info(p) for p in mis_pokemons}
            rivales_info = {p: get_pokemon_info(p) for p in pokemons_rivales}
        except ValueError as e:
            print(e)
            return

        # Evaluar todos contra todos
        resultados = []
        disponibles = mis_pokemons.copy()
        
        for rival in pokemons_rivales:
            if not disponibles:
                print("\n⚠ No hay más Pokémon disponibles para asignar")
                break
                
            rival_info = rivales_info[rival]
            rival_tipos = [t for t in [rival_info["type1"], rival_info["type2"]] if t]
            
            mejor_pokemon = None
            mejor_puntuacion = -float('inf')
            
            for mio in disponibles:
                mi_info = mis_pokemons_info[mio]
                mis_tipos = [t for t in [mi_info["type1"], mi_info["type2"]] if t]
                
                ventaja = calcular_ventaja(mis_tipos, rival_tipos)
                
                # Calcular puntuación (mismo sistema que antes)
                puntuacion = 0
                
                # Velocidad
                if mi_info['speed'] > rival_info['speed']:
                    puntuacion += 1
                
                # Ataque físico
                ataque_ajustado_mio = mi_info['attack'] * ventaja
                if ataque_ajustado_mio > rival_info['defense']:
                    puntuacion += 1
                
                # Ataque especial
                ataque_especial_ajustado_mio = mi_info['sp_attack'] * ventaja
                if ataque_especial_ajustado_mio > rival_info['sp_defense']:
                    puntuacion += 1
                
                # Defensas
                if mi_info['defense'] > rival_info['attack']:
                    puntuacion += 0.5
                
                if mi_info['sp_defense'] > rival_info['sp_attack']:
                    puntuacion += 0.5
                
                # Ventaja de tipos
                if ventaja > 1.5:
                    puntuacion += 1.5
                elif ventaja > 1:
                    puntuacion += 0.5
                elif ventaja < 0.5:
                    puntuacion -= 1.5
                elif ventaja < 1:
                    puntuacion -= 0.5
                
                # Verificar si es el mejor hasta ahora
                if puntuacion > mejor_puntuacion:
                    mejor_puntuacion = puntuacion
                    mejor_pokemon = mio
            
            # Asignar el mejor Pokémon encontrado
            if mejor_pokemon:
                resultados.append({
                    'rival': rival,
                    'mi_pokemon': mejor_pokemon,
                    'puntuacion': mejor_puntuacion,
                    'ventaja_tipos': calcular_ventaja(
                        [t for t in [mis_pokemons_info[mejor_pokemon]["type1"], 
                                    mis_pokemons_info[mejor_pokemon]["type2"]] if t],
                        rival_tipos
                    )
                })
                disponibles.remove(mejor_pokemon)
        
        # Mostrar resultados
        print("\n🎯 ASIGNACIÓN ÓPTIMA DE POKÉMON")
        print("="*70)
        print(f"Tus Pokémon: {', '.join(mis_pokemons)}")
        print(f"Pokémon rivales: {', '.join(pokemons_rivales)}")
        print("="*70)
        
        for res in resultados:
            print(f"\n⚔ CONTRA {res['rival'].upper()}:")
            print(f"   - TU MEJOR OPCIÓN: {res['mi_pokemon'].upper()}")
            print(f"   - Puntuación: {res['puntuacion']:.2f}")
            print(f"   - Ventaja de tipos: {res['ventaja_tipos']:.2f}x")
            print("-"*50)
        
        # Mostrar Pokémon no asignados (si los hay)
        if disponibles:
            print(f"\n📌 TUS POKÉMON NO ASIGNADOS: {', '.join(disponibles)}")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")

def menu_operaciones(mis_pokemons, pokemons_rivales):
    """Menú secundario para operaciones con los Pokémon seleccionados"""
    while True:
        print("\n📊 MENÚ DE OPERACIONES:")
        print("1. Ver ranking completo para cada rival")
        print("2. Ver asignación óptima (sin repetir Pokémon)")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción (1-2): ").strip()
        
        if opcion == "1":
            print("\n📊 RANKING COMPLETO PARA CADA RIVAL")
            print("="*60)
            for rival in pokemons_rivales:
                print(f"\n⭐ RIVAL: {rival.upper()}")
                evaluar_combates(mis_pokemons, rival)
        
        elif opcion == "2":
            evaluar_mejor_equipo(mis_pokemons, pokemons_rivales)
        
        elif opcion == "0":
            break
        
        else:
            print("Opción no válida. Por favor seleccione 1, 2 o 0 (para volver).")

if __name__ == "__main__":
    print("=== SIMULADOR DE COMBATES POKÉMON ===")
    
    # Primero pedir los Pokémon rivales (esto es común a todas las opciones)
    pokemons_rivales = input("Pokémon rivales (separados por comas): ").strip().title().split(',')
    pokemons_rivales = [p.strip() for p in pokemons_rivales if p.strip()]
    
    # Menú principal para seleccionar fuente de tus Pokémon
    while True:
        print("\n🔍 SELECCIONA EL ORIGEN DE TUS POKÉMON:")
        print("1. Introducir manualmente mis Pokémon")
        print("2. Seleccionar una caja")
        print("3. Usar todos mis Pokémon disponibles")
        print("0. Salir")
        
        opcion = input("Seleccione una opción (1-3): ").strip()
        
        if opcion == "1":
            # Opción 1: Introducir manualmente
            mis_pokemons = input("\nTus Pokémon (separados por comas): ").strip().title().split(',')
            mis_pokemons = [p.strip() for p in mis_pokemons if p.strip()]
            
            if not mis_pokemons:
                print("Debes introducir al menos un Pokémon")
                continue
                
            # Menú de operaciones con estos Pokémon
            menu_operaciones(mis_pokemons, pokemons_rivales)
        
        elif opcion == "2":
            # Opción 2: Seleccionar caja
            cajas = session.execute("SELECT nombre FROM cajas")
            lista_cajas = [caja['nombre'] for caja in cajas]
            
            if not lista_cajas:
                print("No hay cajas disponibles.")
                continue
                
            print("\n📦 CAJAS DISPONIBLES:")
            for i, nombre in enumerate(lista_cajas, 1):
                print(f"{i}. {nombre}")
            
            try:
                indice = int(input("\nSeleccione una caja por índice: ")) - 1
                if 0 <= indice < len(lista_cajas):
                    caja_seleccionada = lista_cajas[indice]
                    print(f"\nHas seleccionado: {caja_seleccionada}")
                    
                    # Obtener Pokémon de la caja
                    pokemons_caja = session.execute(
                        "SELECT pokemons FROM cajas WHERE nombre = %s ALLOW FILTERING", 
                        [caja_seleccionada]
                    )
                    mis_pokemons = [p['pokemons'] for p in pokemons_caja][0]
                    
                    if not mis_pokemons:
                        print("La caja está vacía.")
                        continue
                        
                    print("\nPokémon en la caja:")
                    for i, pokemon in enumerate(mis_pokemons, 1):
                        print(f"{i}. {pokemon}")
                    
                    # Menú de operaciones con estos Pokémon
                    menu_operaciones(mis_pokemons, pokemons_rivales)
                else:
                    print("Índice fuera de rango.")
            except ValueError:
                print("Por favor ingrese un número válido.")
        
        elif opcion == "3":
            # Opción 3: Usar todos los Pokémon disponibles
            print("\nObteniendo todos tus Pokémon...")
            todos_pokemons = session.execute("SELECT name FROM pokemon")
            mis_pokemons = [p['name'] for p in todos_pokemons]
            
            if not mis_pokemons:
                print("No se encontraron Pokémon.")
                continue
                
            print(f"\nSe usarán todos tus {len(mis_pokemons)} Pokémon disponibles")
            
            # Menú de operaciones con estos Pokémon
            menu_operaciones(mis_pokemons, pokemons_rivales)
        
        elif opcion == "0":
            print("¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Por favor seleccione 1, 2, 3 o 0 (para salir).")
