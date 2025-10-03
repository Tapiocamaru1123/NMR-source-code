# -*- coding: utf-8 -*-

import os
import csv
import math

# --- ダイアログ部分は省略 ---
dataset_info = DATASET_DIALOG("Select 2D HSQC Data Series to Analyze")
if dataset_info is None: EXIT()
DATA_NAME = dataset_info[0]
DATA_DIR = dataset_info[3]

input_result = INPUT_DIALOG(
    title="Analysis Parameters",
    header="Enter analysis parameters.",
    items=[
        "Start EXPNO:", "End EXPNO:", 
        "GTP Peak F1(15N) ppm:", "GTP Peak F2(1H) ppm:",
        "GDP Peak F1(15N) ppm:", "GDP Peak F2(1H) ppm:",
        "Peak Search Region Width (ppm):",
        "Minimum Intensity (MI, rel):"
    ],
    values=["2", "3", "8.7", "0.6", "8.4", "0.1", "0.5", "0.03"]
)
if input_result is None: EXIT()

try:
    START_EXPNO = int(input_result[0])
    END_EXPNO = int(input_result[1])
    GTP_PEAK_PPM = (float(input_result[2]), float(input_result[3]))
    GDP_PEAK_PPM = (float(input_result[4]), float(input_result[5]))
    REGION_WIDTH_PPM = float(input_result[6])
    MI_VALUE = float(input_result[7])
except ValueError:
    ERRMSG("Invalid input. Please enter numbers."); EXIT()

OUTPUT_CSV_FILE = 'kinetics_GTP_vs_GDP_results.csv'

# --- 関数定義（変更なし） ---
def find_closest_2d_peak_intensity(peak_list, target_ppm):
    if not peak_list: return 0, None
    min_dist = float('inf')
    closest_peak_intensity = 0
    closest_peak_pos = None
    for peak in peak_list:
        try:
            pos = peak.getPositions()
            dist = math.sqrt((pos[0] - target_ppm[0])**2 + (pos[1] - target_ppm[1])**2)
            if dist < min_dist:
                min_dist = dist
                closest_peak_intensity = peak.getIntensity()
                closest_peak_pos = (pos[0], pos[1])
        except (AttributeError, IndexError): continue
    return closest_peak_intensity, closest_peak_pos

# --- メイン処理 ---
MSG("Starting targeted analysis...")
results = []

for expno in range(START_EXPNO, END_EXPNO + 1):
    dataset_spec = [DATA_NAME, str(expno), "1", DATA_DIR]
    
    SHOW_STATUS("Processing EXPNO {}...".format(expno))
    
    RE(dataset_spec, show='n')
    XCMD('xfb')
    
    # PROCNO 1 を指定してダイアログを抑制
    XCMD("wrp 1") # ← ここを修正しました

    RE(dataset_spec, show='n')
    XCMD("delp L")

    gtp_command = "pp f1p={} f1e={} f2p={} f2e={} mi={} psign=Positive".format(
        GTP_PEAK_PPM[0] + REGION_WIDTH_PPM / 2, GTP_PEAK_PPM[0] - REGION_WIDTH_PPM / 2,
        GTP_PEAK_PPM[1] + REGION_WIDTH_PPM / 2, GTP_PEAK_PPM[1] - REGION_WIDTH_PPM / 2, MI_VALUE
    )
    XCMD(gtp_command)

    gdp_command = "pp -a f1p={} f1e={} f2p={} f2e={} mi={} psign=Negative".format(
        GDP_PEAK_PPM[0] + REGION_WIDTH_PPM / 2, GDP_PEAK_PPM[0] - REGION_WIDTH_PPM / 2,
        GDP_PEAK_PPM[1] + REGION_WIDTH_PPM / 2, GDP_PEAK_PPM[1] - REGION_WIDTH_PPM / 2, MI_VALUE
    )
    XCMD(gdp_command)

    try:
        peak_list = GETPEAKSARRAY()
        gtp_intensity, gtp_pos = find_closest_2d_peak_intensity(peak_list, GTP_PEAK_PPM)
        gdp_intensity, gdp_pos = find_closest_2d_peak_intensity(peak_list, GDP_PEAK_PPM)
        results.append({'expno': expno, 'gtp_intensity': gtp_intensity, 'gdp_intensity': gdp_intensity})
    except Exception as e:
        results.append({'expno': expno, 'gtp_intensity': 'Error', 'gdp_intensity': 'Error'})

# --- CSV書き出し（変更なし） ---
output_path = os.path.join(DATA_DIR, DATA_NAME, OUTPUT_CSV_FILE)
try:
    with open(output_path, 'wb') as csvfile:
        fieldnames = ['expno', 'gtp_intensity', 'gdp_intensity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    MSG("Analysis complete. Results saved to:\n" + output_path)
except Exception as e:
    ERRMSG("Error writing CSV file:\n" + str(e))