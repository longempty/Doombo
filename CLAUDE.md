# CLAUDE.md – Doombo

Doombo là web game MMO RPG kiểu Diablo (thế giới chung, giai đoạn đầu tối đa 2 người chơi). Repo hiện dùng để **thiết kế database / ERD** trong `Doombo.drawio`. Thư mục `doombo/` là project Godot (client), chưa đụng tới.

## Bắt đầu session: đọc trước
1. **`SESSION_HANDOFF.md`** là toàn bộ ngữ cảnh, quyết định và tiến trình từ session trước. Tối thiểu đọc **mục 0, 3, 10**, xem mục 6–7 trước khi đề xuất thiết kế.
2. Ở thời điểm bàn giao (2026-10-10), user **chưa trả lời** 2 câu:
   - (a) duyệt vòng 12 trên trang `New Version` để compile thành trang chính thức;
   - (b) ý nghĩa `Skill_Detail.Skill_Duration`.
   
   Hỏi lại khi user quay lại, trừ khi user đưa yêu cầu khác.
3. `git pull`, rồi so file với trạng thái đã ghi trong handoff để biết user có tự sửa trong draw.io không.

## Giao tiếp
- Trả lời **tiếng Việt**, xưng "mình", gọi user là "bạn". User viết văn nói, hay viết tắt.
- Sau mỗi vòng sửa:
  - báo thay đổi **theo từng entity** (+ thêm / ~ sửa / − bỏ / FK);
  - nêu rõ những gì mình tự quyết thay user;
  - đưa câu hỏi còn mở kèm phương án có khuyến nghị.
- **Không đề xuất lại** các phương án user đã từ chối (`SESSION_HANDOFF.md` mục 7).

## Quy tắc với `Doombo.drawio`
- Trang **`Physical ERD`** là bản chính thức: **không sửa trực tiếp**, chỉ thay thế khi compile lúc user duyệt (`tools/erd/compile_official.py`).
- Mọi chỉnh sửa làm trên trang **`New Version`**, rồi chạy `recolor.py` để **tô màu so với `Physical ERD`**:
  - dòng mới `#d5e8d4`, dòng sửa `#ffe6cc`, bảng đổi tên có tiêu đề `#ffe6cc`;
  - note mới / sửa viền đỏ, FK mới đường đỏ;
  - phần đã bỏ được liệt kê trong `note_legend`.
- Lookup:
  - Giá trị Lookup_Code khai báo bằng **note tím**, xếp thành cột cạnh `Range_Buff`.
  - Cột tham chiếu Lookup_Code gắn nhãn xanh `(link Lookup_Code)`; cột lưu `Lookup_Int`; tra bằng (`Lookup_Object`, `Lookup_Int`).
- Luật nghiệp vụ ghi **note vàng đặt cạnh entity**. Entity "phát triển sau" có nền vàng `light-dark(#FFF2CC,#CCCC00)` và **không nối FK**.
- **Không tạo file backup.** Không dời entity không liên quan. Giữ nguyên id các cell để so sánh khác biệt hoạt động đúng.
- **Giữ nguyên các sửa đổi user tự làm.** Nếu chúng làm hỏng tham chiếu thì sửa cho khớp và báo user.
- Sau khi ghi file, nhắc user `git pull` rồi **đóng và mở lại file trong draw.io desktop**, không lưu bản đang mở cũ.

## Công cụ (`tools/erd/`, Python 3 thư viện chuẩn; chạy từ gốc repo, không thêm `-I`)
```bash
python tools/erd/dump.py Doombo.drawio > before.txt                                 # snapshot để so sánh
python tools/erd/recolor.py Doombo.drawio "Physical ERD" "New Version" ""            # tô màu lại + legend
python tools/erd/check.py Doombo.drawio "New Version"                               # phải ra overlaps: 0
python tools/erd/changelog.py Doombo.drawio "Physical ERD" "New Version"            # báo cáo theo entity
python tools/erd/extract.py Doombo.drawio "New Version" tables                      # danh sách entity / FK
python tools/erd/compile_official.py Doombo.drawio                                  # chỉ khi user duyệt
```
Sửa trang bằng `tools/erd/erd_lib.py` (`ErdPage`: `add_row`, `relayout`, `add_table`, `add_edge`, `add_note`, `replace_in`, `remove`, `save`). Ví dụ và bảng id các bảng chính ở `SESSION_HANDOFF.md` mục 4.

## Git
- Chỉ commit / push khi user yêu cầu.
- Một thời điểm chỉ một bên (máy local của user, hoặc session cloud) được sửa `Doombo.drawio`, để tránh conflict XML.
- So sánh nội dung bằng `dump.py` / `changelog.py`, không dùng `git diff` thô (draw.io desktop hay định dạng lại XML).
- **Khi tiến trình thay đổi đáng kể** (duyệt / compile, quyết định mới, vòng sửa mới), cập nhật `SESSION_HANDOFF.md`: mục 5, 6, 7, 8, 10. Mục 5.1 / 5.3 / 5.4 có thể sinh lại bằng `extract.py`.
