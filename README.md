# 照顧服務員技術稽核（線上查詢與閱讀）

依「臺北市立聯合醫院照顧服務技術稽核表」17 個單元整理的閱讀網站：

- **以單元為主**：左側選單選單元，顯示簡報（上一頁／下一頁、縮圖、全螢幕、鍵盤 ←→、手機左右滑動）與依題號排列的稽核項目。
- **關鍵字查詢**：同時搜尋稽核題目與簡報內文（OCR），點結果直接跳到該單元、該頁。
- **網址列圖示、加到主畫面捷徑**（PWA，可離線閱讀看過的內容）。
- 每單元可開啟原始 PDF；原始檔亦放在 [Google 雲端資料夾](https://drive.google.com/drive/folders/103fuY5-RcAzJ-aCYnueIWs1fNSx4tjSB?usp=sharing)。

## 更新內容

```bash
python tools/ocr.py        # 新增／更換單元 PDF 後：轉出 slides/NN/*.webp 並 OCR 到 ocr.json（已做過的單元會略過，要重做先刪 ocr.json 中該單元）
python tools/build.py      # 解析「照服技術稽核.pdf」題目 + OCR 文字 → data.js
python tools/make_icons.py # 重新產生圖示
```

改了 sw.js 快取的檔案清單時，請遞增 `CACHE` 版本號。需要：`pip install pymupdf winocr pillow`（Windows 繁中 OCR）。
