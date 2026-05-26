# 📦 SHIELD Shared Resources

**共享資源目錄** - 所有模組共用的資產與資料

**[TonTon H.-D. Huang Ph.D.](https://TWMAN.ORG)**

- **相關文件**
  - [**專案說明文檔**](https://deep-learning-101.github.io/SHIELD/PROJECT-OVERVIEW)
  - [**Core Module**](https://deep-learning-101.github.io/SHIELD/core/)
  - [**Shared Resources**](https://deep-learning-101.github.io/SHIELD/shared/)
  - [**Modules**](https://deep-learning-101.github.io/SHIELD/modules/)
  - [**Phase 5: AI 審計與合規模組**](https://deep-learning-101.github.io/SHIELD/modules/eval/)
  - [**審計報告目錄**](https://deep-learning-101.github.io/SHIELD/shared/data/audit_results/)

---

## 📋 目錄說明

這個目錄集中管理 SHIELD 項目中所有模組共用的資源，包括圖片、視頻、音頻、資料庫文件等。

採用集中式管理可以：
- ✅ 避免資源重複
- ✅ 統一資源版本控制
- ✅ 簡化資源維護
- ✅ 方便跨模組引用

---

## 📁 目錄結構

```
shared/
├── README.md           # 本文件
├── assets/             # 媒體資源目錄
│   ├── *.png          # 圖片文件
│   ├── *.jpg          # 照片文件
│   ├── *.JPG          # 照片文件（大寫副檔名）
│   ├── *.mp4          # 視頻文件
│   ├── *.mp3          # 音頻文件
│   └── *.srt          # 字幕文件
│
└── data/               # 資料目錄
    ├── *.db           # 資料庫文件
    ├── *.csv          # CSV 資料文件
    ├── *.json         # JSON 資料文件
    └── policies/      # 政策文件目錄（動態生成）
```

---

## 🖼️ Assets 目錄

### 圖片資源

#### Logo 與品牌識別
- `shield-logo.jpg` - SHIELD 主標誌（橫式）
- `shield-logo.png` - SHIELD 主標誌（PNG 透明背景）
- `SHIELD.png` - SHIELD 品牌圖示

#### 系統架構圖
- `shield-poc.png` - 概念驗證架構圖
- `shield-flow.jpg` - 系統流程圖
- `Vectorless-001.png`, `Vectorless-002.png` - 向量化相關示意圖

#### 階段說明圖
- `Phase1-1.png`, `Phase1-2.png`, `Phase1-3.png` - 第一階段說明
- `Phase2.png` - 第二階段說明
- `Phase3-1.png` ~ `Phase3-5.png` - 第三階段說明

#### 功能展示圖
- `101.png` ~ `109.png` - 功能展示系列（1xx 系列）
- `110.JPG`, `111.JPG`, `112.JPG` - 額外功能展示

#### 企業應用圖
- `201.JPG` ~ `212.JPG` - 企業應用場景展示（2xx 系列）

### 視頻資源

- `S.H.I.E.LD.mp4` - SHIELD 系統介紹影片
- `SHIELD-DEMO.mp4` - 系統示範影片
- `SHIELD-Logo.mp4` - Logo 動畫
- `SHIELD-NBLM.mp4` - NotebookLM 相關影片
- `SHIELD-NBLM2.mp4` - NotebookLM 相關影片（第二版）
- `SHIELD-NBLM2.srt` - 字幕文件

### 音頻資源

- `shield.mp3` - NotebookLM Podcast 音頻

---

## 💾 Data 目錄

### 資料庫文件

#### 企業資產資料庫
- `20260319_enterprise_assets.db` - 企業 IT 資產資料
- `enterprise_assets.db` - 企業資產主資料庫（如有）

#### 合規矩陣資料庫
- `20260319_compliance_matrix.db` - 合規性檢查矩陣
- `compliance_matrix.db` - 合規矩陣主資料庫（如有）

### 資料文件

#### 金融業範例資料
- `finance_assets.csv` - 金融業資產清單
- `finance_compliance.json` - 金融業合規要求

### 動態生成目錄

#### Policies 目錄
- 此目錄由系統運行時動態創建
- 存放用戶上傳的政策文件
- 支援 PDF、Word、文本等格式

---

## 🔗 如何在代碼中引用

### 在 Core 模組中引用

Core 模組已經配置好路徑變數：

```python
# core/app.py 中已定義
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "shared", "data")
ASSETS_DIR = os.path.join(BASE_DIR, "shared", "assets")

# 使用範例
logo_path = os.path.join(ASSETS_DIR, "shield-logo.jpg")
db_path = os.path.join(DATA_DIR, "enterprise_assets.db")
```

### 在其他模組中引用

```python
import os

# 計算相對路徑
current_file = os.path.abspath(__file__)
module_dir = os.path.dirname(current_file)
shield_root = os.path.dirname(module_dir)

# 構建共享資源路徑
SHARED_DIR = os.path.join(shield_root, "shared")
ASSETS_DIR = os.path.join(SHARED_DIR, "assets")
DATA_DIR = os.path.join(SHARED_DIR, "data")

# 使用
image_path = os.path.join(ASSETS_DIR, "shield-logo.jpg")
```

### 在 README.md 中引用

Markdown 文件中使用相對路徑：

```markdown
<!-- 從根目錄 README.md 引用 -->
![SHIELD Logo](./shared/assets/shield-logo.jpg)

<!-- 從 core/README.md 引用 -->
![SHIELD Logo](../shared/assets/shield-logo.jpg)

<!-- 從 modules/module-name/README.md 引用 -->
![SHIELD Logo](../../shared/assets/shield-logo.jpg)
```

---

## 📝 資源管理規範

### 新增資源

1. **命名規範**
   - 使用描述性名稱：`feature-screenshot.png` 而非 `img1.png`
   - 保持一致的命名風格
   - 避免使用空格，使用連字符 `-` 或底線 `_`

2. **文件大小**
   - 圖片：建議 < 2MB，使用壓縮工具優化
   - 視頻：建議 < 50MB，或提供外部鏈接
   - 音頻：建議 < 10MB

3. **版本控制**
   - 大文件考慮使用 Git LFS
   - 或將大文件上傳到 CDN，在代碼中引用 URL

### 更新資源

1. **向後兼容**
   - 如果更換資源，保持文件名不變
   - 或更新所有引用該資源的地方

2. **變更記錄**
   - 在 Git commit 中說明更換原因
   - 重大變更通知所有開發者

### 刪除資源

1. **檢查依賴**
   - 使用 `grep -r "filename" .` 檢查是否有引用
   - 確保無處引用後才刪除

2. **存檔備份**
   - 刪除前先備份到外部存儲
   - 或在 Git 歷史中保留記錄

---

## 🔒 安全注意事項

### 敏感資料

⚠️ **絕對不要** 將以下內容放入 shared/ 目錄：

- ❌ API 密鑰
- ❌ 密碼或憑證
- ❌ 個人身份信息（PII）
- ❌ 客戶資料
- ❌ 商業機密

### 正確做法

✅ 使用環境變數：
```bash
# .env 文件（不提交到 Git）
API_KEY=your_secret_key
DATABASE_PASSWORD=your_password
```

✅ 使用配置文件：
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
```

---

## 📊 資源清單

### Assets 統計

```bash
# 查看 assets 目錄大小
du -sh shared/assets/

# 統計各類型文件數量
find shared/assets -type f -name "*.png" | wc -l
find shared/assets -type f -name "*.jpg" -o -name "*.JPG" | wc -l
find shared/assets -type f -name "*.mp4" | wc -l
```

### Data 統計

```bash
# 查看 data 目錄大小
du -sh shared/data/

# 查看資料庫文件資訊
ls -lh shared/data/*.db
```

---

## 🔧 維護工具

### 清理未使用的資源

```bash
# 找出可能未被引用的文件
for file in shared/assets/*; do
    filename=$(basename "$file")
    if ! grep -r "$filename" --exclude-dir=shared .; then
        echo "未引用: $file"
    fi
done
```

### 壓縮圖片資源

```bash
# 使用 ImageMagick 批量壓縮
mogrify -resize 1920x1080\> -quality 85 shared/assets/*.png
mogrify -resize 1920x1080\> -quality 85 shared/assets/*.jpg
```