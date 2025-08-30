import json
import os

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

    if len(results) > 0:
        line_a = results[0]
        if len(line_a) >= 3:
            output["ticket_airline_name"] = line_a[0]
            output["airline_code"] = line_a[1]
            output["ticket_number"] = line_a[2]

    if len(results) > 1:
        line_b = results[1]
        if len(line_b) >= 3:
            output["air_creation_date"] = line_b[2]

    if len(results) > 2:
        line_c = results[2]
        if len(line_c) >= 2:
            output["international_sale"] = line_c[1]

    if len(results) > 5:
        line_e = results[5]
        if len(line_e) >= 2:
            output["passenger_name"] = line_e[1]

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
        print(f"WARNING: No H- lines found in {air_file_path}")

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(air_file_path))[0]
    json_file_name = f"{base_name}.json"
    full_path = os.path.join(output_dir, json_file_name)

    with open(full_path, 'w') as json_file:
        json.dump(output, json_file, indent=4)
        print(f" Saved JSON to {full_path}")


# ===  Traitement automatique ===
input_dir = "air_files"         # Dossier contenant les fichiers .AIR
output_dir = "output_json"      # Dossier de sortie pour les fichiers JSON
prefixes = ['A-', 'D-', 'G-', 'H-', 'T-', 'I']

for filename in os.listdir(input_dir):
    if filename.endswith(".AIR"):
        air_path = os.path.join(input_dir, filename)
        print(f" Processing {air_path}")
        results = extract_data(prefixes, air_path)
        parse_store_data_in_json(results, air_path, prefixes, output_dir)