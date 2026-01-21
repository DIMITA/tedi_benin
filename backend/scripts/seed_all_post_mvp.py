"""
Master seed script for all post-MVP data
Runs all seed scripts in correct order
"""
import subprocess
import sys

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(
            ['python', f'scripts/{script_name}'],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"\n✅ {description} - COMPLETED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED")
        print(f"Error: {e}")
        return False

def main():
    """Run all post-MVP seed scripts"""
    print("\n" + "="*60)
    print("🌟 TEDI POST-MVP DATA SEEDING")
    print("="*60)

    scripts = [
        ('seed_property_types.py', 'Seeding Property Types'),
        ('seed_job_categories.py', 'Seeding Job Categories'),
        ('seed_business_sectors.py', 'Seeding Business Sectors'),
        ('update_agriculture_indices.py', 'Updating Agriculture Indices'),
    ]

    results = {}
    for script, description in scripts:
        results[description] = run_script(script, description)

    # Summary
    print("\n" + "="*60)
    print("📊 SEEDING SUMMARY")
    print("="*60)

    for description, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} - {description}")

    total = len(results)
    successful = sum(1 for success in results.values() if success)

    print(f"\n🎯 Overall: {successful}/{total} scripts completed successfully")

    if successful == total:
        print("\n🎉 ALL POST-MVP DATA SEEDED SUCCESSFULLY!")
        return 0
    else:
        print(f"\n⚠️  {total - successful} script(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
