# Sources de fabrication

Les scripts fabriquent les schémas (SVG/PNG), les PPTX et les DOCX depuis les JSON et le dossier original présents dans le kit. Dépendances : Python, numpy, scikit-learn, Pillow, cairosvg, python-pptx et python-docx. Ils supposent les polices DejaVu Sans disponibles sur le poste. Les polices ne sont pas distribuées.

Ordre : `python build_visuals.py`, puis `python build_doc_figures.py`, puis `python build_decks.py`, puis `python build_docs.py`. Les exports PDF livrés ont été produits avec LibreOffice et vérifiés séparément. Les retouches de mise en page et les contrôles d’export restent nécessaires après modification du contenu. Le fragment décoratif imagegen est fourni dans les illustrations ; il n’est pas régénéré par ces scripts.
