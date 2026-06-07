import pandas as pd
import os

def get_next_user_id(file_path: str):
    try:
        if not os.path.exists(file_path):
            print("File không tồn tại, bắt đầu từ ID: 1")
            return 1
        
        df = pd.read_csv(file_path, usecols=['userId'])
        
        if df.empty:
            return 1
        
        # Lấy giá trị lớn nhất và cộng 1
        max_id = int(df['userId'].max())
        next_id = max_id + 1
        
        return next_id
    
    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
        return None

# Sử dụng thực tế
csv_path = r'F:\project_SW\Media-Recommender-System\data-enrichment\data\movielens\ratings.csv'
new_id = get_next_user_id(csv_path)
print(f"ID mới cho user tiếp theo là: {new_id}")