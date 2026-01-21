"""
Populate commune coordinates with sample data
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.geo import Commune

# Major communes in Benin with their approximate coordinates
COMMUNE_COORDS = {
    'Cotonou': {'lat': 6.3654, 'lon': 2.4183, 'population': 679012, 'area': 79.0},
    'Porto-Novo': {'lat': 6.4969, 'lon': 2.6289, 'population': 264320, 'area': 110.0},
    'Parakou': {'lat': 9.3408, 'lon': 2.6300, 'population': 255478, 'area': 441.0},
    'Djougou': {'lat': 9.7085, 'lon': 1.6660, 'population': 237040, 'area': 3966.0},
    'Bohicon': {'lat': 7.1781, 'lon': 2.0670, 'population': 125092, 'area': 139.0},
    'Kandi': {'lat': 11.1342, 'lon': 2.9387, 'population': 109701, 'area': 3421.0},
    'Abomey': {'lat': 7.1826, 'lon': 1.9913, 'population': 90246, 'area': 142.0},
    'Natitingou': {'lat': 10.3042, 'lon': 1.3793, 'population': 80892, 'area': 3045.0},
    'Lokossa': {'lat': 6.6388, 'lon': 1.7172, 'population': 77065, 'area': 260.0},
    'Ouidah': {'lat': 6.3629, 'lon': 2.0852, 'population': 83503, 'area': 364.0},
    'Malanville': {'lat': 11.8698, 'lon': 3.3833, 'population': 73489, 'area': 3016.0},
    'Savalou': {'lat': 7.9281, 'lon': 1.9757, 'population': 87464, 'area': 2674.0},
    'Pobè': {'lat': 6.9881, 'lon': 2.6699, 'population': 82910, 'area': 400.0},
    'Kétou': {'lat': 7.3631, 'lon': 2.6021, 'population': 80000, 'area': 2183.0},
    'Allada': {'lat': 6.6650, 'lon': 2.1519, 'population': 91778, 'area': 381.0},
    'Aplahoué': {'lat': 6.9308, 'lon': 1.6825, 'population': 70823, 'area': 572.0},
    'Kpomassè': {'lat': 6.5167, 'lon': 2.1167, 'population': 57190, 'area': 305.0},
    'Toffo': {'lat': 6.8447, 'lon': 2.0875, 'population': 74717, 'area': 515.0},
    'Tori-Bossito': {'lat': 6.5000, 'lon': 2.1500, 'population': 44569, 'area': 328.0},
    'Zè': {'lat': 6.7333, 'lon': 2.2667, 'population': 82888, 'area': 653.0},
    'Adjohoun': {'lat': 6.7000, 'lon': 2.4833, 'population': 60401, 'area': 308.0},
    'Aguégués': {'lat': 6.5833, 'lon': 2.4167, 'population': 26650, 'area': 100.0},
    'Avrankou': {'lat': 6.6167, 'lon': 2.5833, 'population': 54934, 'area': 150.0},
    'Bonou': {'lat': 6.9000, 'lon': 2.4500, 'population': 29656, 'area': 250.0},
    'Dangbo': {'lat': 6.5833, 'lon': 2.5333, 'population': 35300, 'area': 340.0},
}


def populate_commune_coordinates():
    """Populate commune coordinates from predefined data"""
    app = create_app()

    with app.app_context():
        updated_count = 0
        not_found = []

        for commune_name, coords in COMMUNE_COORDS.items():
            # Try to find commune by name (case-insensitive)
            commune = Commune.query.filter(
                db.func.lower(Commune.name) == commune_name.lower()
            ).first()

            if commune:
                commune.center_lat = coords['lat']
                commune.center_lon = coords['lon']
                commune.population = coords['population']
                commune.area_km2 = coords['area']
                updated_count += 1
                print(f"✓ Updated {commune_name}: ({coords['lat']}, {coords['lon']})")
            else:
                not_found.append(commune_name)
                print(f"✗ Commune not found: {commune_name}")

        # Commit changes
        db.session.commit()

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Updated: {updated_count} communes")
        print(f"  Not found: {len(not_found)} communes")

        if not_found:
            print(f"\nCommunes not found in database:")
            for name in not_found:
                print(f"  - {name}")

        print(f"{'='*60}")


if __name__ == '__main__':
    populate_commune_coordinates()
