// Login Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const loginForm = document.getElementById('loginForm');
    const idInput = document.getElementById('userId');
    const passwordInput = document.getElementById('userPassword');
    const loginBtn = document.getElementById('loginBtn');

    // Input validation
    function validateForm() {
        const id = idInput.value.trim();
        const password = passwordInput.value.trim();
        
        if (id.length > 0 && password.length > 0) {
            loginBtn.disabled = false;
            loginBtn.style.opacity = '1';
        } else {
            loginBtn.disabled = true;
            loginBtn.style.opacity = '0.6';
        }
    }

    // Add event listeners for real-time validation
    idInput.addEventListener('input', validateForm);
    passwordInput.addEventListener('input', validateForm);

    // Form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const id = idInput.value.trim();
        const password = passwordInput.value.trim();
        const saveId = document.getElementById('saveId').checked;
        
        if (!id || !password) {
            alert('아이디와 비밀번호를 입력해주세요.');
            return;
        }

        // Save ID if checkbox is checked
        if (saveId) {
            localStorage.setItem('savedUserId', id);
        } else {
            localStorage.removeItem('savedUserId');
        }

        // Here you would normally send the data to your server
        console.log('Login attempt:', { id, password, saveId });
        
        // For demo purposes, just show an alert
        alert('로그인 기능은 개발 중입니다.');
    });

    // Load saved ID on page load
    const savedId = localStorage.getItem('savedUserId');
    if (savedId) {
        idInput.value = savedId;
        document.getElementById('saveId').checked = true;
        validateForm();
    }

    // SNS Login handlers
    document.getElementById('naverLogin').addEventListener('click', function() {
        alert('네이버 로그인 기능은 개발 중입니다.');
    });

    document.getElementById('kakaoLogin').addEventListener('click', function() {
        alert('카카오 로그인 기능은 개발 중입니다.');
    });

    // Sidebar functionality
    const sidebarButtons = document.querySelectorAll('.sidebar-btn');
    sidebarButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            switch(action) {
                case 'chat':
                    alert('채팅상담 기능은 개발 중입니다.');
                    break;
                case 'support':
                    alert('고객센터 기능은 개발 중입니다.');
                    break;
                case 'store':
                    alert('매장찾기 기능은 개발 중입니다.');
                    break;
                case 'card':
                    alert('카드혜택 기능은 개발 중입니다.');
                    break;
                case 'event':
                    alert('이벤트 기능은 개발 중입니다.');
                    break;
                case 'top':
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    break;
            }
        });
    });

    // Initial form validation
    validateForm();
});
