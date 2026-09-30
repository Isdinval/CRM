# Español Express Perú — 7 jours pour parler avec ma belle-famille (A2)

Ce projet génère un document PDF complet, structuré et auto-suffisant pour l'apprentissage intensif de l'espagnol péruvien (niveau A2) en 7 jours.

## Structure du projet

```
/espanol_express_peru
├── content/
│   ├── 00_cover.md
│   ├── 01_intro.md
│   ├── 02_jour1.md
│   ├── 03_jour2.md
│   ├── 04_jour3.md
│   ├── 05_jour4.md
│   ├── 06_jour5.md
│   ├── 07_jour6.md
│   ├── 08_jour7.md
│   ├── 09_evaluation.md
│   └── 10_ressources.md
├── assets/
│   └── style.css
├── metadata.yaml
├── build_pdf.py
├── requirements.txt
└── README.md
```

## Préréquis et Installation

1. S'assurer que Python 3.8+ est installé sur votre système.
2. Installer les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```
   *(Note : WeasyPrint nécessite la bibliothèque système cairo/pango si elle n'est pas préinstallée)*.

## Génération du PDF

Pour générer le fichier PDF final `espanol_express_peru.pdf`, exécutez la commande suivante à la racine du projet :

```bash
python build_pdf.py
```

Le fichier `espanol_express_peru.pdf` sera généré à la racine.
