// 鐢ㄦ埛鍏戞崲椤甸潰JavaScript

// HTML杞箟鍑芥暟 - 闃叉XSS鏀诲嚮
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 鍏ㄥ眬鍙橀噺
let currentEmail = '';
let currentCode = '';
let availableTeams = [];
let selectedTeamId = null;
let cleanupCelebration = null;
const HORSE_YEAR_BLESSINGS = [
    '\u9a6c\u5230\u6210\u529f\uff0c\u4e07\u4e8b\u987a\u610f\uff01',
    '\u9a6c\u5e74\u5927\u5409\uff0c\u9616\u5bb6\u5e78\u5b89\uff01',
    '\u9f99\u9a6c\u7cbe\u795e\uff0c\u597d\u8fd0\u957f\u968f\uff01',
    '\u9a6c\u5e74\u5982\u610f\uff0c\u798f\u6ee1\u65b0\u6625\uff01',
    '\u9a8f\u9a6c\u5954\u817e\uff0c\u524d\u7a0b\u9526\u7ee3\uff01',
    '\u9a6c\u97ec\u58f0\u58f0\uff0c\u559c\u4e8b\u8fde\u8fde\uff01',
    '\u4e00\u8dc3\u5343\u91cc\uff0c\u5fc3\u60f3\u4e8b\u6210\uff01',
    '\u65b0\u5c81\u9a6c\u5f00\u65b0\u7bc7\uff0c\u987a\u98ce\u987a\u6c34\uff01'
];

function getRandomHorseYearBlessing() {
    const index = Math.floor(Math.random() * HORSE_YEAR_BLESSINGS.length);
    return HORSE_YEAR_BLESSINGS[index];
}

function animateSuccessCheck() {
    const iconWrap = document.querySelector('.result-success .result-icon.success-check-animate');
    if (!iconWrap) return;

    iconWrap.classList.remove('is-animated');
    // Force reflow so repeated success can replay animation.
    void iconWrap.offsetWidth;
    iconWrap.classList.add('is-animated');

    const halo = iconWrap.querySelector('.success-halo');
    if (halo) {
        halo.classList.remove('is-animated');
        void halo.offsetWidth;
        halo.classList.add('is-animated');
    }

    const animatePath = (path, duration, delay) => {
        if (!path || typeof path.getTotalLength !== 'function') return;
        const length = path.getTotalLength();
        if (!length) return;

        path.style.strokeDasharray = `${length}`;
        path.style.strokeDashoffset = `${length}`;
        path.style.transition = 'none';

        window.setTimeout(() => {
            path.style.transition = `stroke-dashoffset ${duration}ms cubic-bezier(0.22, 1, 0.36, 1)`;
            path.style.strokeDashoffset = '0';
        }, delay);
    };

    animatePath(iconWrap.querySelector('.success-circle-path'), 520, 20);
    animatePath(iconWrap.querySelector('.success-check-path'), 460, 280);
}

// Celebration animation (performance optimized)
function playCelebration(durationMs = 9000) {
    if (typeof document === 'undefined' || !document.body) return;

    if (cleanupCelebration) {
        cleanupCelebration();
    }

    const canvas = document.createElement('canvas');
    canvas.setAttribute('aria-hidden', 'true');
    Object.assign(canvas.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        zIndex: '9999'
    });
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    if (!ctx) { canvas.remove(); return; }

    const prefersReducedMotion = typeof window.matchMedia === 'function'
        && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const confetti = [];
    const sparks = [];
    const confettiColors = ['#bc1f1f', '#d84b1f', '#f4b43d', '#f8d46a', '#ff6b6b', '#ffd700', '#ff4444', '#e8c547'];
    const fireworkHues = [0, 8, 15, 28, 42, 50, 340, 350, 355];
    const maxConfetti = prefersReducedMotion ? 60 : 120;
    const maxSparks = prefersReducedMotion ? 50 : 100;
    const endTime = performance.now() + durationMs;
    const DRAG = 0.99;
    const SPARK_DRAG = 0.98;

    let width = 0, height = 0;
    let animationId = 0;
    let fireworkTimer = 0;
    let visibilityHandler = null;
    let lastFrameTs = 0;
    const timeoutIds = [];

    function resizeCanvas() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
        ctx.setTransform(1, 0, 0, 1, 0, 0);
    }

    function addConfettiPiece(srcX, srcY, angle, speed) {
        if (confetti.length >= maxConfetti) return;
        const life = 3.0 + Math.random() * 2.0;
        confetti.push({
            x: srcX, y: srcY,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            gravity: 55 + Math.random() * 25,
            w: 5 + Math.random() * 7,
            h: 3 + Math.random() * 4,
            rot: Math.random() * 6.28,
            spin: (Math.random() - 0.5) * 5,
            wobble: Math.random() * 6.28,
            wobbleSpd: 2 + Math.random() * 2,
            life, maxLife: life,
            ci: Math.floor(Math.random() * confettiColors.length)
        });
    }

    function burstConfetti(cx, cy, count, baseAngle, spread, speedMin, speedRange) {
        for (let i = 0; i < count; i++) {
            const a = baseAngle + (Math.random() - 0.5) * spread;
            const s = speedMin + Math.random() * speedRange;
            addConfettiPiece(
                cx + (Math.random() - 0.5) * 20,
                cy + (Math.random() - 0.5) * 20,
                a, s
            );
        }
    }

    function addFireworkBurst(x, y) {
        const hue = fireworkHues[Math.floor(Math.random() * fireworkHues.length)];
        const count = Math.min(24, maxSparks - sparks.length);
        if (count <= 0) return;
        for (let i = 0; i < count; i++) {
            const angle = (6.28 * i) / count + (Math.random() - 0.5) * 0.4;
            const speed = 120 + Math.random() * 180;
            const life = 1.0 + Math.random() * 0.7;
            sparks.push({
                x, y, px: x, py: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                gravity: 140 + Math.random() * 60,
                life, maxLife: life,
                size: 1.5 + Math.random() * 2,
                hue
            });
        }
    }

    function launchFirework() {
        if (document.hidden || !width || !height) return;
        if (sparks.length >= maxSparks * 0.8) return;
        addFireworkBurst(
            width * (0.15 + Math.random() * 0.7),
            height * (0.08 + Math.random() * 0.3)
        );
    }

    function update(dt) {
        let i = 0;
        while (i < confetti.length) {
            const p = confetti[i];
            p.vx *= DRAG;
            p.vy = Math.min(p.vy + p.gravity * dt, 140);
            p.x += (p.vx + Math.sin(p.wobble) * 10) * dt;
            p.y += p.vy * dt;
            p.rot += p.spin * dt;
            p.wobble += p.wobbleSpd * dt;
            p.life -= dt;
            if (p.life <= 0 || p.y > height + 30) {
                confetti[i] = confetti[confetti.length - 1];
                confetti.pop();
            } else {
                i++;
            }
        }

        i = 0;
        while (i < sparks.length) {
            const p = sparks[i];
            p.px = p.x;
            p.py = p.y;
            p.vx *= SPARK_DRAG;
            p.vy += p.gravity * dt;
            p.x += p.vx * dt;
            p.y += p.vy * dt;
            p.life -= dt;
            if (p.life <= 0 || p.y > height + 20) {
                sparks[i] = sparks[sparks.length - 1];
                sparks.pop();
            } else {
                i++;
            }
        }
    }

    function draw() {
        ctx.clearRect(0, 0, width, height);

        // Batch confetti by color to reduce fillStyle changes
        for (let ci = 0; ci < confettiColors.length; ci++) {
            let hasAny = false;
            for (let j = 0; j < confetti.length; j++) {
                if (confetti[j].ci === ci) { hasAny = true; break; }
            }
            if (!hasAny) continue;

            ctx.fillStyle = confettiColors[ci];
            for (let j = 0; j < confetti.length; j++) {
                const p = confetti[j];
                if (p.ci !== ci) continue;
                const alpha = p.life / p.maxLife;
                if (alpha <= 0.01) continue;

                ctx.globalAlpha = alpha;
                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.rot);
                ctx.fillRect(-p.w * 0.5, -p.h * 0.5, p.w, p.h);
                ctx.restore();
            }
        }

        // Sparks: trail line + core dot (2 draws instead of 3, no glow arc)
        ctx.globalCompositeOperation = 'lighter';
        for (let i = 0; i < sparks.length; i++) {
            const p = sparks[i];
            const alpha = p.life / p.maxLife;
            if (alpha <= 0.02) continue;

            ctx.globalAlpha = alpha * 0.6;
            ctx.beginPath();
            ctx.strokeStyle = 'hsl(' + p.hue + ',95%,62%)';
            ctx.lineWidth = Math.max(1, p.size * 0.7);
            ctx.moveTo(p.px, p.py);
            ctx.lineTo(p.x, p.y);
            ctx.stroke();

            ctx.globalAlpha = alpha * 0.9;
            ctx.beginPath();
            ctx.fillStyle = 'hsl(' + p.hue + ',100%,78%)';
            ctx.arc(p.x, p.y, p.size * 0.8, 0, 6.28);
            ctx.fill();
        }
        ctx.globalCompositeOperation = 'source-over';
        ctx.globalAlpha = 1;
    }

    function tick(ts) {
        if (!lastFrameTs) lastFrameTs = ts;
        const elapsed = ts - lastFrameTs;
        if (elapsed < 16) {
            animationId = window.requestAnimationFrame(tick);
            return;
        }
        lastFrameTs = ts;
        const dt = Math.min(elapsed / 1000, 0.05);
        update(dt);
        draw();

        if (performance.now() < endTime || confetti.length > 0 || sparks.length > 0) {
            animationId = window.requestAnimationFrame(tick);
        } else {
            destroy();
        }
    }

    function destroy() {
        if (fireworkTimer) window.clearInterval(fireworkTimer);
        if (animationId) window.cancelAnimationFrame(animationId);
        timeoutIds.forEach(id => window.clearTimeout(id));
        if (visibilityHandler) document.removeEventListener('visibilitychange', visibilityHandler);
        window.removeEventListener('resize', resizeCanvas);
        canvas.remove();
        cleanupCelebration = null;
    }

    cleanupCelebration = destroy;
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    visibilityHandler = () => { if (document.hidden) destroy(); };
    document.addEventListener('visibilitychange', visibilityHandler);

    // Initial bursts - reduced particle counts
    const rm = prefersReducedMotion ? 0.5 : 1;
    burstConfetti(width * 0.05, height * 0.05, Math.floor(20 * rm), 0.86, 0.7, 130, 100);
    burstConfetti(width * 0.95, height * 0.05, Math.floor(20 * rm), Math.PI - 0.86, 0.7, 130, 100);
    burstConfetti(width * 0.5, height * 0.95, Math.floor(40 * rm), -Math.PI / 2, 0.9, 200, 150);
    burstConfetti(width * 0.05, height * 0.95, Math.floor(15 * rm), -0.74, 0.6, 160, 120);
    burstConfetti(width * 0.95, height * 0.95, Math.floor(15 * rm), -(Math.PI - 0.74), 0.6, 160, 120);

    // Fireworks - fewer and less frequent
    launchFirework();
    timeoutIds.push(window.setTimeout(launchFirework, 300));
    timeoutIds.push(window.setTimeout(launchFirework, 600));
    fireworkTimer = window.setInterval(launchFirework, prefersReducedMotion ? 1200 : 800);

    animationId = window.requestAnimationFrame(tick);
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    let icon = 'info';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'alert-circle';

    toast.innerHTML = `<i data-lucide="${icon}"></i><span>${message}</span>`;
    toast.className = `toast ${type} show`;

    if (window.lucide) {
        lucide.createIcons();
    }

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 鍒囨崲姝ラ
function showStep(stepNumber) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(`step${stepNumber}`).classList.add('active');
}

// 杩斿洖姝ラ1
function backToStep1() {
    showStep(1);
    selectedTeamId = null;
}

// 姝ラ1: 楠岃瘉鍏戞崲鐮佸苟鐩存帴鍏戞崲
document.getElementById('verifyForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    const code = document.getElementById('code').value.trim();
    const verifyBtn = document.getElementById('verifyBtn');

    // 楠岃瘉
    if (!email || !code) {
        showToast('请填写完整信息', 'error');
        return;
    }

    // 淇濆瓨鍒板叏灞€鍙橀噺
    currentEmail = email;
    currentCode = code;

    // 绂佺敤鎸夐挳
    verifyBtn.disabled = true;
    verifyBtn.textContent = '正在兑换...';

    // 鐩存帴璋冪敤鍏戞崲鎺ュ彛 (team_id = null 琛ㄧず鑷姩閫夋嫨)
    await confirmRedeem(null);

    // 鎭㈠鎸夐挳鐘舵€?(濡傛灉 confirmRedeem 澶辫触骞舵樉绀轰簡閿欒涔熸病鍏崇郴锛屽洜涓虹敤鎴峰彲浠ョ偣杩斿洖閲嶈瘯)
    verifyBtn.disabled = false;
    verifyBtn.textContent = '验证兑换码';
});

// 娓叉煋Team鍒楄〃
function renderTeamsList() {
    const teamsList = document.getElementById('teamsList');
    teamsList.innerHTML = '';

    availableTeams.forEach(team => {
        const teamCard = document.createElement('div');
        teamCard.className = 'team-card';
        teamCard.onclick = () => selectTeam(team.id);

        const planBadge = team.subscription_plan === 'Plus' ? 'badge-plus' : 'badge-pro';

        teamCard.innerHTML = `
            <div class="team-name">${escapeHtml(team.team_name) || 'Team ' + team.id}</div>
            <div class="team-info">
                <div class="team-info-item">
                    <i data-lucide="users" style="width: 14px; height: 14px;"></i>
                    <span>${team.current_members}/${team.max_members} 成员</span>
                </div>
                <div class="team-info-item">
                    <span class="team-badge ${planBadge}">${escapeHtml(team.subscription_plan) || 'Plus'}</span>
                </div>
                ${team.expires_at ? `
                <div class="team-info-item">
                    <i data-lucide="calendar" style="width: 14px; height: 14px;"></i>
                    <span>到期: ${formatDate(team.expires_at)}</span>
                </div>
                ` : ''}
            </div>
        `;

        teamsList.appendChild(teamCard);
        if (window.lucide) lucide.createIcons();
    });
}

// 閫夋嫨Team
function selectTeam(teamId) {
    selectedTeamId = teamId;

    // 鏇存柊UI
    document.querySelectorAll('.team-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');

    // 绔嬪嵆纭鍏戞崲
    confirmRedeem(teamId);
}

// 鑷姩閫夋嫨Team
function autoSelectTeam() {
    if (availableTeams.length === 0) {
        showToast('没有可用的 Team', 'error');
        return;
    }

    // 鑷姩閫夋嫨绗竴涓猅eam(鍚庣浼氭寜杩囨湡鏃堕棿鎺掑簭)
    confirmRedeem(null);
}

// 纭鍏戞崲
async function confirmRedeem(teamId) {
    try {
        const response = await fetch('/redeem/confirm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: currentEmail,
                code: currentCode,
                team_id: teamId
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 鍏戞崲鎴愬姛
            showSuccessResult(data);
        } else {
            // 鍏戞崲澶辫触
            showErrorResult(data.error || '兑换失败');
        }
    } catch (error) {
        showErrorResult('网络错误，请稍后重试');
    }
}

// 鏄剧ず鎴愬姛缁撴灉
function showSuccessResult(data) {
    const resultContent = document.getElementById('resultContent');
    const teamInfo = data.team_info || {};
    const blessing = getRandomHorseYearBlessing();

    resultContent.innerHTML = `
        <div class="result-success">
            <div class="result-icon success-check-animate">
                <span class="success-halo"></span>
                <svg class="success-checkmark" viewBox="0 0 64 64" aria-hidden="true">
                    <circle class="success-circle-path" cx="32" cy="32" r="25"></circle>
                    <path class="success-check-path" d="M19 33.5L28.5 43L46 24"></path>
                </svg>
            </div>
            <div class="result-title">🧧 兑换成功!</div>
            <div class="result-blessing">🎊 ${escapeHtml(blessing)} 🎊</div>
            <div class="result-message">${escapeHtml(data.message) || '您已成功加入 Team'}</div>

            <div class="result-details">
                <div class="result-detail-item">
                    <span class="result-detail-label">🏠 Team 名称</span>
                    <span class="result-detail-value">${escapeHtml(teamInfo.team_name) || '-'}</span>
                </div>
                <div class="result-detail-item">
                    <span class="result-detail-label">📧 邮箱地址</span>
                    <span class="result-detail-value">${escapeHtml(currentEmail)}</span>
                </div>
                ${teamInfo.expires_at ? `
                <div class="result-detail-item">
                    <span class="result-detail-label">📅 到期时间</span>
                    <span class="result-detail-value">${formatDate(teamInfo.expires_at)}</span>
                </div>
                ` : ''}
            </div>

            <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 2rem; background: rgba(188,31,31,0.04); padding: 1rem; border-radius: 8px; border: 1px solid rgba(188,31,31,0.1);">
                ✉️ 邀请邮件已发送到您的邮箱，请查收并按照邮件指引接受邀请。</p>

            <button onclick="location.reload()" class="btn btn-primary">
                <i data-lucide="refresh-cw"></i> 🧧 再次兑换
            </button>
        </div>
    `;
    if (window.lucide) lucide.createIcons();
    window.requestAnimationFrame(() => animateSuccessCheck());

    showStep(3);
    playCelebration(12000);
    // 额外的新年飘落特效
    playNewYearOverlay(8000);
}

// 鏄剧ず閿欒缁撴灉
function showErrorResult(errorMessage) {
    const resultContent = document.getElementById('resultContent');

    resultContent.innerHTML = `
        <div class="result-error">
            <div class="result-icon"><i data-lucide="x-circle" style="width: 64px; height: 64px; color: var(--danger);"></i></div>
            <div class="result-title">兑换失败</div>
            <div class="result-message">${escapeHtml(errorMessage)}</div>

            <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 2rem;">
                <button onclick="backToStep1()" class="btn btn-secondary">
                    <i data-lucide="arrow-left"></i> 返回重试
                </button>
                <button onclick="location.reload()" class="btn btn-primary">
                    <i data-lucide="rotate-ccw"></i> 重新开始</button>
            </div>
        </div>
    `;
    if (window.lucide) lucide.createIcons();

    showStep(3);
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';

    try {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    } catch (e) {
        return dateString;
    }
}

/**
 * Physics-based falling particle engine.
 * Each particle has: gravity, mass, air drag, 3D tumble (rotateX/Y/Z),
 * lateral drift coupled to tumble, random initial velocity.
 * Driven by requestAnimationFrame for 60fps smoothness.
 */
const PhysicsFall = (() => {
    const G = 120;          // gravity (px/s^2) — softer than real
    const instances = [];

    function createParticle(container, char, opts = {}) {
        const W = container.clientWidth || window.innerWidth;
        const H = container.clientHeight || window.innerHeight;
        const el = document.createElement('span');
        el.className = 'phys-particle';
        el.textContent = char;
        el.style.fontSize = (opts.size || 18) + 'px';
        if (opts.color) el.style.color = opts.color;
        if (opts.textShadow) el.style.textShadow = opts.textShadow;
        if (opts.fontFamily) el.style.fontFamily = opts.fontFamily;
        if (opts.fontWeight) el.style.fontWeight = opts.fontWeight;
        el.style.opacity = '0';
        container.appendChild(el);

        // Random physics properties per particle
        const mass = 0.5 + Math.random() * 1.5;            // 0.5~2.0 — lighter = more floaty
        const dragCoeff = 0.015 + Math.random() * 0.025;   // air resistance — bigger = slower terminal velocity
        const crossSection = (opts.size || 18) * 0.06;     // larger char = more drag

        return {
            el,
            // Position
            x: opts.x !== undefined ? opts.x : (Math.random() * (W - 30) + 15),
            y: opts.y !== undefined ? opts.y : -(20 + Math.random() * 60),
            // Velocity
            vx: opts.vx !== undefined ? opts.vx : (Math.random() - 0.5) * 30,
            vy: opts.vy !== undefined ? opts.vy : (Math.random() * 15),
            // Physics
            mass,
            drag: dragCoeff,
            cross: crossSection,
            // 3D tumble angles (radians)
            rx: Math.random() * 6.28,
            ry: Math.random() * 6.28,
            rz: Math.random() * 6.28,
            // Tumble angular velocities (rad/s) — random per particle
            wrx: (Math.random() - 0.5) * 3.5,
            wry: (Math.random() - 0.5) * 4.0,
            wrz: (Math.random() - 0.5) * 2.0,
            // Tumble → lateral coupling (how much tumble pushes sideways)
            tumbleCoupling: 8 + Math.random() * 20,
            // Alpha
            opacity: opts.opacity !== undefined ? opts.opacity : (0.3 + Math.random() * 0.5),
            fadeIn: true,
            // Bounds
            maxY: H + 80,
            W,
        };
    }

    function stepParticle(p, dt) {
        // Gravity
        const gForce = G * p.mass;

        // Air drag (velocity-dependent, quadratic-ish)
        const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy) + 0.01;
        const dragMag = p.drag * p.cross * speed;
        const dragX = -p.vx / speed * dragMag;
        const dragY = -p.vy / speed * dragMag;

        // Tumble-induced lateral force: the tumbling creates asymmetric air resistance
        // This gives each particle a unique, non-sinusoidal sideways drift
        const tumbleLateral = Math.sin(p.rx) * Math.cos(p.ry * 0.7) * p.tumbleCoupling;

        // Apply forces  (F = ma → a = F/m)
        const ax = (dragX + tumbleLateral) / p.mass;
        const ay = (gForce + dragY) / p.mass;

        p.vx += ax * dt;
        p.vy += ay * dt;

        // Terminal velocity clamp
        p.vy = Math.min(p.vy, 200);

        p.x += p.vx * dt;
        p.y += p.vy * dt;

        // Update tumble
        p.rx += p.wrx * dt;
        p.ry += p.wry * dt;
        p.rz += p.wrz * dt;

        // Slight tumble damping (air friction on rotation)
        p.wrx *= (1 - 0.1 * dt);
        p.wry *= (1 - 0.1 * dt);
        p.wrz *= (1 - 0.08 * dt);

        // Add tiny random torque impulses for chaos
        if (Math.random() < 0.02) {
            p.wrx += (Math.random() - 0.5) * 1.2;
            p.wry += (Math.random() - 0.5) * 1.2;
        }

        // Wrap horizontally
        if (p.x < -30) p.x = p.W + 20;
        if (p.x > p.W + 30) p.x = -20;

        // Fade in
        let alpha = p.opacity;
        if (p.fadeIn && p.y > 0) p.fadeIn = false;
        if (p.fadeIn) alpha *= Math.max(0, 1 - Math.abs(p.y) / 60);
        // Fade out near bottom
        if (p.y > p.maxY - 120) alpha *= Math.max(0, (p.maxY - p.y) / 120);

        // Apply transform
        p.el.style.opacity = alpha.toFixed(3);
        p.el.style.transform =
            'translate3d(' + p.x.toFixed(1) + 'px,' + p.y.toFixed(1) + 'px,0)' +
            ' rotateX(' + (p.rx * 57.3).toFixed(1) + 'deg)' +
            ' rotateY(' + (p.ry * 57.3).toFixed(1) + 'deg)' +
            ' rotateZ(' + (p.rz * 57.3).toFixed(1) + 'deg)';
    }

    function resetParticle(p) {
        p.y = -(20 + Math.random() * 60);
        p.x = Math.random() * p.W;
        p.vx = (Math.random() - 0.5) * 30;
        p.vy = Math.random() * 10;
        p.wrx = (Math.random() - 0.5) * 3.5;
        p.wry = (Math.random() - 0.5) * 4.0;
        p.wrz = (Math.random() - 0.5) * 2.0;
        p.fadeIn = true;
    }

    /**
     * Start a continuous physics falling loop (for background blossoms).
     * Particles recycle when they fall off screen.
     */
    function startLoop(container, chars, count, sizeRange, opacityRange) {
        const particles = [];
        for (let i = 0; i < count; i++) {
            const char = chars[Math.floor(Math.random() * chars.length)];
            const size = sizeRange[0] + Math.random() * (sizeRange[1] - sizeRange[0]);
            const opacity = opacityRange[0] + Math.random() * (opacityRange[1] - opacityRange[0]);
            const p = createParticle(container, char, {
                size,
                opacity,
                y: -(Math.random() * (container.clientHeight || window.innerHeight) + 40), // stagger start
            });
            // Start scattered across screen height for continuous look
            p.y = Math.random() * (p.maxY + 60) - 60;
            particles.push(p);
        }

        let lastTs = 0;
        let rafId = 0;

        function tick(ts) {
            if (!lastTs) lastTs = ts;
            const dt = Math.min((ts - lastTs) / 1000, 0.05);
            lastTs = ts;

            for (let i = 0; i < particles.length; i++) {
                stepParticle(particles[i], dt);
                if (particles[i].y > particles[i].maxY) {
                    resetParticle(particles[i]);
                }
            }
            rafId = requestAnimationFrame(tick);
        }

        rafId = requestAnimationFrame(tick);
        const inst = { stop: () => cancelAnimationFrame(rafId), particles };
        instances.push(inst);
        return inst;
    }

    /**
     * Start a timed physics falling burst (for success overlay).
     * Spawns in waves, particles are removed after falling off screen.
     */
    function startBurst(container, chars, opts = {}) {
        const totalWaves = opts.waves || 5;
        const perWave = opts.perWave || 6;
        const waveInterval = opts.waveInterval || 1200;
        const durationMs = opts.duration || 8000;
        const particles = [];
        let waveCount = 0;
        let lastTs = 0;
        let rafId = 0;
        const timers = [];

        function spawnWave() {
            if (waveCount >= totalWaves) return;
            waveCount++;
            const W = container.clientWidth || window.innerWidth;
            for (let i = 0; i < perWave; i++) {
                const char = chars[Math.floor(Math.random() * chars.length)];
                const size = 22 + Math.random() * 18;
                const pOpts = { size, opacity: 0.7 + Math.random() * 0.3 };
                // Start from random X at top
                pOpts.x = 10 + Math.random() * (W - 40);
                pOpts.y = -(10 + Math.random() * 50);
                pOpts.vx = (Math.random() - 0.5) * 40;
                pOpts.vy = 5 + Math.random() * 20;

                if (char === '福') {
                    pOpts.color = '#e8a517';
                    pOpts.textShadow = '0 0 10px rgba(244,180,61,0.5), 0 0 20px rgba(244,180,61,0.2)';
                    pOpts.fontFamily = "'Ma Shan Zheng', serif";
                    pOpts.fontWeight = '900';
                }

                particles.push(createParticle(container, char, pOpts));
            }
        }

        function tick(ts) {
            if (!lastTs) lastTs = ts;
            const dt = Math.min((ts - lastTs) / 1000, 0.05);
            lastTs = ts;

            let i = 0;
            while (i < particles.length) {
                stepParticle(particles[i], dt);
                if (particles[i].y > particles[i].maxY + 40) {
                    particles[i].el.remove();
                    particles[i] = particles[particles.length - 1];
                    particles.pop();
                } else {
                    i++;
                }
            }

            if (particles.length > 0 || waveCount < totalWaves) {
                rafId = requestAnimationFrame(tick);
            }
        }

        // Spawn first wave immediately, rest on timers
        spawnWave();
        for (let w = 1; w < totalWaves; w++) {
            timers.push(setTimeout(() => {
                spawnWave();
                // Restart rAF if it stopped
                if (!rafId) rafId = requestAnimationFrame(tick);
            }, w * waveInterval));
        }

        rafId = requestAnimationFrame(tick);

        // Cleanup after duration
        const cleanupTimer = setTimeout(() => {
            cancelAnimationFrame(rafId);
            particles.forEach(p => p.el.remove());
            particles.length = 0;
            container.remove();
        }, durationMs + 5000);
        timers.push(cleanupTimer);

        return {
            stop: () => {
                cancelAnimationFrame(rafId);
                timers.forEach(t => clearTimeout(t));
                particles.forEach(p => p.el.remove());
                container.remove();
            }
        };
    }

    return { createParticle, stepParticle, resetParticle, startLoop, startBurst };
})();

/**
 * Background blossom falling — physics driven, continuous loop.
 */
function startPhysicsBlossoms() {
    const container = document.getElementById('fallingBlossoms');
    if (!container) return;
    const chars = ['🌸', '✿', '❀', '🏵', '💮', '🌺', '🧧', '福'];
    const count = Math.min(22, Math.max(10, Math.floor(window.innerWidth / 95)));
    PhysicsFall.startLoop(container, chars, count, [16, 34], [0.58, 0.95]);
}

/**
 * New Year overlay — physics-driven burst on success.
 */
function playNewYearOverlay(durationMs = 8000) {
    if (typeof document === 'undefined' || !document.body) return;

    const overlay = document.createElement('div');
    overlay.setAttribute('aria-hidden', 'true');
    overlay.className = 'falling-blossoms'; // reuse the same styles (fixed, overflow:hidden, perspective)
    overlay.style.zIndex = '9998';
    document.body.appendChild(overlay);

    const nyChars = ['🧧', '福', '✨', '🏮', '🎊', '💰', '🐴', '🎉', '🧨', '🎆'];
    const perWave = Math.min(8, Math.max(4, Math.floor(window.innerWidth / 120)));

    PhysicsFall.startBurst(overlay, nyChars, {
        waves: 5,
        perWave,
        waveInterval: 1200,
        duration: durationMs
    });
}


/* ============ Warranty (质保) Tab & Logic ============ */

function switchTab(tab) {
    const redeemSteps = ['step1', 'step2', 'step3'];
    const warrantyPanel = document.getElementById('warrantyPanel');
    const tabRedeem = document.getElementById('tab-redeem');
    const tabWarranty = document.getElementById('tab-warranty');
    const tabSlider = document.getElementById('tabSlider');

    if (tab === 'warranty') {
        redeemSteps.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });
        if (warrantyPanel) warrantyPanel.style.display = 'block';
        tabRedeem.classList.remove('active');
        tabWarranty.classList.add('active');
        updateTabSlider(tabWarranty, tabSlider);
    } else {
        if (warrantyPanel) warrantyPanel.style.display = 'none';
        redeemSteps.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = '';
        });
        showStep(1);
        tabRedeem.classList.add('active');
        tabWarranty.classList.remove('active');
        updateTabSlider(tabRedeem, tabSlider);
    }
    if (window.lucide) lucide.createIcons();
}

// 初始化 tab 滑块位置
window.addEventListener('load', () => {
    const activeBtn = document.querySelector('.tab-btn.active');
    updateTabSlider(activeBtn);
});

function updateTabSlider(targetBtn, sliderEl, animate = true) {
    const slider = sliderEl || document.getElementById('tabSlider');
    if (!slider || !targetBtn) return;
    const parent = targetBtn.parentElement;
    if (!parent) return;
    const parentRect = parent.getBoundingClientRect();
    const rect = targetBtn.getBoundingClientRect();
    const apply = () => {
        slider.style.width = rect.width + 'px';
        slider.style.transform = 'translateX(' + (rect.left - parentRect.left) + 'px)';
    };
    if (!animate) {
        const prevTransition = slider.style.transition;
        slider.style.transition = 'none';
        apply();
        void slider.offsetWidth;
        requestAnimationFrame(() => { slider.style.transition = prevTransition || ''; });
    } else {
        apply();
    }
}

window.addEventListener('resize', () => {
    const activeBtn = document.querySelector('.tab-btn.active');
        updateTabSlider(activeBtn, null, false);
});

/* Warranty Query Form */
(function initWarrantyForm() {
    const form = document.getElementById('warrantyForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const code = document.getElementById('warrantyCode').value.trim();
        const btn = document.getElementById('warrantyQueryBtn');
        const resultDiv = document.getElementById('warrantyResult');

        if (!code) { showToast('请输入兑换码', 'error'); return; }

        btn.disabled = true;
        btn.innerHTML = '<i data-lucide="loader" class="spin"></i> 查询中...';
        if (window.lucide) lucide.createIcons();

        try {
            const res = await fetch('/redeem/warranty/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: '查询失败' }));
                resultDiv.innerHTML = renderWarrantyError(err.detail || '查询失败');
            } else {
                const data = await res.json();
                resultDiv.innerHTML = renderWarrantyInfo(data.warranty_info, code);
            }
        } catch (err) {
            resultDiv.innerHTML = renderWarrantyError('网络错误，请稍后重试');
        }

        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="search"></i> 查询质保状态';
        if (window.lucide) lucide.createIcons();
    });
})();

function renderWarrantyError(msg) {
    return '<div style="padding:1rem;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.18);border-radius:10px;color:#dc2626;font-size:0.92rem;">' +
           '<i data-lucide="alert-circle" style="width:16px;height:16px;vertical-align:middle;margin-right:6px;"></i>' +
           escapeHtml(msg) + '</div>';
}

function renderWarrantyInfo(info, code) {
    const remaining = info.remaining_days;
    let badgeCls = 'wi-badge-ok';
    let badgeText = remaining + ' 天';
    if (remaining <= 7) { badgeCls = 'wi-badge-danger'; badgeText = remaining + ' 天 (即将到期)'; }
    else if (remaining <= 14) { badgeCls = 'wi-badge-warn'; badgeText = remaining + ' 天'; }

    let html = '<div class="warranty-info-card">';
    html += '<div class="wi-row"><span class="wi-label">兑换码</span><span class="wi-value">' + escapeHtml(info.code) + '</span></div>';
    html += '<div class="wi-row"><span class="wi-label">状态</span><span class="wi-value"><span class="wi-badge wi-badge-ok">质保中</span></span></div>';
    html += '<div class="wi-row"><span class="wi-label">使用邮箱</span><span class="wi-value">' + escapeHtml(info.used_by_email || '-') + '</span></div>';
    html += '<div class="wi-row"><span class="wi-label">使用时间</span><span class="wi-value">' + escapeHtml(info.used_at) + '</span></div>';
    html += '<div class="wi-row"><span class="wi-label">质保截止</span><span class="wi-value">' + escapeHtml(info.warranty_deadline) + '</span></div>';
    html += '<div class="wi-row"><span class="wi-label">剩余质保</span><span class="wi-value"><span class="wi-badge ' + badgeCls + '">' + badgeText + '</span></span></div>';
    html += '<div class="wi-row"><span class="wi-label">已质保次数</span><span class="wi-value">' + (info.warranty_redeem_count || 0) + ' 次</span></div>';
    html += '</div>';

    // Records
    if (info.records && info.records.length) {
        html += '<div class="warranty-records"><h4>📋 使用记录</h4>';
        info.records.forEach(function(r) {
            html += '<div class="wr-item">';
            if (r.is_warranty_redeem) html += '<span class="wr-tag">质保</span>';
            else html += '<span class="wr-tag" style="background:rgba(34,197,94,0.1);color:#16a34a;">首次</span>';
            html += '<span>' + escapeHtml(r.email) + '</span>';
            html += '<span style="margin-left:auto;color:#999;font-size:0.8rem;">' + escapeHtml(r.redeemed_at || '') + '</span>';
            html += '</div>';
        });
        html += '</div>';
    }

    // Warranty redeem button
    if (info.can_warranty_redeem) {
        html += '<div style="margin-top:1.2rem;">';
        html += '<p style="font-size:0.85rem;color:#666;margin-bottom:0.8rem;">如需重新加入 Team，请输入邮箱后点击下方按钮：</p>';
        html += '<div class="form-group" style="margin-bottom:0.8rem;">';
        html += '<input type="email" id="warrantyEmail" placeholder="请输入邮箱地址" class="form-input" required>';
        html += '</div>';
        html += '<button onclick="doWarrantyRedeem(\'' + escapeHtml(code) + '\')" class="btn btn-primary" id="warrantyRedeemBtn" style="width:100%;">';
        html += '<i data-lucide="refresh-cw"></i> 质保重新兑换</button>';
        html += '</div>';
    }

    if (window.lucide) setTimeout(function() { lucide.createIcons(); }, 0);
    return html;
}

async function doWarrantyRedeem(code) {
    const emailInput = document.getElementById('warrantyEmail');
    const btn = document.getElementById('warrantyRedeemBtn');
    const resultDiv = document.getElementById('warrantyResult');

    if (!emailInput || !emailInput.value.trim()) {
        showToast('请输入邮箱地址', 'error');
        return;
    }
    const email = emailInput.value.trim();

    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader" class="spin"></i> 正在兑换...';
    if (window.lucide) lucide.createIcons();

    try {
        const res = await fetch('/redeem/warranty/redeem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: '兑换失败' }));
            showToast(err.detail || '质保兑换失败', 'error');
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="refresh-cw"></i> 质保重新兑换';
            if (window.lucide) lucide.createIcons();
            return;
        }

        const data = await res.json();
        showToast(data.message || '质保兑换成功！', 'success');

        resultDiv.innerHTML =
            '<div style="padding:1.2rem;background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.18);border-radius:10px;text-align:center;">' +
            '<div style="font-size:2rem;margin-bottom:0.5rem;">🎉</div>' +
            '<div style="font-weight:600;color:#16a34a;font-size:1.05rem;margin-bottom:0.4rem;">' + escapeHtml(data.message) + '</div>' +
            '<div style="font-size:0.85rem;color:#666;">第 ' + (data.warranty_count || '?') + ' 次质保兑换 · 请查收邮箱邀请</div>' +
            '</div>';

        // Celebration effects
        if (typeof playCelebration === 'function') playCelebration();
        if (typeof playNewYearOverlay === 'function') playNewYearOverlay();

    } catch (err) {
        showToast('网络错误，请稍后重试', 'error');
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="refresh-cw"></i> 质保重新兑换';
        if (window.lucide) lucide.createIcons();
    }
}
