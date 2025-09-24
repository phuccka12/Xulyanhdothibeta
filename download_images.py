from bing_image_downloader import downloader

# Danh sách các món ăn muốn tải
foods = [
    "pho bo", "banh mi", "com tam", "bun cha",
    "goi cuon", "bun bo hue", "ga ran", "khoai tay chien"
]

# Vòng lặp tải ảnh
for food in foods:
    downloader.download(
        food,
        limit=20,  # số ảnh muốn tải cho mỗi món
        output_dir='dataset',  # thư mục lưu ảnh
        adult_filter_off=True,
        force_replace=False,
        timeout=60
    )
