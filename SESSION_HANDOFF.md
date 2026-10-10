# Doombo – Bàn giao session thiết kế ERD

> **Cập nhật:** 2026-10-10 · **Nguồn:** session Claude Code (desktop, Windows) đã làm việc với user từ 2026-10-09.
> Session mới (cloud / GitHub) **đọc hết file này trước khi làm tiếp**. File này thay cho toàn bộ ngữ cảnh hội thoại và bộ nhớ local không đồng bộ được.

---

## 0. Tóm tắt nhanh

- **Dự án:** thiết kế database (ERD → bảng + "package" xử lý nghiệp vụ) cho **Doombo**, web game MMO RPG kiểu **Diablo**, thế giới chung, giai đoạn đầu tối đa 2 người chơi cùng lúc.
- **Sản phẩm đang làm:** file **`Doombo.drawio`** ở gốc repo, có 3 trang:
  - **`Physical ERD`**: trang **chính thức**, sạch, không có màu đánh dấu thay đổi.
  - **`New Version`**: trang **làm việc**, mọi thay đổi mới được **tô màu so với `Physical ERD`**.
  - **`ERD Diagram`**: sơ đồ khái niệm cũ, **đã lỗi thời**, chưa cập nhật.
- **Đang ở đâu:** vòng chỉnh sửa lớn mới nhất (thêm Quest, Achievement, Skill Effect / Status, Level_Exp, Game_Config, đồ rơi, các mục phát triển sau…) **đã nằm trên `New Version` và đang chờ user duyệt**.
- **Bước tiếp theo:**
  1. Chờ user duyệt hoặc góp ý `New Version`.
  2. Khi user đồng ý → **compile** `New Version` thành `Physical ERD` chính thức (mục 4.5).
  3. Tiếp tục các mục còn mở (mục 9).
- **Chỗ hội thoại đang dừng và các việc đang dở:** xem **mục 10**. User **chưa trả lời** 2 câu hỏi cuối của Claude.
- **Đồng bộ máy local ↔ cloud:** xem mục 11. **Công cụ Python** để sửa file và tô màu: thư mục `tools/erd/` (Phụ lục A).
- **Ngôn ngữ:** user viết **tiếng Việt** (văn nói, hay viết tắt / sai chính tả nhẹ). Trả lời bằng tiếng Việt, xưng "mình", gọi user là "bạn".

---

## 1. Bối cảnh game (do user mô tả)

- **Thể loại:** web MMO RPG kiểu Diablo, multiplayer. Hiện tại **1 thế giới chung duy nhất**: "2 người chơi" chỉ là giới hạn ban đầu, sau này mở rộng thêm người, **không phải** chia phòng 2 người.
- **Vật phẩm:**
  - Có đồ tiêu thụ (máu, mana…) và trang bị.
  - **Item_Basic** là mẫu gốc: chỉ số cơ bản cố định, thay đổi theo Quality.
  - **Item** là thực thể thật trong game = phần Basic + các buff random (số lượng buff và độ mạnh tùy Quality).
  - Mỗi Item là duy nhất, chỉ được xóa khi không còn nằm ở Inventory / Chest / Equipment (và Vendor).
- **Đồ rơi:** đánh quái hoặc mở rương trên map rơi ra đồ, gồm 1 khung chỉ số cố định + 1 khung chỉ số random theo Quality.
- **Class và skill:**
  - Class có thể tiến hóa và rẽ nhánh. Ví dụ Warrior lên Lv20 tiến hóa thành Barbarian hoặc Guardian.
  - Mỗi Class có cây skill riêng; một số skill dùng chung giữa nhiều Class.
- **Chest (rương cá nhân):** theo **Account**, các Character cùng Account dùng chung. **Inventory** theo **Character**.
- **Region:** chỉ đơn giản là map (Map 1, Map 2…). Region quy định quái xuất hiện, đồ rơi và NPC của khu vực. Vendor ở đó bán đồ liên quan, đổi hàng mỗi ngày; Vendor bán đồ tiêu thụ thì giữ hàng, chỉ đổi giá.
- **Creep (quái):** có stat theo Quality (dựa trên stat gốc, giống cách làm với Item) và có skill riêng. Boss dùng chung entity Creep. Có Boss xuất hiện theo giờ: ví dụ 11:00, nếu chưa bị giết trước 11:30 thì biến mất, lặp lại mỗi ngày.
- **Tiền tệ:**
  - **Gold** riêng từng Character.
  - **Diamond** theo Account (dùng chung).
  - Diamond **chỉ nhận được qua Quest / Achievement**; hiện **chưa** làm nạp tiền hay cửa hàng.
- **Quest:** gồm tuyến chính (MAIN), phụ (SIDE), hằng ngày (DAILY) và sự kiện (EVENT). Có **QUEST_ITEM**: vật phẩm không có tác dụng, chỉ để thu thập rồi nộp cho NPC nhận thưởng.
- **NPC (phát triển sau):** thương nhân lang thang xuất hiện ngẫu nhiên trên map (và trong Dungeon), bán đồ quý không mua được ở nơi khác.
- **Database:**
  - Kiểu dữ liệu đang dùng theo **PostgreSQL**: BIGINT, TIMESTAMPTZ, NUMERIC, TEXT…
  - "Package" là lớp stored procedure / function xử lý nghiệp vụ. **Chưa viết DDL / SQL nào**, hiện mới ở mức ERD.
- **Repo:** có project Godot `doombo/` (client game, map isometric). Phiên làm việc này **chỉ đụng tới `Doombo.drawio`**.

---

## 2. Repo và file

| Đường dẫn | Ghi chú |
|---|---|
| `Doombo.drawio` | File ERD chính, được user mở bằng **draw.io desktop** (khi lưu, file ghi `host="Electron"`). |
| `doombo/` | Project Godot (không liên quan tới việc thiết kế ERD). |
| `README.md`, `.gitignore` | `.gitignore` bỏ qua `*.bkp` và `.$*` (file backup của draw.io). |
| `ERD/`, `Database/` | Thư mục user mới tạo, hiện **trống**. |

- **Remote:** `https://github.com/longempty/Doombo` (nhánh `main`).
- Trên máy user, thư mục nằm trong **OneDrive**. Lúc OneDrive đang đồng bộ, file có thể tạm "biến mất" vài giây; cần kiểm tra lại trước khi kết luận file mất.

**Quy ước về các trang trong `Doombo.drawio`:**

| Trang | Vai trò | Quy tắc |
|---|---|---|
| `Physical ERD` | Bản **chính thức** | **Không sửa trực tiếp.** Chỉ thay thế khi compile. Không có note chú thích, không có màu đánh dấu thay đổi. |
| `New Version` | Bản **làm việc** | Mọi chỉnh sửa làm ở đây. Màu tô thể hiện chênh lệch so với `Physical ERD`. Có note chú thích (`note_legend`). |
| `ERD Diagram` | ERD khái niệm cũ | Chưa cập nhật theo thiết kế mới. User chưa yêu cầu sửa. |

---

## 3. Quy ước làm việc với user (BẮT BUỘC tuân theo)

1. **Tô màu mọi thay đổi** so với bản trước, cả thuộc tính lẫn note. Luật này áp dụng chung cho mọi lần sửa.
   | Ký hiệu | Ý nghĩa |
   |---|---|
   | Nền dòng `#d5e8d4` (xanh lá) | thuộc tính mới (kể cả mọi dòng của bảng mới) |
   | Nền dòng `#ffe6cc` (cam) | thuộc tính bị sửa: tên, kiểu, ràng buộc |
   | Nền tiêu đề bảng `#ffe6cc` | bảng bị đổi tên |
   | Nền dòng `#f8cecc` (hồng) | "chưa chốt, cần trao đổi" (chỉ dùng khi cần) |
   | Viền note `strokeColor=#FF0000; strokeWidth=3` | note mới hoặc bị sửa |
   | Đường nối `strokeColor=#FF0000; strokeWidth=2` | quan hệ (FK) mới; so theo cặp (nguồn, đích), không theo id |
   | Note `note_legend` (nền xám) trên trang làm việc | liệt kê bảng đổi tên, bảng / thuộc tính / liên kết **đã bỏ** (phần đã bỏ không tô màu được) |
2. **Note lookup:** khai báo giá trị Lookup_Code bằng **note nền tím** (`fillColor=#e1d5e7; strokeColor=#9673a6`), giống note "Skill Type" mẫu của user.
   - Ghi rõ `Lookup_Object = ...` và các giá trị `1 – X, 2 – Y…`.
   - Tất cả xếp **1 cột cạnh bảng `Range_Buff`** (x ≈ 3420), không đặt cạnh từng bảng vì user thấy rối mắt.
3. **Cột tham chiếu Lookup_Code** có nhãn `(link Lookup_Code)` **in đậm, màu xanh `#0050EF`** ngay trong tên thuộc tính.
4. **Luật nghiệp vụ** ghi trong **note vàng** (`fillColor=#fff2cc; strokeColor=#d6b656`), đặt **cạnh entity liên quan**, không gộp 1 note lớn. Note thừa hoặc đã xử lý xong thì được phép xóa hoặc gộp.
5. **Entity "phát triển sau"** (có cũng được, không có cũng được) để **nền vàng** `fillColor=light-dark(#FFF2CC,#CCCC00)`, **không nối liên kết**, đặt chung một khu.
6. **Không tạo file backup.** Không tạo trang copy trừ khi user yêu cầu (quy trình hiện tại: `Physical ERD` + `New Version`).
7. **Không dời entity không liên quan** tới thay đổi; được dời entity liên quan để tránh chồng hình. **Không đổi thuộc tính** khi user chỉ yêu cầu sắp xếp lại bố cục.
8. **User hay tự sửa file** trong draw.io desktop: dời bảng, xóa cột, đổi tên, vẽ lại đường nối. **Trước mỗi lần ghi, luôn so file với bản mình ghi lần trước** để thấy user đã sửa gì và giữ nguyên các sửa đổi đó. Nếu user bỏ một cột mà các chỗ khác vẫn tham chiếu (ví dụ `Chest_Tab_Count`), sửa các tham chiếu cho khớp và **báo lại user**.
9. **Sau khi ghi file**, nhắc user **đóng rồi mở lại file trong draw.io desktop, đừng lưu bản đang mở cũ**, nếu không thay đổi sẽ bị ghi đè.
10. **Sau mỗi vòng sửa**, trả lời gồm:
    - tổng hợp thay đổi **theo từng entity** (+ thêm / ~ sửa / − bỏ / FK);
    - những gì mình tự quyết thay user, kèm lý do;
    - câu hỏi còn mở, có phương án gợi ý.
    - Khi đề xuất một hướng đi, đưa ra lựa chọn có khuyến nghị; **không đề xuất lại phương án user đã từ chối** (mục 7).
11. **Không commit / push** khi user chưa yêu cầu.

---

## 4. Quy trình kỹ thuật khi sửa `Doombo.drawio`

### 4.1 Cấu trúc XML
- File là **XML không nén**: `<mxfile><diagram name="..."><mxGraphModel><root><mxCell .../>…`.
- **Bảng** là `mxCell` có `style` chứa `swimlane;…childLayout=stackLayout;…startSize=26` (một số bảng cũ có `startSize=30`), `parent="1"`.
- **Thuộc tính (dòng)** là `mxCell` con có `parent` bằng id của bảng; tọa độ `y` xếp chồng theo `startSize + 30*i`; chiều cao bảng = `startSize + 30 × số dòng`.
  - Style của dòng: `text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;rotatable=0;whiteSpace=wrap;html=1;`
- **FK** là `mxCell edge="1"`, `source`/`target` trỏ vào **id của dòng**, style `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;`. Chiều mũi tên vẽ không thống nhất; xác định FK dựa vào nhãn `(FK)` của cột.
- **Note** là `mxCell` có `shape=note`; nội dung là HTML (`<br>`, `<b>`, `<span style=...>`).
- **Id:** id gốc của user có dạng ngẫu nhiên (`aidSqVbqEgVGXthLOxOh-xx`, `JXMNVE_-JRXyASBiuB6P-xx`…). Id do Claude tạo đặt tên dễ đọc: `tbl_*`, `note_rule_*`, `note_lk_*`, `note_legend`, `edge_*`. **Giữ nguyên id khi sửa** để việc so sánh khác biệt hoạt động đúng.

### 4.2 Cách sửa
- Dùng **Python `xml.etree.ElementTree`** qua thư viện **`tools/erd/erd_lib.py`** (class `ErdPage`): `add_row`, `relayout`, `order_rows`, `add_table`, `add_edge`, `add_note`, `replace_in`, `restyle`, `remove`, `save`. Mọi sửa đổi làm trên **trang `New Version`**.
- Viết script sửa trong thư mục tạm, dùng `assert` / `replace_in` để nếu có bước lỗi thì **không ghi file dở**; chỉ gọi `save()` ở cuối.
- Sau khi thêm hoặc bớt dòng, gọi `relayout(table)` để tính lại y và chiều cao. Nhãn dài thì nới rộng: `relayout(table, width=…)`.
- Khi thêm bảng hoặc note mới, chọn tọa độ ở vùng trống (bảng 4.4) rồi chạy `check.py` để chắc chắn không chồng hình.

Ví dụ:
```python
import sys; sys.path.insert(0, "tools/erd")
from erd_lib import ErdPage, LINK, lookup_note, LOOKUP_NOTE
p = ErdPage("Doombo.drawio", "New Version")
p.add_row("cziWY0EkAAtVQsHl7tzw-5", "acc_xxx", "Xxx_Type (int)" + LINK)   # thêm cột vào Account
p.relayout("cziWY0EkAAtVQsHl7tzw-5")
p.add_table("tbl_new", "New_Table", 4600, 1060, 300,
            [("nt_id", "New_ID (int, PK)"), ("nt_char", "Character_ID (BIGINT, FK)")])
p.add_edge("edge_nt_char", "nt_char", "cziWY0EkAAtVQsHl7tzw-2")         # FK sang Character.Character_ID
p.save()
```

### 4.3 Kiểm tra sau mỗi lần ghi (chạy từ gốc repo, dùng `python` thường, **không** thêm `-I`)
1. Trước khi sửa: `python tools/erd/dump.py Doombo.drawio > before.txt`. Sau khi sửa: dump lại rồi so sánh, để chắc chắn `Physical ERD` và `ERD Diagram` **không đổi**. Phần trang `New Version` thay đổi đúng như dự định.
2. `python tools/erd/recolor.py Doombo.drawio "Physical ERD" "New Version" ""`: tô màu lại toàn bộ và dựng lại `note_legend`.
3. `python tools/erd/check.py Doombo.drawio "New Version"`: phải ra `overlaps: 0`; đồng thời liệt kê các chỗ đang được tô màu.
4. `python tools/erd/changelog.py Doombo.drawio "Physical ERD" "New Version"`: lấy danh sách thay đổi theo entity, dùng khi báo cáo cho user.

**Id các bảng hay dùng** (id gốc của user, giữ nguyên):

| Bảng | Id | Cột PK (id) |
|---|---|---|
| Account | `cziWY0EkAAtVQsHl7tzw-5` | `cziWY0EkAAtVQsHl7tzw-6` |
| Character | `cziWY0EkAAtVQsHl7tzw-1` | `cziWY0EkAAtVQsHl7tzw-2` |
| Character_Stat | `aidSqVbqEgVGXthLOxOh-101` | `aidSqVbqEgVGXthLOxOh-102` |
| Class | `cziWY0EkAAtVQsHl7tzw-15` | `cziWY0EkAAtVQsHl7tzw-16` |
| Item | `JXMNVE_-JRXyASBiuB6P-179` | `JXMNVE_-JRXyASBiuB6P-180` |
| Item_Basic | `E8S67BiSvyNXWUljgaMx-5` | `E8S67BiSvyNXWUljgaMx-6` |
| Item_Stat | `JXMNVE_-JRXyASBiuB6P-213` | `JXMNVE_-JRXyASBiuB6P-217` |
| Inventory | `tbl_inventory_item` | `inv_item_item` |
| Personal_Chest | `tbl_chest_item` | `chest_item_item` |
| Character_Equipment | `aidSqVbqEgVGXthLOxOh-13` | `aidSqVbqEgVGXthLOxOh-14` |
| Region | `aidSqVbqEgVGXthLOxOh-116` | `aidSqVbqEgVGXthLOxOh-117` |
| NPC | `aidSqVbqEgVGXthLOxOh-23` | `aidSqVbqEgVGXthLOxOh-24` |
| Vendor | `aidSqVbqEgVGXthLOxOh-34` | `aidSqVbqEgVGXthLOxOh-36` |
| Creep | `aidSqVbqEgVGXthLOxOh-56` | `aidSqVbqEgVGXthLOxOh-57` |
| Creep_Stat | `aidSqVbqEgVGXthLOxOh-62` | `aidSqVbqEgVGXthLOxOh-63` |
| Creep_Skill | `aidSqVbqEgVGXthLOxOh-70` | `aidSqVbqEgVGXthLOxOh-71` |
| Creep_Skill_Detail | `aidSqVbqEgVGXthLOxOh-79` | `aidSqVbqEgVGXthLOxOh-80` |
| Skill | `FU3Yxe4wLFygVKeGAofF-3` | `FU3Yxe4wLFygVKeGAofF-4` |
| Skill_Detail | `tbl_skill_level` | `aidSqVbqEgVGXthLOxOh-29` |
| Skill_Effect | `JXMNVE_-JRXyASBiuB6P-66` | `se_id` |
| Status | `FU3Yxe4wLFygVKeGAofF-14` | `FU3Yxe4wLFygVKeGAofF-15` |
| Quest | `JXMNVE_-JRXyASBiuB6P-28` | `JXMNVE_-JRXyASBiuB6P-29` |
| Achievement | `YVxcspwUH4dH9gIVws8s-1` | `YVxcspwUH4dH9gIVws8s-2` |
| Lookup_Code | `JXMNVE_-JRXyASBiuB6P-73` | `JXMNVE_-JRXyASBiuB6P-74` |
| Range_Buff | `JXMNVE_-JRXyASBiuB6P-122` | — |

Với các bảng khác, tìm id bằng cách dò nhãn trong output của `dump.py`.

### 4.4 Bố cục hiện tại của `New Version` (tọa độ xấp xỉ)

| Khu vực | Vị trí |
|---|---|
| Game_Config, Level_Exp, note key Game_Config | góc trên trái (x −320..550, y −720..−320) |
| Legend | x −320..10, y −160..540 |
| Account / Character / Inventory / Personal_Chest / Equipment | x 350..1320, y 300..1060 |
| Class / Skill / Character_Skill_* | x −350..1540, y 1000..1850 |
| Item / Item_Stat / Item_Basic / Region / Region_* | x 1550..2430, y 230..1540 |
| Nhóm Creep | x 1070..2470, y −360..240 |
| Rule – Stat | phía trên nhóm Creep, y −860 |
| NPC / Vendor | x 2350..2740, y 490..930 |
| Các note rule Creep / Region / Vendor / Lookup | x 2530..4470, y −100..1020 |
| Cụm hiệu ứng skill (Skill_Effect, Status, Status_Stat, Creep_Skill_Effect + rule) | x 1300..2370, y 1700..2350 |
| Khu **phát triển sau** (nền vàng) | x 2540..3100, y 1050..2430 |
| Range_Buff | x 3120..3330, y 1030..2106 |
| Cột note lookup tím | x 3420..3700, y 1030..3550 |
| Cụm Quest + Achievement + rule | x 3760..4470, y 1060..2370 |

### 4.5 Compile `New Version` → `Physical ERD` (khi user duyệt)
Lệnh: `python tools/erd/compile_official.py Doombo.drawio`, sau đó `python tools/erd/recolor.py Doombo.drawio "Physical ERD" "New Version" ""`. Script làm đúng các bước dưới đây (đã chạy thử trên bản sao):

1. Deep-copy trang `New Version`, đặt tên `Physical ERD`, giữ `id` của trang `Physical ERD` cũ, rồi **thay thế** trang cũ ở cùng vị trí.
2. Trên bản chính thức, **xóa màu đánh dấu**:
   - nền dòng `#d5e8d4`, `#ffe6cc`, `#f8cecc` → `none`;
   - tiêu đề bảng `#ffe6cc` → bỏ `fillColor`;
   - note viền `#FF0000` → khôi phục viền gốc theo màu nền (`#fff2cc` → `#d6b656`, `#e1d5e7` → `#9673a6`), bỏ `strokeWidth`;
   - edge đỏ → bỏ `strokeColor` và `strokeWidth`.
   - **Xóa `note_legend`** khỏi bản chính thức.
   - **Giữ nguyên** các quy ước: note tím, nền vàng của mục phát triển sau, nhãn `(link Lookup_Code)`.
3. Giữ trang `New Version` làm trang làm việc, chạy lại `recolor.py` so với bản chính thức mới (lúc này gần như không còn màu).
4. Kiểm tra: bản chính thức có 0 màu đánh dấu và không có legend; `ERD Diagram` không đổi; không có hình chồng nhau.

---

## 5. Trạng thái hiện tại

### 5.1 Toàn bộ entity trên `New Version` (trích tự động từ file)
- Ký hiệu: `PK` khóa chính, `FK` khóa ngoại, `NULL` cho phép rỗng, `(link Lookup_Code)` cột lưu `Lookup_Int`.
- Dòng "FK:" liệt kê các đường nối đi ra từ bảng đó (theo chiều đã vẽ).
- Bảng gắn *(phát triển sau)* là bảng nền vàng, không nối liên kết.

<details><summary>Bấm để xem danh sách đầy đủ (51 bảng)</summary>

#### Account
- Account_ID (BIGINT, PK)
- Username (VARCHAR, UNIQUE)
- Diamond (BIGINT)
- Password_Hash (TEXT)
- PhoneNumber (VARCHAR)
- EmailAddress (VARCHAR, UNIQUE)
- Created_At (TIMESTAMPTZ)
- Last_Login_At (TIMESTAMPTZ)
- Account_Status (int) (link Lookup_Code)
- FK: Account.Account_ID → Character.Account_ID

#### Achievement
- Achievement_ID (int, PK)
- Achievement_Name (varchar)
- Achievement_Description (text)
- Condition_Type (int) (link Lookup_Code)
- Target_ID (int, NULL)
- Target_Value (int)
- Reward_Type (int) (link Lookup_Code)
- Reward_Item_Basic_ID (int, FK, NULL)
- Reward_Amount (int)
- FK: Achievement.Reward_Item_Basic_ID → Item_Basic.Item_Basic_ID

#### Character
- Character_ID (BIGINT, PK)
- Account_ID (BIGINT, FK)
- Class_ID (BIGINT, FK)
- CharacterNum (int) (slot)
- Name (VARCHAR, UNIQUE)
- Gold (BIGINT)
- Level (INTEGER)
- Exp (BIGINT)
- SkillPoint (INTEGER)
- Created_At (TIMESTAMPTZ)

#### Character_Achievement
- Character_ID (BIGINT, PK/FK)
- Achievement_ID (int, PK/FK)
- Progress (int)
- Completed_At (TIMESTAMPTZ, NULL)
- Rewarded_At (TIMESTAMPTZ, NULL) (NULL = chưa nhận)
- FK: Character_Achievement.Character_ID → Character.Character_ID; Character_Achievement.Achievement_ID → Achievement.Achievement_ID

#### Character_Dungeon  — *(phát triển sau)*
- Character_ID (BIGINT, PK/FK)
- Dungeon_ID (int, PK/FK)
- Clear_Count (int)
- Best_Time (int) (giây)
- Last_Clear_At (TIMESTAMPTZ)

#### Character_Equipment
- Character_ID (BIGINT, PK/FK)
- Item_ID (BIGINT, FK, UNIQUE)
- Equip_Slot (varchar, PK)
- Equipped_At (TIMESTAMPTZ)
- FK: Character_Equipment.Character_ID → Character.Character_ID; Character_Equipment.Item_ID → Item.Item_ID

#### Character_Quest
- Character_ID (BIGINT, PK/FK)
- Quest_ID (int, PK/FK)
- Quest_Status (int) (link Lookup_Code)
- Accepted_At (TIMESTAMPTZ)
- Completed_At (TIMESTAMPTZ, NULL)
- FK: Character_Quest.Character_ID → Character.Character_ID; Character_Quest.Quest_ID → Quest.Quest_ID

#### Character_Quest_Progress
- Character_ID (BIGINT, PK/FK)
- Quest_ID (int, PK/FK)
- Objective_No (int, PK/FK)
- Current_Count (int)
- FK: Character_Quest_Progress.Character_ID → Character_Quest.Character_ID; Character_Quest_Progress.Objective_No → Quest_Objective.Objective_No

#### Character_Skill_Learned
- Character_Skill_Learned_ID (BIGINT, PK)
- Character_ID (BIGINT, FK)
- Skill_ID (BIGINT, FK)
- SkillLevel (INTEGER)
- LearnedAt (TIMESTAMPTZ)
- FK: Character_Skill_Learned.Character_ID → Character.Character_ID; Character_Skill_Learned.Skill_ID → Skill.Skill_ID

#### Character_Skill_Slot
- Character_ID (BIGINT, PK/FK)
- SkillNo (INTEGER, PK)
- Character_Skill_Learned_ID (BIGINT, FK)
- FK: Character_Skill_Slot → Character_Skill_Learned.Character_Skill_Learned_ID; Character_Skill_Slot.Character_ID → Character.Character_ID

#### Character_Stat
- Character_ID (BIGINT, PK/FK)
- Character_Current_Physic_Damage (int)
- Character_Current_Magic_Damage (int)
- Character_Current_Attack_Speed (int)
- Character_Current_Cast_Speed (int)
- Character_Current_Armor (int)
- Character_Current_Magic_Resist (int)
- Character_Current_Fire_Resist (int, %)
- Character_Current_Poison_Resist (int, %)
- Character_Current_Ice_Resist (int, %)
- Character_Current_Lightning_Resist (int, %)
- Character_Current_HP (int)
- Character_Current_Regen_HP (numeric)
- Character_Current_MP (int)
- Character_Current_Regen_MP (numeric)
- Character_Current_Movement (int)
- Updated_At (TIMESTAMPTZ)
- FK: Character_Stat.Character_ID → Character.Character_ID

#### Class
- Class_ID (BIGINT, PK)
- ClassNum (int)
- ClassType (int) (link Lookup_Code)
- ClassName (TEXT)
- Basic_Physic_Damage (int)
- Basic_Magic_Damage (int)
- Basic_Attack_Speed (int)
- Basic_Cast_Speed (int)
- Basic_Armor (int)
- Basic_Magic_Resist (int)
- Basic_HP (int)
- Basic_MP (int)
- Basic_Movement (int)
- Basic_Regen_HP (numeric)
- Basic_Regen_MP (numeric)
- FK: Class.Class_ID → Character.Class_ID; Class.Class_ID → Class_Evolution.From_Class_ID; Class.Class_ID → Class_Evolution.To_Class_ID; Class.Class_ID → Class_Skill.Class_ID

#### Class_Evolution
- Class_Evolution_ID (BIGINT, PK)
- From_Class_ID (BIGINT, FK)
- To_Class_ID (BIGINT, FK)
- RequiredCharacterLevel (INTEGER)

#### Class_Skill
- Class_Skill_ID (BIGINT, PK)
- Class_ID (BIGINT, FK)
- Skill_ID (BIGINT, FK)
- RequiredCharacterLevel (integer)
- MaxSkillLevel (integer)
- FK: Class_Skill.Class_Skill_ID → Class_Skill_Prerequisite.Class_Skill_ID; Class_Skill.Class_Skill_ID → Class_Skill_Prerequisite.Prerequisite_Class_Skill_ID

#### Class_Skill_Prerequisite
- Class_Skill_ID (BIGINT, PK/FK)
- Prerequisite_Class_Skill_ID (BIGINT, PK/FK)
- RequiredSkillLevel (integer)

#### Class_Stat_Growth
- Class_ID (BIGINT, PK/FK)
- Stat_Code (int, PK) (link Lookup_Code)
- Value_Per_Level (numeric)
- FK: Class_Stat_Growth.Class_ID → Class.Class_ID

#### Creep
- Creep_ID (int, PK)
- Creep_Num (int)
- Creep_Type (int) (link Lookup_Code)
- Creep_Name (varchar)
- Is_Boss (boolean)

#### Creep_Drop
- Creep_ID (int, PK/FK)
- Item_Basic_ID (int, PK/FK)
- Drop_Rate (numeric) (%)
- Quality_Min (int) (link Lookup_Code)
- FK: Creep_Drop.Creep_ID → Creep.Creep_ID; Creep_Drop.Item_Basic_ID → Item_Basic.Item_Basic_ID

#### Creep_Skill
- Creep_Skill_ID (int, PK)
- Creep_Skill_Num (int)
- Creep_Skill_Type (int) (link Lookup_Code)
- Creep_Skill_Damage_Type (int) (link Lookup_Code)
- Creep_Skill_Name (TEXT)
- Creep_Skill_Description (TEXT)

#### Creep_Skill_Assign
- Creep_ID (int, PK/FK)
- Creep_Skill_ID (int, PK/FK)
- Creep_Skill_Level (int) (VD Zombie – Bite = 3)
- FK: Creep_Skill_Assign.Creep_ID → Creep.Creep_ID; Creep_Skill_Assign.Creep_Skill_ID → Creep_Skill.Creep_Skill_ID

#### Creep_Skill_Detail
- Creep_Skill_Detail_ID (int, PK)
- Creep_Skill_ID (int, FK)
- Creep_Skill_Level (INTEGER)
- Creep_Skill_Damage (int)
- Creep_Skill_Scale_Ratio (numeric)
- Creep_Skill_Cooldown (NUMERIC)
- Creep_Skill_Cast_Time (numeric)
- Creep_Skill_Range (NUMERIC)
- Creep_Skill_Speed (numeric)
- Creep_Skill_Duration (NUMERIC)
- FK: Creep_Skill_Detail.Creep_Skill_ID → Creep_Skill.Creep_Skill_ID

#### Creep_Skill_Effect
- Creep_Skill_Effect_ID (int, PK)
- Creep_Skill_Detail_ID (int, FK)
- Effect_Target (int) (link Lookup_Code)
- Status_ID (int, FK, NULL)
- Stat_Code (int, NULL) (link Lookup_Code)
- Stat_Value (numeric, NULL)
- Is_Percent (boolean)
- Chance (numeric) (%, 100 = luôn)
- Duration (numeric) (giây, NULL = vĩnh viễn)
- Tick_Damage (int, NULL)
- Tick_Scale_Ratio (numeric, NULL)
- FK: Creep_Skill_Effect.Creep_Skill_Detail_ID → Creep_Skill_Detail.Creep_Skill_Detail_ID; Creep_Skill_Effect.Status_ID → Status.Status_ID

#### Creep_Stat
- Creep_Stat_ID (int, PK)
- Creep_ID (int, FK)
- Creep_Quality (int) (link Lookup_Code)
- Creep_Physic_Damage (int)
- Creep_Magic_Damage (int)
- Creep_Attack_Speed (int)
- Creep_Cast_Speed (int)
- Creep_Armor (int)
- Creep_Magic_Resist (int)
- Creep_Fire_Resist (int, %)
- Creep_Poison_Resist (int, %)
- Creep_Ice_Resist (int, %)
- Creep_Lightning_Resist (int, %)
- Creep_HP (int)
- Creep_Regen_HP (numeric)
- Creep_Movement (int)
- Creep_Exp (int) (exp khi bị giết)
- Creep_Gold_Min (int)
- Creep_Gold_Max (int)
- FK: Creep_Stat.Creep_ID → Creep.Creep_ID

#### Currency_Log  — *(phát triển sau)*
- Currency_Log_ID (BIGINT, PK)
- Account_ID (BIGINT)
- Character_ID (BIGINT, NULL)
- Currency (varchar) (GOLD / DIAMOND)
- Amount (BIGINT) (+ / −)
- Balance_After (BIGINT)
- Reason (varchar)
- Ref_ID (BIGINT, NULL)
- Created_At (TIMESTAMPTZ)

#### Dungeon  — *(phát triển sau)*
- Dungeon_ID (int, PK)
- Region_ID (int, FK) (map có lối vào)
- Dungeon_Num (int)
- Dungeon_Name (varchar)
- Dungeon_Description (text)
- Dungeon_Requirement_Level (int)
- Max_Player (int) (VD 2)
- Time_Limit (int) (giây, NULL = không giới hạn)
- Daily_Limit (int) (NULL = không giới hạn)

#### Dungeon_Creep  — *(phát triển sau)*
- Dungeon_ID (int, PK/FK)
- Creep_ID (int, PK/FK)
- Spawn_Count (int)

#### Game_Config
- Config_Key (varchar, PK)
- Config_Value (varchar)
- Description (text)
- Updated_At (TIMESTAMPTZ)

#### Inventory
- Item_ID (BIGINT, PK, FK)
- Character_ID (BIGINT, FK)
- Pos_X (int) (cột ô trái-trên)
- Pos_Y (int) (hàng ô trái-trên)
- Placed_At (TIMESTAMPTZ)
- FK: Inventory.Item_ID → Item.Item_ID; Inventory.Character_ID → Character.Character_ID

#### Item
- Item_ID (BIGINT, PK)
- Item_Basic_ID (int, FK)
- Item_Durability (int) (%, 0–100)
- Item_Quality (int) (link Lookup_Code)
- Item_Quality_Bonus (numeric)
- Item_Price (int)
- Item_Physic_Damage (int)
- Item_Movement (int)
- Item_Magic_Damage (int)
- Item_Attack_Speed (int)
- Item_Cast_Speed (int)
- Item_Armor (int)
- Item_Magic_Resist (int)
- Item_MP (int)
- Item_HP (int)
- Created_At (TIMESTAMPTZ)
- FK: Item.Item_Basic_ID → Item_Basic.Item_Basic_ID

#### Item_Basic
- Item_Basic_ID (int, PK)
- Item_Num (int)
- Item_Type (int) (link Lookup_Code)
- Item_Name (varchar)
- Item_Description (text)
- Item_Height (int)
- Item_Width (int)
- Item_Requirement_Level (int)
- Item_Basic_Price (int)
- Item_Basic_Physic_Damage (int)
- Item_Basic_Magic_Damage (int)
- Item_Basic_Attack_Speed (int)
- Item_Basic_Cast_Speed (int)
- Item_Basic_Armor (int)
- Item_Basic_Magic_Resist (int)
- Item_Basic_HP (int)
- Item_Basic_MP (int)
- Item_Basic_Movement (int)

#### Item_Log  — *(phát triển sau)*
- Item_Log_ID (BIGINT, PK)
- Item_ID (BIGINT)
- Item_Basic_ID (int)
- Character_ID (BIGINT, NULL)
- Action (varchar) (DROP / BUY / SELL / MOVE…)
- From_Location (varchar)
- To_Location (varchar)
- Created_At (TIMESTAMPTZ)

#### Item_Stat
- Item_ID (BIGINT, PK/FK)
- Item_Stat_Code (int, PK) (link Lookup_Code)
- Item_Stat_Value (numeric)
- FK: Item_Stat.Item_ID → Item.Item_ID

#### Level_Exp
- Level (int, PK)
- Exp_Required (BIGINT) (exp để lên level kế)
- Skill_Point_Reward (int)

#### Lookup_Code (key)
- Lookup_ID (int, PK)
- Lookup_Object (varchar)
- Lookup_Int (int)
- Lookup_Code (varchar)
- Lookup_Description (text)

#### NPC
- NPC_ID (int, PK)
- Region_ID (int, FK, NULL) (NULL = NPC lang thang)
- NPC_Type (int) (link Lookup_Code)
- NPC_Num (int)
- NPC_Name (varchar)
- NPC_Description (text)
- FK: NPC.Region_ID → Region.Region_ID

#### NPC_Spawn  — *(phát triển sau)*
- NPC_Spawn_ID (int, PK)
- NPC_ID (int, FK)
- Region_ID (int, FK, NULL)
- Dungeon_ID (int, FK, NULL)
- Spawn_Chance (numeric) (%)
- Check_Interval (int) (phút)
- Stay_Duration (int) (phút)
- Stock_Quality_Min (int) (link Lookup_Code)

#### Personal_Chest
- Item_ID (BIGINT, PK, FK)
- Account_ID (BIGINT, FK)
- Chest_Tab (int) (1 → số tab tối đa)
- Pos_X (int) (cột ô trái-trên)
- Pos_Y (int) (hàng ô trái-trên)
- Placed_At (TIMESTAMPTZ)
- FK: Personal_Chest.Item_ID → Item.Item_ID; Personal_Chest.Account_ID → Account.Account_ID

#### Quest
- Quest_ID (int, PK)
- Quest_Num (int)
- Quest_Type (int) (link Lookup_Code)
- Quest_Name (varchar)
- Quest_Description (text)
- Region_ID (int, FK)
- NPC_ID (int, FK) (NPC giao quest)
- Return_NPC_ID (int, FK, NULL) (NPC nhận trả)
- Required_Level (int)
- Prerequisite_Quest_ID (int, FK, NULL)
- Event_Start_At (TIMESTAMPTZ, NULL)
- Event_End_At (TIMESTAMPTZ, NULL)
- FK: Quest.Region_ID → Region.Region_ID; Quest.NPC_ID → NPC.NPC_ID; Quest.Return_NPC_ID → NPC.NPC_ID; Quest.Prerequisite_Quest_ID → Quest.Quest_ID

#### Quest_Objective
- Quest_ID (int, PK/FK)
- Objective_No (int, PK)
- Objective_Type (int) (link Lookup_Code)
- Target_ID (int) (Creep / Item_Basic / NPC / Region)
- Required_Count (int)
- FK: Quest_Objective.Quest_ID → Quest.Quest_ID

#### Quest_Reward
- Quest_ID (int, PK/FK)
- Reward_No (int, PK)
- Reward_Type (int) (link Lookup_Code)
- Item_Basic_ID (int, FK, NULL)
- Reward_Quality (int, NULL) (link Lookup_Code)
- Amount (int)
- FK: Quest_Reward.Quest_ID → Quest.Quest_ID; Quest_Reward.Item_Basic_ID → Item_Basic.Item_Basic_ID

#### Range_Buff
- Range_buff_ID (int)
- Object_Type (int)
- Object_Quality (int)
- Number_Of_Buff_Min (int)
- Number_Of_Buff_Max (int)
- Physic_Damage_Min (int)
- Physic_Damage_Max (int)
- Magic_Damage_Min (int)
- Magic_Damage_Max (int)
- Attack_Speed_Min (int)
- Attack_Speed_Max (int)
- Cast_Speed_Min (int)
- Cast_Speed_Max (int)
- Armor_Min (int)
- Armor_Max (int)
- Magic_Resist_Min (int)
- Magic_Resist_Max (int)
- Fire_Resist_Min (int, %)
- Fire_Resist_Max (int, %)
- Poison_Resist_Min (int, %)
- Poison_Resist_Max (int, %)
- Ice_Resist_Min (int, %)
- Ice_Resist_Max (int, %)
- Lightning_Resist_Min (int, %)
- Lightning_Resist_Max (int, %)
- HP_Min (int)
- HP_Max (int)
- Regen_HP_Min (numeric)
- Regen_HP_Max (numeric)
- MP_Min (int)
- MP_Max (int)
- Regen_MP_Min (numeric)
- Regen_MP_Max (numeric)
- Movement_Min (int)
- Movement_Max (int)

#### Region
- Region_ID (int, PK)
- Region_Num (int)
- Region_Name (varchar)

#### Region_Chest
- Region_Chest_ID (int, PK)
- Region_ID (int, FK)
- Chest_Type (int) (link Lookup_Code)
- Max_Spawn (int)
- Respawn_Time (int) (giây)
- Drop_Count_Min (int)
- Drop_Count_Max (int)
- Gold_Min (int)
- Gold_Max (int)
- FK: Region_Chest.Region_ID → Region.Region_ID

#### Region_Creep
- Region_Creep_ID (int, PK)
- Region_ID (int, FK)
- Creep_ID (int, FK)
- Spawn_Time (TIME) (NULL = luôn xuất hiện)
- Despawn_Time (TIME) (VD 11:30)
- Max_Spawn (int) (số con tối đa cùng lúc, VD 5)
- Respawn_Time (int) (giây, NULL = không hồi)
- FK: Region_Creep.Region_ID → Region.Region_ID; Region_Creep.Creep_ID → Creep.Creep_ID

#### Region_Item_Basic
- Region_ID (int, PK/FK)
- Item_Basic_ID (int, PK/FK)
- Drop_Weight (int) (trọng số random)
- FK: Region_Item_Basic.Region_ID → Region.Region_ID; Region_Item_Basic.Item_Basic_ID → Item_Basic.Item_Basic_ID

#### Skill
- Skill_ID (BIGINT, PK)
- Skill_Num (int)
- Skill_Damage_Type (int) (link Lookup_Code)
- SkillName (TEXT)
- SkillDescription (TEXT)
- SkillType (int) (link Lookup_Code)
- FK: Skill.Skill_ID → Class_Skill.Skill_ID; Skill.Skill_ID → Skill_Detail.Skill_ID

#### Skill_Detail
- Skill_Detail_ID (int, PK)
- Skill_ID (BIGINT, FK)
- Skill_Level (INTEGER)
- Skill_Damage (int)
- Skill_Scale_Ratio (numeric) (VD 0.3)
- Skill_Cost (int)
- Skill_Cooldown (NUMERIC)
- Skill_Cast_Time (numeric)
- Skill_Range (NUMERIC)
- Skill_Speed (numeric)
- Skill_Duration (NUMERIC)

#### Skill_Effect
- Skill_Effect_ID (int, PK)
- Skill_Detail_ID (int, FK)
- Effect_Target (int) (link Lookup_Code)
- Status_ID (int, FK, NULL)
- Stat_Code (int, NULL) (link Lookup_Code)
- Stat_Value (numeric, NULL)
- Is_Percent (boolean)
- Chance (numeric) (%, 100 = luôn)
- Duration (numeric) (giây, NULL = vĩnh viễn)
- Tick_Damage (int, NULL)
- Tick_Scale_Ratio (numeric, NULL)
- FK: Skill_Effect.Skill_Detail_ID → Skill_Detail.Skill_Detail_ID; Skill_Effect.Status_ID → Status.Status_ID

#### Status
- Status_ID (int, PK)
- StatusName (TEXT)
- StatusDescription (TEXT)
- Status_Type (int) (link Lookup_Code)
- Damage_Type (int) (link Lookup_Code)
- StatusDuration (NUMERIC) (giây, mặc định)
- Tick_Interval (numeric) (giây, cho DOT / HOT)
- Max_Stack (int)

#### Status_Stat
- Status_ID (int, PK/FK)
- Stat_Code (int, PK) (link Lookup_Code)
- Stat_Value (numeric)
- Is_Percent (boolean)
- FK: Status_Stat.Status_ID → Status.Status_ID

#### Vendor
- Item_ID (BIGINT, PK, FK)
- NPC_ID (int, FK)
- Pos_X (int) (cột ô trái-trên)
- Pos_Y (int) (hàng ô trái-trên)
- PriceBuy (int)
- Placed_At (TIMESTAMPTZ)
- FK: Vendor.Item_ID → Item.Item_ID; Vendor.NPC_ID → NPC.NPC_ID

</details>

### 5.2 Thay đổi đang chờ user duyệt (`New Version` so với `Physical ERD` chính thức)
Đây là vòng sửa mới nhất, chưa compile. Các thay đổi chính:

- **Bảng mới (phần chính):**
  - Level_Exp, Class_Stat_Growth, Game_Config
  - Region_Chest, Creep_Drop
  - Status_Stat, Creep_Skill_Effect
  - Quest_Objective, Quest_Reward, Character_Quest, Character_Quest_Progress
  - Character_Achievement
- **Đổi tên và chuyển từ "phát triển sau" sang dùng chính thức:**
  - Skill_Bonus → **Skill_Effect**
  - Archivement → **Achievement**
  - **Status** và **Quest** (được mở rộng thêm cột)
- **Sửa entity cũ:**
  - **Skill_Detail:** bỏ 7 cột cộng stat (Armor, Magic_Resist, HP, Regen_HP, MP, Regen_MP, Movement), chuyển sang Skill_Effect.
  - **Creep_Skill_Detail:** bỏ 4 cột tương tự, chuyển sang Creep_Skill_Effect.
  - **Character_Skill_Learned:** ID thành BIGINT, đánh dấu PK/FK.
  - **Character_Skill_Slot:** PK thành (`Character_ID`, `SkillNo`), bỏ ID riêng.
  - **NPC:** `Region_ID` cho phép NULL (thương nhân lang thang).
  - **Class, Skill, Class_Evolution:** đánh dấu PK.
  - **Dungeon_Creep:** bỏ `Is_Boss`.
- **Lookup:**
  - SKILL_TYPE và SKILL_DAMAGE_TYPE dùng chung cho Character và Creep. SKILL_TYPE thêm SUMMON. SKILL_DAMAGE_TYPE sắp lại thành PHYSICAL…NONE.
  - ITEM_STAT đổi tên thành STAT.
  - ITEM_TYPE thêm QUEST_ITEM; NPC_TYPE thêm TRAVELING_MERCHANT.
  - Thêm STATUS_TYPE, EFFECT_TARGET, CHEST_TYPE, QUEST_TYPE, QUEST_OBJECTIVE_TYPE, QUEST_STATUS, REWARD_TYPE, ACHIEVEMENT_CONDITION.
- **Phát triển sau (mới, nền vàng):** Item_Log, Currency_Log, NPC_Spawn, Character_Dungeon. Dungeon thêm `Daily_Limit`.
- **Note:**
  - Rule – Region gộp thành Rule – Region / Drop.
  - Mới: Rule – Skill Effect / Status, Rule – Quest / Achievement, Rule – Log, Rule – Thương nhân lang thang, note key Game_Config.
  - Mọi chỗ ghi "hằng số package" đổi thành "Game_Config".

<details><summary>Bấm để xem danh sách chi tiết theo entity (sinh từ changelog.py)</summary>

```text
## Class
  ~ Class_ID (BIGINT)  →  Class_ID (BIGINT, PK)
## Skill
  ~ Skill_ID (BIGINT)  →  Skill_ID (BIGINT, PK)
## Character_Skill_Learned
  ~ Character_Skill_Learned_ID (int)  →  Character_Skill_Learned_ID (BIGINT, PK)
  ~ Character_ID (BIGINT)  →  Character_ID (BIGINT, FK)
  ~ Skill_ID (BIGINT)  →  Skill_ID (BIGINT, FK)
## Character_Skill_Slot
  + Character_ID (BIGINT, PK/FK)
  ~ SkillNo (INTEGER)  →  SkillNo (INTEGER, PK)
  ~ Character_Skill_Learned_ID (int)  →  Character_Skill_Learned_ID (BIGINT, FK)
  - Character_Skill_Slot _ID (BIGINT)
  FK+ Character_Skill_Slot.Character_ID (BIGINT, PK/FK) → Character.Character_ID (BIGINT, PK)
## Skill_Detail
  ~ Skill_Detail_ID (int)  →  Skill_Detail_ID (int, PK)
  - Skill_Armor (int)
  - Skill_Magic_Resist (int)
  - Skill_HP (int)
  - Skill_Regen_HP (numeric)
  - Skill_MP (int)
  - Skill_Regen_MP (numeric)
  - Skill_Movement (int)
## Class_Evolution
  ~ Class_Evolution_ID (BIGINT)  →  Class_Evolution_ID (BIGINT, PK)
## NPC
  ~ Region_ID (int, FK)  →  Region_ID (int, FK, NULL) (NULL = NPC lang thang)
## Creep_ Skill_Detail
  - Creep_Skill_Armor (int)
  - Creep_Skill_HP (int)
  - Creep_Skill_Magic_Resist (int)
  - Creep_Skill_Movement (int)
## Quest  [màu header: light-dark(#FFFFFF,#CCCC00) → None]
  ~ Quest_ID (int)  →  Quest_ID (int, PK)
  + Quest_Name (varchar)
  + Quest_Description (text)
  ~ Region_ID (int)  →  Region_ID (int, FK)
  ~ NPC_ID (int)  →  NPC_ID (int, FK) (NPC giao quest)
  + Return_NPC_ID (int, FK, NULL) (NPC nhận trả)
  + Required_Level (int)
  + Prerequisite_Quest_ID (int, FK, NULL)
  + Event_Start_At (TIMESTAMPTZ, NULL)
  + Event_End_At (TIMESTAMPTZ, NULL)
  FK+ Quest.Region_ID (int, FK) → Region.Region_ID (int, PK)
  FK+ Quest.NPC_ID (int, FK) (NPC giao quest) → NPC.NPC_ID (int, PK)
  FK+ Quest.Return_NPC_ID (int, FK, NULL) (NPC nhận trả) → NPC.NPC_ID (int, PK)
  FK+ Quest.Prerequisite_Quest_ID (int, FK, NULL) → Quest.Quest_ID (int, PK)
## Skill_Effect — ĐỔI TÊN từ Skill_Bonus  [màu header: light-dark(#0050EF,#CCCC00) → #ffe6cc]
  + Skill_Effect_ID (int, PK)
  ~ Skill_Detail_ID (int)  →  Skill_Detail_ID (int, FK)
  ~ Skill_Effect_Type (int)  →  Effect_Target (int) (link Lookup_Code)
  + Status_ID (int, FK, NULL)
  + Stat_Code (int, NULL) (link Lookup_Code)
  + Stat_Value (numeric, NULL)
  + Is_Percent (boolean)
  + Chance (numeric) (%, 100 = luôn)
  + Duration (numeric) (giây, NULL = vĩnh viễn)
  + Tick_Damage (int, NULL)
  + Tick_Scale_Ratio (numeric, NULL)
  - Skill_ID (BIGINT, FK)
  - 
  FK+ Skill_Effect.Skill_Detail_ID (int, FK) → Skill_Detail.Skill_Detail_ID (int, PK)
  FK+ Skill_Effect.Status_ID (int, FK, NULL) → Status.Status_ID (int, PK)
## Status  [màu header: light-dark(#0050EF,#999900) → None]
  ~ Status_ID (BIGINT)  →  Status_ID (int, PK)
  + Status_Type (int) (link Lookup_Code)
  + Damage_Type (int) (link Lookup_Code)
  ~ StatusDuration (NUMERIC)  →  StatusDuration (NUMERIC) (giây, mặc định)
  + Tick_Interval (numeric) (giây, cho DOT / HOT)
  + Max_Stack (int)
## Achievement — ĐỔI TÊN từ Archivement  [màu header: light-dark(#FFFFFF,#999900) → #ffe6cc]
  ~ Item 1  →  Achievement_ID (int, PK)
  ~ Item 2  →  Achievement_Name (varchar)
  ~ Item 3  →  Achievement_Description (text)
  + Condition_Type (int) (link Lookup_Code)
  + Target_ID (int, NULL)
  + Target_Value (int)
  + Reward_Type (int) (link Lookup_Code)
  + Reward_Item_Basic_ID (int, FK, NULL)
  + Reward_Amount (int)
  FK+ Achievement.Reward_Item_Basic_ID (int, FK, NULL) → Item_Basic.Item_Basic_ID (int, PK)
## Dungeon
  + Daily_Limit (int) (NULL = không giới hạn)
## Dungeon_Creep
  - Is_Boss (boolean)
## Level_Exp — BẢNG MỚI
  + Level (int, PK)
  + Exp_Required (BIGINT) (exp để lên level kế)
  + Skill_Point_Reward (int)
## Game_Config — BẢNG MỚI
  + Config_Key (varchar, PK)
  + Config_Value (varchar)
  + Description (text)
  + Updated_At (TIMESTAMPTZ)
## Class_Stat_Growth — BẢNG MỚI
  + Class_ID (BIGINT, PK/FK)
  + Stat_Code (int, PK) (link Lookup_Code)
  + Value_Per_Level (numeric)
  FK+ Class_Stat_Growth.Class_ID (BIGINT, PK/FK) → Class.Class_ID (BIGINT, PK)
## Region_Chest — BẢNG MỚI
  + Region_Chest_ID (int, PK)
  + Region_ID (int, FK)
  + Chest_Type (int) (link Lookup_Code)
  + Max_Spawn (int)
  + Respawn_Time (int) (giây)
  + Drop_Count_Min (int)
  + Drop_Count_Max (int)
  + Gold_Min (int)
  + Gold_Max (int)
  FK+ Region_Chest.Region_ID (int, FK) → Region.Region_ID (int, PK)
## Creep_Drop — BẢNG MỚI
  + Creep_ID (int, PK/FK)
  + Item_Basic_ID (int, PK/FK)
  + Drop_Rate (numeric) (%)
  + Quality_Min (int) (link Lookup_Code)
  FK+ Creep_Drop.Creep_ID (int, PK/FK) → Creep.Creep_ID (int, PK)
  FK+ Creep_Drop.Item_Basic_ID (int, PK/FK) → Item_Basic.Item_Basic_ID (int, PK)
## Status_Stat — BẢNG MỚI
  + Status_ID (int, PK/FK)
  + Stat_Code (int, PK) (link Lookup_Code)
  + Stat_Value (numeric)
  + Is_Percent (boolean)
  FK+ Status_Stat.Status_ID (int, PK/FK) → Status.Status_ID (int, PK)
## Creep_Skill_Effect — BẢNG MỚI
  + Creep_Skill_Effect_ID (int, PK)
  + Creep_Skill_Detail_ID (int, FK)
  + Effect_Target (int) (link Lookup_Code)
  + Status_ID (int, FK, NULL)
  + Stat_Code (int, NULL) (link Lookup_Code)
  + Stat_Value (numeric, NULL)
  + Is_Percent (boolean)
  + Chance (numeric) (%, 100 = luôn)
  + Duration (numeric) (giây, NULL = vĩnh viễn)
  + Tick_Damage (int, NULL)
  + Tick_Scale_Ratio (numeric, NULL)
  FK+ Creep_Skill_Effect.Creep_Skill_Detail_ID (int, FK) → Creep_ Skill_Detail.Creep_Skill_Detail_ID (int, PK)
  FK+ Creep_Skill_Effect.Status_ID (int, FK, NULL) → Status.Status_ID (int, PK)
## Quest_Objective — BẢNG MỚI
  + Quest_ID (int, PK/FK)
  + Objective_No (int, PK)
  + Objective_Type (int) (link Lookup_Code)
  + Target_ID (int) (Creep / Item_Basic / NPC / Region)
  + Required_Count (int)
  FK+ Quest_Objective.Quest_ID (int, PK/FK) → Quest.Quest_ID (int, PK)
## Quest_Reward — BẢNG MỚI
  + Quest_ID (int, PK/FK)
  + Reward_No (int, PK)
  + Reward_Type (int) (link Lookup_Code)
  + Item_Basic_ID (int, FK, NULL)
  + Reward_Quality (int, NULL) (link Lookup_Code)
  + Amount (int)
  FK+ Quest_Reward.Quest_ID (int, PK/FK) → Quest.Quest_ID (int, PK)
  FK+ Quest_Reward.Item_Basic_ID (int, FK, NULL) → Item_Basic.Item_Basic_ID (int, PK)
## Character_Quest — BẢNG MỚI
  + Character_ID (BIGINT, PK/FK)
  + Quest_ID (int, PK/FK)
  + Quest_Status (int) (link Lookup_Code)
  + Accepted_At (TIMESTAMPTZ)
  + Completed_At (TIMESTAMPTZ, NULL)
  FK+ Character_Quest.Character_ID (BIGINT, PK/FK) → Character.Character_ID (BIGINT, PK)
  FK+ Character_Quest.Quest_ID (int, PK/FK) → Quest.Quest_ID (int, PK)
## Character_Quest_Progress — BẢNG MỚI
  + Character_ID (BIGINT, PK/FK)
  + Quest_ID (int, PK/FK)
  + Objective_No (int, PK/FK)
  + Current_Count (int)
  FK+ Character_Quest_Progress.Character_ID (BIGINT, PK/FK) → Character_Quest.Character_ID (BIGINT, PK/FK)
  FK+ Character_Quest_Progress.Objective_No (int, PK/FK) → Quest_Objective.Objective_No (int, PK)
## Character_Achievement — BẢNG MỚI
  + Character_ID (BIGINT, PK/FK)
  + Achievement_ID (int, PK/FK)
  + Progress (int)
  + Completed_At (TIMESTAMPTZ, NULL)
  + Rewarded_At (TIMESTAMPTZ, NULL) (NULL = chưa nhận)
  FK+ Character_Achievement.Character_ID (BIGINT, PK/FK) → Character.Character_ID (BIGINT, PK)
  FK+ Character_Achievement.Achievement_ID (int, PK/FK) → Achievement.Achievement_ID (int, PK)
## Item_Log — BẢNG MỚI
  + Item_Log_ID (BIGINT, PK)
  + Item_ID (BIGINT)
  + Item_Basic_ID (int)
  + Character_ID (BIGINT, NULL)
  + Action (varchar) (DROP / BUY / SELL / MOVE…)
  + From_Location (varchar)
  + To_Location (varchar)
  + Created_At (TIMESTAMPTZ)
## Currency_Log — BẢNG MỚI
  + Currency_Log_ID (BIGINT, PK)
  + Account_ID (BIGINT)
  + Character_ID (BIGINT, NULL)
  + Currency (varchar) (GOLD / DIAMOND)
  + Amount (BIGINT) (+ / −)
  + Balance_After (BIGINT)
  + Reason (varchar)
  + Ref_ID (BIGINT, NULL)
  + Created_At (TIMESTAMPTZ)
## NPC_Spawn — BẢNG MỚI
  + NPC_Spawn_ID (int, PK)
  + NPC_ID (int, FK)
  + Region_ID (int, FK, NULL)
  + Dungeon_ID (int, FK, NULL)
  + Spawn_Chance (numeric) (%)
  + Check_Interval (int) (phút)
  + Stay_Duration (int) (phút)
  + Stock_Quality_Min (int) (link Lookup_Code)
## Character_Dungeon — BẢNG MỚI
  + Character_ID (BIGINT, PK/FK)
  + Dungeon_ID (int, PK/FK)
  + Clear_Count (int)
  + Best_Time (int) (giây)
  + Last_Clear_At (TIMESTAMPTZ)

## NOTES
  ~ SkillType / Creep_Skill_Type Lookup_Object = SKILL_TYPE 1 – PASSIVE 2 
  ~ Skill_Damage_Type Lookup_Object = SKILL_DAMAGE_TYPE Skill, Creep_Skill
  ~ Rule – Chest / Inventory (lưới kiểu Diablo) 1. Chest theo Account (Per
  ~ Rule – Item (thế giới dùng chung, 2 người chơi) 1. Chỉ Chest và Invent
  ~ Rule – Vendor (dùng chung cho mọi người chơi, bán theo lưới) 1. NPC_Ty
  ~ Item_Type Lookup_Object = ITEM_TYPE 1 – WEAPON → MAIN_HAND 2 – WEAPON_
  ~ Quality (dùng chung) Lookup_Object = QUALITY Item, Creep_Stat, Creep_D
  ~ Stat_Code (dùng chung) Lookup_Object = STAT Item_Stat, Class_Stat_Grow
  ~ NPC_Type Lookup_Object = NPC_TYPE 1 – VENDOR_EQUIPMENT 2 – VENDOR_CONS
  ~ Rule – Lookup_Code 1. Cột có (link Lookup_Code) ở entity lưu Lookup_In
  ~ Rule – Character 1. CharacterNum = thứ tự slot nhân vật trong Account:
  ~ Rule – Region / Drop 1. Region = 1 map (Map 1, Map 2…), kèm NPC của kh
  ~ Rule – Dungeon (phát triển sau) 1. Region = map mở; Dungeon = khu vực 
  ~ Rule – Creep / Boss 1. Boss dùng chung entity Creep (Is_Boss = TRUE) v
  ~ Rule – Stat (kiểu Diablo, dùng chung Character / Item / Creep) 1. Bộ 1
  + Game_Config – key mẫu (thay cho các "hằng số package" trước đây) RESIS
  + Rule – Skill Effect / Status 1. Skill_Effect (skill của Character) và 
  + Rule – Quest / Achievement 1. Quest_Type: MAIN (tuyến chính, nối nhau 
  + Rule – Log (phát triển sau) Item_Log / Currency_Log ghi trong cùng tra
  + Rule – Thương nhân lang thang (phát triển sau) 1. NPC_Type = TRAVELING
  + Status_Type Lookup_Object = STATUS_TYPE 1 – BUFF 2 – DEBUFF (VD làm ch
  + Effect_Target Lookup_Object = EFFECT_TARGET 1 – SELF 2 – ENEMY 3 – ARE
  + Chest_Type Lookup_Object = CHEST_TYPE 1 – NORMAL 2 – RARE 3 – BOSS
  + Quest_Type Lookup_Object = QUEST_TYPE 1 – MAIN 2 – SIDE 3 – DAILY 4 – 
  + Objective_Type Lookup_Object = QUEST_OBJECTIVE_TYPE 1 – KILL (Target =
  + Quest_Status Lookup_Object = QUEST_STATUS 1 – ACCEPTED 2 – COMPLETED 3
  + Reward_Type Lookup_Object = REWARD_TYPE 1 – EXP 2 – GOLD 3 – DIAMOND 4
  + Condition_Type (Achievement) Lookup_Object = ACHIEVEMENT_CONDITION 1 –
```
</details>

### 5.3 Giá trị Lookup đã khai báo (các note tím)
`Lookup_Code` gồm `Lookup_ID (PK)`, `Lookup_Object`, `Lookup_Int`, `Lookup_Code`, `Lookup_Description`, ràng buộc **UNIQUE (`Lookup_Object`, `Lookup_Int`)**. Cột ở các entity lưu `Lookup_Int`.

```text
SkillType / Creep_Skill_Type
Lookup_Object = SKILL_TYPE
1 – PASSIVE
2 – CAST_ON_SELF
3 – CAST_ON_TARGET
4 – AOE
5 – SUMMON (gọi quái / triệu hồi)

Skill_Damage_Type
Lookup_Object = SKILL_DAMAGE_TYPE
Skill, Creep_Skill, Status (DOT)
1 – PHYSICAL
2 – MAGIC
3 – FIRE
4 – ICE
5 – POISON
6 – LIGHTNING
7 – HEAL
8 – NONE (chỉ buff / debuff)

Account_Status
Lookup_Object = ACCOUNT_STATUS
1 – ACTIVE
2 – LOCKED
3 – BANNED

Item_Type
Lookup_Object = ITEM_TYPE
1 – WEAPON → MAIN_HAND
2 – WEAPON_2H → MAIN_HAND, khóa OFF_HAND
3 – SHIELD → OFF_HAND
4 – HELMET → HEAD
5 – ARMOR → CHEST
6 – GLOVES → GLOVES
7 – BELT → BELT
8 – BOOTS → BOOTS
9 – AMULET → AMULET
10 – RING → RING_LEFT / RING_RIGHT
11 – POTION_HP (consumable)
12 – POTION_MP (consumable)
13 – QUEST_ITEM (chỉ để nộp quest)

Quality (dùng chung)
Lookup_Object = QUALITY
Item, Creep_Stat, Creep_Drop, Quest_Reward, NPC_Spawn
1 – NORMAL
2 – RARE
3 – EPIC
4 – LEGENDARY

Stat_Code (dùng chung)
Lookup_Object = STAT
Item_Stat, Class_Stat_Growth, Status_Stat, Skill_Effect
1 – PHYSIC_DAMAGE
2 – MAGIC_DAMAGE
3 – ATTACK_SPEED
4 – CAST_SPEED
5 – ARMOR
6 – MAGIC_RESIST
7 – FIRE_RESIST (%)
8 – POISON_RESIST (%)
9 – ICE_RESIST (%)
10 – LIGHTNING_RESIST (%)
11 – HP
12 – REGEN_HP
13 – MP
14 – REGEN_MP
15 – MOVEMENT

NPC_Type
Lookup_Object = NPC_TYPE
1 – VENDOR_EQUIPMENT
2 – VENDOR_CONSUMABLE
3 – QUEST
4 – TRAVELING_MERCHANT (phát triển sau)

Status_Type
Lookup_Object = STATUS_TYPE
1 – BUFF
2 – DEBUFF (VD làm chậm)
3 – DOT (độc, bỏng, chảy máu)
4 – HOT (hồi máu theo thời gian)
5 – CC (choáng, đóng băng)

Effect_Target
Lookup_Object = EFFECT_TARGET
1 – SELF
2 – ENEMY
3 – AREA_ENEMY
4 – AREA_ALLY

Chest_Type
Lookup_Object = CHEST_TYPE
1 – NORMAL
2 – RARE
3 – BOSS

Quest_Type
Lookup_Object = QUEST_TYPE
1 – MAIN
2 – SIDE
3 – DAILY
4 – EVENT

Objective_Type
Lookup_Object = QUEST_OBJECTIVE_TYPE
1 – KILL (Target = Creep_ID)
2 – COLLECT (Target = Item_Basic_ID)
3 – TALK (Target = NPC_ID)
4 – REACH (Target = Region_ID)

Quest_Status
Lookup_Object = QUEST_STATUS
1 – ACCEPTED
2 – COMPLETED
3 – REWARDED

Reward_Type
Lookup_Object = REWARD_TYPE
1 – EXP
2 – GOLD
3 – DIAMOND
4 – ITEM

Condition_Type (Achievement)
Lookup_Object = ACHIEVEMENT_CONDITION
1 – KILL_CREEP (Target = Creep_ID)
2 – REACH_LEVEL
3 – COMPLETE_QUEST (Target = Quest_ID, NULL = bất kỳ)
4 – COLLECT_QUALITY (Target = Quality)
5 – OPEN_CHEST
6 – CLEAR_DUNGEON (phát triển sau)
```

Các lookup **chưa khai báo giá trị**:
- `CLASS_TYPE`, `CREEP_TYPE`: user sẽ nghĩ sau.
- `Range_Buff.Object_Type` / `Object_Quality`: **user nói để nguyên**, không gắn nhãn link.

### 5.4 Luật nghiệp vụ (nội dung các note vàng trên `New Version`, nguyên văn)

```text
Skill unlock rule:
1. Class_Skill = class may learn skill + required character level
2. Class_Skill_Prerequisite = links a target Class_Skill to its prerequisite Class_Skill + required skill level
3. Character_Skill_Learned = character has actually learned it
4. Character_Skill_Slot references learned skill, so only learned skills can be equipped

Class evolution:
Warrior at Character Lv 20
Barbarian at Character Lv 40
Guardian at Character Lv 40
Use From_Class_ID → To_Class_ID so one class can branch into multiple classes.

Rule – Chest / Inventory (lưới kiểu Diablo)
1. Chest theo Account (Personal_Chest.Account_ID, mọi Character của Account dùng chung), chia tab bằng Chest_Tab. Inventory theo Character (Inventory.Character_ID).
2. Item chiếm Item_Width × Item_Height ô (query từ Item_Basic); chỉ lưu ô trái-trên (Pos_X, Pos_Y), bắt đầu từ 0.
3. Kích thước lưới mỗi tab Chest và Inventory cố định (Game_Config, thống nhất với FE). Hợp lệ khi item nằm trọn trong lưới và không chồng ô với item khác cùng tab / Inventory (check trong package).
4. move_item: xóa chỗ cũ + insert chỗ mới trong 1 transaction.
5. Consumable không cộng dồn: 1 Item = 1 vật phẩm, có Height/Width riêng.
6. Số tab Chest cố định cho mọi Account (VD 5 tab, Game_Config): Chest_Tab từ 1 đến số tab tối đa, không lưu số tab trên Account.
7. Xóa Character → xóa Inventory + Character_Equipment của Character đó rồi DELETE các Item; Personal_Chest giữ nguyên vì thuộc Account.

Rule – Equip
1. equip_item(char, item, slot): Item phải đang nằm trong Inventory của chính Character đó + Level ≥ Item_Requirement_Level + Item_Type hợp với Equip_Slot → DELETE khỏi Inventory, INSERT Character_Equipment; slot đã có đồ thì swap đồ cũ về lưới.
2. Không FK Character_Equipment → Inventory vì đồ đang mặc không chiếm ô lưới. unequip_item cần còn chỗ trống trong lưới.

Rule – Item (thế giới dùng chung, 2 người chơi)
1. Chỉ Chest và Inventory là riêng; Vendor, rương trên map, đồ rơi từ quái đều thấy như nhau — ai nhặt / mua trước thì được.
2. Sinh Item (rơi đồ hoặc Vendor refresh): chọn Item_Basic theo Region_Item_Basic của map (random theo Drop_Weight) → random Item_Quality → các cột stat cố định của Item = stat Item_Basic nhân Item_Quality_Bonus (VD 1.2 = +20%), tính 1 lần lúc sinh rồi lưu lại → Range_Buff (Object_Type, Object_Quality) cho số buff + khoảng giá trị → mỗi buff 1 dòng Item_Stat.
3. Level của Item lấy theo Item_Basic.Item_Requirement_Level (không lưu riêng trên Item).
4. Đồ rơi chỉ giữ trong bộ nhớ game server, chưa ghi DB. Khi nhặt: INSERT Item + Item_Stat + Inventory trong 1 transaction; Inventory hết chỗ thì không nhặt được.
5. Item luôn chỉ ở 1 nơi: Inventory / Personal_Chest / Character_Equipment / Vendor (Item_ID là PK hoặc UNIQUE ở các bảng này). Chỉ DELETE Item khi không còn ở nơi nào.
6. Item_Durability = % độ bền (0–100), Item mới luôn = 100.
7. Consumable: lượng hồi lấy từ Item_Basic_HP / Item_Basic_MP; dùng xong DELETE Item.
8. QUEST_ITEM: không có tác dụng, Item_Price = 0, không bán được cho Vendor; chỉ rơi (khai báo ở Creep_Drop) cho người đang nhận quest cần nó; nộp quest thì DELETE.

Rule – Vendor (dùng chung cho mọi người chơi, bán theo lưới)
1. NPC_Type quyết định loại Vendor: VENDOR_EQUIPMENT (đồ random, đổi mỗi ngày) / VENDOR_CONSUMABLE (đồ cố định, chỉ đổi giá).
2a. Vendor không có bảng hàng riêng: hàng được chọn qua NPC.Region_ID → Region_Item_Basic, random theo Drop_Weight (giống đồ rơi của map đó).
2b. Mỗi dòng Vendor = 1 Item đang bày bán trên lưới của NPC, giống Inventory (Pos_X, Pos_Y, kích thước theo Item_Basic, không chồng ô); kích thước lưới cố định (Game_Config).
3. Refresh VENDOR_EQUIPMENT mỗi ngày (1 transaction): DELETE toàn bộ dòng Vendor của NPC (kể cả đồ người chơi đã bán vào) + các Item đó → sinh Item mới: random Item_Basic trong Region_Item_Basic của map có NPC (theo Drop_Weight, không phải Consumable) + random Quality / stat như đồ rơi → INSERT Item + Item_Stat + Vendor (package tự xếp vào lưới, PriceBuy = Item_Price × hệ số bán). Vendor bán Item thật có stat ngẫu nhiên, không bán Item_Basic.
4. Refresh VENDOR_CONSUMABLE: giữ Item, chỉ UPDATE PriceBuy = giá gốc × hệ số random.
5. Mua: đủ Gold → DELETE FROM Vendor WHERE Item_ID = ? AND NPC_ID = ? → chỉ ai xóa được đúng 1 dòng mới mua thành công (chống 2 người mua cùng lúc) → trừ Gold = PriceBuy → INSERT Inventory (Inventory hết chỗ thì rollback).
6. Mua Consumable: dòng giữ nguyên, mỗi lần mua clone ra 1 Item mới vào Inventory.
7. Bán cho VENDOR_EQUIPMENT (package): Character.Gold += Item.Item_Price → DELETE khỏi Inventory → INSERT Vendor với PriceBuy = Item_Price × 2 (ai cũng mua lại được). Lưới hết chỗ thì DELETE Item.
8. Bán cho VENDOR_CONSUMABLE: chỉ nhận Gold rồi DELETE Item (không bày lại → refresh không phải phân biệt hàng gốc với đồ người chơi bán).

Equip_Slot (varchar + CHECK, không dùng Lookup):
HEAD | CHEST | GLOVES | BELT | BOOTS
AMULET | RING_LEFT | RING_RIGHT
MAIN_HAND | OFF_HAND
WEAPON_2H chiếm MAIN_HAND và khóa OFF_HAND.

Rule – Lookup_Code
1. Cột có (link Lookup_Code) ở entity lưu Lookup_Int (1, 2, 3…). Tra: WHERE Lookup_Object = ? AND Lookup_Int = ? — VD Item.Item_Quality = 3 → ('QUALITY', 3) → EPIC. UNIQUE (Lookup_Object, Lookup_Int).
2. Lookup dùng chung: STAT (Item_Stat, Class_Stat_Growth, Status_Stat, Skill_Effect), QUALITY (Item, Creep_Stat, Creep_Drop, Quest_Reward, NPC_Spawn), SKILL_TYPE / SKILL_DAMAGE_TYPE (Skill, Creep_Skill, Status), REWARD_TYPE (Quest_Reward, Achievement), EFFECT_TARGET (Skill_Effect, Creep_Skill_Effect).

Rule – Character
1. CharacterNum = thứ tự slot nhân vật trong Account: UNIQUE (Account_ID, CharacterNum); số slot tối đa = Game_Config MAX_CHARACTER_SLOT.
2. Tạo Character (1 transaction): INSERT Character → Character_Stat (tính từ Class).
3. Character_Stat là bảng tính sẵn = Class.Basic_* + Class_Stat_Growth × (Level − 1) + stat Item đang mặc (cột cố định + Item_Stat) + Skill_Effect passive; tính lại khi equip / unequip, lên level, tiến hóa Class, học skill.
4. Character_Current_HP / MP = HP / MP tối đa đã tính. Máu / mana đang có trong trận chỉ giữ ở game server; login lại hồi sinh đầy nên không lưu.
5. Lên level theo Level_Exp: Exp ≥ Exp_Required → Level + 1, SkillPoint + Skill_Point_Reward.
6. Character_Skill_Learned UNIQUE (Character_ID, Skill_ID); Character_Skill_Slot PK (Character_ID, SkillNo) → 1 ô chỉ gắn 1 skill.
7. CHECK Gold ≥ 0 (theo Character), Diamond ≥ 0 (theo Account).

Rule – Region / Drop
1. Region = 1 map (Map 1, Map 2…), kèm NPC của khu vực đó (NPC.Region_ID).
2. Đồ rơi từ quái: chọn Item_Basic theo Region_Item_Basic của map, random theo Drop_Weight (VD Kiếm 70, Rìu 25, Nhẫn 5 → 70% / 25% / 5%); Vendor refresh cũng chọn như vậy.
3. Creep_Drop: đồ riêng của 1 Creep / Boss, rơi thêm theo Drop_Rate %, Quality ≥ Quality_Min (VD Boss luôn rơi 1 món ≥ EPIC); quest item cũng khai báo ở đây.
4. Region_Chest: tối đa Max_Spawn rương trên map, mở xong sau Respawn_Time giây xuất hiện lại; rơi Drop_Count_Min – Max món (chọn như mục 2, Chest_Type càng cao Quality càng tốt) + Gold_Min – Max.
5. Creep / Boss xuất hiện theo Region_Creep (xem Rule – Creep / Boss). Login lại: BE đưa người chơi về điểm hồi sinh.

Rule – Dungeon (phát triển sau)
1. Region = map mở; Dungeon = khu vực instance riêng, lối vào nằm trong 1 Region (Dungeon.Region_ID).
2. Quái trong Dungeon khai báo ở Dungeon_Creep (Spawn_Count con mỗi lượt); Boss trong Dungeon xác định bằng Creep.Is_Boss (không lưu riêng ở Dungeon_Creep).
3. Vào được khi Character.Level ≥ Dungeon_Requirement_Level và số người ≤ Max_Player.
4. Đồ rơi: Item_Basic theo Region_ID của Dungeon.
5. Character_Dungeon lưu số lần clear (giới hạn Daily_Limit mỗi ngày) và kỷ lục Best_Time; thương nhân lang thang có thể xuất hiện trong Dungeon (NPC_Spawn.Dungeon_ID).
6. Lượt chơi (người trong phòng, quái còn sống, thời gian Time_Limit) chỉ giữ trong bộ nhớ game server, không ghi DB.

Rule – Creep / Boss
1. Boss dùng chung entity Creep (Is_Boss = TRUE) vì cùng cấu trúc stat (Creep_Stat theo Quality) và skill (Creep_Skill_Assign) — không cần tách bảng Boss.
2. Creep xuất hiện ở map nào khai báo trong Region_Creep (1 Creep nhiều map). Quái chỉ có trong Dungeon thì không có dòng Region_Creep.
3. Quái thường (Spawn_Time / Despawn_Time NULL): luôn có trên map, tối đa Max_Spawn con cùng lúc; con nào bị giết thì sau Respawn_Time giây mới hồi lại 1 con (VD Zombie – Map 1: Max_Spawn = 5, Respawn_Time = 60).
4. Quái / Boss theo giờ: chỉ xuất hiện trong khung Spawn_Time – Despawn_Time, lặp lại mỗi ngày (VD Boss 11:00 – 11:30, Max_Spawn = 1, Respawn_Time NULL): bị giết thì chờ khung giờ hôm sau; chưa bị tiêu diệt trước Despawn_Time thì biến mất.
5. Quality của mỗi con random lúc spawn (tỉ lệ là Game_Config) → lấy dòng Creep_Stat tương ứng.
6. Trạng thái sống / chết, máu còn lại, thời điểm hồi của quái và Boss chỉ giữ trong bộ nhớ game server, dùng chung cho 2 người chơi.

Rule – Stat (kiểu Diablo, dùng chung Character / Item / Creep)
1. Bộ 15 stat chung (Lookup STAT): Physic_Damage, Magic_Damage, Attack_Speed, Cast_Speed, Armor, Magic_Resist, Fire / Poison / Ice / Lightning_Resist, HP, Regen_HP, MP, Regen_MP, Movement. Cùng tên ở Character_Stat, Range_Buff, Creep_Stat (Creep không có MP). Class.Basic_* có 11 stat — không có 4 kháng nguyên tố vì gốc luôn = 0; Item_Basic / Item chỉ có 9 stat cố định, phần còn lại đến từ Item_Stat (random).
2. Đơn vị: Damage, Armor, Magic_Resist, HP, MP = số nguyên (điểm). Regen_HP / Regen_MP = numeric, lượng hồi mỗi giây (VD 1.5). Fire / Poison / Ice / Lightning_Resist = int % (0–100), cộng dồn rồi cắt ở trần 75% (Game_Config). Attack_Speed / Cast_Speed / Movement = int %, 100 = tốc độ chuẩn; Item / Item_Stat cộng thêm % (VD +15).
3. Character_Stat = Class.Basic_* + Class_Stat_Growth × (Level − 1) + 9 cột cố định của các Item đang mặc + Item_Stat của chúng + Skill_Effect (passive / buff). Kháng nguyên tố của Character chỉ đến từ Item_Stat và Skill passive / buff, nhân vật không tự tăng / giảm được.
4. Sát thương skill = Skill_Damage + Skill_Scale_Ratio × stat người dùng (PHYSICAL → Physic_Damage, MAGIC / FIRE / ICE / POISON / LIGHTNING / HEAL → Magic_Damage; NONE = không gây sát thương); loại sát thương theo Skill_Damage_Type. VD Fireball: 100 + 0.3 × 100 Magic_Damage = 130 sát thương lửa.
5. Giảm sát thương (đề xuất): Sát thương nhận = Raw × K / (K + Phòng thủ) với Phòng thủ = Armor (PHYSICAL) hoặc Magic_Resist (MAGIC + nguyên tố), K = 100 (Game_Config); nguyên tố nhân thêm × (1 − Resist%). VD 130 lửa, Magic_Resist 100, Fire 50% → 130 × 0.5 × 0.5 = 32.5.
6. Creep_Stat: 1 dòng cho mỗi (Creep_ID, Creep_Quality) — UNIQUE; Creep_Exp, Creep_Gold_Min / Max là phần thưởng khi giết (Gold random trong khoảng).
7. Creep_Skill là danh sách skill của quái; Creep_Skill_Assign gán skill + level cố định cho từng Creep (VD Zombie – Bite lv3 ở mọi Quality). Quality chỉ đổi Creep_Stat → sát thương skill vẫn tăng nhờ công thức mục 4: Creep_Skill_Damage + Creep_Skill_Scale_Ratio × Creep_Stat.

Game_Config – key mẫu (thay cho các "hằng số package" trước đây)
RESIST_CAP = 75 · DEFENSE_K = 100
INVENTORY_GRID = 10×4 · CHEST_GRID = 10×10 · VENDOR_GRID = 10×10
CHEST_TAB_MAX = 5 · MAX_CHARACTER_SLOT = 4
VENDOR_PRICE_RATE = 1.2 · BUYBACK_RATE = 2
QUALITY_SPAWN_RATE = 80 / 15 / 4 / 1 (NORMAL → LEGENDARY)
DAILY_RESET_TIME = 00:00

Rule – Skill Effect / Status
1. Skill_Effect (skill của Character) và Creep_Skill_Effect (skill của Creep) cùng cấu trúc; mỗi level skill có thể có nhiều hiệu ứng.
2. Passive cộng stat: Stat_Code + Stat_Value (Is_Percent), Duration NULL = vĩnh viễn → cộng vào Character_Stat.
3. Buff / debuff: Status_ID trỏ tới Status (stat bị đổi khai báo ở Status_Stat, VD làm chậm: MOVEMENT −30%); Chance = tỉ lệ gây hiệu ứng; Duration ghi đè StatusDuration.
4. DOT (độc, bỏng, chảy máu) / HOT: mỗi Tick_Interval gây Tick_Damage + Tick_Scale_Ratio × stat người dùng, loại sát thương = Status.Damage_Type, bị giảm theo Rule – Stat.
5. Status đang dính trên Character / Creep chỉ giữ ở game server (không lưu DB), cộng dồn tối đa Max_Stack.

Rule – Quest / Achievement
1. Quest_Type: MAIN (tuyến chính, nối nhau bằng Prerequisite_Quest_ID), SIDE (phụ), DAILY (reset mỗi ngày lúc Game_Config DAILY_RESET_TIME: Character_Quest + Progress của quest DAILY được làm lại), EVENT (chỉ nhận trong Event_Start_At – Event_End_At).
2. Nhận quest khi Character.Level ≥ Required_Level và quest tiên quyết đã REWARDED; tiến độ từng mục tiêu lưu ở Character_Quest_Progress.
3. Quest thu thập: Objective COLLECT, Target_ID = Item_Basic có Item_Type QUEST_ITEM; nộp cho Return_NPC_ID (NULL = NPC giao) → DELETE các Item đó → COMPLETED → nhận thưởng → REWARDED.
4. Phần thưởng (Quest_Reward, Achievement): EXP / GOLD vào Character, DIAMOND vào Account (nguồn Diamond hiện tại chỉ từ Quest + Achievement), ITEM → sinh Item mới vào Inventory (đủ chỗ mới nhận).
5. Achievement theo Character: Progress cộng dồn theo Condition_Type; đạt Target_Value → Completed_At; bấm nhận → Rewarded_At.

Rule – Log (phát triển sau)
Item_Log / Currency_Log ghi trong cùng transaction với thao tác; không đặt FK để log vẫn còn khi Item / Character đã bị xóa. Dùng để truy vết mất đồ, bug nhân bản, gian lận.

Rule – Thương nhân lang thang (phát triển sau)
1. NPC_Type = TRAVELING_MERCHANT, NPC.Region_ID = NULL; nơi có thể xuất hiện khai báo ở NPC_Spawn (map hoặc Dungeon).
2. Mỗi Check_Interval phút random theo Spawn_Chance; xuất hiện thì ở lại Stay_Duration phút rồi biến mất.
3. Khi xuất hiện: sinh hàng Vendor với Quality ≥ Stock_Quality_Min (đồ quý, không mua được ở Vendor thường); biến mất thì xóa hàng.
```

---

## 6. Quyết định thiết kế đã chốt (kèm lý do)

**Lưu trữ đồ (lưới kiểu Diablo)**
- Item chiếm `Item_Width × Item_Height` ô (lấy từ Item_Basic). Chỉ lưu ô trái-trên (`Pos_X`, `Pos_Y`). Kiểm tra chồng ô trong package.
- **Inventory** là 1 bảng, mỗi dòng 1 item, nối thẳng với Character. Không có bảng header (đã bỏ bảng Inventory 1-1 cũ). Lưới cố định.
- **Personal_Chest** là 1 bảng: `Item_ID`, `Account_ID`, `Chest_Tab`, `Pos_X/Y`. Số tab cố định (`Game_Config CHEST_TAB_MAX`), lưới cố định. Đã bỏ header, `Chest_Name`, `Chest_Tab_Count`.
- **Character_Equipment:**
  - PK là (`Character_ID`, `Equip_Slot`), `Item_ID` không được trùng.
  - Muốn mặc đồ thì item phải đang nằm trong Inventory của chính Character đó. Điều này kiểm tra trong package, **không đặt FK**, vì đồ đang mặc không chiếm ô lưới.
  - `Equip_Slot` lưu varchar + CHECK, **không dùng lookup** (ít giá trị).
  - WEAPON_2H chiếm MAIN_HAND và khóa OFF_HAND.
- Một Item luôn chỉ ở **đúng 1 nơi**: Inventory / Personal_Chest / Character_Equipment / Vendor.
- **Không cộng dồn:** 1 Item = 1 vật phẩm (đã bỏ `Item_Quantity` và `Item_Max_Stack`).

**Thế giới chung**
- Chỉ Chest và Inventory là riêng. Vendor, rương trên map, đồ rơi đều dùng chung: ai nhặt hoặc mua trước thì được.
- Đồ rơi chỉ giữ trong bộ nhớ game server, khi được nhặt mới ghi DB.
- Trạng thái quái, Boss, Status đang dính, HP/MP hiện tại đều chỉ giữ ở server.
- Không có entity Game_World / phòng.

**Character**
- Không lưu Region: login lại BE đưa người chơi về điểm hồi sinh.
- `CharacterNum` là thứ tự slot nhân vật, không trùng trong cùng Account.
- Character_Stat là bảng tính sẵn. `Character_Current_HP/MP` nghĩa là HP/MP **tối đa** đã tính (đã bỏ các cột `_Max`; HP/MP đang có không lưu).
- Gold theo Character, Diamond theo Account.

**Item**
- Stat cố định của Item = stat của Item_Basic × `Item_Quality_Bonus`, tính 1 lần lúc sinh rồi lưu lại.
- Buff random lưu ở Item_Stat; số lượng buff và khoảng giá trị lấy từ Range_Buff.
- Level của Item lấy theo `Item_Requirement_Level` (đã bỏ `Item.Item_Level`).
- `Item_Durability` là % (0–100), đồ mới luôn 100 (không có độ bền gốc).
- Có `Item_Cast_Speed`.
- `QUEST_ITEM` không có tác dụng, giá 0, không bán được, chỉ rơi cho người đang nhận quest.
- Quality: NORMAL / RARE / EPIC / LEGENDARY, dùng chung cho Item, Creep_Stat, Creep_Drop, Quest_Reward, NPC_Spawn.

**Vendor (dùng chung, bán theo lưới)**
- Mỗi dòng Vendor là 1 Item thật có stat random. PK là `Item_ID`, có `NPC_ID`, `Pos_X/Y`, `PriceBuy`.
- Loại Vendor do `NPC_Type` quyết định. Hàng chọn qua NPC.Region_ID → Region_Item_Basic, random theo `Drop_Weight`.
- Refresh mỗi ngày: xóa hết hàng cũ và sinh hàng mới. Vendor bán đồ tiêu thụ giữ hàng, chỉ đổi giá.
- Khi mua: `DELETE … WHERE Item_ID = ?`, ai xóa được đúng 1 dòng thì người đó mua thành công (chống 2 người mua cùng lúc).
- Bán cho Vendor đồ: Gold += `Item_Price`, rồi đưa đồ vào lưới Vendor với giá mua lại ×2 (ai cũng mua lại được). **Không có cờ Is_Buyback.**
- Bán cho Vendor đồ tiêu thụ: chỉ nhận Gold rồi xóa Item.

**Region / đồ rơi**
- Region chỉ là map.
- **Region_Item_Basic** (n-n, có `Drop_Weight`; user đồng ý sau khi được giải thích ví dụ Kiếm 70 / Rìu 25 / Nhẫn 5).
- **Region_Creep:** `Spawn_Time`, `Despawn_Time`, `Max_Spawn`, `Respawn_Time`.
- **Region_Chest:** rương trên map. **Creep_Drop:** đồ riêng của quái / Boss, kể cả quest item.

**Creep / Boss**
- Boss là Creep có `Is_Boss = TRUE`. Không tách bảng Boss vì cùng cấu trúc stat và skill.
- Creep_Stat có 1 dòng cho mỗi (Creep, Quality); Quality của mỗi con quái random lúc spawn.
- User đã đổi tên Creep_Detail thành **Creep_Stat**.
- Creep_Skill là danh sách skill. **Creep_Skill_Assign** gán skill với **level cố định** cho từng Creep (ví dụ Zombie – Bite lv3 ở mọi Quality). Quality chỉ đổi stat, nên sát thương skill tự tăng theo stat.

**Stat và chiến đấu (kiểu Diablo)**
- 15 stat chung (lookup STAT), cùng tên ở Character_Stat, Range_Buff, Creep_Stat.
- Class.Basic_* chỉ có 11 stat: **không có kháng nguyên tố** (gốc luôn 0, chỉ đến từ đồ và skill).
- Đơn vị:
  - Regen là numeric, lượng hồi mỗi giây.
  - Kháng lửa / độc / băng / sét là int %, trần 75%.
  - `Magic_Resist` là **điểm** như Armor, không phải %.
  - Attack / Cast speed và Movement là int %, với 100 là chuẩn.
- Sát thương là **1 con số**, không dùng khoảng min–max.
- **Sát thương skill = `Skill_Damage` + `Skill_Scale_Ratio` × stat.** User xác nhận `Skill_Bonus` cũ chính là hệ số này nên đã đổi tên.
- Giảm sát thương (**đề xuất, chưa chốt cân bằng**): `Raw × K/(K + Armor hoặc Magic_Resist) × (1 − Resist%)`, K = 100.
- Đồ có sát thương nguyên tố (+X sát thương lửa…) → **phát triển sau**.
- Đã sửa chính tả trong tên cột: `Attack_Spped` → `Attack_Speed`, `Lighting` → `Lightning`.

**Skill effect / Status**
- Skill_Effect và Creep_Skill_Effect gồm passive cộng stat, buff / debuff, DOT / HOT, kèm `Chance`, `Duration`, `Tick_Damage`, `Tick_Scale_Ratio`.
- Status định nghĩa hiệu ứng, Status_Stat định nghĩa stat bị thay đổi.
- Lookup SKILL_TYPE và SKILL_DAMAGE_TYPE dùng chung cho Character, Creep và Status.

**Quest / Achievement**
- Quest gồm MAIN / SIDE / DAILY / EVENT, chuỗi quest qua `Prerequisite_Quest_ID`, có NPC nhận trả quest (`Return_NPC_ID`), thời gian event.
- Quest_Objective có các loại KILL / COLLECT / TALK / REACH. Quest_Reward có EXP / GOLD / DIAMOND / ITEM.
- Character_Quest và Character_Quest_Progress lưu tiến độ. Quest DAILY reset theo `DAILY_RESET_TIME`.
- Achievement theo Character, có thưởng; Character_Achievement có `Rewarded_At`.

**Tiến trình / cấu hình**
- Level_Exp: exp cần để lên cấp và điểm skill nhận được.
- Class_Stat_Growth: stat tăng theo level.
- Game_Config thay **toàn bộ** "hằng số package" trước đây: RESIST_CAP, DEFENSE_K, kích thước lưới, CHEST_TAB_MAX, MAX_CHARACTER_SLOT, các hệ số giá, tỉ lệ Quality khi spawn, DAILY_RESET_TIME.

**Lookup**
- Không có cột `Lookup_Type`: `Lookup_Object` đã ghi cụ thể (ITEM_TYPE, ITEM_STAT/STAT, QUALITY…).
- Note tím đặt cạnh Range_Buff; cột tham chiếu gắn nhãn xanh `(link Lookup_Code)`.

---

## 7. Phương án user đã TỪ CHỐI hoặc thay thế (KHÔNG đề xuất lại)

- **Vendor_Item_Pool:** thay bằng Region_Item_Basic qua NPC.Region_ID.
- **`Region_Type` (TOWN / FIELD / DUNGEON), `Region_Level`, `Character.Region_ID`:** Region chỉ là map; BE lo việc hồi sinh.
- **Cột `Lookup_Type` trong Lookup_Code:** `Lookup_Object` ghi rõ luôn loại.
- **Cờ `Vendor.Is_Buyback`, `Vendor_ID`, `StoreSlot`:** thay bằng lưới `Pos_X/Y`; mua lại xử lý trong package.
- **Bảng header Inventory, `Grid_Width/Height` ở Inventory / Chest; header Personal_Chest, `Chest_Name`, `Account.Chest_Tab_Count`.**
- **Cộng dồn vật phẩm (`Item_Quantity`, `Item_Max_Stack`), `Item_Basic_Durability`, `Item.Item_Level`.**
- **`Equip_Slot` dạng lookup.**
- **Cột `Character_Current_HP_Max` / `_MP_Max`, lưu HP/MP hiện tại.**
- **Game_World / chia phòng.**
- **Gắn link Lookup cho `Range_Buff.Object_Quality`.**
- **Tách bảng Boss riêng.**
- **Sát thương dạng khoảng min–max.**
- **Kháng nguyên tố gốc ở Class (`Basic_*_Resist`):** user tự xóa.
- **Đề xuất "level skill của quái = thứ tự Quality":** thay bằng Creep_Skill_Assign.
- **`Dungeon_Creep.Is_Boss`:** dùng `Creep.Is_Boss`.
- **Nạp thẻ / cửa hàng Diamond:** chưa làm.

---

## 8. Lịch sử các vòng chỉnh sửa (tóm tắt)

1. **Lưới kiểu Diablo:**
   - Personal_Chest theo Account, có tab; Inventory theo Character.
   - Đổi Item_Equipment thành Character_Equipment.
   - Thêm `Item_Level` / `Item_Quantity` (sau đó đều bỏ) và note luật lưới.
2. **Sắp xếp lại bố cục**; thêm luật Equip (cần có trong Inventory, kiểm tra bằng package) và luật Vendor (refresh, mua bán).
3. **Nhân bản trang làm v2.** Chốt thế giới chung. Rà Account / Character / Character_Stat. Đề xuất Vendor_Item_Pool, sau đó bị bỏ.
4. **Đặt quy ước tô màu** và note tím lookup; tách luật thành nhiều note cạnh entity; bỏ Region trên Character.
5. **Lookup:** dời cột note tím cạnh Range_Buff; chốt Quality = NORMAL / RARE / EPIC / LEGENDARY; Equip_Slot không dùng lookup; thêm nhãn `(link Lookup_Code)`.
6. **Lookup_Code** dùng `Lookup_Object` + `Lookup_Int`. Gộp Inventory. Lưới cố định. Vendor bán theo lưới và cho mua lại. Đề xuất Dungeon. Region đơn giản hóa.
7. **v3:**
   - Thêm Region_Item_Basic và Region_Creep; Creep và Boss dùng chung entity.
   - Gộp Personal_Chest; bỏ `Chest_Name` và `HP/MP_Max`.
   - Dời Dungeon sang phần phát triển sau.
8. **Gộp v2 và v3 thành "New Version"**, so sánh với bản gốc. Giải thích `Drop_Weight`. Rà stat theo kiểu Diablo: sửa chính tả, mở rộng Creep_Stat, Creep_Skill dùng lookup.
9. **Mô hình chiến đấu:** công thức scale và giảm sát thương; thêm Creep_Skill_Assign; `Skill_Bonus` → `Skill_Scale_Ratio`. Thử kết nối draw.io (chỉ để xem trước).
10. **Bỏ kháng gốc ở Class** và `Chest_Tab_Count` (user tự bỏ); Region_Creep thêm `Max_Spawn` / `Respawn_Time`.
11. **Compile New Version thành `Physical ERD` chính thức** (thay trang gốc cũ); `New Version` trở thành trang làm việc; bỏ `Dungeon_Creep.Is_Boss`.
12. **(Đang chờ duyệt)** Bổ sung các entity còn thiếu theo góc nhìn kiến trúc: mục A, B, C (xem 5.2).

---

## 9. Việc tiếp theo và câu hỏi còn mở (tổng quan)

1. **Chờ user duyệt vòng 12** trên `New Version`. Đồng ý thì compile (mục 4.5); có góp ý thì sửa tiếp trên `New Version` và tô màu.
2. **Câu hỏi mở:** `Skill_Detail.Skill_Duration` hiện được hiểu là thời gian tồn tại của chính skill (ví dụ vùng lửa cháy 5 giây). Thời gian buff / debuff nằm ở `Skill_Effect.Duration`. Cần user xác nhận.
3. **Cân bằng chiến đấu:** công thức giảm sát thương mới là đề xuất (chi tiết ở mục 10.3).
4. **Trang `ERD Diagram`** đã lỗi thời; Claude đã đề nghị cập nhật, user chưa yêu cầu.
5. **Để sau** (user đã nói chưa cần):
   - lịch sử đăng nhập / session;
   - cửa hàng nạp Diamond (hiện chưa có kế hoạch);
   - đồ Unique / Set có affix cố định;
   - ô bình máu nhanh (Hotbar);
   - Friend / Mail;
   - `Character.Deleted_At` (xóa mềm);
   - sát thương nguyên tố trên đồ;
   - lookup CLASS_TYPE / CREEP_TYPE.
6. **Giai đoạn sau ERD:** viết DDL (PostgreSQL) và các package / function chính:
   - `move_item`, `equip_item`, `unequip_item`;
   - refresh / mua / bán Vendor;
   - nhặt đồ, nhận / trả quest, nhận thưởng achievement;
   - tính lại Character_Stat; spawn / respawn quái.

---

## 10. Tiến trình hiện tại: hội thoại đang dừng ở đâu, việc gì còn dở

### 10.1 Trạng thái file (đã kiểm tra lúc bàn giao, 2026-10-10)
- `Doombo.drawio` trong repo **chính là trạng thái sau vòng 12**. Nội dung đã được so khớp từng dòng với lần ghi cuối của Claude; user commit trong commit "Initial commit" (2026-10-10 09:16).
- **`Physical ERD`** = bản chính thức, compile ở vòng 11. Không có màu đánh dấu, không có legend.
- **`New Version`** = `Physical ERD` + toàn bộ thay đổi vòng 12, đã tô màu (`check.py` liệt kê đủ), `overlaps: 0`. Note chú thích (`note_legend`) đang ghi:
  - **Bảng đổi tên:** Skill_Bonus → Skill_Effect, Archivement → Achievement.
  - **Thuộc tính đã bỏ:**
    - `Character_Skill_Slot.Character_Skill_Slot_ID`;
    - 7 cột của `Skill_Detail` (Skill_Armor, Skill_Magic_Resist, Skill_HP, Skill_Regen_HP, Skill_MP, Skill_Regen_MP, Skill_Movement);
    - 4 cột của `Creep_Skill_Detail` (Creep_Skill_Armor, Creep_Skill_HP, Creep_Skill_Magic_Resist, Creep_Skill_Movement);
    - `Skill_Bonus.Skill_ID` và 1 dòng trống của Skill_Bonus;
    - `Dungeon_Creep.Is_Boss`.
  - **Liên kết đã bỏ:** 4 mũi tên từ note "Phát triển sau" tới Skill_Bonus / Status / Archivement / Quest, vì các bảng này giờ dùng chính thức. Note "Phát triển sau" đã dời về khu nền vàng.

### 10.2 Diễn biến cuối của hội thoại
1. **Yêu cầu cuối của user (vòng 12)**, cụ thể:
   - Làm các mục A (entity thiếu cho vòng chơi chính), B (hoàn thiện phần phát triển sau) và C (sửa entity có sẵn) mà Claude đã đề xuất.
   - Mục D (đăng nhập, cửa hàng…) để sau. **Thế giới là 1 map chung**, không có phòng.
   - **Diamond chỉ nhận qua Achievement / Quest.**
   - Quest có MAIN / SIDE / DAILY / EVENT.
   - Item_Type có **QUEST_ITEM** (chỉ thu thập rồi nộp cho NPC).
   - NPC sau này có **thương nhân lang thang** xuất hiện ngẫu nhiên trên map hoặc trong Dungeon, bán đồ quý, tỉ lệ xuất hiện thấp.
   - Cái gì "có cũng được, không có cũng được" thì để vào phát triển sau.
   - Lookup SKILL_TYPE / SKILL_DAMAGE_TYPE dùng chung cho Creep và Character.
   - Được phép xóa note thừa.
2. **Claude đã làm xong** (chi tiết ở 5.2) và trả lời:
   - tổng hợp các bảng mới, các entity đã sửa, phần phát triển sau và các note;
   - nhắc user **đóng rồi mở lại file trong draw.io desktop, đừng lưu bản đang mở cũ**;
   - hỏi: (a) user xem New Version, **ổn thì báo để compile thành trang chính thức**; (b) xác nhận ý nghĩa `Skill_Duration`.
3. **User chưa trả lời (a) và (b).** User chuyển sang yêu cầu tạo file bàn giao này, thêm `CLAUDE.md` và push lên GitHub để làm tiếp trên session cloud.
4. **Việc đầu tiên ở session mới:** chào ngắn, xác nhận đã nắm trạng thái, rồi **hỏi lại (a) và (b)**. Hoặc nếu user đưa yêu cầu mới thì làm theo yêu cầu mới, nhưng nhắc rằng vòng 12 chưa được compile.

### 10.3 Các luồng việc đang dở

| # | Việc | Trạng thái hiện tại | Cần gì để xong |
|---|---|---|---|
| 1 | Duyệt vòng 12 trên `New Version` | chờ user | User đồng ý → `compile_official.py` + `recolor.py` + `check.py` → báo kết quả. User góp ý → sửa `New Version` → recolor → báo theo entity. |
| 2 | Ý nghĩa `Skill_Detail.Skill_Duration` | Claude đang hiểu là "thời gian tồn tại của skill"; `Skill_Effect.Duration` là thời gian hiệu ứng | User xác nhận; nếu trùng ý nghĩa thì bỏ 1 trong 2 cột. |
| 3 | Cân bằng chiến đấu | Rule – Stat mục 5 ghi đề xuất: `Raw × K/(K + phòng thủ) × (1 − kháng%)`, K = 100, trần kháng 75%. Ví dụ phép lửa 130 vào mục tiêu có Magic_Resist 100 và kháng lửa 50% → 32.5. | Claude đã đưa bảng ví dụ và phương án đơn giản hơn (sát thương nguyên tố chỉ trừ % kháng, bỏ qua Magic_Resist → 65). Đã khuyên giữ kháng của đa số quái ở 0–30%, có thể cho K tăng theo level. **User chưa chọn.** |
| 4 | Lookup CLASS_TYPE, CREEP_TYPE | chưa có giá trị | user sẽ nghĩ sau |
| 5 | Trang `ERD Diagram` lỗi thời | chưa sửa | chờ user yêu cầu |
| 6 | Phát triển sau: Dungeon, Dungeon_Creep, Character_Dungeon, NPC_Spawn, Item_Log, Currency_Log | đã có bảng nền vàng + note luật, **chưa nối FK** | Khi user muốn làm: bỏ nền vàng, nối FK, tô màu thay đổi. |
| 7 | Mục D (để sau) | chưa làm | chờ user |
| 8 | DDL SQL + package | chưa bắt đầu | sau khi ERD ổn định |
| 9 | Kết nối draw.io MCP | Ở session local có connector `create_diagram` (chỉ hiển thị XML để xem trước, không ghi file). Toàn trang ~157k ký tự là quá lớn, chỉ xem được từng nhóm bảng. | Session cloud có thể không có connector này; việc sửa file vẫn dùng script Python. |

### 10.4 Khi user nhắn tiếp: cách xử lý
- **Trước mọi thao tác:**
  - `git pull`;
  - chạy `dump.py` và so với bản dump trước đó, hoặc `changelog.py` so với `Physical ERD`, để biết user đã tự sửa gì trong draw.io (user hay dời bảng, xóa cột, đổi tên, vẽ lại đường nối).
  - **Giữ nguyên các sửa đổi của user**; nếu sửa đổi làm hỏng tham chiếu ở chỗ khác thì sửa cho khớp và báo user.
- **"ok / chốt / duyệt / compile":** chạy compile (mục 4.5) → recolor → check → báo kết quả. Chỉ commit / push nếu user yêu cầu.
- **Góp ý chỉnh sửa:**
  - sửa `New Version` bằng `erd_lib`;
  - recolor → check (0 chồng hình) → changelog;
  - báo theo entity (+ / ~ / − / FK), nêu rõ những gì Claude tự quyết, các câu hỏi còn mở và phương án gợi ý.
- **Hỏi thiết kế:** trả lời dựa trên mục 6. **Không đề xuất lại** các phương án ở mục 7. Đưa lựa chọn có khuyến nghị.
- **Sau khi ghi file:** nhắc user `git pull` rồi **mở lại file trong draw.io**, không lưu bản cũ đang mở.

---

## 11. Đồng bộ giữa máy local (draw.io desktop) và session cloud

- User sửa `Doombo.drawio` bằng **draw.io desktop** trên Windows, thư mục nằm trong OneDrive. Session cloud sửa bản trong repo GitHub. **Chỉ một bên được sửa tại một thời điểm.** File drawio là 1 file XML lớn, merge conflict rất khó gỡ.
- **Quy trình:**
  1. User lưu file trong draw.io → commit và push (hoặc nhờ Claude làm).
  2. Session cloud `git pull` → sửa → commit và push khi user yêu cầu.
  3. User `git pull` → **đóng rồi mở lại** file trong draw.io trước khi sửa tiếp.
- Draw.io desktop khi lưu có thể đổi thứ tự hoặc định dạng thuộc tính XML (`host="Electron"`…). Vì vậy **so sánh nội dung bằng `dump.py` / `changelog.py`**, không dùng `git diff` thô.
- **Nếu gặp conflict:** đừng tự giải quyết bằng cách chọn một bên. Hỏi user muốn giữ bản nào, hoặc dùng `changelog.py` để so 2 phiên bản rồi áp lại phần thiếu.
- **Commit message:** viết ngắn gọn. Chỉ commit / push khi user yêu cầu.

---

## Phụ lục A – Công cụ trong `tools/erd/` (Python 3, chỉ dùng thư viện chuẩn)
Chạy từ **gốc repo** bằng `python` thường (không thêm `-I`, vì `compile_official.py` cần import `erd_lib.py` cùng thư mục). Tất cả đã chạy thử thành công trên bản sao của `Doombo.drawio`.

| Script | Lệnh | Tác dụng |
|---|---|---|
| `erd_lib.py` | `sys.path.insert(0, "tools/erd"); from erd_lib import ErdPage` | Thư viện sửa trang: thêm / xóa / sắp xếp dòng, thêm bảng / note / FK, tự tính lại layout, `save()` (tự bỏ edge treo). Có sẵn các hằng style: `ROW_STYLE`, `TABLE_STYLE`, `RULE_NOTE`, `LOOKUP_NOTE`, `DEFERRED_FILL`, `LINK`, và hàm `lookup_note()`. |
| `dump.py` | `python tools/erd/dump.py Doombo.drawio > out.txt` | In toàn bộ bảng, dòng, tọa độ và đường nối của mọi trang, để so sánh trước và sau khi sửa. |
| `recolor.py` | `python tools/erd/recolor.py Doombo.drawio "Physical ERD" "New Version" ""` | Xóa màu cũ, tô lại theo khác biệt (so dòng theo id, nếu không có id thì theo nhãn; so edge theo cặp), dựng lại `note_legend`. Tham số 4: id các dòng "chưa chốt" (tô hồng), ngăn cách bằng dấu phẩy. |
| `check.py` | `python tools/erd/check.py Doombo.drawio "New Version"` | Kiểm tra chồng hình (phải ra `overlaps: 0`) và liệt kê các chỗ đang tô NEW / MOD / RED. |
| `changelog.py` | `python tools/erd/changelog.py Doombo.drawio "Physical ERD" "New Version"` | Tổng hợp thay đổi theo entity (+ / ~ / − / FK+ / FK−) và các note mới / sửa, dùng để báo cáo cho user. |
| `extract.py` | `python tools/erd/extract.py Doombo.drawio "New Version" tables` (hoặc `notes`) | Xuất danh sách entity, thuộc tính và FK dạng markdown, hoặc nội dung toàn bộ note. Mục 5.1, 5.3, 5.4 của file này được sinh bằng script này. |
| `compile_official.py` | `python tools/erd/compile_official.py Doombo.drawio` | Đưa `New Version` thành `Physical ERD` chính thức, xóa màu đánh dấu và legend. Chạy `recolor.py` ngay sau đó. |
