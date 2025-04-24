#!/usr/bin/env python3

import os
import pydicom
import argparse
import logging
import csv

def clean_text(string):
    forbidden_symbols = ["*", ".", ",", "\"", "\\", "/", "|", "[", "]", ":", ";", " "]
    for symbol in forbidden_symbols:
        string = string.replace(symbol, "_")
    return string.lower()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

parser = argparse.ArgumentParser(description='Extract DICOM metadata and save to CSV.')
parser.add_argument("--input", required=True)
parser.add_argument("--output_csv", required=True)
args = parser.parse_args()

input_dir = args.input
output_csv = args.output_csv

fields = [
    "PatientID", "StudyDate", "StationName", "DeviceSerialNumber",
    "MagneticFieldStrength", "StudyDescription", "SeriesDescription",
    "SeriesNumber", "Modality", "AcquisitionDuration", "PulseSequenceName",
    "InstanceNumber", "SeriesInstanceUID", "StudyInstanceUID"
]

rows = []

for root, dirs, files in os.walk(input_dir):
    dicom_files = [f for f in files if not f.startswith('.') and not f.endswith('.json')]
    if not dicom_files:
        continue

    first_dicom_path = os.path.join(root, dicom_files[0])
    try:
        ds = pydicom.read_file(first_dicom_path, force=True)
        row = {key: ds.get(key, "NA") for key in fields}
        rows.append(row)
    except Exception as e:
        logging.warning(f"Could not read {first_dicom_path}: {e}")

logging.info(f"Writing {len(rows)} rows to CSV: {output_csv}")
with open(output_csv, mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

