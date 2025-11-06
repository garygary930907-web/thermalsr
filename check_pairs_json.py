import json
import numpy as np
from pathlib import Path

def check_thermal_rgb_pairs_from_json(json_path, thermal_dir, rgb_dir):
    """
    從 JSON 檔案檢查 thermal-RGB 配對資訊
    
    Args:
        json_path: pairs_mapping_v3.json 的路徑
        thermal_dir: thermal .npy 檔案的資料夾路徑
        rgb_dir: RGB .jpg 檔案的資料夾路徑
    """
    # 讀取 JSON 檔案
    with open(json_path, 'r', encoding='utf-8') as f:
        pairs = json.load(f)
    
    print(f"總共找到 {len(pairs)} 組配對\n")
    print("="*80)
    
    # 檢查檔案是否存在
    thermal_files = sorted(Path(thermal_dir).glob("*.npy"))
    rgb_files = sorted(Path(rgb_dir).glob("*.jpg"))
    
    print(f"Thermal 檔案數量: {len(thermal_files)} (.npy)")
    print(f"RGB 檔案數量: {len(rgb_files)} (.jpg)")
    print("="*80)
    
    # 顯示前 5 組配對的詳細資訊
    print("\n前 5 組配對詳細資訊：\n")
    for i, pair in enumerate(pairs[:5]):
        print(f"配對 ID: {pair['pair_id']}")
        print(f"  Thermal 幀索引: {i} (frame_{i:05d}.npy)")
        print(f"  RGB 幀索引: {pair['rgb_frame_idx']} (frame_{pair['rgb_frame_idx']:05d}.jpg)")
        print(f"  時間戳記: {pair['timestamp']}")
        print(f"  時間誤差: {pair['rgb_error_ms']:.2f} ms")
        print(f"  標籤: {pair['label']}")
        print(f"  模態: {pair['modality']}")
        
        # 檢查檔案是否存在
        thermal_file = Path(thermal_dir) / f"frame_{i:05d}.npy"
        rgb_file = Path(rgb_dir) / f"frame_{pair['rgb_frame_idx']:05d}.jpg"
        
        thermal_exists = thermal_file.exists()
        rgb_exists = rgb_file.exists()
        
        print(f"  Thermal 檔案存在: {'✓' if thermal_exists else '✗'} {thermal_file}")
        print(f"  RGB 檔案存在: {'✓' if rgb_exists else '✗'} {rgb_file}")
        
        # 如果檔案存在，顯示檔案資訊
        if thermal_exists:
            thermal_data = np.load(thermal_file)
            print(f"    Thermal 形狀: {thermal_data.shape}, 資料型別: {thermal_data.dtype}")
        
        if rgb_exists:
            from PIL import Image
            rgb_img = Image.open(rgb_file)
            print(f"    RGB 尺寸: {rgb_img.size}, 模式: {rgb_img.mode}")
        
        print("-" * 80)
    
    # 統計分析
    print("\n統計分析：")
    print("="*80)
    
    # 計算平均時間誤差
    avg_error = sum(p['rgb_error_ms'] for p in pairs) / len(pairs)
    print(f"平均時間誤差: {avg_error:.2f} ms")
    
    # 找出最大和最小誤差
    max_error = max(pairs, key=lambda x: x['rgb_error_ms'])
    min_error = min(pairs, key=lambda x: x['rgb_error_ms'])
    
    print(f"最大時間誤差: {max_error['rgb_error_ms']:.2f} ms (配對 {max_error['pair_id']})")
    print(f"最小時間誤差: {min_error['rgb_error_ms']:.2f} ms (配對 {min_error['pair_id']})")
    
    # 檢查誤差分布
    error_ranges = {
        "< 5 ms": 0,
        "5-10 ms": 0,
        "10-15 ms": 0,
        "> 15 ms": 0
    }
    
    for pair in pairs:
        error = pair['rgb_error_ms']
        if error < 5:
            error_ranges["< 5 ms"] += 1
        elif error < 10:
            error_ranges["5-10 ms"] += 1
        elif error < 15:
            error_ranges["10-15 ms"] += 1
        else:
            error_ranges["> 15 ms"] += 1
    
    print("\n時間誤差分布:")
    for range_name, count in error_ranges.items():
        percentage = (count / len(pairs)) * 100
        print(f"  {range_name}: {count} 組 ({percentage:.1f}%)")
    
    # 檢查是否有重複的 RGB 幀
    rgb_indices = [p['rgb_frame_idx'] for p in pairs]
    unique_indices = set(rgb_indices)
    
    if len(rgb_indices) != len(unique_indices):
        print(f"\n⚠️  警告: 發現重複使用的 RGB 幀!")
        print(f"  總配對數: {len(rgb_indices)}")
        print(f"  唯一 RGB 幀數: {len(unique_indices)}")
    else:
        print(f"\n✓ 所有 RGB 幀都是唯一的")
    
    # 驗證所有配對的檔案都存在
    print("\n檔案完整性檢查:")
    print("="*80)
    missing_thermal = []
    missing_rgb = []
    
    for i, pair in enumerate(pairs):
        thermal_file = Path(thermal_dir) / f"frame_{i:05d}.npy"
        rgb_file = Path(rgb_dir) / f"frame_{pair['rgb_frame_idx']:05d}.jpg"
        
        if not thermal_file.exists():
            missing_thermal.append(f"frame_{i:05d}.npy")
        if not rgb_file.exists():
            missing_rgb.append(f"frame_{pair['rgb_frame_idx']:05d}.jpg")
    
    if missing_thermal:
        print(f"✗ 缺少 {len(missing_thermal)} 個 Thermal 檔案")
        print(f"  範例: {missing_thermal[:5]}")
    else:
        print(f"✓ 所有 Thermal 檔案都存在")
    
    if missing_rgb:
        print(f"✗ 缺少 {len(missing_rgb)} 個 RGB 檔案")
        print(f"  範例: {missing_rgb[:5]}")
    else:
        print(f"✓ 所有 RGB 檔案都存在")
    
    return pairs

# 使用範例
if __name__ == "__main__":
    json_path = "/home/gary/claude4.5/output1/adaptive_pairing/pairs_mapping_v3.json"
    thermal_dir = "/home/gary/claude4.5/output1/aligned_dataset/thermal"  # .npy 檔案資料夾
    rgb_dir = "/home/gary/claude4.5/output1/labelme_project/images"          # .jpg 檔案資料夾
    
    if Path(json_path).exists():
        pairs_data = check_thermal_rgb_pairs_from_json(json_path, thermal_dir, rgb_dir)
        
        # 額外功能：可以輕鬆篩選特定條件的配對
        print("\n" + "="*80)
        print("高品質配對 (誤差 < 5ms):")
        high_quality = [p for p in pairs_data if p['rgb_error_ms'] < 5]
        print(f"找到 {len(high_quality)} 組高品質配對")
        
    else:
        print(f"❌ 找不到檔案: {json_path}")