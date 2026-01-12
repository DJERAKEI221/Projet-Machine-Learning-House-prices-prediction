import json
import re

# Lire le notebook
with open('notebooks/exploration_base_donnees.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Parcourir toutes les cellules
replacements_count = 0
for cell in notebook['cells']:
    if cell['cell_type'] == 'code' or cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])
        original_source = source
        
        # Remplacer toutes les variations de R²
        # R^2 -> R²
        source = re.sub(r'R\^2', 'R²', source)
        # R2 (sans espace avant) -> R²
        source = re.sub(r'\bR2\b', 'R²', source)
        # r^2 -> R² (en gardant la majuscule pour la cohérence)
        source = re.sub(r'r\^2', 'R²', source)
        # r2 -> R²
        source = re.sub(r'\br2\b', 'R²', source)
        # R-squared -> R²
        source = re.sub(r'R-squared', 'R²', source, flags=re.IGNORECASE)
        # R squared -> R²
        source = re.sub(r'R\s+squared', 'R²', source, flags=re.IGNORECASE)
        # coefficient of determination -> R²
        source = re.sub(r'coefficient\s+of\s+determination', 'R²', source, flags=re.IGNORECASE)
        
        if source != original_source:
            cell['source'] = source.splitlines(keepends=True)
            if cell['source'] and not cell['source'][-1].endswith('\n'):
                cell['source'][-1] = cell['source'][-1] + '\n'
            replacements_count += len(re.findall(r'R²', source)) - len(re.findall(r'R²', original_source))
            print(f"Cellule modifiée (type: {cell['cell_type']})")

# Sauvegarder le notebook modifié
with open('notebooks/exploration_base_donnees.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print(f"Notebook mis à jour! {replacements_count} remplacements effectués.")
