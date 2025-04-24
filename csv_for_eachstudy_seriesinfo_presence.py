#!/usr/bin/env python3
import csv
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description='Check sequence presence per PatientID and StudyDate.')
parser.add_argument('--input_csv', required=True)
parser.add_argument('--output_csv', required=True)
args = parser.parse_args()

input_csv = args.input_csv
output_csv = args.output_csv

# Prepare data structure for sequence presence
sequence_flags = defaultdict(lambda: {
    "T1w": 0, "T2w": 0, "fMRI": 0, "dMRI": 0, "SWI": 0
})

with open(input_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pid = row["PatientID"]
        study_date = row.get("StudyDate", "NA")
        key = (pid, study_date)

        if row.get("T1w_Descriptions", "").strip():
            sequence_flags[key]["T1w"] = 1
        if row.get("T2w_Descriptions", "").strip():
            sequence_flags[key]["T2w"] = 1
        if row.get("fMRI_Descriptions", "").strip():
            sequence_flags[key]["fMRI"] = 1
        if row.get("dMRI_Descriptions", "").strip():
            sequence_flags[key]["dMRI"] = 1
        if row.get("SWI_Descriptions", "").strip():
            sequence_flags[key]["SWI"] = 1

# Write to CSV
with open(output_csv, 'w', newline='') as out_csv:
    fieldnames = ["PatientID", "StudyDate", "T1w", "T2w", "fMRI", "dMRI", "SWI"]
    writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
    writer.writeheader()

    for (pid, study_date), flags in sequence_flags.items():
        writer.writerow({
            "PatientID": pid,
            "StudyDate": study_date,
            "T1w": flags["T1w"],
            "T2w": flags["T2w"],
            "fMRI": flags["fMRI"],
            "dMRI": flags["dMRI"],
            "SWI": flags["SWI"]
        })

