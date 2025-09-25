document.addEventListener('DOMContentLoaded', () => {
    // Lấy tất cả các element cần thiết từ HTML
    const authGateDiv = document.getElementById('auth-gate');
    const mainContentDiv = document.getElementById('main-content');
    const appHeader = document.getElementById('app-header');
    const welcomeMessageSpan = document.getElementById('welcome-message');
    const logoutButton = document.getElementById('logout-button');
    const uploadForm = document.getElementById('upload-form');
    const imageInput = document.getElementById('image-input');
    const resultsContainer = document.getElementById('results-container');
    const dropZone = document.getElementById('drop-zone'); // Giả sử khu vực kéo-thả có id="drop-zone"

    let selectedFile = null; // Biến này sẽ lưu file mà người dùng đã chọn

    // === CÁC HÀM XỬ LÝ SỰ KIỆN ===

    // 1. Hàm đăng xuất
    function handleLogout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
        alert('Bạn đã đăng xuất.');
        window.location.href = 'login.html';
    }

    // 2. Hàm kiểm tra trạng thái đăng nhập khi trang được tải
    function checkLoginStatus() {
        const token = localStorage.getItem('authToken');
        const username = localStorage.getItem('username');

        if (!token || !username) {
            // Nếu chưa đăng nhập, ẩn nội dung chính và hiển thị yêu cầu đăng nhập
            mainContentDiv.classList.add('hidden');
            appHeader.classList.add('hidden');
            authGateDiv.innerHTML = `
                <div class="container" style="text-align: center; padding-top: 50px;">
                    <p class="error">Vui lòng <a href="login.html">đăng nhập</a> để sử dụng chức năng này.</p>
                </div>
            `;
        } else {
            // Nếu đã đăng nhập, hiển thị nội dung chính và lời chào
            authGateDiv.innerHTML = '';
            mainContentDiv.classList.remove('hidden');
            appHeader.classList.remove('hidden');
            welcomeMessageSpan.textContent = `Xin chào, ${username}!`;
        }
    }

    // 3. Hàm hiển thị kết quả phân tích
    function displayResults(data) {
        if (!data.detected_foods || data.detected_foods.length === 0) {
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

    // 4. Hàm xử lý khi submit form
    async function handleFormSubmit(event) {
        event.preventDefault();

        if (!selectedFile) {
            resultsContainer.innerHTML = '<p class="error">Vui lòng chọn một file ảnh!</p>';
            return;
        }

        const token = localStorage.getItem('authToken');
        if (!token) {
            handleLogout();
            return;
        }

        const submitButton = uploadForm.querySelector('button');
        submitButton.disabled = true;
        resultsContainer.innerHTML = '<p>Đang phân tích, vui lòng chờ...</p>';

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('http://127.0.0.1:8000/api/predict/', {
                method: 'POST',
                headers: { 'Authorization': `Token ${token}` },
                body: formData,
            });

            const responseData = await response.json();
            if (!response.ok) {
                throw new Error(responseData.detail || responseData.error || `Lỗi server: ${response.status}`);
            }
            
            displayResults(responseData);

        } catch (error) {
            console.error("Có lỗi xảy ra:", error);
            resultsContainer.innerHTML = `<p class="error">${error.message}</p>`;
            if (error.message.includes('Xác thực')) {
                setTimeout(handleLogout, 2000);
            }
        } finally {
            submitButton.disabled = false;
        }
    }

    // === GẮN CÁC SỰ KIỆN VÀO GIAO DIỆN ===

    checkLoginStatus(); // Chạy kiểm tra đăng nhập

    if (logoutButton) logoutButton.addEventListener('click', handleLogout);
    if (uploadForm) uploadForm.addEventListener('submit', handleFormSubmit);

    // Xử lý khi chọn file bằng nút input
    if (imageInput) {
        imageInput.addEventListener('change', (event) => {
            if (event.target.files && event.target.files[0]) {
                selectedFile = event.target.files[0];
                resultsContainer.innerHTML = `<p>Đã chọn file: ${selectedFile.name}</p>`;
            }
        });
    }

    // Xử lý kéo-thả (nếu có)
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => { e.preventDefault(); e.stopPropagation(); }, false);
        });
        dropZone.addEventListener('drop', (event) => {
            const files = event.dataTransfer.files;
            if (files && files[0]) {
                selectedFile = files[0];
                resultsContainer.innerHTML = `<p>Đã chọn file: ${selectedFile.name}</p>`;
            }
        }, false);
        dropZone.addEventListener('click', () => imageInput.click());
    }
});