#!/usr/bin/env python3

import os
import pydicom
import argparse
import logging
import csv
from datetime import datetime

def clean_text(string):
    forbidden_symbols = ["*", ".", ",", "\"", "\\", "/", "|", "[", "]", ":", ";", " "]
    for symbol in forbidden_symbols:
        string = string.replace(symbol, "_")
    return string.lower()

def format_birthdate(birth_str):
    try:
        return datetime.strptime(birth_str, "%Y%m%d").strftime("%Y-%m-%d")
    except:
        return "NA"

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
    "PatientID", "PatientBirthDate", "StudyDate", "StationName", "DeviceSerialNumber",
    "MagneticFieldStrength", "StudyDescription", "SeriesDescription",
    "SeriesNumber", "Modality", "AcquisitionDuration", "PulseSequenceName",
    "InstanceNumber", "SeriesInstanceUID", "StudyInstanceUID",
    "PixelSpacing", "SliceThickness", "SpacingBetweenSlices",
    "ImageOrientationPatient", "Rows", "Columns",
    "FOV_Row_mm", "FOV_Col_mm"
]

rows = []

for root, dirs, files in os.walk(input_dir):
    dicom_files = [f for f in files if not f.startswith('.') and not f.endswith('.json')]
    if not dicom_files:
        continue

    first_dicom_path = os.path.join(root, dicom_files[0])
    try:
        ds = pydicom.dcmread(first_dicom_path, force=True)

        row = {}
        for key in fields:
            if key == "PixelSpacing":
                val = ds.get("PixelSpacing", "NA")
                row[key] = ";".join(map(str, val)) if val != "NA" else "NA"
            elif key == "ImageOrientationPatient":
                val = ds.get("ImageOrientationPatient", "NA")
                row[key] = ";".join(map(str, val)) if val != "NA" else "NA"
            elif key == "FOV_Row_mm" or key == "FOV_Col_mm":
                continue  # Will calculate later
            elif key == "PatientBirthDate":
                birth_raw = ds.get("PatientBirthDate", "NA")
                row[key] = format_birthdate(birth_raw)
            else:
                row[key] = ds.get(key, "NA")

        # Compute Field of View
        pixel_spacing = ds.get("PixelSpacing", None)
        rows_px = ds.get("Rows", None)
        cols_px = ds.get("Columns", None)

        if pixel_spacing and rows_px and cols_px:
            try:
                row["FOV_Row_mm"] = round(float(pixel_spacing[0]) * int(rows_px), 2)
                row["FOV_Col_mm"] = round(float(pixel_spacing[1]) * int(cols_px), 2)
            except Exception:
                row["FOV_Row_mm"] = "NA"
                row["FOV_Col_mm"] = "NA"
        else:
            row["FOV_Row_mm"] = "NA"
            row["FOV_Col_mm"] = "NA"

        rows.append(row)
    except Exception as e:
        logging.warning(f"Could not read {first_dicom_path}: {e}")

logging.info(f"Writing {len(rows)} rows to CSV: {output_csv}")
with open(output_csv, mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

