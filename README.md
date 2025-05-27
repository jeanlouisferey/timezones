# timezonesc
This program generates a visual timetable showing working hours across the different countries relative to a reference country time.

It's particularly useful for teams working across multiple time zones to easily coordinate meetings and collaboration times.

## Features
- Automatically detects winter/summer time for the reference country
- Shows time conversions for working hours (8:00-20:00 French time)
- Color codes different periods of the day:
  - Early/Late hours (before 9:00 or after 18:00)
  - Noon hours (12:00)
  - Normal working hours
- Supports all countries worldwide using ISO 3166-1 alpha-3 codes
- Get reference country from command line parameters
- Generates a clear, easy-to-read table as a PNG file
- You can modify the colors with command line parameters (by default you have early_late_color='#FFD700' (Gold), noon_color='#87CEEB' (Sky Blue) and normal_color='white' (White)

## Installation

1. Make sure you have Python 3.8 or higher installed on your system.

2. Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

This will install the following dependencies:
- pytz: For timezone handling
- Pillow: For image generation
- pandas: For data manipulation
- pycountry: For worldwide country support and ISO codes

## Usage

1. Create a text file containing the list of countries you want to display using their ISO 3166-1 alpha-3 codes, one per line. For example:
```
# African countries
SEN  # Senegal
MAR  # Morocco
TUN  # Tunisia
EGY  # Egypt

# European countries
FRA  # France
ESP  # Spain
BEL  # Belgium
POL  # Poland

# Asia
IND  # India
PAK  # Pakistan
```

You can find the alpha-3 code for any country on the [ISO 3166-1 Wikipedia page](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3).

2. Run the program with your reference country code and countries file:
```bash
python src/main.py -r "FRA" -c data/countries.txt
```

This will generate a timetable.png file in the current directory.

### Command Line Options

- `-r, --reference`: Reference country code (e.g., "FRA", "IND")
- `-c, --countries`: Path to text file containing list of country codes
- `-o, --output`: Output PNG file path (default: timetable.png)
- `--early-late-color`: Color for early/late hours (default: #FFD700 - Gold)
- `--noon-color`: Color for noon hours (default: #87CEEB - Sky Blue)
- `--normal-color`: Color for normal working hours (default: white)

### Examples

1. Basic usage with default colors:
```bash
python src/main.py -r "FRA" -c data/countries.txt
```

2. Using different reference country:
```bash
python src/main.py -r "IND" -c data/countries.txt -o india_timetable.png
```

3. Custom colors:
```bash
python src/main.py -r "FRA" -c data/countries.txt \
    --early-late-color "#FFA500" \
    --noon-color "#98FB98" \
    --normal-color "#F0F8FF" \
    -o custom_colors.png
```

### Common Country Codes

Here are some commonly used country codes:

#### Africa
- SEN: Senegal
- GNB: Guinea-Bissau
- GIN: Guinea
- SLE: Sierra Leone
- CIV: Ivory Coast
- MLI: Mali
- BFA: Burkina Faso
- LBR: Liberia
- MAR: Morocco
- CMR: Cameroon
- COD: DR Congo
- CAF: Central African Republic
- TUN: Tunisia
- EGY: Egypt
- BWA: Botswana
- MDG: Madagascar

#### Europe
- FRA: France
- ESP: Spain
- BEL: Belgium
- POL: Poland
- SVK: Slovakia
- LUX: Luxembourg
- MDA: Moldova
- ROU: Romania
- LTU: Lithuania
- GBR: United Kingdom

#### Asia
- JOR: Jordan
- IND: India
- PAK: Pakistan
- UZB: Uzbekistan
- ARE: UAE
- RUS: Russia

#### Americas
- USA: United States

### Notes

- For countries spanning multiple time zones (like the United States or Russia), the program uses the primary/capital timezone by default.
- The program automatically handles daylight saving time (summer/winter time) for all countries.
- Times are displayed in 24-hour format for clarity.
- For time zones with 30-minute offsets (like India), the program correctly displays the actual time including minutes.
