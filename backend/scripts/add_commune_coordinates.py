"""
Script to add GPS coordinates to communes in Benin
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models.geo import Commune

# Approximate coordinates for major communes in Benin
COMMUNE_COORDINATES = {
    # Littoral
    "Cotonou": (6.3654, 2.4183),

    # Atlantique
    "Abomey-Calavi": (6.4489, 2.3554),
    "Allada": (6.6656, 2.1516),
    "Ouidah": (6.3634, 2.0852),
    "Sô-Ava": (6.4526, 2.4293),

    # Ouémé
    "Porto-Novo": (6.4969, 2.6289),
    "Adjarra": (6.4718, 2.6072),
    "Sèmè-Kpodji": (6.3880, 2.5833),
    "Akpro-Missérété": (6.5500, 2.5667),

    # Zou
    "Abomey": (7.1849, 1.9922),
    "Bohicon": (7.1781, 2.0677),
    "Cové": (7.2248, 2.3023),
    "Djidja": (7.3333, 1.9333),

    # Borgou
    "Parakou": (9.3372, 2.6300),
    "Tchaourou": (8.8845, 2.5991),
    "Nikki": (9.9381, 3.2090),

    # Alibori
    "Kandi": (11.1347, 2.9386),
    "Malanville": (11.8700, 3.3833),
    "Banikoara": (11.2979, 2.4384),

    # Atacora
    "Natitingou": (10.3048, 1.3796),
    "Tanguiéta": (10.6217, 1.2651),
    "Boukoumbé": (10.1833, 1.1000),

    # Donga
    "Djougou": (9.7065, 1.6658),
    "Bassila": (9.0167, 1.6667),

    # Collines
    "Savalou": (7.9281, 1.9753),
    "Dassa-Zoumè": (7.7500, 2.1833),
    "Savè": (8.0333, 2.4833),

    # Mono
    "Lokossa": (6.6386, 1.7185),
    "Grand-Popo": (6.2786, 1.8169),
    "Comè": (6.4067, 1.8783),

    # Couffo
    "Aplahoué": (6.9333, 1.6833),
    "Dogbo": (6.8000, 1.7833),

    # Plateau
    "Pobè": (6.9667, 2.6667),
    "Kétou": (7.3633, 2.6005),
    "Sakété": (6.7333, 2.6500),
}


def add_coordinates():
    """Add GPS coordinates to communes"""
    print("Adding GPS coordinates to communes...")

    updated = 0

    for commune_name, (lat, lon) in COMMUNE_COORDINATES.items():
        commune = Commune.query.filter_by(name=commune_name).first()

        if commune:
            commune.center_lat = lat
            commune.center_lon = lon
            updated += 1
            print(f"✓ Updated {commune_name}: ({lat}, {lon})")
        else:
            print(f"⚠ Commune not found: {commune_name}")

    db.session.commit()

    print(f"\n✓ Updated {updated} communes with coordinates")


def main():
    """Main function"""
    print("=" * 60)
    print("TEDI Commune Coordinates Update")
    print("=" * 60)

    # Create Flask app context
    app = create_app('development')

    with app.app_context():
        add_coordinates()

        print("\n" + "=" * 60)
        print("✓ Coordinates updated successfully!")
        print("=" * 60)
        print("\nYou can now view communes on the map: http://localhost:3000/map")


if __name__ == '__main__':
    main()
