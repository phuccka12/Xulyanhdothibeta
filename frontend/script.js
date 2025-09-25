const uploadForm = document.getElementById('upload-form');
const imageInput = document.getElementById('image-input');
const resultsContainer = document.getElementById('results-container');
const submitButton = uploadForm.querySelector('button');

// KIỂM TRA TRẠNG THÁI ĐĂNG NHẬẬP KHI TẢI TRANG
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('authToken');
    if (!token) {
        // Nếu không có token, không cho phép sử dụng và yêu cầu đăng nhập
        uploadForm.innerHTML = `
            <p class="error">Vui lòng <a href="login.html">đăng nhập</a> để sử dụng chức năng này.</p>
        `;
    }
});

uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    // Lấy token từ Local Storage
    const token = localStorage.getItem('authToken');
    if (!token) {
        alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
        window.location.href = 'login.html';
        return;
    }

    const file = imageInput.files[0];
    if (!file) {
        resultsContainer.innerHTML = '<p class="error">Vui lòng chọn một file ảnh!</p>';
        return;
    }

    submitButton.disabled = true;
    resultsContainer.innerHTML = '<p>Đang phân tích, vui lòng chờ...</p>';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://12_7.0.0.1:8000/api/predict/', {
            method: 'POST',
            headers: {
                // Thêm header Authorization để gửi token
                'Authorization': `Token ${token}`
            },
            body: formData,
        });

        if (response.status === 401) { // Lỗi xác thực
            throw new Error('Xác thực không thành công. Vui lòng đăng nhập lại.');
        }
        if (!response.ok) {
            throw new Error(`Lỗi server: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error("Có lỗi xảy ra:", error);
        resultsContainer.innerHTML = `<p class="error">${error.message}</p>`;
        // Nếu lỗi xác thực, xóa token cũ và chuyển hướng
        if (error.message.includes('Xác thực')) {
            localStorage.removeItem('authToken');
            setTimeout(() => { window.location.href = 'login.html'; }, 2000);
        }
    } finally {
        submitButton.disabled = false;
    }
});

function displayResults(data) {
    // ... hàm này giữ nguyên như cũ ...
    if (data.detected_foods.length === 0) {
        resultsContainer.innerHTML = '<p>Không phát hiện được món ăn nào trong ảnh.</p>';
        return;
    }
    let foodListHtml = '<ul>';
    data.detected_foods.forEach(food => {
        foodListHtml += `<li>
            <strong>${food.class_name}</strong> - Calo: ${food.calories} kcal 
            (Độ tin cậy: ${Math.round(food.confidence * 100)}%)
        </li>`;
    });
    foodListHtml += '</ul>';
    resultsContainer.innerHTML = `
        <h2>Kết quả phân tích</h2>
        <h3>Tổng lượng Calo: ${data.total_calories} kcal</h3>
        ${foodListHtml}
    `;
}