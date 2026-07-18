import sys
import os

# Point everything to D drive
os.environ['ARGOS_PACKAGES_DIR'] = 'D:\\argos_packages'
os.environ['ARGOS_TRANSLATE_PACKAGES_DIR'] = 'D:\\argos_packages'
os.makedirs('D:\\argos_packages', exist_ok=True)

sys.path.insert(0, 'D:\\grading_project\\libs')

from argostranslate import package, settings

# Override storage path
settings.data_dir = 'D:\\argos_packages'
settings.package_data_dir = 'D:\\argos_packages'

print("Updating package index...")
package.update_package_index()

available = package.get_available_packages()

# Find German to English
de_en = next(
    filter(lambda x: x.from_code == "de" and x.to_code == "en", available)
)

# Find English to German
en_de = next(
    filter(lambda x: x.from_code == "en" and x.to_code == "de", available)
)

print(f"Downloading German → English...")
de_en_path = de_en.download()
package.install_from_path(de_en_path)
print("German → English done!")

print(f"Downloading English → German...")
en_de_path = en_de.download()
package.install_from_path(en_de_path)
print("English → German done!")

print("All translation models ready!")