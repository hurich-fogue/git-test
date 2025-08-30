import os
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === Fonctions de traitement ===
def extract_data(prefixes, file_path):
    results = []
    with open(file_path, 'r') as file:
        data = [line.rstrip() for line in file]
    for prefix in prefixes:
        matched_lines = [line for line in data if line.startswith(prefix)]
        if prefix == 'H-':
            h_group = []
            for item in matched_lines:
                content = item[2:].strip()
                values = []
                for val in content.split(';'):
                    parts = val.strip().split()
                    values.extend(parts)
                h_group.append(values)
            results.append(h_group)
        else:
            result_string = ""
            for item in matched_lines:
                result_string += item[2:].strip()
            values = []
            for val in result_string.split(';'):
                parts = val.strip().split()
                values.extend(parts)
            results.append(values)
    return results

def parse_store_data_in_json(results, air_file_path, prefixes, output_dir):
    output = {}
    if len(results) > 0 and len(results[0]) >= 3:
        output["ticket_airline_name"] = results[0][0]
        output["airline_code"] = results[0][1]
        output["ticket_number"] = results[0][2]
    if len(results) > 1 and len(results[1]) >= 3:
        output["air_creation_date"] = results[1][2]
    if len(results) > 2 and len(results[2]) >= 2:
        output["international_sale"] = results[2][1]
    if len(results) > 5 and len(results[5]) >= 2:
        output["passenger_name"] = results[5][1]

    h_descriptions = [
        "ttonbr","segment_number", "stop_over_indicator", "origin_airport_code", "origin_city",
        "destination_airport_code", "destination_city", "airline_code", "flight_number",
        "class_of_service", "class_of_booking", "departure_date", "departure_time",
        "arrival_time", "arrival_date", "status", "pnr_status", "meal_code",
        "number_of_stops", "equipment_type", "enter", "shared_comm", "baggage_allowance",
        "check_in_terminal", "check_in_time", "ticket_type", "flight_duration_time",
        "non_smoking", "multi_pnr", "cpn_nr", "cpn_in", "cpn_sn"
    ]

    try:
        h_lines = results[3]
        output["segments"] = []
        for h_line in h_lines:
            segment = {}
            for i, desc in enumerate(h_descriptions):
                if i < len(h_line):
                    segment[desc] = h_line[i]
            output["segments"].append(segment)
    except IndexError:
        pass

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(air_file_path))[0]
    json_file_name = f"{base_name}.json"
    full_path = os.path.join(output_dir, json_file_name)

    with open(full_path, 'w') as json_file:
        json.dump(output, json_file, indent=4)
        print(f"✅ Fichier traité : {json_file_name}")

# === Surveillance du dossier ===
class AIRFileHandler(FileSystemEventHandler):
    def __init__(self, input_dir, output_dir, prefixes):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.prefixes = prefixes

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".AIR"):
            return
        time.sleep(0.5)  # Laisse le temps au fichier de s'écrire complètement
        air_path = event.src_path
        print(f"📥 Nouveau fichier détecté : {air_path}")
        try:
            results = extract_data(self.prefixes, air_path)
            parse_store_data_in_json(results, air_path, self.prefixes, self.output_dir)
            os.remove(air_path)
            print(f"Fichier supprimé : {air_path}")
        except Exception as e:
            print(f"❌ Erreur avec {air_path} : {e}")

# === Lancement ===
input_dir = "air_files"
output_dir = "output_json"
prefixes = ['A-', 'D-', 'G-', 'H-', 'T-', 'I']

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

event_handler = AIRFileHandler(input_dir, output_dir, prefixes)
observer = Observer()
observer.schedule(event_handler, input_dir, recursive=False)
observer.start()

print(f"👀 Surveillance activée sur : {input_dir}")
print("Ajoute un fichier .AIR pour lancer le traitement automatique...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()