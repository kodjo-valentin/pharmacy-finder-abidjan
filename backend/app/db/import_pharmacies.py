import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Chemin vers le fichier GeoJSON (depuis backend/app/db/ vers data/raw/)
GEOJSON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(
        __file__)), "..", "..", "..", "data", "raw", "pharmacies_abidjan.geojson"
)

DB_PASSWORD = os.getenv("DB_PASSWORD")

# Utilise pg8000 (driver pur Python) au lieu de psycopg2 pour eviter
# le bug d'encodage Windows rencontre avec psycopg2
DATABASE_URL = "postgresql+pg8000://neondb_owner:npg_lBGWws0nci2e@ep-dawn-violet-asxsxd9h-pooler.c-4.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"


DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and "?sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

engine = create_engine(DATABASE_URL, connect_args={"ssl_context": True})


def import_pharmacies():
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data["features"]
    print(f"Nombre de pharmacies trouvees dans le fichier : {len(features)}")

    inserted = 0
    skipped = 0

    with engine.connect() as conn:
        # Vide la table avant de reimporter
        conn.execute(text("TRUNCATE TABLE pharmacies RESTART IDENTITY;"))

        for feature in features:
            props = feature.get("properties", {})
            nom = props.get("name", "Pharmacie sans nom")
            geometry = feature.get("geometry", {})

            if geometry.get("type") != "Point":
                skipped += 1
                continue

            lon, lat = geometry["coordinates"]

            conn.execute(
                text("""
                    INSERT INTO pharmacies (nom, adresse, geom)
                    VALUES (:nom, :adresse, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
                """),
                {"nom": nom, "adresse": None, "lon": lon, "lat": lat},
            )
            inserted += 1

        conn.commit()

    print(f"Importees avec succes : {inserted}")
    print(f"Ignorees (pas un point) : {skipped}")


if __name__ == "__main__":
    import_pharmacies()
