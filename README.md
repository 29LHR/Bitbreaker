# Codebreaker

A cryptography dashboard for classical cipher decryption and analysis, built with Python and CustomTkinter.

## Features

### 10 Classical Ciphers
| Cipher | Type | Attack Method |
|--------|------|---------------|
| **Caesar** | Shift substitution | Brute force (26 shifts) |
| **Affine** | ax + b (mod 26) | Brute force (312 keys) |
| **Vigenère** | Polyalphabetic | Dictionary attack |
| **Beaufort** | Reciprocal polyalphabetic | Dictionary attack |
| **Autokey** | Key = keyword + ciphertext | Dictionary attack |
| **Playfair** | Digraph substitution | Dictionary attack (all 13 variants) |
| **Transposition** | Columnar permutation | Permutation key search |
| **Hill** | Matrix (2×2/3×3) | Matrix enumeration |
| **ADFGVX** | Fractionating + transposition | Dual dictionary attack |
| **Jefferson Disk** | 36-wheel mechanical | Order + offset search |

### Analysis Tools
- **Index of Coincidence** - Measure text randomness to identify cipher type
- **Letter Distribution** - Frequency analysis with English comparison chart

### Filtering Options
All dictionary-based attacks support configurable filters:
- **IoC Range** - Index of Coincidence bounds (default 0.06–0.07 for English)
- **Word Checks** - Require "the" and/or "and" in decrypted text
- **Common Letters** - Require ≥8 of "etaoin shrdlu" present

## Installation

```bash
git clone https://github.com/yourusername/Codebreaker.git
cd Codebreaker
pip install -r requirements.txt
```

### Requirements
- Python 3.10+
- `customtkinter`
- `numpy` (for Hill cipher)
- `matplotlib` (for distribution analysis)

```bash
pip install customtkinter numpy matplotlib
```

## Usage

1. Run the dashboard:
```bash
python main.py
```

2. Load ciphertext via **Cipher Text** in the sidebar, or edit `cipherText.txt` directly

3. Navigate to **Classical Ciphers** and select a cipher tool

4. For dictionary-based ciphers:
   - Choose dictionary (Full ~370k words / Short ~5k common words)
   - Configure filters in the Filter Configuration dialog
   - Click "Start Attack" and monitor progress

5. Results appear in a scrollable window and are saved to `decrypts/<cipher>.txt`

## Project Structure

```
Codebreaker/
├── main.py                 # Main dashboard application
├── cipherlib.py           # Base classes & dialogs (CipherBase, FilterConfigDialog, etc.)
├── requirements.txt
├── cipherText.txt         # Input ciphertext (auto-loaded)
├── shortwords.json        # Short dictionary (~5k words)
├── words.json             # Full dictionary (~370k words)
├── ciphers/
│   ├── __init__.py
│   ├── caesar.py
│   ├── affine.py
│   ├── vigenere.py
│   ├── beaufort.py
│   ├── autokey.py
│   ├── playfair.py
│   ├── transposition.py
│   ├── hill.py
│   ├── adfgvx.py
│   └── jefferson.py
├── analysis/
│   ├── __init__.py
│   ├── ioc.py
│   └── distribution.py
└── decrypts/              # Output directory (auto-created)
    ├── caesar.txt
    ├── vigenere.txt
    ├── ...
```

## Screenshots

### Dashboard
Clean sidebar navigation with quick actions and recent activity log.

### Cipher Tools
Each cipher opens in a modal window with decrypt button, ciphertext management, and results display.

### Filter Configuration
Checkboxes for IoC range, word filters, and common letter detection.

## Dictionary Files

Download or generate word lists:
- `words.json` - Full dictionary (one word per line, lowercase)
- `shortwords.json` - Common words subset

Format: JSON object with words as keys (values ignored):
```json
{"the": 1, "and": 1, "hello": 1, ...}
```

## Building Dictionaries

```bash
# From a word list file (one word per line)
python -c "
import json
with open('wordlist.txt') as f:
    words = {line.strip().lower(): 1 for line in f if line.strip()}
with open('words.json', 'w') as f:
    json.dump(words, f)
"
```

## License

MIT License - feel free to use and modify.

## Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Dictionary attack methodology inspired by classical cryptanalysis techniques
- Cipher implementations based on standard algorithms from cryptography literature