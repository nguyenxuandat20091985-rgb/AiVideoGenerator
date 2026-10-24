# AiVideoGenerator – Facebook Video Auto Processor & Poster

Tự động tải video Facebook → xử lý FFmpeg (cắt 2s đầu/cuối, flip, speed 1.03x, watermark) → đăng lên Facebook Page của bạn qua Meta Graph API.

## Tính năng

- Download video public từ Facebook bằng `yt-dlp`
- Xử lý video bằng FFmpeg:
  - Cắt 2 giây đầu và 2 giây cuối
  - Lật ngang (hflip)
  - Tăng tốc 1.03x
  - Chèn watermark text
- Upload lên Facebook Page (video thường hoặc Reels)
- Tự động xóa file tạm sau khi đăng xong
- Cấu hình qua file `.env`

## Yêu cầu hệ thống

- Python 3.10+
- FFmpeg đã cài và có trong PATH
- Tài khoản Facebook Page + Meta App

### Cài FFmpeg

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install ffmpeg
```

## Cài đặt

```bash
git clone https://github.com/nguyenxuandat20091985-rgb/AiVideoGenerator.git
cd AiVideoGenerator

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Cấu hình

1. Copy file môi trường:

```bash
cp .env.example .env
```

2. Điền thông tin vào `.env`:

```env
FB_PAGE_ID=your_page_id
FB_PAGE_ACCESS_TOKEN=your_long_lived_page_access_token
WATERMARK_TEXT=YourBrand
```

### Cách lấy FB_PAGE_ID và FB_PAGE_ACCESS_TOKEN

1. Vào [Meta for Developers](https://developers.facebook.com/) → tạo App (type Business).
2. Thêm sản phẩm **Facebook Login** và **Pages API**.
3. Dùng [Graph API Explorer](https://developers.facebook.com/tools/explorer/):
   - Chọn App của bạn
   - Get Token → Get Page Access Token → chọn Page
   - Permissions cần: `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`, `publish_video`
4. Đổi short-lived token thành long-lived:

```bash
curl "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
```

5. Lấy Page ID: Graph API Explorer gọi `me/accounts` → copy `id` của Page.

> **Lưu ý:** Token Page dài hạn thường sống 60 ngày. Nên lưu và refresh định kỳ.

## Cách chạy

```bash
python main.py "https://www.facebook.com/watch/?v=XXXXXXXX"
```

Hoặc chạy interactive:

```bash
python main.py
```

## Cấu trúc thư mục

```
AiVideoGenerator/
├── main.py                 # Entry point
├── modules/
│   ├── downloader.py       # yt-dlp download Facebook video
│   ├── processor.py        # FFmpeg processing
│   └── uploader.py         # Meta Graph API upload
├── .env.example
├── requirements.txt
└── README.md
```

## Tham số xử lý FFmpeg (có thể chỉnh trong processor.py)

| Tham số       | Giá trị mặc định | Ý nghĩa                  |
|---------------|------------------|--------------------------|
| cut_start     | 2 giây           | Cắt đầu video            |
| cut_end       | 2 giây           | Cắt cuối video           |
| speed         | 1.03             | Tốc độ phát              |
| flip          | hflip            | Lật ngang                |
| watermark     | text             | Chữ watermark góc dưới   |

## Upload Reels (tùy chọn)

Trong `main.py` có flag `--reels`. Khi bật sẽ dùng flow Reels Publishing API (3 bước).

```bash
python main.py "URL" --reels
```

## Lưu ý quan trọng

- Chỉ dùng với video **public** hoặc video bạn có quyền tải.
- Flip + speed + watermark giúp giảm rủi ro bản quyền, nhưng **không đảm bảo 100%**.
- Meta có rate limit, đừng spam quá nhiều request.
- Token hết hạn → upload sẽ fail, cần refresh.

## License

MIT
