# LabelMe 標註專案 - 病床姿勢辨識 (v3)

## 專案資訊
- 總圖片數: 5,098
- 建立時間: 2025-11-04 22:52:32
- 版本: v3 - 修正時間戳配對

## ✅ 修正內容
- Thermal 時間戳手動加上毫秒偏移（125ms/幀）
- 每個 Thermal 配到不同的 RGB 幀（不再重複）
- RGB 幀間隔約 3 幀（符合 FPS 比例）

## 開始標註
```bash
cd /home/gary/claude4.5/output1/labelme_project
labelme images --labels classes.txt --output annotations
```

## 標註類別
- **lying**: 躺著
- **sitting**: 坐著
- **fallen**: 跌倒
- **empty**: 空床（跳過或標小區域）
- **uncertain**: 不確定

## 快捷鍵
- `Ctrl+N`: 建立新標註
- `Ctrl+S`: 儲存
- `D`: 下一張
- `A`: 上一張
