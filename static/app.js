class QueensSolver {
    constructor() {
        this.initElements();
        this.bindEvents();
        this.selectedFile = null;
    }

    initElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.uploadContent = document.getElementById('uploadContent');
        this.previewContent = document.getElementById('previewContent');
        this.fileInput = document.getElementById('fileInput');
        this.solveBtn = document.getElementById('solveBtn');
        this.previewImage = document.getElementById('previewImage');
        this.fileName = document.getElementById('fileName');
        this.changeImageBtn = document.getElementById('changeImageBtn');
        this.loading = document.getElementById('loading');
        this.resultMainSection = document.getElementById('resultMainSection');
        this.resultMessage = document.getElementById('resultMessage');
        this.imageGallery = document.getElementById('imageGallery');
    }

    bindEvents() {
        // 點擊上傳區域
        this.uploadArea.addEventListener('click', (e) => {
            this.fileInput.click();
        });

        // 更換圖片按鈕
        this.changeImageBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.fileInput.click();
        });

        // 檔案選擇
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // 拖放功能
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                this.handleFileSelect(file);
            }
        });

        // 求解按鈕
        this.solveBtn.addEventListener('click', () => {
            this.solveProblem();
        });


        // 加上觸控效果 僅在有觸控功能的裝置上
        this.addTouchEffect(this.solveBtn);
        this.addTouchEffect(this.changeImageBtn);
        this.addTouchEffect(this.uploadArea);
    }

    addTouchEffect(btn) {
        if (!btn) return;
        let removeTimer = null;
        btn.addEventListener('touchstart', function(e) {
            btn.classList.add('active-touch');
            if (removeTimer) clearTimeout(removeTimer);
        });
        btn.addEventListener('touchend', function(e) {
            removeTimer = setTimeout(() => {
                btn.classList.remove('active-touch');
            }, 150);
        });
        btn.addEventListener('touchcancel', function(e) {
            btn.classList.remove('active-touch');
            if (removeTimer) clearTimeout(removeTimer);
        });
    }

    handleFileSelect(file) {
        if (!file || !file.type.startsWith('image/')) {
            this.showMessage('請選擇圖片檔案', 'error');
            return;
        }

        this.selectedFile = file;
        
        // 顯示預覽圖片
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImage.src = e.target.result;
            this.fileName.textContent = file.name;
            
            // 切換顯示狀態
            this.uploadContent.style.display = 'none';
            this.previewContent.style.display = 'flex';
            
            // 啟用求解按鈕
            this.solveBtn.disabled = false;
        };
        reader.readAsDataURL(file);

        // 隱藏之前的結果
        this.resultMainSection.style.display = 'none';
    }

    displayResult(result) {
        this.resultMessage.textContent = result.message;
        
        // 清空圖片庫
        this.imageGallery.innerHTML = '';
        
        if (result.result_images && result.result_images.length > 0) {
            result.result_images.forEach((imageUrl, index) => {
                const galleryItem = document.createElement('div');
                galleryItem.className = 'gallery-item';
                
                galleryItem.innerHTML = `
                    <img src="${imageUrl}" alt="結果圖片 ${index + 1}" loading="lazy">
                    <p>解答 ${index + 1}</p>
                `;
                
                this.imageGallery.appendChild(galleryItem);
            });
        }
        
        // 顯示第二個主要框框並加上動畫
        this.resultMainSection.classList.remove('show');
        this.resultMainSection.style.display = 'block';
        setTimeout(() => {
            this.resultMainSection.classList.add('show');
        }, 100);
        
        // 平滑滾動到結果區域
        this.resultMainSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    async solveProblem() {
        if (!this.selectedFile) {
            this.showMessage('請先選擇圖片', 'error');
            return;
        }

        this.showLoading(true);
        this.resultMainSection.style.display = 'none';

        try {
            const formData = new FormData();
            formData.append('file', this.selectedFile);

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            this.showLoading(false);

            if (response.ok) {
                this.displayResult(result);
            } else {
                // 其他狀態碼顯示錯誤訊息
                this.showMessage('嚴重錯誤', 'error');
            }
        } catch (error) {
            this.showLoading(false);
            this.showMessage(`網路錯誤: ${error.message}`, 'error');
        }
    }

    showLoading(show) {
        this.loading.style.display = show ? 'block' : 'none';
        this.solveBtn.disabled = show;
    }

    showMessage(message, type = 'info') {
        console.log(`${type.toUpperCase()}: ${message}`);
        
        if (type === 'error') {
            alert(`錯誤: ${message}`);
        }
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
    new QueensSolver();
});