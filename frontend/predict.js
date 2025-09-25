document.addEventListener('DOMContentLoaded', () => {
    // Lấy tất cả các element cần thiết
    const authGateDiv = document.getElementById('auth-gate');
    const mainContentDiv = document.getElementById('main-content');
    const appHeader = document.getElementById('app-header');
    const welcomeMessageSpan = document.getElementById('welcome-message');
    const logoutButton = document.getElementById('logout-button');
    const uploadForm = document.getElementById('upload-form');
    const imageInput = document.getElementById('image-input');
    const resultsContainer = document.getElementById('results-container');
    const dropZone = document.getElementById('drop-zone'); // Khu vực kéo thả

    let selectedFile = null; // Biến để lưu file người dùng chọn

    // === HÀM XỬ LÝ SỰ KIỆN ===

    // 1. Hàm đăng xuất
    function handleLogout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
        alert('Bạn đã đăng xuất.');
        window.location.href = 'login.html';
    }

    // 2. Hàm kiểm tra đăng nhập khi tải trang
    function checkLoginStatus() {
        const token = localStorage.getItem('authToken');
        const username = localStorage.getItem('username');

        if (!token || !username) {
            mainContentDiv.classList.add('hidden');
            appHeader.classList.add('hidden');
            authGateDiv.innerHTML = `
                <div class="container" style="text-align: center; padding-top: 50px;">
                    <p class="error">Vui lòng <a href="login.html">đăng nhập</a> để sử dụng chức năng này.</p>
                </div>
            `;
        } else {
            authGateDiv.innerHTML = '';
            mainContentDiv.classList.remove('hidden');
            appHeader.classList.remove('hidden');
            welcomeMessageSpan.textContent = `Xin chào, ${username}!`;
        }
    }

    // 3. Hàm hiển thị kết quả
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

    // === GẮN CÁC SỰ KIỆN VÀO ELEMENT ===

    // Chạy kiểm tra đăng nhập
    checkLoginStatus();

    // Gắn sự kiện cho nút đăng xuất
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }

    // Gắn sự kiện cho nút chọn file input
    if (imageInput) {
        imageInput.addEventListener('change', (event) => {
            if (event.target.files && event.target.files[0]) {
                selectedFile = event.target.files[0];
                resultsContainer.innerHTML = `<p>Đã chọn file: ${selectedFile.name}</p>`;
            }
        });
    }

    // Gắn sự kiện cho khu vực kéo-thả
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        dropZone.addEventListener('drop', (event) => {
            const dt = event.dataTransfer;
            const files = dt.files;
            if (files && files[0]) {
                selectedFile = files[0];
                resultsContainer.innerHTML = `<p>Đã chọn file: ${selectedFile.name}</p>`;
            }
        }, false);
        
        dropZone.addEventListener('click', () => imageInput.click());
    }

    // Gắn sự kiện submit cho form
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (event) => {
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

                if (!response.ok) {
                    const errorData = await response.json();
                    const errorMessage = errorData.detail || errorData.error || `Lỗi server: ${response.status}`;
                    throw new Error(errorMessage);
                }
                
                const data = await response.json();
                displayResults(data);

            } catch (error) {
                console.error("Có lỗi xảy ra:", error);
                resultsContainer.innerHTML = `<p class="error">${error.message}</p>`;
                if (error.message.includes('Xác thực')) {
                    setTimeout(handleLogout, 2000);
                }
            } finally {
                submitButton.disabled = false;
            }
        });
    }
});