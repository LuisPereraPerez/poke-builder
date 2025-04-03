import pandas as pd
import uuid
from cassandra.cluster import Cluster

# Conectar a Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()

# Seleccionar Keyspace
session.set_keyspace('poke_builder')

# Cargar dataset
df = pd.read_csv("pokemon.csv")

# Insertar datos en Cassandra
for _, row in df.iterrows():
    session.execute("""
        INSERT INTO pokemon (id, num_pokedex, name, type1, type2, total, hp, attack, defense, sp_attack, sp_defense, speed, generation, lengendary)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        uuid.uuid4(),
        int(row["id"]),
        row['Name'],
        row['Type 1'],
        None if pd.isna(row['Type 2']) else row['Type 2'],  # Evitar NaN en Type 2
        row['Total'],
        row['HP'],
        row['Attack'],
        row['Defense'],
        row['Sp. Atk'],
        row['Sp. Def'],
        row['Speed'],
        row["Gen"],
        row["Legendary"]
    ))

print("Datos insertados correctamente ✅")
