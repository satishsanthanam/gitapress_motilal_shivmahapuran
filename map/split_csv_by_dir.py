import os
import pandas as pd

# Load the master English CSV file
csv_file = 'sivapuran-ninja.csv'

if not os.path.exists(csv_file):
    print(f"❌ Error: Could not find '{csv_file}' in current directory.")
    exit(1)

print(f"📖 Reading '{csv_file}'...")
df = pd.read_csv(csv_file)

# Mapping strategy for directory prefixes
dir_mapping = {
    '000': './00',       # Māhātmya
    '010': './01',       # Vidyeśvara Saṁhitā
    '021': './02/01',    # Rudra Saṁhitā - Sṛṣṭi Khaṇḍa
    '022': './02/02',    # Rudra Saṁhitā - Satī Khaṇḍa
    '023': './02/03',    # Rudra Saṁhitā - Pārvatī Khaṇḍa
    '024': './02/04',    # Rudra Saṁhitā - Kumāra Khaṇḍa
    '025': './02/05',    # Rudra Saṁhitā - Yuddha Khaṇḍa
    '030': './03',       # Śatarudra Saṁhitā
    '040': './04',       # Koṭirudra Saṁhitā
    '050': './05',       # Umā Saṁhitā
    '060': './06',       # Kailāsa Saṁhitā
    '071': './07/01',    # Vāyavīya Saṁhitā (Part 1)
    '072': './07/02'     # Vāyavīya Saṁhitā (Part 2)
}

def get_target_dir(code_str):
    """Maps code like '010-04' to target directory path like './01/ch_04'."""
    parts = str(code_str).split('-')
    if len(parts) != 2:
        return None
    prefix, adhyaya = parts
    base_dir = dir_mapping.get(prefix, './misc')
    return os.path.join(base_dir, f"ch_{adhyaya}")

processed_chapters = 0

# Group rows by 'samhita-adhyaya' and write each group to its chapter directory
for code, group in df.groupby('samhita-adhyaya'):
    target_dir = get_target_dir(code)
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)
        output_file = os.path.join(target_dir, 'english.csv')
        group.to_csv(output_file, index=False)
        processed_chapters += 1

print(f"✅ Success! Created {processed_chapters} chapter CSV files in your directory tree.")