            HƯỚNG DẪN SỬ DỤNG CHƯƠNG TRÌNH GIẢI SOKOBAN VỚI BỐN THUẬT TOÁN BFS, DFS, UCS VÀ A* 

GUI được thiết kế dễ sử dụng, với các hình đại diện liên quan chặt chẽ đến các thành phần của trò chơi Sokoban.
Để chạy chương trình, đầu tiên chúng ta sẽ sử dụng lệnh "python main.py" và thực hiện tiếp các bước sau.
Bước 1: Ở màn hình khởi động, người sử dụng sẽ được lựa chọn loại thuật toán và test case muốn giải trong hai bảng chọn được hiển thị.

Bước 2: Sau khi thuật toán và test case được chọn, chương trình sẽ tự động chuyển đến màn hình đã vẽ map, tương ứng với input từ file txt.
Giao diện chính của chương trình có 4 nút chức năng, ứng với các vai trò sau:
- Start: bắt đầu thực hiện thuật toán và test case đã chọn.
- Pause: Tạm dừng quá trình thực hiện thuật toán.
- Stop: Reset lại thuật toán đang được thực hiện.
- Back: Quay về màn hình khởi động để lựa chọn thuật toán và test case khác.

Bước 3: Khi thuật toán đã thực hiện xong, và Ares đã đẩy được đá đến vị trí mục tiêu, bản đồ sẽ dừng lại để người kiểm tra xem kết quả cuối cùng.
Nếu muốn thực hiện một thuật toán khác với test case khác thì nhấn nút “Back” để lựa chọn lại.

Tính năng được cài đặt thêm: khi chạy lệnh "python main.py --mode debug" thì người chơi sẽ có thể dùng các phím mũi tên để tự di chuyển Ares để đẩy đá, như một trò chơi Sokoban thật sự.

