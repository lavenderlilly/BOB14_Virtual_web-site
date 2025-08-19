// Verify Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
  /*** 이메일 입력 페이지 ***/
  const verifyForm = document.getElementById('verifyForm');
  const emailInput = document.getElementById('userEmail');
  const verifyBtn = document.getElementById('verifyBtn');

  if (verifyForm && emailInput && verifyBtn) {
    function validateEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    }
    function updateVerifyButton() {
      const ok = validateEmail((emailInput.value || '').trim());
      verifyBtn.disabled = !ok;
      verifyBtn.style.opacity = ok ? '1' : '0.6';
    }
    emailInput.addEventListener('input', updateVerifyButton);

    // ✅ 폼 제출을 막지 말고 서버로 보내기
    verifyForm.addEventListener('submit', function(e) {
      if (!validateEmail(emailInput.value.trim())) {
        e.preventDefault();
        alert('올바른 이메일 주소를 입력해주세요.');
      }
      // else: 그대로 제출 -> Flask /verify POST가 메일 보내고 verify_check.html 렌더
    });

    updateVerifyButton();
  }

  /*** 인증코드 입력 페이지 ***/
  const codeForm = document.getElementById('codeForm');
  const codeInputs = document.querySelectorAll('.code-input');
  const confirmBtn = document.getElementById('confirmBtn');
  const resendBtn = document.getElementById('resendBtn');
  const codeHidden = document.getElementById('codeHidden');

  if (codeForm && codeInputs.length > 0) {
    // 숫자만, 이동/붙여넣기 UX
    codeInputs.forEach((input, index) => {
      input.addEventListener('input', function(e) {
        const v = e.target.value.replace(/\D/g, '');
        e.target.value = v.slice(-1); // 한 글자만
        if (e.target.value && index < codeInputs.length - 1) {
          codeInputs[index + 1].focus();
        }
        updateConfirmButton();
      });
      input.addEventListener('keydown', function(e) {
        if (e.key === 'Backspace' && !e.target.value && index > 0) {
          codeInputs[index - 1].focus();
        }
        if (e.key === 'ArrowLeft' && index > 0) codeInputs[index - 1].focus();
        if (e.key === 'ArrowRight' && index < codeInputs.length - 1) codeInputs[index + 1].focus();
      });
      input.addEventListener('paste', function(e) {
        e.preventDefault();
        const numbers = (e.clipboardData.getData('text') || '').replace(/\D/g, '').slice(0, 6);
        numbers.split('').forEach((d, i) => { if (i < codeInputs.length) codeInputs[i].value = d; });
        updateConfirmButton();
      });
    });

    function getCode() {
      return Array.from(codeInputs).map(i => i.value).join('');
    }
    function updateConfirmButton() {
      const ok = getCode().length === 6;
      confirmBtn.disabled = !ok;
      confirmBtn.style.opacity = ok ? '1' : '0.6';
    }

    // ✅ 폼 제출을 막지 말고, 제출 직전에 hidden에 코드 넣고 그대로 POST
    codeForm.addEventListener('submit', function(e) {
      const code = getCode();
      if (code.length !== 6) {
        e.preventDefault();
        alert('6자리 인증코드를 모두 입력해주세요.');
        return;
      }
      if (codeHidden) codeHidden.value = code;
      // 그대로 제출 -> Flask /verify/check POST가 세션 설정 후 대시보드로 redirect
    });

    // 재전송 버튼(선택 사항: UX만)
    if (resendBtn) {
      let t = 0, interval = null;
      function updateResend() {
        resendBtn.textContent = t > 0 ? `재전송 (${t}초)` : '재전송';
        resendBtn.disabled = t > 0;
      }
      function start() {
        t = 60;
        updateResend();
        interval = setInterval(() => {
          t -= 1;
          updateResend();
          if (t <= 0 && interval) { clearInterval(interval); interval = null; }
        }, 1000);
      }
      resendBtn.addEventListener('click', () => {
        // 여기서 원하면 /verify 로 다시 POST 하도록 구현 가능(이메일 hidden 필요)
        alert('인증코드가 재전송되었습니다.');
        start();
      });
      start();
    }

    updateConfirmButton();
  }

  /*** 사이드바 데모 버튼(기능 없음) ***/
  const sidebarButtons = document.querySelectorAll('.sidebar-btn');
  sidebarButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const action = btn.getAttribute('data-action');
      switch(action) {
        case 'top': window.scrollTo({ top: 0, behavior: 'smooth' }); break;
        default: alert('데모 기능입니다.');
      }
    });
  });
});

