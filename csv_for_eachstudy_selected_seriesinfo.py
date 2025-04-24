#!/usr/bin/env python3
import csv
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description='Group DICOM series by modality and study.')
parser.add_argument('--input_csv', required=True)
parser.add_argument('--output_csv', required=True)
args = parser.parse_args()

input_csv = args.input_csv
output_csv = args.output_csv

# Dictionary: (PatientID, StudyDate) → list of rows
study_data = defaultdict(list)

with open(input_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pid = row['PatientID']
        sid = row.get('StudyDate', 'NA')  # Use StudyDate as study identifier
        study_data[(pid, sid)].append(row)

# Prepare grouped output
output_rows = []
for (pid, sid), rows in study_data.items():
    t1w_descs, t1w_psns = [], []
    t2w_descs, t2w_psns = [], []
    fmri_descs, fmri_psns = [], []
    dmri_descs, dmri_psns = [], []
    swi_descs, swi_psns = [], []

    for row in rows:
        desc = row.get("SeriesDescription", "").lower()
        psn = row.get("PulseSequenceName", "")
        orig_desc = row.get("SeriesDescription", "NA")
        orig_psn = row.get("PulseSequenceName", "NA")

        if "t1" in desc:
            t1w_descs.append(orig_desc)
            t1w_psns.append(orig_psn)
        elif "t2" in desc:
            t2w_descs.append(orig_desc)
            t2w_psns.append(orig_psn)
        elif "func" in desc or "fmap" in desc:
            fmri_descs.append(orig_desc)
            fmri_psns.append(orig_psn)
        elif "dwi" in desc or "dmri" in desc:
            dmri_descs.append(orig_desc)
            dmri_psns.append(orig_psn)
        elif "swi" in desc:
            swi_descs.append(orig_desc)
            swi_psns.append(orig_psn)

    output_rows.append({
        "PatientID": pid,
        "StudyDate": sid,
        "T1w_Descriptions": "; ".join(t1w_descs),
        "T1w_PulseSequences": "; ".join(t1w_psns),
        "T2w_Descriptions": "; ".join(t2w_descs),
        "T2w_PulseSequences": "; ".join(t2w_psns),
        "fMRI_Descriptions": "; ".join(fmri_descs),
        "fMRI_PulseSequences": "; ".join(fmri_psns),
        "dMRI_Descriptions": "; ".join(dmri_descs),
        "dMRI_PulseSequences": "; ".join(dmri_psns),
        "SWI_Descriptions": "; ".join(swi_descs),
        "SWI_PulseSequences": "; ".join(swi_psns),
    })

# Write new CSV
fieldnames = [
    "PatientID", "StudyDate",
    "T1w_Descriptions", "T1w_PulseSequences",
    "T2w_Descriptions", "T2w_PulseSequences",
    "fMRI_Descriptions", "fMRI_PulseSequences",
    "dMRI_Descriptions", "dMRI_PulseSequences",
    "SWI_Descriptions", "SWI_PulseSequences"
]

with open(output_csv, 'w', newline='') as out_csv:
    writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

