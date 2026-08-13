import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Trên máy chủ đã triển khai, thiếu DATABASE_URL là hỏng chết người mà lại
# trông như bình thường: ứng dụng rơi về SQLite trên ổ đĩa tạm, khởi động ngon
# lành, kiểm tra sức khoẻ báo xanh, và mọi tài khoản biến mất ở lần triển khai
# kế tiếp. Không ai thấy gì cho tới khi một thầy cô đăng nhập không được.
#
# Render đặt sẵn RENDER=true trong mọi dịch vụ, nên chỗ này phân biệt được
# "đang chạy thật" với "đang chạy trên máy của mình" mà không cần thêm biến.
_TREN_MAY_CHU = bool(os.getenv("RENDER") or os.getenv("GALS_YEU_CAU_DATABASE_URL"))

if not DATABASE_URL:
    if _TREN_MAY_CHU:
        raise RuntimeError(
            "Thiếu DATABASE_URL. Từ chối khởi động: nếu rơi về SQLite trên ổ "
            "đĩa tạm thì toàn bộ tài khoản và bài viết sẽ mất ở lần triển khai "
            "sau, mà không có dấu hiệu gì. Nối cơ sở dữ liệu vào dịch vụ này "
            "rồi triển khai lại."
        )
    DATABASE_URL = f"sqlite:///{BASE_DIR / 'gals.db'}"

SECRET_KEY = os.getenv("SECRET_KEY", "gals-demo-secret-doi-khi-deploy")
SESSION_COOKIE = "gals_session"

# Phiên bản của hai văn bản pháp lý. Đổi số ở đây thì lần đăng nhập sau sẽ hỏi
# lại — bảng `consents` vì thế ghi được người dùng đã đồng ý với đúng bản nào.
PHIEN_BAN_RIENG_TU = "1.0"
# Ngày văn bản có hiệu lực. Đổi phiên bản thì đổi cả ngày này.
NGAY_HIEU_LUC = "16 tháng 08 năm 2026"
PHIEN_BAN_DIEU_KHOAN = "1.0"

# Đăng nhập bằng tài khoản có sẵn. Không có biến thì không hiện nút — không
# bao giờ có khoá nào nằm trong kho mã.
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "").strip()
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "").strip()
# "common" cho phép cả tài khoản trường lẫn tài khoản cá nhân; đặt mã tenant
# nếu chỉ muốn nhận một tổ chức.
MICROSOFT_TENANT = os.getenv("MICROSOFT_TENANT", "common").strip() or "common"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "").strip()

GEMINI_MODEL_PREFERENCE = (
    "gemini-flash-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
)

# Đợt thử nghiệm chỉ dành cho người từ 16 tuổi.
#
# Đăng ký trực tiếp vốn đã yêu cầu 16+, nhưng dưới 16 mà **có mã lớp hợp lệ**
# thì vẫn vào được, với lập luận rằng nhà trường đã xin phép gia đình. Trong đợt
# thử nghiệm này thì lập luận đó không dùng được: chưa có đường đồng ý của người
# giám hộ nào được dựng, chưa có đường nào được thử. Bật cờ này là đóng hẳn lối
# đó lại thay vì tin rằng nó ổn — và cả câu hỏi về đồng ý của người giám hộ rời
# khỏi phạm vi rủi ro của đợt thử nghiệm, đổi lấy đúng một câu `if`.
#
# Tắt cờ (đặt "0") thì hành vi cũ trở lại nguyên vẹn.
PILOT_16_PLUS = os.getenv("PILOT_16_PLUS", "1").strip() != "0"

MAX_MESSAGES_PER_SESSION = 30
MAX_CALLS_PER_HOUR = int(os.getenv("MAX_CALLS_PER_HOUR", "400"))

STEAM_FIELDS = (
    {"key": "khoa_hoc", "name": "Khoa học", "letter": "S", "accent": "teal"},
    {"key": "cong_nghe", "name": "Công nghệ", "letter": "T", "accent": "indigo"},
    {"key": "ky_thuat", "name": "Kỹ thuật", "letter": "E", "accent": "slate"},
    {"key": "nghe_thuat", "name": "Nghệ thuật", "letter": "A", "accent": "amber"},
    {"key": "toan", "name": "Toán", "letter": "M", "accent": "plum"},
)

FIELD_NAME_BY_KEY = {f["key"]: f["name"] for f in STEAM_FIELDS}
FIELD_KEY_BY_NAME = {f["name"]: f["key"] for f in STEAM_FIELDS}

PROJECT_CATEGORIES = (
    {"key": "nghe_thuat", "label": "Nghệ thuật"},
    {"key": "ky_thuat", "label": "Kỹ thuật"},
    {"key": "ca_hai", "label": "Cả hai"},
)


def gemini_enabled() -> bool:
    return bool(GEMINI_API_KEY)
