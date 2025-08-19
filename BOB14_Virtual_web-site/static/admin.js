// Admin Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin panel loaded');

    // Password toggle functionality
    setupPasswordToggles();
    
    // User management
    setupUserActions();
    
    // Sidebar functionality
    setupSidebar();
    
    // Auto-refresh stats
    setupStatsRefresh();
    
    // Table sorting
    setupTableSorting();
    
    // Search functionality
    setupSearch();
});

function setupPasswordToggles() {
    const passwordFields = document.querySelectorAll('.password-field');
    
    passwordFields.forEach((field, index) => {
        const originalText = field.textContent;
        const hiddenText = '•'.repeat(originalText.length);
        let isHidden = true;
        
        // Initially hide password
        field.textContent = hiddenText;
        field.classList.add('password-hidden');
        
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'password-toggle';
        toggleBtn.innerHTML = `
            <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
        `;
        
        toggleBtn.addEventListener('click', function() {
            if (isHidden) {
                field.textContent = originalText;
                field.classList.remove('password-hidden');
                toggleBtn.innerHTML = `
                    <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                    </svg>
                `;
            } else {
                field.textContent = hiddenText;
                field.classList.add('password-hidden');
                toggleBtn.innerHTML = `
                    <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                `;
            }
            isHidden = !isHidden;
        });
        
        field.parentNode.insertBefore(toggleBtn, field.nextSibling);
    });
}

function setupUserActions() {
    // Edit user buttons
    const editButtons = document.querySelectorAll('.btn-edit');
    editButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            const username = this.getAttribute('data-username');
            
            if (confirm(`${username} 사용자를 수정하시겠습니까?`)) {
                // Here you would normally open an edit modal or redirect to edit page
                alert(`${username} 수정 기능은 개발 중입니다.`);
            }
        });
    });
    
    // Delete user buttons
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            const username = this.getAttribute('data-username');
            
            if (confirm(`정말로 ${username} 사용자를 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.`)) {
                // Here you would normally send delete request to server
                this.closest('tr').style.opacity = '0.5';
                this.closest('tr').style.pointerEvents = 'none';
                alert(`${username} 사용자가 삭제되었습니다.`);
            }
        });
    });
    
    // Add user button
    const addUserBtn = document.getElementById('addUserBtn');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', function() {
            alert('새 사용자 추가 기능은 개발 중입니다.');
        });
    }
    
    // Export button
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            // Simple CSV export simulation
            const users = Array.from(document.querySelectorAll('.users-table tbody tr')).map(row => {
                const cells = row.querySelectorAll('td');
                return {
                    username: cells[0].querySelector('h4').textContent,
                    email: cells[0].querySelector('p').textContent,
                    password: cells[1].querySelector('.password-field').textContent,
                    status: cells[2].querySelector('.status-badge').textContent
                };
            });
            
            console.log('Exporting users:', users);
            alert('사용자 데이터 내보내기 기능은 개발 중입니다.');
        });
    }
}

function setupSidebar() {
    const sidebarButtons = document.querySelectorAll('.sidebar-btn');
    sidebarButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            switch(action) {
                case 'chat':
                    alert('채팅상담 관리 기능은 개발 중입니다.');
                    break;
                case 'support':
                    alert('고객센터 관리 기능은 개발 중입니다.');
                    break;
                case 'store':
                    alert('매장 관리 기능은 개발 중입니다.');
                    break;
                case 'card':
                    alert('카드혜택 관리 기능은 개발 중입니다.');
                    break;
                case 'event':
                    alert('이벤트 관리 기능은 개발 중입니다.');
                    break;
                case 'top':
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    break;
            }
        });
    });
}

function setupStatsRefresh() {
    function updateStats() {
        const statNumbers = document.querySelectorAll('.stat-number');
        statNumbers.forEach(stat => {
            // Simulate small changes in stats
            const currentValue = parseInt(stat.textContent.replace(/,/g, ''));
            if (Math.random() > 0.9) { // 10% chance to update
                const change = Math.floor(Math.random() * 3) - 1; // -1, 0, or +1
                const newValue = Math.max(0, currentValue + change);
                stat.textContent = newValue.toLocaleString();
            }
        });
    }
    
    // Update stats every 30 seconds
    setInterval(updateStats, 30000);
}

function setupTableSorting() {
    const headers = document.querySelectorAll('.users-table th');
    headers.forEach((header, index) => {
        if (index < 3) { // Only make first 3 columns sortable
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(index);
            });
        }
    });
}

function sortTable(columnIndex) {
    const table = document.querySelector('.users-table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Simple sorting logic
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        return aText.localeCompare(bText);
    });
    
    // Clear and re-append sorted rows
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
    
    // Visual feedback
    const headers = document.querySelectorAll('.users-table th');
    headers.forEach(h => h.style.backgroundColor = '#f9fafb');
    headers[columnIndex].style.backgroundColor = '#e5e7eb';
    
    setTimeout(() => {
        headers[columnIndex].style.backgroundColor = '#f9fafb';
    }, 1000);
}

function setupSearch() {
    // Add search functionality if search input exists
    const searchInput = document.getElementById('userSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('.users-table tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}

// Utility functions
function formatDate(date) {
    return new Intl.DateTimeFormat('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function showNotification(message, type = 'info') {
    // Simple notification system
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-size: 14px;
        z-index: 9999;
        max-width: 300px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    `;
    
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#10b981';
            break;
        case 'error':
            notification.style.backgroundColor = '#ef4444';
            break;
        case 'warning':
            notification.style.backgroundColor = '#f59e0b';
            break;
        default:
            notification.style.backgroundColor = '#3b82f6';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Security warning acknowledgment
function acknowledgeSecurityWarning() {
    const warning = document.querySelector('.warning-alert');
    if (warning) {
        warning.style.opacity = '0.5';
        warning.style.pointerEvents = 'none';
        showNotification('보안 경고를 확인했습니다.', 'info');
    }
}

// Global functions for inline event handlers
window.acknowledgeSecurityWarning = acknowledgeSecurityWarning;
