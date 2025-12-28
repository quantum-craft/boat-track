🚢 Marine Traffic Data Downloader
這是一個用於下載 Marine Traffic 數據的自動化工具。透過 uv 進行依賴管理，根據設定的時間區間與 MMSI 下載數據，並自動合併檔案。

📋 前置需求 (Prerequisites)
本專案適用於 Windows 環境。在開始之前，請確保您已安裝以下工具：

1. 安裝 uv (Python 套件管理器)
   請開啟 PowerShell 並執行以下指令：

PowerShell

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" 2. 安裝 Git

請前往 Git 官網下載並安裝 Windows 版本： 🔗 https://git-scm.com/install/windows

🚀 安裝步驟 (Installation) 3. 下載專案
開啟終端機 (Terminal) 或 PowerShell，執行以下指令將專案 Clone 下來：

Bash

git clone <YOUR_REPOSITORY_URL>
(請將 <YOUR_REPOSITORY_URL> 替換為實際的專案網址)

4. 進入專案資料夾
   Bash

cd <PROJECT_FOLDER_NAME> 5. 安裝相依套件
使用 uv 同步並安裝所有需要的 Python 套件：

Bash

uv sync
⚙️ 設定 (Configuration)
在執行程式前，請完成以下兩個設定檔案。

1. 設定 API Key (.env)
   在專案根目錄下新增一個名為 .env 的檔案，並填入您的 Marine Traffic API Key：

Code snippet

MARINE*TRAFFIC_API_KEY=您的\_API_KEY*填在這裡
⚠️ 注意：請勿將 API Key 洩漏給他人或上傳至公開的儲存庫。

2. 設定下載參數 (config.yaml)
   編輯根目錄下的 config.yaml 檔案，填入欲查詢的起訖時間以及船隻的 MMSI 編號。

YAML

# config.yaml 範例

start_date: "2023-01-01"
end_date: "2023-01-02"
mmsi: 123456789
▶️ 使用方法 (Usage)
完成設定後，執行主程式開始下載：

Bash

uv run main.py
📂 輸出結果 (Output)
程式執行完畢後，檔案將會儲存在以下目錄：

./temp：存放下載過程中的原始檔案片段。

./results：存放最終合併完成的完整檔案。

🛠️ 疑難排解 (Troubleshooting)
如果在安裝 uv 時遇到權限問題，請嘗試以 系統管理員身分 (Run as Administrator) 執行 PowerShell。

請確認 .env 檔案名稱開頭有一個點，且副檔名不是 .txt。
