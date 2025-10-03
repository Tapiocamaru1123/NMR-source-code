# -*- coding: utf-8 -*-

# --- メイン処理 ---

# 1. データセットの選択ダイアログ
dataset_info = DATASET_DIALOG("Select 2D HSQC Data Series to Process")
if dataset_info is None:
    MSG("No data set selected. Script terminated.")
    EXIT() 

DATA_NAME = dataset_info[0]
DATA_DIR = dataset_info[3]

# 2. 処理する実験番号の範囲を入力
input_result = INPUT_DIALOG(
    title="Processing Parameters",
    header="Enter the EXPNO range to process.",
    items=["Start EXPNO:", "End EXPNO:"],
    values=["2", "3"]
)
if input_result is None:
    MSG("Parameters not entered. Script terminated.")
    EXIT()

try:
    START_EXPNO = int(input_result[0])
    END_EXPNO = int(input_result[1])
except ValueError:
    ERRMSG("Invalid input. Please enter numbers."); EXIT()

# --- メイン処理ループ ---
MSG("Starting batch processing ...")

for expno in range(START_EXPNO, END_EXPNO + 1):
    dataset_spec = [DATA_NAME, str(expno), "1", DATA_DIR]
    
    # 処理状況をステータスバーに表示
    SHOW_STATUS("Processing EXPNO {}...".format(expno))
    
    # 1. 生データを読み込む
    RE(dataset_spec, show='n')
    
    # 2. フーリエ変換を実行
    XCMD('xfb')
    
    # wrpコマンドを削除したため、ここでは処理結果は保存されません

# --- 完了メッセージ ---
MSG("All specified datasets have been processed with 'xfb'.")