import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from geopy.geocoders import Nominatim

load_dotenv()

DB_PASSWORD = os.getenv("DB_PASSWORD")
DATABASE_URL = f"postgresql+pg8000://postgres:{DB_PASSWORD}@localhost:5432/pharmacy_finder"
engine = create_engine(DATABASE_URL)

# Geocodeur Nominatim - user_agent obligatoire (n'importe quel nom unique)
geolocator = Nominatim(user_agent="pharmacy_finder_app_valentin")


def geocode_quartier(quartier: str):
    """
    Transforme un nom de quartier ou d'adresse en coordonnees GPS.
    On ajoute toujours 'Abidjan, Cote d'Ivoire' pour ameliorer la precision.
    """
    requete = f"{quartier}, Abidjan, Côte d'Ivoire"
    location = geolocator.geocode(requete)

    if location is None:
        return None

    return {"latitude": location.latitude, "longitude": location.longitude}


def find_nearest_pharmacies(quartier: str, rayon_km: float = 1.0, limite: int = 5):
    """
    Trouve les pharmacies les plus proches d'un quartier donne,
    dans un rayon en kilometres specifie.
    """
    position = geocode_quartier(quartier)

    if position is None:
        return {"erreur": f"Impossible de localiser '{quartier}'. Vérifie le nom du quartier."}

    lat = position["latitude"]
    lon = position["longitude"]
    rayon_metres = rayon_km * 1000

    query = text("""
        SELECT
            nom,
            ST_Y(geom) AS latitude,
            ST_X(geom) AS longitude,
            ST_Distance(
                geom::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            ) AS distance_metres
        FROM pharmacies
        WHERE ST_DWithin(
            geom::geography,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
            :rayon
        )
        ORDER BY distance_metres ASC
        LIMIT :limite
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"lon": lon, "lat": lat, "rayon": rayon_metres, "limite": limite})
        rows = result.fetchall()

    pharmacies = [
        {
            "nom": row.nom,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "distance_km": round(row.distance_metres / 1000, 2),
        }
        for row in rows
    ]

    return {
        "position_recherchee": {"quartier": quartier, "latitude": lat, "longitude": lon},
        "rayon_km": rayon_km,
        "nombre_trouve": len(pharmacies),
        "pharmacies": pharmacies,
    }


# Test rapide si on execute ce fichier directement
if __name__ == "__main__":
    print("Test de geocodage :")
    print(geocode_quartier("Cocody"))

    print("\nTest de recherche de pharmacies proches :")
    resultat = find_nearest_pharmacies("Cocody", rayon_km=2.0, limite=5)
    print(resultat)
