#!/usr/bin/env python3
"""
build_pdf.py — Script de génération du PDF "Español Express Perú"
"""

import os
import sys
import glob
import yaml
import markdown
from weasyprint import HTML, CSS

def build_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    content_dir = os.path.join(base_dir, "content")
    assets_dir = os.path.join(base_dir, "assets")
    metadata_path = os.path.join(base_dir, "metadata.yaml")
    output_pdf = os.path.join(base_dir, "espanol_express_peru.pdf")

    print("🚀 Démarrage de la compilation du PDF Español Express Perú...")

    # Load metadata
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = yaml.safe_load(f)

    # Find all markdown files in content directory
    md_files = sorted(glob.glob(os.path.join(content_dir, "*.md")))
    if not md_files:
        print("❌ Erreur : Aucun fichier Markdown trouvé dans /content.")
        sys.exit(1)

    print(f"📄 {len(md_files)} fichiers Markdown trouvés.")

    # Initialize Markdown converter
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'attr_list',
        'md_in_html',
        'nl2br'
    ])

    full_html_body = []

    for md_file in md_files:
        filename = os.path.basename(md_file)
        print(f"  └─ Traitement de : {filename}")
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
            html_chunk = md.convert(text)
            full_html_body.append(f'<section class="section-{filename.replace(".md", "")}">\n{html_chunk}\n</section>\n')
            md.reset()

    # Combine into full HTML document
    css_path = os.path.join(assets_dir, "style.css")

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{metadata.get('title', 'Español Express Perú')} - {metadata.get('subtitle', '')}</title>
    <link rel="stylesheet" href="file://{css_path}">
</head>
<body>
{''.join(full_html_body)}
</body>
</html>
"""

    # Save intermediate combined HTML for debugging if needed
    temp_html_path = os.path.join(base_dir, "output.html")
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("🎨 Application du style CSS et rendu PDF avec WeasyPrint...")
    try:
        html_obj = HTML(string=html_content, base_url=base_dir)
        html_obj.write_pdf(output_pdf)
        print(f"✅ SUCCÈS ! PDF généré avec succès : {output_pdf}")
        file_size_mb = os.path.getsize(output_pdf) / (1024 * 1024)
        print(f"📦 Taille du fichier : {file_size_mb:.2f} MB")
    except Exception as e:
        print(f"❌ Erreur lors de la génération WeasyPrint : {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_pdf()
