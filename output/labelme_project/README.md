# LabelMe 標註專案 - 病床姿勢辨識

## 專案資訊
- 總圖片數: 5,132
- 建立時間: 2025-11-04 20:42:07
- 使用者: rochi190

## 開始標註
```bash
cd /home/gary/claude4.5/output/labelme_project
labelme images --labels classes.txt --output annotations
```

## 標註類別
- **lying**: 躺著（平躺在床上）
- **sitting**: 坐著（坐在床上或床邊）
- **fallen**: 跌倒（跌落床下）
- **empty**: 空床（無人）
- **uncertain**: 不確定（畫面不清楚）

## 標註步驟
1. LabelMe 視窗會自動開啟
2. 點擊「Create Polygons」或按 `Ctrl+N`
3. 用滑鼠框選**人體區域**（盡量完整）
4. 從下拉選單選擇姿勢類別
5. 按 `Ctrl+S` 儲存
6. 按 `D` 下一張圖片

## 快捷鍵
- `Ctrl+N`: 建立新標註
- `Ctrl+S`: 儲存
- `D`: 下一張
- `A`: 上一張
- `Ctrl+Z`: 復原

## 標註進度追蹤
```bash
ls annotations/*.json | wc -l
```

## 資料來源
- 配對策略: Adaptive Pairing（處理不固定 FPS）
- 配對數據: /home/gary/claude4.5/output/adaptive_pairing/pairs_mapping.json
