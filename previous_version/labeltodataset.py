"""
將 LabelMe 標註轉換為訓練用格式
"""

import json
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# 路徑配置
LABELME_DIR = Path('./output/labelme_project')
IMAGES_DIR = LABELME_DIR / 'images'
ANNOTATIONS_DIR = LABELME_DIR / 'annotations'
METADATA_CSV = LABELME_DIR / 'image_metadata.csv'

OUTPUT_DIR = Path('./output/person_pose_dataset')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 類別映射
CLASS_MAPPING = {
    'lying': 0,
    'sitting': 1,
    'fallen': 2,
    'empty': 3,
    'uncertain': 4
}

def parse_labelme_json(json_path: Path) -> dict:
    """
    解析 LabelMe JSON 檔案
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    labels = []
    masks = []
    
    for shape in data['shapes']:
        label = shape['label']
        points = np.array(shape['points'], dtype=np.int32)
        
        labels.append(label)
        masks.append(points)
    
    return {
        'image_path': data['imagePath'],
        'labels': labels,
        'masks': masks,
        'image_height': data['imageHeight'],
        'image_width': data['imageWidth']
    }

def create_mask_image(points: np.ndarray, height: int, width: int) -> np.ndarray:
    """
    從多邊形點建立 mask
    """
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    return mask

def convert_all_annotations():
    """
    轉換所有 LabelMe 標註
    """
    json_files = list(ANNOTATIONS_DIR.glob('*.json'))
    
    if not json_files:
        print(f"❌ 未找到標註檔案於 {ANNOTATIONS_DIR}")
        return
    
    print(f"找到 {len(json_files)} 個標註檔案")
    
    # 載入 metadata
    metadata_df = pd.read_csv(METADATA_CSV)
    
    # 準備輸出
    masks_dir = OUTPUT_DIR / 'person_masks'
    masks_dir.mkdir(exist_ok=True)
    
    results = []
    
    for json_path in tqdm(json_files, desc="轉換標註"):
        # 解析 JSON
        annotation = parse_labelme_json(json_path)
        
        # 找對應的 metadata
        image_name = Path(annotation['image_path']).name
        meta_row = metadata_df[metadata_df['filename'] == image_name]
        
        if meta_row.empty:
            print(f"⚠️ 找不到 {image_name} 的 metadata")
            continue
        
        pair_id = meta_row.iloc[0]['pair_id']
        timestamp = meta_row.iloc[0]['timestamp']
        
        # 處理每個標註 (通常只有一個)
        for idx, (label, points) in enumerate(zip(annotation['labels'], annotation['masks'])):
            # 建立 mask
            mask = create_mask_image(
                points,
                annotation['image_height'],
                annotation['image_width']
            )
            
            # 儲存 mask
            mask_filename = f"{pair_id}_mask.png"
            mask_path = masks_dir / mask_filename
            cv2.imwrite(str(mask_path), mask)
            
            # 記錄結果
            results.append({
                'pair_id': pair_id,
                'timestamp': timestamp,
                'image_file': image_name,
                'mask_file': mask_filename,
                'pose_label': label,
                'pose_class': CLASS_MAPPING.get(label, -1),
                'mask_path': str(mask_path)
            })
    
    # 儲存結果
    results_df = pd.DataFrame(results)
    output_csv = OUTPUT_DIR / 'pose_labels.csv'
    results_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ 轉換完成!")
    print(f"   標註數: {len(results)}")
    print(f"   Masks: {masks_dir}")
    print(f"   Labels CSV: {output_csv}")
    
    # 統計
    print(f"\n📊 標註統計:")
    print(results_df['pose_label'].value_counts())
    
    return results_df

if __name__ == '__main__':
    results = convert_all_annotations()