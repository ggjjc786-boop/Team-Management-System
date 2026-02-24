/**
 * 免费车位页面 JS
 */

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function showToast(message, type) {
    var toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = 'toast toast-' + (type || 'info') + ' show';
    clearTimeout(window._toastTimer);
    window._toastTimer = setTimeout(function() {
        toast.classList.remove('show');
    }, 3500);
}

// 页面加载时获取免费车位列表
document.addEventListener('DOMContentLoaded', function() {
    loadFreeSpots();
});

async function loadFreeSpots() {
    var listDiv = document.getElementById('freeSpotList');
    if (!listDiv) return;

    listDiv.innerHTML =
        '<div style="text-align:center;padding:2rem;color:#999;">' +
        '<i data-lucide="loader" class="spin" style="width:24px;height:24px;"></i>' +
        '<p style="margin-top:0.5rem;">' + t('loading') + '</p></div>';
    if (window.lucide) lucide.createIcons();

    try {
        var res = await fetch('/redeem/free-spots');
        if (!res.ok) throw new Error('fetch error');
        var data = await res.json();

        if (!data.teams || data.teams.length === 0) {
            listDiv.innerHTML =
                '<div style="text-align:center;padding:2rem;color:#92400e;">' +
                '<div style="font-size:2.5rem;margin-bottom:0.5rem;">🚏</div>' +
                '<p style="font-size:1rem;font-weight:600;">' + t('freespot_no_spots') + '</p>' +
                '<p style="font-size:0.85rem;color:#999;margin-top:0.4rem;">' + t('freespot_redirecting') + '</p></div>';
            setTimeout(function() {
                window.location.href = '/waiting-room';
            }, 1500);
            return;
        }

        var html = '';
        data.teams.forEach(function(team) {
            var spotsLeft = team.available_spots || (team.max_members - team.current_members);
            html += '<div class="freespot-item">';
            html += '<div class="freespot-info">';
            html += '<div class="freespot-name">' + escapeHtml(team.team_name || 'Team ' + team.id) + '</div>';
            html += '<div class="freespot-meta">';
            html += '<span><i data-lucide="users" style="width:12px;height:12px;"></i> ' + team.current_members + '/' + team.max_members + '</span>';
            html += '<span class="freespot-avail">' + spotsLeft + ' ' + t('freespot_avail') + '</span>';
            if (team.subscription_plan) {
                html += '<span>' + escapeHtml(team.subscription_plan) + '</span>';
            }
            html += '</div></div>';
            html += '<button class="btn btn-primary btn-sm freespot-join-btn" onclick="joinFreeSpot(' + team.id + ', this)">';
            html += '<i data-lucide="log-in"></i> ' + t('freespot_join') + '</button>';
            html += '</div>';
        });
        listDiv.innerHTML = html;
        if (window.lucide) lucide.createIcons();

    } catch (err) {
        listDiv.innerHTML =
            '<div style="text-align:center;padding:2rem;color:#dc2626;">' +
            '<i data-lucide="alert-circle" style="width:24px;height:24px;margin-bottom:0.5rem;"></i>' +
            '<p>' + t('freespot_load_fail') + '</p></div>';
        if (window.lucide) lucide.createIcons();
    }
}

async function joinFreeSpot(teamId, btnEl) {
    var emailInput = document.getElementById('freeSpotEmail');
    var resultDiv = document.getElementById('freeSpotResult');

    if (!emailInput || !emailInput.value.trim()) {
        showToast(t('freespot_enter_email'), 'error');
        if (emailInput) emailInput.focus();
        return;
    }

    var email = emailInput.value.trim();
    // 简单邮箱格式校验
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showToast(t('invalid_email'), 'error');
        emailInput.focus();
        return;
    }

    if (btnEl) {
        btnEl.disabled = true;
        btnEl.innerHTML = '<i data-lucide="loader" class="spin"></i> ' + t('freespot_joining');
        if (window.lucide) lucide.createIcons();
    }

    try {
        var res = await fetch('/redeem/free-spot/join', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, team_id: teamId })
        });

        if (!res.ok) {
            var err = await res.json().catch(function() { return { detail: t('freespot_join_fail') }; });
            showToast(err.detail || t('freespot_join_fail'), 'error');
            if (btnEl) {
                btnEl.disabled = false;
                btnEl.innerHTML = '<i data-lucide="log-in"></i> ' + t('freespot_join');
                if (window.lucide) lucide.createIcons();
            }
            return;
        }

        var data = await res.json();
        showToast(data.message || t('freespot_join_success'), 'success');

        if (resultDiv) {
            var teamInfo = data.team_info || {};
            resultDiv.innerHTML =
                '<div style="padding:1.4rem;background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.18);border-radius:12px;text-align:center;">' +
                '<div style="font-size:2.5rem;margin-bottom:0.5rem;">🎉</div>' +
                '<div style="font-weight:600;color:#16a34a;font-size:1.2rem;margin-bottom:0.5rem;">' + escapeHtml(data.message) + '</div>' +
                '<div style="font-size:0.95rem;color:#bc1f1f;margin-bottom:0.5rem;">🎊 马到成功，万事顺意！🎊</div>' +
                (teamInfo.team_name ? '<div style="font-size:0.85rem;color:#666;margin-bottom:0.3rem;">Team: ' + escapeHtml(teamInfo.team_name) + '</div>' : '') +
                '<div style="font-size:0.85rem;color:#666;">' + t('freespot_check_email') + '</div>' +
                '</div>';
        }

        // 播放庆祝动画（与兑换码上车成功一致）
        if (typeof playCelebration === 'function') playCelebration(12000);
        if (typeof playNewYearOverlay === 'function') playNewYearOverlay(8000);

        // 刷新列表
        loadFreeSpots();

    } catch (err) {
        showToast(t('network_error'), 'error');
        if (btnEl) {
            btnEl.disabled = false;
            btnEl.innerHTML = '<i data-lucide="log-in"></i> ' + t('freespot_join');
            if (window.lucide) lucide.createIcons();
        }
    }
}
