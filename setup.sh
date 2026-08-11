#!/bin/bash
set -e
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt_tab', quiet=True); nltk.download('averaged_perceptron_tagger_eng', quiet=True)"
