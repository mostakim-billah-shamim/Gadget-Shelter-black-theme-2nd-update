

// Auth_baseForm design


// Toast Notification Engine
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;
    const iconMap = { success: '✓', error: '✕', info: 'ℹ' };

    toast.innerHTML = `<div class="toast-icon">${iconMap[type] || '✓'}</div><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = "all 0.4s ease";
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-20px)";
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

// Password Show/Hide Toggle
function togglePasswordVisibility(fieldId, btn) {
    const input = document.getElementById(fieldId);
    if (!input) return;

    if (input.type === "password") {
        input.type = "text";
        btn.textContent = "🙈";
    } else {
        input.type = "password";
        btn.textContent = "👁️";
    }
}

// Unified Form & Banner Switcher
function switchForm(type) {
    const loginSec = document.getElementById('loginFormSection');
    const signupSec = document.getElementById('signupFormSection');
    const bannerTitle = document.getElementById('bannerTitle');
    const bannerDesc = document.getElementById('bannerDesc');

    if (!loginSec || !signupSec) return;

    if (type === 'signup') {
        loginSec.classList.add('hidden');
        signupSec.classList.remove('hidden');

        if (bannerTitle) bannerTitle.innerHTML = 'Unlock Next-Gen <span>Gadgets.</span>';
        if (bannerDesc) bannerDesc.textContent = 'Join Gadget. to experience hyper-fast shipping, member-only tech drops, and special hardware discounts.';
    } else {
        signupSec.classList.add('hidden');
        loginSec.classList.remove('hidden');

        if (bannerTitle) bannerTitle.innerHTML = 'Discover High Tech <span>Gear.</span>';
        if (bannerDesc) bannerDesc.textContent = 'Access ultra-fast devices, exclusive discounts, and next-generation tech gadgets built for your modern lifestyle.';
    }
}

// Auto Tab Switcher on Page Load (Detects Query Param, Hash, or Path)
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    const hashParam = window.location.hash.replace('#', '');
    const path = window.location.pathname;

    const isSignup = tabParam === 'signup' || hashParam === 'signup' || path.includes('register') || path.includes('signup');
    const isLogin = tabParam === 'login' || hashParam === 'login' || path.includes('login');

    if (isSignup) {
        switchForm('signup');
    } else if (isLogin) {
        switchForm('login');
    }
});