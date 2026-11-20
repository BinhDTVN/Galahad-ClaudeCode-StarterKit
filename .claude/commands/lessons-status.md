---
description: Cập nhật TRẠNG THÁI các lesson trong .claude/LESSONS.md (open / closed / promoted / expired / supersedes). Không xoá lesson, không sửa chữ; chỉ thêm hoặc đổi tag trạng thái sau khi owner duyệt.
allowed-tools: Read, Edit, Grep, Glob
---

# /lessons-status — dọn LESSONS.md bằng trạng thái, không bằng xoá

Một danh sách lesson phẳng sẽ tới lúc tự hại mình: lesson đã xử lý xong đọc y hệt lesson còn
sống, và agent cứ thế hành động lại theo một cảnh báo đã hết hiệu lực. Xoá thì mất dấu vết
"vì sao trước đây ta nghĩ khác". Lệnh này gắn trạng thái vào chính dòng lesson.

## Trạng thái

Tag trạng thái đứng sau các tag nội dung, cùng khối tag đầu dòng:

| Tag | Nghĩa |
|---|---|
| (không có) | coi như open |
| `[status:open]` | còn hiệu lực, cứ làm theo |
| `[status:closed]` | việc đã xử lý xong, đừng làm lại |
| `[status:promoted][enforced:<nơi>]` | đã thành luật ở chỗ khác: `CLAUDE.md`, `hook:<file>`, `skill:<tên>`. Dòng giữ làm bằng chứng |
| `[status:expired]` | sự kiện hoặc trạng thái đã qua, chỉ còn là lịch sử |
| `[supersedes:<ngày-tag-tag>]` | gắn trên lesson MỚI thay lesson cũ. Lesson cũ giữ nguyên |

Ví dụ: `- [2026-09-01][hook][windows][status:promoted][enforced:hook:memory_first.py] Hook ...`

Mã của một lesson là ngày nén cộng các tag nội dung: `[2026-09-01][hook][windows]` thành
`20260901-hook-windows`. Tag trạng thái không tính vào mã, nên đổi trạng thái không làm gãy
con trỏ `supersedes:`.

## Các bước

1. **Đọc** `.claude/LESSONS.md`. File lớn thì làm theo từng nhóm tag (Grep theo tag), mỗi lần
   tối đa khoảng 40 dòng.
2. **Đề xuất** từng dòng theo bảng `dòng | mã | trạng thái mới | lý do + bằng chứng`:
   - `promoted` chỉ khi chỉ ra được nơi thi hành có thật (mở `CLAUDE.md`, hook, skill đó ra
     xem, đừng đoán theo tên).
   - `expired` chỉ khi lesson là sự kiện hoặc trạng thái (bản mới nhất, đang chờ, hôm nay),
     không phải một luật bền.
   - `closed` cần bằng chứng việc đã xong (commit, ticket đã đóng).
   - `supersedes` khi có lesson mới hơn nói khác: đề xuất gắn trên dòng MỚI.
   - Không chắc thì để nguyên, và ghi vào danh sách "để nguyên vì …". Không bỏ qua trong im
     lặng.
3. **Trình owner** theo nhóm trạng thái: số dòng, 2–3 ví dụ, các dòng còn nghi. Chờ duyệt.
4. **Áp** bằng Edit, chỉ cho các nhóm đã duyệt: thêm hoặc thay tag trạng thái trong khối tag
   đầu dòng. Không đổi một chữ nào của phần nội dung lesson, không xoá dòng.
5. **Tổng kết**: bảng số lượng theo trạng thái trước và sau, cộng danh sách "để nguyên vì …".

## Không làm

Không xoá lesson. Không sửa nội dung lesson. Không gắn `promoted` khi chưa mở nơi thi hành ra
xem. Không sửa lesson cũ để ghi "đã bị thay"; dùng `supersedes:` trên lesson mới.
