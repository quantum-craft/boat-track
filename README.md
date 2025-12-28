For windows

### 安裝 uv

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 安裝 git

```
https://git-scm.com/install/windows
```

### git clone 這個專案

### 進入資料夾

### 新增一個檔案 .env

#### 裡面填入 MARINE_TRAFFIC_API_KEY=xxxx, xxxx 是 api key

### uv sync

### 編輯 config.yaml

#### 填入起訖時間以及 mmsi

### uv run main.py

#### 下載的檔案片段在./temp 下

#### 拼起來的檔案在./results 下
