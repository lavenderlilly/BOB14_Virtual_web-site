// Dashboard Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('로그아웃 하시겠습니까?')) {
                window.location.href = '/logout';
            }
        });
    }

    // Product Carousel functionality
    let currentSlide = 0;
    const products = document.querySelectorAll('.product-card');
    const totalProducts = products.length;
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    if (prevBtn && nextBtn && products.length > 0) {
        nextBtn.addEventListener('click', function() {
            currentSlide = (currentSlide + 1) % totalProducts;
            console.log('Next slide:', currentSlide);
            // Here you could add actual carousel sliding animation
        });

        prevBtn.addEventListener('click', function() {
            currentSlide = (currentSlide - 1 + totalProducts) % totalProducts;
            console.log('Previous slide:', currentSlide);
            // Here you could add actual carousel sliding animation
        });
    }

    // Service card interactions
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('click', function(e) {
            e.preventDefault();
            const serviceName = this.querySelector('.service-name').textContent;
            alert(`${serviceName} 기능은 개발 중입니다.`);
        });
    });

    // Order status interactions
    const orderItems = document.querySelectorAll('.order-item');
    orderItems.forEach(item => {
        item.addEventListener('click', function() {
            const orderName = this.querySelector('h4').textContent;
            alert(`${orderName} 상세 정보를 확인합니다.`);
        });
        
        // Add hover effect
        item.style.cursor = 'pointer';
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

    // Welcome animation
    const welcomeCard = document.querySelector('.welcome-card');
    if (welcomeCard) {
        // Add a subtle animation on load
        setTimeout(() => {
            welcomeCard.style.transform = 'scale(1.02)';
            setTimeout(() => {
                welcomeCard.style.transform = 'scale(1)';
            }, 200);
        }, 500);
    }

    // Auto-refresh stats (simulation)
    function updateStats() {
        const statNumbers = document.querySelectorAll('.stat-number');
        statNumbers.forEach(stat => {
            const currentValue = parseInt(stat.textContent);
            if (Math.random() > 0.8) { // 20% chance to update
                const newValue = currentValue + Math.floor(Math.random() * 3) - 1; // -1, 0, or +1
                stat.textContent = Math.max(0, newValue);
            }
        });
    }

    // Update stats every 30 seconds (for demo purposes)
    setInterval(updateStats, 30000);

    // Navigation menu interactions
    const navLinks = document.querySelectorAll('.nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
                const linkText = this.textContent;
                alert(`${linkText} 페이지로 이동합니다.`);
            }
        });
    });

    console.log('Dashboard loaded successfully');
});

// Add some utility functions
function formatDate(date) {
    return new Intl.DateTimeFormat('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(date);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW'
    }).format(amount);
}

// Example function to update user stats (could be called from server)
function updateUserStats(stats) {
    if (stats.orders !== undefined) {
        const orderStat = document.querySelector('.stat-item:nth-child(1) .stat-number');
        if (orderStat) orderStat.textContent = stats.orders;
    }
    
    if (stats.services !== undefined) {
        const serviceStat = document.querySelector('.stat-item:nth-child(2) .stat-number');
        if (serviceStat) serviceStat.textContent = stats.services;
    }
    
    if (stats.points !== undefined) {
        const pointStat = document.querySelector('.stat-item:nth-child(3) .stat-number');
        if (pointStat) pointStat.textContent = stats.points;
    }
}
