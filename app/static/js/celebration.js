/**
 * Shared celebration animations: confetti, fireworks, physics falling, new year overlay.
 * Used by redeem page and free spot page on success.
 */

let cleanupCelebration = null;

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
    const maxConfetti = prefersReducedMotion ? 40 : 80;
    const maxSparks = prefersReducedMotion ? 30 : 60;
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

    const rm = prefersReducedMotion ? 0.5 : 1;
    burstConfetti(width * 0.05, height * 0.05, Math.floor(20 * rm), 0.86, 0.7, 130, 100);
    burstConfetti(width * 0.95, height * 0.05, Math.floor(20 * rm), Math.PI - 0.86, 0.7, 130, 100);
    burstConfetti(width * 0.5, height * 0.95, Math.floor(40 * rm), -Math.PI / 2, 0.9, 200, 150);
    burstConfetti(width * 0.05, height * 0.95, Math.floor(15 * rm), -0.74, 0.6, 160, 120);
    burstConfetti(width * 0.95, height * 0.95, Math.floor(15 * rm), -(Math.PI - 0.74), 0.6, 160, 120);

    launchFirework();
    timeoutIds.push(window.setTimeout(launchFirework, 300));
    timeoutIds.push(window.setTimeout(launchFirework, 600));
    fireworkTimer = window.setInterval(launchFirework, prefersReducedMotion ? 1500 : 1000);

    animationId = window.requestAnimationFrame(tick);
}

/**
 * Physics-based falling particle engine.
 */
const PhysicsFall = (() => {
    const G = 120;
    const instances = [];

    function createParticle(container, char, opts = {}) {
        const W = container.clientWidth || window.innerWidth;
        const H = container.clientHeight || window.innerHeight;
        const el = document.createElement('span');
        el.className = 'phys-particle';
        el.textContent = char;
        el.style.fontSize = (opts.size || 18) + 'px';
        el.style.contain = 'layout style';
        if (opts.color) el.style.color = opts.color;
        if (opts.textShadow) el.style.textShadow = opts.textShadow;
        if (opts.fontFamily) el.style.fontFamily = opts.fontFamily;
        if (opts.fontWeight) el.style.fontWeight = opts.fontWeight;
        el.style.opacity = '0';
        container.appendChild(el);

        const mass = 0.5 + Math.random() * 1.5;
        const dragCoeff = 0.015 + Math.random() * 0.025;
        const crossSection = (opts.size || 18) * 0.06;

        return {
            el,
            x: opts.x !== undefined ? opts.x : (Math.random() * (W - 30) + 15),
            y: opts.y !== undefined ? opts.y : -(20 + Math.random() * 60),
            vx: opts.vx !== undefined ? opts.vx : (Math.random() - 0.5) * 30,
            vy: opts.vy !== undefined ? opts.vy : (Math.random() * 15),
            mass,
            drag: dragCoeff,
            cross: crossSection,
            rx: Math.random() * 6.28,
            ry: Math.random() * 6.28,
            rz: Math.random() * 6.28,
            wrx: (Math.random() - 0.5) * 3.5,
            wry: (Math.random() - 0.5) * 4.0,
            wrz: (Math.random() - 0.5) * 2.0,
            tumbleCoupling: 8 + Math.random() * 20,
            opacity: opts.opacity !== undefined ? opts.opacity : (0.3 + Math.random() * 0.5),
            fadeIn: true,
            maxY: H + 80,
            W,
        };
    }

    function stepParticle(p, dt) {
        const gForce = G * p.mass;
        const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy) + 0.01;
        const dragMag = p.drag * p.cross * speed;
        const dragX = -p.vx / speed * dragMag;
        const dragY = -p.vy / speed * dragMag;
        const tumbleLateral = Math.sin(p.rx) * Math.cos(p.ry * 0.7) * p.tumbleCoupling;

        const ax = (dragX + tumbleLateral) / p.mass;
        const ay = (gForce + dragY) / p.mass;

        p.vx += ax * dt;
        p.vy += ay * dt;
        p.vy = Math.min(p.vy, 200);

        p.x += p.vx * dt;
        p.y += p.vy * dt;

        p.rx += p.wrx * dt;
        p.ry += p.wry * dt;
        p.rz += p.wrz * dt;

        p.wrx *= (1 - 0.1 * dt);
        p.wry *= (1 - 0.1 * dt);
        p.wrz *= (1 - 0.08 * dt);

        if (Math.random() < 0.02) {
            p.wrx += (Math.random() - 0.5) * 1.2;
            p.wry += (Math.random() - 0.5) * 1.2;
        }

        if (p.x < -30) p.x = p.W + 20;
        if (p.x > p.W + 30) p.x = -20;

        let alpha = p.opacity;
        if (p.fadeIn && p.y > 0) p.fadeIn = false;
        if (p.fadeIn) alpha *= Math.max(0, 1 - Math.abs(p.y) / 60);
        if (p.y > p.maxY - 120) alpha *= Math.max(0, (p.maxY - p.y) / 120);

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

    function startLoop(container, chars, count, sizeRange, opacityRange) {
        const particles = [];
        for (let i = 0; i < count; i++) {
            const char = chars[Math.floor(Math.random() * chars.length)];
            const size = sizeRange[0] + Math.random() * (sizeRange[1] - sizeRange[0]);
            const opacity = opacityRange[0] + Math.random() * (opacityRange[1] - opacityRange[0]);
            const p = createParticle(container, char, {
                size,
                opacity,
                y: -(Math.random() * (container.clientHeight || window.innerHeight) + 40),
            });
            p.y = Math.random() * (p.maxY + 60) - 60;
            particles.push(p);
        }

        let lastTs = 0;
        let rafId = 0;

        function tick(ts) {
            if (!lastTs) { lastTs = ts; }
            const elapsed = ts - lastTs;
            if (elapsed < 33) { rafId = requestAnimationFrame(tick); return; }
            const dt = Math.min(elapsed / 1000, 0.05);
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

        spawnWave();
        for (let w = 1; w < totalWaves; w++) {
            timers.push(setTimeout(() => {
                spawnWave();
                if (!rafId) rafId = requestAnimationFrame(tick);
            }, w * waveInterval));
        }

        rafId = requestAnimationFrame(tick);

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
    const chars = ['🌸', '✿', '❀', '🏵', '💮', '🌺'];
    const count = Math.min(8, Math.max(4, Math.floor(window.innerWidth / 200)));
    PhysicsFall.startLoop(container, chars, count, [12, 26], [0.2, 0.55]);
}

/**
 * New Year overlay — physics-driven burst on success.
 */
function playNewYearOverlay(durationMs = 8000) {
    if (typeof document === 'undefined' || !document.body) return;

    const overlay = document.createElement('div');
    overlay.setAttribute('aria-hidden', 'true');
    overlay.className = 'falling-blossoms';
    overlay.style.zIndex = '9998';
    document.body.appendChild(overlay);

    const nyChars = ['福', '✨', '🏮', '🎊', '💰', '🐴', '🎉', '🎆', '🧧', '⭐'];
    const perWave = Math.min(8, Math.max(4, Math.floor(window.innerWidth / 120)));

    PhysicsFall.startBurst(overlay, nyChars, {
        waves: 5,
        perWave,
        waveInterval: 1200,
        duration: durationMs
    });
}

/**
 * Couplet rotation — auto-flip couplets with different content sets.
 */
function initCoupletRotation() {
    var coupletSets = [
        { left: '天增岁月人增寿', right: '春满乾坤福满门', cross: '恭贺新春' },
        { left: '爆竹声中辞旧岁', right: '梅花香里报新春', cross: '万象更新' },
        { left: '春回大地千山秀', right: '日暖神州万物荣', cross: '春意盎然' },
        { left: '一帆风顺年年好', right: '万事如意步步高', cross: '吉星高照' },
        { left: '喜居宝地千年旺', right: '福照家门万事兴', cross: '喜迎新春' },
        { left: '龙马精神歌盛世', right: '凤鸾祥瑞贺新年', cross: '龙凤呈祥' },
        { left: '花开富贵家家乐', right: '灯照吉祥岁岁安', cross: '花好月圆' },
        { left: '财源广进添百福', right: '吉庆有余纳千祥', cross: '招财进宝' },
        { left: '和顺满门添百福', right: '平安二字值千金', cross: '家和万事兴' },
        { left: '迎喜迎春迎富贵', right: '接财接福接平安', cross: '迎春接福' },
        { left: '红梅含苞傲冬雪', right: '绿柳吐絮迎新春', cross: '辞旧迎新' },
        { left: '天赐阳光照前路', right: '地生万物迎春来', cross: '紫气东来' },
        { left: '年丰人寿家家乐', right: '国泰民安处处春', cross: '国泰民安' },
        { left: '张灯结彩迎新春', right: '欢天喜地度佳节', cross: '普天同庆' }
    ];
    var idx = 0;
    var leftWrap = document.querySelector('.couplet-wrapper.couplet-left');
    var rightWrap = document.querySelector('.couplet-wrapper.couplet-right');
    var crossWrap = document.querySelector('.crossbeam-wrapper');
    if (!leftWrap || !rightWrap || !crossWrap) return;

    var leftFront = leftWrap.querySelector('.couplet-front');
    var leftBack = leftWrap.querySelector('.couplet-back');
    var rightFront = rightWrap.querySelector('.couplet-front');
    var rightBack = rightWrap.querySelector('.couplet-back');
    var crossFront = crossWrap.querySelector('.crossbeam-front');
    var crossBack = crossWrap.querySelector('.crossbeam-back');

    setInterval(function() {
        var nextIdx = (idx + 1) % coupletSets.length;
        var nextSet = coupletSets[nextIdx];
        var isFlipped = leftWrap.classList.contains('flipped');

        if (isFlipped) {
            leftFront.textContent = nextSet.left;
            rightFront.textContent = nextSet.right;
            crossFront.textContent = nextSet.cross;
            leftWrap.classList.remove('flipped');
            rightWrap.classList.remove('flipped');
            crossWrap.classList.remove('flipped');
        } else {
            leftBack.textContent = nextSet.left;
            rightBack.textContent = nextSet.right;
            crossBack.textContent = nextSet.cross;
            leftWrap.classList.add('flipped');
            rightWrap.classList.add('flipped');
            crossWrap.classList.add('flipped');
        }
        idx = nextIdx;
    }, 6000);
}
