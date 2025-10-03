# -*- coding: utf-8 -*-

import os
import csv
# import math # This script does not use the math library

# --- ダイアログ部分は省略 ---
dataset_info = DATASET_DIALOG("Select PRE-PROCESSED 2D HSQC Data Series")
if dataset_info is None: EXIT() 
DATA_NAME = dataset_info[0]
DATA_DIR = dataset_info[3]

input_result = INPUT_DIALOG(
    title="Analysis Parameters",
    header="Enter EXPNO range and peak picking sensitivity (MI).",
    items=["Start EXPNO:", "End EXPNO:", "Minimum Intensity (MI, rel):"],
    values=["2", "3", "0.100"] 
)
if input_result is None: EXIT()

try:
    START_EXPNO = int(input_result[0])
    END_EXPNO = int(input_result[1])
    MI_VALUE = str(input_result[2])
except ValueError:
    ERRMSG("Invalid input. Please enter numbers."); EXIT()

OUTPUT_CSV_FILE = 'global_peak_list.csv'

# --- メイン処理 ---
MSG("Starting global peak picking (no region)...")
results = []

for expno in range(START_EXPNO, END_EXPNO + 1):
    dataset_spec = [DATA_NAME, str(expno), "1", DATA_DIR]
    SHOW_STATUS("Analyzing EXPNO {}...".format(expno))
    RE(dataset_spec, show='n')
    
    XCMD("delp L") 

    # --- 範囲指定(Region)を削除し、それ以外のパラメータを指定 ---
    
    # Sensitivity (感度)
    PUTPAR("MI", MI_VALUE) # ダイアログで入力した値を使用
    PUTPAR("MAXI", "1.0000")
    PUTPAR("PPDIAG", "0")
    PUTPAR("PPRESOL", "1")
    
    # Miscellaneous (その他)
    PUTPAR("PPIPTYP", "None")
    PUTPAR("PSIGN", "Positive")
    
    PP()

    # --- 見つかった全ピークの情報を取得 ---
    try:
        peak_list = GETPEAKSARRAY()
        if peak_list:
            for i, peak in enumerate(peak_list):
                pos = peak.getPositions()
                intensity = peak.getIntensity()
                results.append({
                    'expno': expno, 'peak_id': i + 1,
                    'f1_ppm': pos[0], 'f2_ppm': pos[1],
                    'intensity': intensity
                })
    except Exception as e:
        results.append({'expno': expno, 'peak_id': 'Error', 'f1_ppm': str(e), 'f2_ppm': '', 'intensity': ''})

# --- CSV書き出し部分は省略 ---
output_path = os.path.join(DATA_DIR, DATA_NAME, OUTPUT_CSV_FILE)
try:
    with open(output_path, 'wb') as csvfile:
        fieldnames = ['expno', 'peak_id', 'f1_ppm', 'f2_ppm', 'intensity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    MSG("Analysis complete. Peak list saved to:\n" + output_path)
except Exception as e:
    ERRMSG("Error writing CSV file:\n" + str(e))