// Lấy các element từ HTML
const uploadForm = document.getElementById('upload-form');
const imageInput = document.getElementById('image-input');
const resultsContainer = document.getElementById('results-container');

// Bắt sự kiện khi người dùng nhấn nút "Phân tích"
uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // Ngăn form tải lại trang

    const file = imageInput.files[0];
    if (!file) {
        resultsContainer.innerHTML = '<p class="error">Vui lòng chọn một file ảnh!</p>';
        return;
    }

    // Hiển thị trạng thái đang xử lý
    resultsContainer.innerHTML = '<p>Đang phân tích, vui lòng chờ...</p>';

    // Tạo FormData để gửi file
    const formData = new FormData();
    formData.append('file', file);

    // Gửi yêu cầu đến server Flask
    try {
       const response = await fetch('http://127.0.0.1:8000/api/predict/',{
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Lỗi server: ${response.status}`);
        }

        const data = await response.json();
        
        // Hiển thị kết quả ra màn hình
        displayResults(data);

    } catch (error) {
        console.error("Có lỗi xảy ra:", error);
        resultsContainer.innerHTML = `<p class="error">Không thể kết nối đến server. Hãy đảm bảo backend đang chạy!</p>`;
    }
});

// Hàm để hiển thị kết quả
function displayResults(data) {
    // Nếu không phát hiện món ăn nào
    if (data.detected_foods.length === 0) {
        resultsContainer.innerHTML = '<p>Không phát hiện được món ăn nào trong ảnh.</p>';
        return;
    }

    // Tạo HTML để hiển thị danh sách món ăn
    let foodListHtml = '<ul>';
    data.detected_foods.forEach(food => {
        foodListHtml += `<li>
            <strong>${food.class_name}</strong> - Calo: ${food.calories} kcal 
            (Độ tin cậy: ${Math.round(food.confidence * 100)}%)
        </li>`;
    });
    foodListHtml += '</ul>';

    // Cập nhật nội dung cho div kết quả
    resultsContainer.innerHTML = `
        <h2>Kết quả phân tích</h2>
        <h3>Tổng lượng Calo: ${data.total_calories} kcal</h3>
        ${foodListHtml}
    `;
}