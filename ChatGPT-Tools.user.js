// ==UserScript==
// @name         ChatGPT Tools
// @namespace    https://linux.do/u/npc1
// @version      9.4
// @description  ChatGPT 工具箱 - Token 获取、Plus 支付链接、全自动注册、账号管理与对话导出
// @author       npc1
// @match        https://chatgpt.com/*
// @match        https://*.chatgpt.com/*
// @match        https://chat.openai.com/*
// @match        https://auth.openai.com/*
// @match        https://auth0.openai.com/*
// @match        https://pay.openai.com/*
// @icon         data:image/png;base64,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
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// @grant        GM_xmlhttpRequest
// @grant        GM_setClipboard
// @grant        GM_addStyle
// @grant        GM_addElement
// @grant        GM_cookie
// @grant        unsafeWindow
// @connect      dash.xphdfs.me
// @connect      tempmail.plus
// @connect      *
// @run-at       document-idle
// @license      MIT
// ==/UserScript==

(function () {
    'use strict';
    const _0xb = s => atob(s);
    const _0x8d = ['tm-app-root', 'npcmail_api_key', 'registered_accounts', 'auto_reg_data', 'auto_reg_step', 'tm_auto_redirect_team'];
    const _0xg = i => _0x8d[i];
    const _0x3c = _0xb('aHR0cHM6Ly9kYXNoLnhwaGRmcy5tZQ==');
    const _0x4e = { API_KEY: _0xg(0x1), ACCOUNTS: _0xg(0x2), AUTO_REG: _0xg(0x3), AUTO_REG_STEP: _0xg(0x4), AUTO_REDIRECT_TEAM: _0xg(0x5) };
    const _0x_TM_API = 'https://tempmail.plus/api';
    const _0x_TM_DOMAINS = ['mailto.plus', 'fexpost.com', 'fexbox.org', 'mailbox.in.ua', 'rover.info', 'chitthi.in', 'fextemp.com', 'any.pink', 'merepost.com'];
    const _0x5f = { IDLE: 'idle', GOTO_SIGNUP: 'goto_signup', FILL_EMAIL: 'fill_email', FILL_PASSWORD: 'fill_password', WAIT_CODE: 'wait_code', FILL_CODE: 'fill_code', FILL_PROFILE: 'fill_profile', COMPLETE: 'complete' };

    /* ═══════════════ 对话导出 - 页面上下文执行（绕过沙箱 Promise 互操作问题） ═══════════════ */
    const _EXP = (function () {
        const W = (typeof unsafeWindow !== 'undefined') ? unsafeWindow : window;
        let _jsZipReady = false;

        // 通过 GM_addElement 在页面上下文加载 JSZip（绕过 CSP）
        function _loadJSZip() {
            return new Promise((resolve) => {
                if (W.JSZip) { _jsZipReady = true; resolve(); return; }
                try {
                    GM_addElement('script', {
                        src: 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js',
                        type: 'text/javascript'
                    });
                } catch (e) {
                    console.warn('[Exporter] GM_addElement failed, trying direct injection:', e);
                    const s = document.createElement('script');
                    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
                    document.head.appendChild(s);
                }
                // 轮询等待 JSZip 在页面上下文中可用
                const t = setInterval(() => {
                    if (W.JSZip) { clearInterval(t); _jsZipReady = true; resolve(); }
                }, 100);
                setTimeout(() => { clearInterval(t); resolve(); }, 15000); // 15s 超时
            });
        }

        // 预加载 JSZip
        _loadJSZip();

        // 在页面上下文注入导出核心逻辑
        // 这样所有 fetch、Promise、JSZip 都在同一个原生上下文中运行，不会有互操作问题
        function _injectPageExporter() {
            if (W.__expPageReady) return;
            W.__expPageReady = true;

            // 网络拦截：捕获 Token 和 Workspace ID（在页面上下文中运行）
            W.__expAccessToken = null;
            W.__expCapturedWsIds = W.__expCapturedWsIds || new Set();

            const rawFetch = W.fetch;
            W.fetch = function (resource, options) {
                try {
                    const headers = options && options.headers;
                    if (headers) {
                        // 捕获 Token
                        let auth = null;
                        if (typeof headers === 'object' && !(headers instanceof W.Headers)) {
                            auth = headers.Authorization || headers.authorization;
                        } else if (headers instanceof W.Headers) {
                            auth = headers.get('Authorization');
                        }
                        if (auth && typeof auth === 'string' && auth.startsWith('Bearer ')) {
                            const tk = auth.slice(7);
                            if (tk && tk.toLowerCase() !== 'dummy') W.__expAccessToken = tk;
                        }
                        // 捕获 Workspace ID
                        var wsId = (typeof headers === 'object' && !(headers instanceof W.Headers)) ? headers['ChatGPT-Account-Id'] : null;
                        if (wsId) W.__expCapturedWsIds.add(wsId);
                    }
                } catch (_) { }
                return rawFetch.apply(this, arguments);
            };

            const rawXhrOpen = W.XMLHttpRequest.prototype.open;
            W.XMLHttpRequest.prototype.open = function () {
                this.addEventListener('readystatechange', function () {
                    if (this.readyState === 4) {
                        try {
                            var a = this.getRequestHeader('Authorization');
                            if (a && a.startsWith('Bearer ')) {
                                var tk = a.slice(7);
                                if (tk && tk.toLowerCase() !== 'dummy') W.__expAccessToken = tk;
                            }
                            var wid = this.getRequestHeader('ChatGPT-Account-Id');
                            if (wid) W.__expCapturedWsIds.add(wid);
                        } catch (_) { }
                    }
                });
                return rawXhrOpen.apply(this, arguments);
            };
        }

        _injectPageExporter();

        // === 以下辅助函数在沙箱中运行，但最终的 ZIP 生成在页面上下文 ===
        const BASE_DELAY = 600, JITTER_RANGE = 400, PAGE_LIMIT = 100;

        function _getToken() { return W.__expAccessToken; }

        async function ensureAccessToken() {
            if (_getToken()) return _getToken();
            try {
                const r = await W.fetch('/api/auth/session?unstable_client=true');
                const session = await r.json();
                if (session.accessToken) { W.__expAccessToken = session.accessToken; return session.accessToken; }
            } catch (_) { }
            return null;
        }

        const sleep = ms => new Promise(r => setTimeout(r, ms));
        const jitter = () => BASE_DELAY + Math.random() * JITTER_RANGE;
        const sanitize = name => name.replace(/[\/\\?%*:|"|<>]/g, '-').trim();

        function getOaiDeviceId() {
            const m = document.cookie.match(/oai-did=([^;]+)/);
            return m ? m[1] : null;
        }

        function genFilename(convData) {
            const shortId = convData.conversation_id.split('-').pop();
            let baseName = convData.title;
            if (!baseName || baseName.trim().toLowerCase() === 'new chat') baseName = 'Untitled';
            return sanitize(baseName) + '_' + shortId + '.json';
        }

        function downloadFile(blob, filename) {
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(a.href);
        }

        async function _apiFetch(url, workspaceId) {
            const token = _getToken();
            const deviceId = getOaiDeviceId();
            if (!deviceId) throw new Error('无法获取 oai-device-id');
            const headers = { 'Authorization': 'Bearer ' + token, 'oai-device-id': deviceId };
            if (workspaceId) headers['ChatGPT-Account-Id'] = workspaceId;
            const r = await W.fetch(url, { headers });
            if (!r.ok) throw new Error('API 请求失败 (' + r.status + '): ' + url);
            return r.json();
        }

        async function getProjects(workspaceId) {
            if (!workspaceId) return [];
            try {
                const data = await _apiFetch('/backend-api/gizmos/snorlax/sidebar', workspaceId);
                const projects = [];
                if (data.items) data.items.forEach(function (item) {
                    if (item && item.gizmo && item.gizmo.id && item.gizmo.display && item.gizmo.display.name)
                        projects.push({ id: item.gizmo.id, title: item.gizmo.display.name });
                });
                return projects;
            } catch (_) { return []; }
        }

        async function collectIds(onStatus, workspaceId, gizmoId) {
            const all = new Set();
            if (gizmoId) {
                let cursor = '0';
                do {
                    const j = await _apiFetch('/backend-api/gizmos/' + gizmoId + '/conversations?cursor=' + cursor, workspaceId);
                    if (j.items) j.items.forEach(function (it) { all.add(it.id); });
                    cursor = j.cursor;
                    await sleep(jitter());
                } while (cursor);
            } else {
                for (const is_archived of [false, true]) {
                    let offset = 0, has_more = true, page = 0;
                    do {
                        if (onStatus) onStatus('📂 ' + (is_archived ? 'Archived' : 'Active') + ' p' + (++page));
                        const j = await _apiFetch('/backend-api/conversations?offset=' + offset + '&limit=' + PAGE_LIMIT + '&order=updated' + (is_archived ? '&is_archived=true' : ''), workspaceId);
                        if (j.items && j.items.length > 0) {
                            j.items.forEach(function (it) { all.add(it.id); });
                            has_more = j.items.length === PAGE_LIMIT;
                            offset += j.items.length;
                        } else has_more = false;
                        await sleep(jitter());
                    } while (has_more);
                }
            }
            return Array.from(all);
        }

        async function getConversation(id, workspaceId) {
            const j = await _apiFetch('/backend-api/conversation/' + id, workspaceId);
            j.__fetched_at = new Date().toISOString();
            return j;
        }

        function detectAllWorkspaceIds() {
            const foundIds = new Set(W.__expCapturedWsIds || []);
            try {
                const el = document.getElementById('__NEXT_DATA__');
                if (el) {
                    const data = JSON.parse(el.textContent);
                    const accounts = data && data.props && data.props.pageProps && data.props.pageProps.user && data.props.pageProps.user.accounts;
                    if (accounts) Object.values(accounts).forEach(function (acc) { if (acc && acc.account && acc.account.id) foundIds.add(acc.account.id); });
                }
            } catch (_) { }
            try {
                for (let i = 0; i < W.localStorage.length; i++) {
                    const key = W.localStorage.key(i);
                    if (key && (key.includes('account') || key.includes('workspace'))) {
                        const value = W.localStorage.getItem(key);
                        if (value) {
                            const m = value.match(/ws-[a-f0-9-]{36}/i);
                            if (m) foundIds.add(m[0]);
                            else if (/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(value.replace(/"/g, '')))
                                foundIds.add(value.replace(/"/g, ''));
                        }
                    }
                }
            } catch (_) { }
            return Array.from(foundIds);
        }

        // 导出主流程 — ZIP 生成在页面上下文中执行
        async function startExport(mode, workspaceId, onStatus) {
            if (!onStatus) onStatus = function () { };
            onStatus('🔑 验证身份...');
            if (!await ensureAccessToken()) { onStatus('❌ 无法获取 Token'); return false; }

            // 确保 JSZip 已加载到页面上下文
            if (!W.JSZip) {
                onStatus('📦 正在加载 JSZip...');
                await _loadJSZip();
                if (!W.JSZip) { onStatus('❌ JSZip 加载失败，请刷新页面重试'); return false; }
            }

            try {
                // 收集所有对话数据
                onStatus('📂 获取对话列表…');
                const allFiles = []; // { path, content }
                const orphanIds = await collectIds(onStatus, workspaceId, null);
                for (let i = 0; i < orphanIds.length; i++) {
                    onStatus('📥 根目录 (' + (i + 1) + '/' + orphanIds.length + ')');
                    const c = await getConversation(orphanIds[i], workspaceId);
                    allFiles.push({ path: genFilename(c), content: JSON.stringify(c, null, 2) });
                    await sleep(jitter());
                }
                onStatus('🔍 获取项目列表…');
                const projects = await getProjects(workspaceId);
                for (const project of projects) {
                    const folderName = sanitize(project.title);
                    onStatus('📂 项目: ' + project.title);
                    const pIds = await collectIds(onStatus, workspaceId, project.id);
                    for (let i = 0; i < pIds.length; i++) {
                        onStatus('📥 ' + project.title.substring(0, 10) + '... (' + (i + 1) + '/' + pIds.length + ')');
                        const c = await getConversation(pIds[i], workspaceId);
                        allFiles.push({ path: folderName + '/' + genFilename(c), content: JSON.stringify(c, null, 2) });
                        await sleep(jitter());
                    }
                }

                onStatus('📦 生成 ZIP…');
                // 在页面上下文中执行 JSZip 操作，彻底避免沙箱 Promise 问题
                const date = new Date().toISOString().slice(0, 10);
                const fname = mode === 'team' ? 'chatgpt_team_' + workspaceId + '_' + date + '.zip' : 'chatgpt_personal_' + date + '.zip';

                // 将文件列表传递给页面上下文，在那里创建 ZIP
                W.__expFilesToZip = allFiles;
                W.__expZipFilename = fname;
                W.__expZipDone = null; // null=pending, true=success, string=error

                // 在页面上下文中运行 ZIP 生成（用 Function 构造器绕过 CSP inline 限制）
                // 由于 CSP 可能阻止 eval/Function，我们直接在沙箱中通过 unsafeWindow 调用页面的 JSZip
                try {
                    const PageJSZip = W.JSZip;
                    const zip = new PageJSZip();
                    for (let i = 0; i < allFiles.length; i++) {
                        zip.file(allFiles[i].path, allFiles[i].content);
                    }
                    // generateAsync 返回的是页面上下文的原生 Promise
                    const pagePromise = zip.generateAsync({ type: 'blob', compression: 'DEFLATE' });
                    // 使用回调方式处理，完全不依赖 await 与跨上下文 Promise 互操作
                    const blob = await new Promise(function (resolve, reject) {
                        pagePromise.then(
                            function (result) { resolve(result); },
                            function (err) { reject(err); }
                        );
                        // 安全超时
                        setTimeout(function () { reject(new Error('ZIP 生成超时')); }, 120000);
                    });
                    downloadFile(blob, fname);
                    return true;
                } catch (zipErr) {
                    console.error('[Exporter] ZIP generation error:', zipErr);
                    onStatus('❌ ZIP 生成失败: ' + zipErr.message);
                    return false;
                }
            } catch (e) {
                console.error('导出错误:', e);
                onStatus('❌ ' + e.message);
                return false;
            }
        }

        return { startExport, detectAllWorkspaceIds };
    })();

    /* ═══════════════ 对话导出 - 导出对话框 UI ═══════════════ */
    function _expShowExportDialog() {
        if (document.getElementById('tm-export-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'tm-export-overlay';
        overlay.className = 'tm-ov show';
        const dialog = document.createElement('div');
        dialog.className = 'tm-md';
        dialog.style.maxWidth = '450px';
        const closeDialog = () => { overlay.classList.remove('show'); setTimeout(() => { if (overlay.parentNode) document.body.removeChild(overlay); }, 300); };

        function doExport(mode, workspaceId) {
            closeDialog();
            const _st = (msg) => _tmToast(msg, 'loading');
            _EXP.startExport(mode, workspaceId, _st).then(ok => {
                if (ok) _tmToast('✅ 对话导出完成！', 'success', 4000);
            });
        }

        const renderStep = (step) => {
            let html = '';
            switch (step) {
                case 'team':
                    const detectedIds = _EXP.detectAllWorkspaceIds();
                    html = `<div class="tm-md-h"><div class="tm-md-t">🏢 导出团队空间</div><button class="tm-md-x" data-exp-close>✕</button></div><div class="tm-md-b">`;
                    if (detectedIds.length > 1) {
                        html += `<div class="tm-alert tm-alert-s">🔎 检测到多个 Workspace，请选择一个:</div><div class="tm-fld">`;
                        detectedIds.forEach((id, index) => {
                            html += `<label class="tm-chk" style="margin-bottom:6px;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.04)"><input type="radio" name="exp_workspace_id" value="${id}" ${index === 0 ? 'checked' : ''}><code style="font-family:monospace;font-size:11px;color:rgba(255,255,255,.7)">${id}</code></label>`;
                        });
                        html += `</div>`;
                    } else if (detectedIds.length === 1) {
                        html += `<div class="tm-alert tm-alert-s">✅ 已自动检测到 Workspace ID:</div><div class="tm-code" id="exp-workspace-id-code" style="margin-bottom:12px">${detectedIds[0]}</div>`;
                    } else {
                        html += `<div class="tm-alert tm-alert-w">⚠️ 未能自动检测到 Workspace ID。请尝试刷新页面或打开一个团队对话，或在下方手动输入。</div><div class="tm-fld"><label class="tm-lbl">手动输入 Team Workspace ID</label><input type="text" class="tm-inp" id="exp-team-id-input" placeholder="粘贴您的 Workspace ID (ws-...)"></div>`;
                    }
                    html += `</div><div class="tm-md-f"><button class="tm-btn tm-btn-s" id="exp-back-btn">← 返回</button><button class="tm-btn tm-btn-p" id="exp-start-team-btn">📦 开始导出 (ZIP)</button></div>`;
                    break;
                case 'initial': default:
                    html = `<div class="tm-md-h"><div class="tm-md-t">📦 导出对话</div><button class="tm-md-x" data-exp-close>✕</button></div><div class="tm-md-b"><div class="tm-fld" style="margin-bottom:16px"><button class="tm-btn" id="exp-select-personal" style="width:100%;padding:16px;text-align:left;background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.08);display:block"><strong style="font-size:14px;color:rgba(255,255,255,.95);display:block;margin-bottom:4px">👤 个人空间</strong><span style="font-size:11px;color:rgba(255,255,255,.5)">导出您个人账户下的所有对话</span></button></div><div class="tm-fld"><button class="tm-btn" id="exp-select-team" style="width:100%;padding:16px;text-align:left;background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.08);display:block"><strong style="font-size:14px;color:rgba(255,255,255,.95);display:block;margin-bottom:4px">🏢 团队空间</strong><span style="font-size:11px;color:rgba(255,255,255,.5)">导出团队空间下的对话，将自动检测 Workspace ID</span></button></div></div><div class="tm-md-f"><button class="tm-btn tm-btn-s" data-exp-close>取消</button></div>`;
                    break;
            }
            dialog.innerHTML = html;
            dialog.querySelectorAll('[data-exp-close]').forEach(b => b.onclick = closeDialog);
            if (step === 'initial') {
                document.getElementById('exp-select-personal').onclick = () => doExport('personal', null);
                document.getElementById('exp-select-team').onclick = () => renderStep('team');
            } else if (step === 'team') {
                document.getElementById('exp-back-btn').onclick = () => renderStep('initial');
                document.getElementById('exp-start-team-btn').onclick = () => {
                    let wid = '';
                    const rc = dialog.querySelector('input[name="exp_workspace_id"]:checked');
                    const ce = document.getElementById('exp-workspace-id-code');
                    const ie = document.getElementById('exp-team-id-input');
                    if (rc) wid = rc.value; else if (ce) wid = ce.textContent; else if (ie) wid = ie.value.trim();
                    if (!wid) { alert('请选择或输入一个有效的 Team Workspace ID！'); return; }
                    doExport('team', wid);
                };
            }
        };

        overlay.appendChild(dialog);
        document.body.appendChild(overlay);
        overlay.onclick = (e) => { if (e.target === overlay) closeDialog(); };
        renderStep('initial');
    }


    /* ═══════════════ CSS ═══════════════ */
    GM_addStyle(`
@keyframes tm-spin{to{transform:rotate(360deg)}}
@keyframes tm-in{from{opacity:0;transform:translateY(8px) scale(.96)}to{opacity:1;transform:none}}
@keyframes tm-pop{0%{transform:scale(0);opacity:0}60%{transform:scale(1.08)}100%{transform:scale(1);opacity:1}}
@keyframes tm-bar{from{width:100%}to{width:0}}
@keyframes tm-pulse{0%,100%{box-shadow:0 4px 20px rgba(16,163,127,.5),0 0 0 0 rgba(16,163,127,.3)}50%{box-shadow:0 4px 20px rgba(16,163,127,.5),0 0 0 8px rgba(16,163,127,0)}}
@keyframes tm-shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes tm-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
@keyframes tm-glow{0%,100%{opacity:.5}50%{opacity:1}}
@keyframes tm-slideUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes tm-aurora{0%{background-position:0% 50%}25%{background-position:100% 0%}50%{background-position:100% 100%}75%{background-position:0% 100%}100%{background-position:0% 50%}}
@keyframes tm-lightsweep{0%{transform:translateX(-200%) skewX(-18deg);opacity:0}15%{opacity:1}85%{opacity:1}100%{transform:translateX(700%) skewX(-18deg);opacity:0}}
@keyframes tm-borderShift{0%,100%{border-color:rgba(16,163,127,.22)}33%{border-color:rgba(99,102,241,.18)}66%{border-color:rgba(236,72,153,.16)}}
@keyframes tm-breathe{0%,100%{box-shadow:0 0 0 2px rgba(16,163,127,.12),inset 0 0 8px rgba(16,163,127,.02)}50%{box-shadow:0 0 0 3px rgba(16,163,127,.35),inset 0 0 20px rgba(16,163,127,.07)}}
@keyframes tm-stagger{from{opacity:0;transform:translateY(16px) scale(.97)}to{opacity:1;transform:none}}
@keyframes tm-rippleOut{0%{transform:scale(0);opacity:.4}100%{transform:scale(1);opacity:0}}
@keyframes tm-cardShine{from{transform:translateX(-250%) skewX(-18deg)}to{transform:translateX(500%) skewX(-18deg)}}
@keyframes tm-iconPop{0%{transform:scale(1)}40%{transform:scale(.8) rotate(-8deg)}70%{transform:scale(1.18) rotate(4deg)}100%{transform:scale(1) rotate(0)}}
@keyframes tm-fabMorph{0%,100%{box-shadow:0 4px 20px rgba(16,163,127,.5),0 0 0 0 rgba(16,163,127,.25),0 0 30px rgba(16,163,127,.15)}33%{box-shadow:0 4px 20px rgba(99,102,241,.5),0 0 0 0 rgba(99,102,241,.25),0 0 30px rgba(99,102,241,.15)}66%{box-shadow:0 4px 20px rgba(236,72,153,.5),0 0 0 0 rgba(236,72,153,.25),0 0 30px rgba(236,72,153,.15)}}
@keyframes tm-toastSlide{from{transform:translateX(-50%) translateY(-30px) scale(.85);opacity:0}to{transform:translateX(-50%) translateY(0) scale(1);opacity:1}}
@keyframes tm-successPulse{0%{box-shadow:0 0 0 0 rgba(16,163,127,.45)}70%{box-shadow:0 0 0 22px rgba(16,163,127,0)}100%{box-shadow:0 0 0 0 rgba(16,163,127,0)}}
@keyframes tm-titleGradient{0%{background-position:0% center}100%{background-position:200% center}}
@keyframes tm-glassRefract{0%,100%{background-position:0% 0%}50%{background-position:100% 100%}}
@keyframes tm-dotFloat{0%{transform:translateY(0) scale(1);opacity:.4}50%{transform:translateY(-12px) scale(1.3);opacity:.8}100%{transform:translateY(0) scale(1);opacity:.4}}
#tm-app-root{font-family:'Segoe UI',Inter,-apple-system,BlinkMacSystemFont,Roboto,sans-serif;position:fixed;bottom:24px;right:24px;z-index:2147483647;display:flex;flex-direction:column-reverse;align-items:flex-end;gap:12px;pointer-events:none}
#tm-app-root *{box-sizing:border-box}
.tm-fab{width:50px;height:50px;border-radius:50%;background:linear-gradient(135deg,#10a37f 0%,#0d8a6a 100%);box-shadow:0 4px 20px rgba(16,163,127,.5),0 0 0 0 rgba(16,163,127,.3);border:none;cursor:grab;display:flex;align-items:center;justify-content:center;transition:.3s cubic-bezier(.34,1.56,.64,1);color:#fff;pointer-events:auto;touch-action:none;user-select:none;position:relative;overflow:hidden;animation:tm-pulse 3s ease-in-out infinite}
.tm-fab::after{content:'';position:absolute;inset:0;background:radial-gradient(circle at 30% 30%,rgba(255,255,255,.2),transparent 60%);pointer-events:none}
.tm-fab:hover{transform:scale(1.08);box-shadow:0 6px 24px rgba(16,163,127,.6),0 0 0 4px rgba(16,163,127,.15)}
.tm-fab:active{cursor:grabbing}
.tm-fab.open{background:linear-gradient(135deg,#1a1a2e,#16213e);box-shadow:0 4px 20px rgba(0,0,0,.4);animation:none}
.tm-fab.open svg{transform:rotate(45deg)}
.tm-fab.dragging{cursor:grabbing!important;transform:scale(1.12);box-shadow:0 8px 32px rgba(16,163,127,.65)}
#tm-app-root.dragging .tm-panel{opacity:0!important;pointer-events:none!important;transform:translateY(12px) scale(.92)!important}
.tm-fab svg{width:22px;height:22px;transition:transform .35s cubic-bezier(.4,0,.2,1);filter:drop-shadow(0 1px 2px rgba(0,0,0,.2))}
.tm-panel{width:300px;background:rgba(15,15,25,.88);backdrop-filter:blur(20px) saturate(1.4);-webkit-backdrop-filter:blur(20px) saturate(1.4);border:1px solid rgba(255,255,255,.08);border-radius:20px;box-shadow:0 16px 48px rgba(0,0,0,.35),0 0 0 1px rgba(255,255,255,.05) inset;overflow:hidden;opacity:0;transform:translateY(14px) scale(.92);pointer-events:none;transform-origin:bottom right;transition:.32s cubic-bezier(.34,1.56,.64,1)}
.tm-panel.show{opacity:1;transform:none;pointer-events:auto}
.tm-p-head{padding:18px 18px 6px;display:flex;justify-content:space-between;align-items:center}
.tm-p-title{font-size:16px;font-weight:700;color:#fff;letter-spacing:-.3px}
.tm-p-ver{font-size:9px;color:rgba(255,255,255,.45);background:rgba(255,255,255,.08);padding:3px 8px;border-radius:6px;font-weight:600;letter-spacing:.3px}
.tm-p-body{padding:8px 10px 12px}
.tm-g{display:grid;grid-template-columns:1fr 1fr 1fr;gap:5px;margin-bottom:8px}
.tm-gi{display:flex;flex-direction:column;align-items:center;gap:6px;padding:12px 6px;border-radius:14px;border:1px solid transparent;background:rgba(255,255,255,.04);cursor:pointer;transition:.2s;color:rgba(255,255,255,.8);opacity:0;animation:tm-slideUp .35s ease forwards}
.tm-panel.show .tm-gi:nth-child(1){animation-delay:.05s}
.tm-panel.show .tm-gi:nth-child(2){animation-delay:.08s}
.tm-panel.show .tm-gi:nth-child(3){animation-delay:.11s}
.tm-panel.show .tm-gi:nth-child(4){animation-delay:.14s}
.tm-panel.show .tm-gi:nth-child(5){animation-delay:.17s}
.tm-panel.show .tm-gi:nth-child(6){animation-delay:.2s}
.tm-panel.show .tm-gi:nth-child(7){animation-delay:.23s}
.tm-gi:hover{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.08);transform:translateY(-1px)}
.tm-gi:active{transform:scale(.95);background:rgba(255,255,255,.06)}
.tm-gi-ic{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:17px;box-shadow:0 2px 8px rgba(0,0,0,.2);transition:.3s cubic-bezier(.34,1.56,.64,1)}
.tm-gi:hover .tm-gi-ic{transform:scale(1.12) translateY(-2px);box-shadow:0 4px 14px rgba(0,0,0,.3)}
.tm-gi-lb{font-size:10px;font-weight:600;line-height:1.2;text-align:center;opacity:.85}
.tm-sep{height:1px;background:rgba(255,255,255,.06);margin:4px 10px}
.tm-li{display:flex;align-items:center;gap:8px;padding:9px 12px;border-radius:10px;border:none;background:transparent;cursor:pointer;transition:.2s;color:rgba(255,255,255,.5);width:100%;text-align:left;font-size:12px;font-weight:500;opacity:0;animation:tm-slideUp .3s ease forwards;animation-delay:.25s}
.tm-li+.tm-li{animation-delay:.3s}
.tm-li:hover{background:rgba(255,255,255,.07);color:rgba(255,255,255,.8);padding-left:16px}
.tm-li svg{width:15px;height:15px;opacity:.4;flex-shrink:0}
/* Modal - Liquid Glass */
.tm-ov{position:fixed;inset:0;background:rgba(0,0,0,.4);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);z-index:2147483648;display:flex;justify-content:center;align-items:center;opacity:0;visibility:hidden;transition:.3s}
.tm-ov.show{opacity:1;visibility:visible}
.tm-md{background:rgba(255,255,255,.06);backdrop-filter:blur(20px) saturate(1.4);-webkit-backdrop-filter:blur(20px) saturate(1.4);width:420px;max-width:92vw;max-height:85vh;border-radius:24px;overflow:hidden;transform:translateY(24px) scale(.92) rotateX(2deg);transition:.4s cubic-bezier(.34,1.56,.64,1);display:flex;flex-direction:column;box-shadow:0 24px 80px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.2),inset 0 -1px 0 rgba(255,255,255,.05),inset 0 0 30px rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.12)}
.tm-ov.show .tm-md{transform:none}
.tm-md-h{padding:14px 18px;border-bottom:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,.03)}
.tm-md-t{font-size:15px;font-weight:700;color:rgba(255,255,255,.95);display:flex;align-items:center;gap:6px;text-shadow:0 1px 2px rgba(0,0,0,.2)}
.tm-md-x{width:28px;height:28px;border-radius:8px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.06);color:rgba(255,255,255,.5);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;transition:.2s}
.tm-md-x:hover{background:rgba(239,68,68,.65);color:#fff;border-color:rgba(239,68,68,.3)}
.tm-md-b{padding:16px 18px;overflow-y:auto;flex:1}
.tm-md-b::-webkit-scrollbar{width:5px}.tm-md-b::-webkit-scrollbar-track{background:transparent}.tm-md-b::-webkit-scrollbar-thumb{background:rgba(255,255,255,.12);border-radius:4px}.tm-md-b::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.2)}
.tm-md-f{padding:12px 18px;border-top:1px solid rgba(255,255,255,.08);display:flex;justify-content:flex-end;gap:6px;background:rgba(255,255,255,.02)}
/* Form - Liquid Glass */
.tm-inp{width:100%;padding:9px 12px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:10px;font-size:13px;color:rgba(255,255,255,.9);outline:none;transition:.25s}
.tm-inp:focus{border-color:rgba(16,163,127,.5);box-shadow:0 0 0 2px rgba(16,163,127,.15),inset 0 0 10px rgba(16,163,127,.05);background:rgba(255,255,255,.1)}
.tm-inp::placeholder{color:rgba(255,255,255,.3)}
.tm-sel{appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' fill='%23aaa' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 10px center;padding-right:28px}
.tm-sel option{background:#1a1a2e;color:rgba(255,255,255,.9)}
.tm-lbl{display:block;margin-bottom:4px;font-size:11px;font-weight:600;color:rgba(255,255,255,.55);text-transform:uppercase;letter-spacing:.3px}
.tm-fld{margin-bottom:14px}
.tm-fld:last-child{margin-bottom:0}
.tm-chk{display:flex;align-items:center;gap:8px;cursor:pointer;font-size:12px;color:rgba(255,255,255,.75)}
.tm-chk input{width:16px;height:16px;accent-color:#10a37f}
/* Buttons - Liquid Glass */
.tm-btn{border:1px solid rgba(255,255,255,.08);padding:8px 14px;border-radius:10px;font-size:12px;font-weight:600;cursor:pointer;transition:.25s cubic-bezier(.4,0,.2,1);display:inline-flex;align-items:center;gap:4px;position:relative;overflow:hidden}
.tm-btn:hover{filter:brightness(1.15);transform:translateY(-1px);box-shadow:0 4px 16px rgba(0,0,0,.15)}
.tm-btn:active{transform:scale(.95) translateY(0);box-shadow:none}
.tm-btn-p{background:rgba(16,163,127,.6);color:#fff;border-color:rgba(16,163,127,.25);box-shadow:0 2px 10px rgba(16,163,127,.2)}
.tm-btn-s{background:rgba(255,255,255,.08);color:rgba(255,255,255,.7);border-color:rgba(255,255,255,.1)}
.tm-btn-d{background:rgba(239,68,68,.12);color:rgba(239,68,68,.9);border-color:rgba(239,68,68,.12)}
.tm-btn-sm{padding:4px 10px;font-size:11px;border-radius:8px}
/* Cards - Liquid Glass */
.tm-card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:12px;margin-bottom:8px;transition:.25s}
.tm-card:hover{border-color:rgba(16,163,127,.35);box-shadow:0 4px 16px rgba(16,163,127,.1),inset 0 0 15px rgba(16,163,127,.03);transform:translateY(-1px)}
.tm-card-t{font-size:12px;font-weight:600;color:rgba(255,255,255,.92);word-break:break-all}
.tm-card-sub{font-size:11px;color:rgba(255,255,255,.5);font-family:monospace;margin-top:2px}
.tm-card-meta{font-size:10px;color:rgba(255,255,255,.35);margin-top:4px}
.tm-card-acts{display:flex;gap:4px;margin-top:8px;flex-wrap:wrap}
.tm-empty{text-align:center;padding:32px 16px;color:rgba(255,255,255,.4);font-size:13px}
/* Code - Liquid Glass */
.tm-code{background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.08);border-radius:10px;padding:10px 12px;font-family:'SF Mono',Menlo,monospace;font-size:11px;color:rgba(255,255,255,.8);word-break:break-all;max-height:100px;overflow-y:auto}
/* Alert - Liquid Glass */
.tm-alert{padding:10px 12px;border-radius:10px;font-size:11px;display:flex;align-items:flex-start;gap:6px;margin-bottom:12px}
.tm-alert-w{background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.2);color:rgba(251,191,36,.9)}
.tm-alert-s{background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.2);color:rgba(16,185,129,.9)}
.tm-alert-e{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.2);color:rgba(239,68,68,.9)}
/* Status bar */
/* Toast */
.tm-toast{position:fixed;top:16px;left:50%;transform:translateX(-50%) translateY(-20px);z-index:2147483650;display:flex;align-items:center;gap:8px;padding:10px 18px;border-radius:12px;font-size:13px;font-weight:600;box-shadow:0 8px 32px rgba(0,0,0,.2);opacity:0;visibility:hidden;transition:.35s cubic-bezier(.34,1.56,.64,1);pointer-events:none}
.tm-toast.show{opacity:1;visibility:visible;pointer-events:auto;transform:translateX(-50%) translateY(0)}
.tm-toast.loading{background:linear-gradient(135deg,#10a37f,#0e8c6b);color:#fff}
.tm-toast.success{background:linear-gradient(135deg,#059669,#047857);color:#fff}
.tm-toast.error{background:linear-gradient(135deg,#dc2626,#b91c1c);color:#fff}
.tm-toast .sp{width:14px;height:14px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:tm-spin .7s linear infinite}
.tm-sbar{position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:2147483650;display:flex;align-items:center;gap:8px;padding:10px 18px;border-radius:10px;font-size:13px;font-weight:600;box-shadow:0 6px 24px rgba(0,0,0,.15);background:linear-gradient(135deg,#10a37f,#0e8c6b);color:#fff;display:none}
.tm-sbar.show{display:flex}
.tm-sbar .sp{width:14px;height:14px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:tm-spin .7s linear infinite}
.tm-sbar .x{background:rgba(255,255,255,.2);border:none;color:#fff;padding:3px 10px;border-radius:5px;font-size:11px;font-weight:600;cursor:pointer;margin-left:10px}
.tm-sbar .x:hover{background:rgba(255,255,255,.3)}
/* Success - Liquid Glass */
.tm-suc-ic{width:64px;height:64px;margin:0 auto 12px;background:rgba(16,163,127,.15);border:1px solid rgba(16,163,127,.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:30px;animation:tm-pop .5s ease-out;box-shadow:0 4px 16px rgba(16,163,127,.15)}
.tm-suc-t{font-size:18px;font-weight:700;color:rgba(16,185,129,.95);margin-bottom:4px;text-shadow:0 1px 3px rgba(0,0,0,.15)}
.tm-suc-sub{font-size:12px;color:rgba(255,255,255,.5);margin-bottom:16px}
.tm-suc-info{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:12px;margin-bottom:12px}
.tm-suc-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0}
.tm-suc-row+.tm-suc-row{border-top:1px solid rgba(255,255,255,.06)}
.tm-suc-lb{font-size:11px;color:rgba(255,255,255,.4);font-weight:500}
.tm-suc-val{font-size:12px;color:rgba(255,255,255,.9);font-weight:600;font-family:monospace;word-break:break-all;max-width:200px;text-align:right}
.tm-suc-redir{background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.15);border-radius:10px;padding:10px 12px;margin-bottom:12px}
.tm-suc-redir-txt{font-size:12px;color:rgba(16,185,129,.9);font-weight:500;margin-bottom:8px}
.tm-suc-prog{height:3px;background:rgba(16,185,129,.1);border-radius:2px;overflow:hidden}
.tm-suc-prog-bar{height:100%;background:linear-gradient(90deg,rgba(16,185,129,.8),rgba(5,150,105,.8));border-radius:2px;width:100%}
/* ═══════════════ Liquid Glass Animations ═══════════════ */
/* Modal aurora background + light sweep */
.tm-md{position:relative;animation:tm-borderShift 8s ease infinite}
.tm-md::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(16,163,127,.06),rgba(99,102,241,.04),rgba(236,72,153,.03),rgba(59,130,246,.04),rgba(16,163,127,.06));background-size:300% 300%;animation:tm-aurora 15s ease infinite;pointer-events:none;z-index:0;border-radius:24px}
.tm-md::after{content:'';position:absolute;top:0;left:0;width:22%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.08),rgba(255,255,255,.03),transparent);pointer-events:none;z-index:1;animation:tm-lightsweep 8s ease-in-out 2s infinite;will-change:transform,opacity}
.tm-md-h,.tm-md-b,.tm-md-f{position:relative;z-index:2}
/* Staggered entrance for form fields */
.tm-ov.show .tm-fld{opacity:0;animation:tm-stagger .5s cubic-bezier(.16,1,.3,1) forwards}
.tm-ov.show .tm-fld:nth-child(1){animation-delay:.04s}
.tm-ov.show .tm-fld:nth-child(2){animation-delay:.08s}
.tm-ov.show .tm-fld:nth-child(3){animation-delay:.12s}
.tm-ov.show .tm-fld:nth-child(4){animation-delay:.16s}
.tm-ov.show .tm-fld:nth-child(5){animation-delay:.2s}
.tm-ov.show .tm-fld:nth-child(6){animation-delay:.24s}
.tm-ov.show .tm-fld:nth-child(7){animation-delay:.28s}
.tm-ov.show .tm-fld:nth-child(8){animation-delay:.32s}
.tm-ov.show .tm-alert{opacity:0;animation:tm-stagger .5s cubic-bezier(.16,1,.3,1) .02s forwards}
.tm-ov.show .tm-chk{opacity:0;animation:tm-stagger .45s cubic-bezier(.16,1,.3,1) .2s forwards}
/* Input breathing glow on focus */
.tm-inp:focus{animation:tm-breathe 2.5s ease-in-out infinite}
/* Card hover shine sweep */
.tm-card{position:relative;overflow:hidden}
.tm-card::after{content:'';position:absolute;top:0;left:0;width:40%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.07),rgba(255,255,255,.02),transparent);pointer-events:none;z-index:1;will-change:transform}
.tm-card:hover::after{animation:tm-cardShine .7s ease}
/* Grid icon bounce on click */
.tm-gi:active .tm-gi-ic{animation:tm-iconPop .45s cubic-bezier(.34,1.56,.64,1)}
.tm-gi:hover .tm-gi-ic{transform:scale(1.15) translateY(-3px) rotate(3deg);box-shadow:0 8px 24px rgba(0,0,0,.35),0 0 15px rgba(255,255,255,.08)}
.tm-gi{transition:.25s cubic-bezier(.34,1.56,.64,1)}
.tm-gi:hover{transform:translateY(-2px)}
/* FAB rainbow morph glow */
.tm-fab{animation:tm-fabMorph 6s ease infinite}
.tm-fab.open{animation:none}
.tm-fab:hover{animation:none;box-shadow:0 6px 28px rgba(16,163,127,.6),0 0 0 5px rgba(16,163,127,.12)}
/* Glass toast notifications */
.tm-toast{backdrop-filter:blur(10px) saturate(1.3);-webkit-backdrop-filter:blur(10px) saturate(1.3);border:1px solid rgba(255,255,255,.15)}
.tm-toast.show{animation:tm-toastSlide .45s cubic-bezier(.34,1.56,.64,1)}
.tm-toast.loading{background:linear-gradient(135deg,rgba(16,163,127,.85),rgba(14,140,107,.85))}
.tm-toast.success{background:linear-gradient(135deg,rgba(5,150,105,.85),rgba(4,120,87,.85))}
.tm-toast.error{background:linear-gradient(135deg,rgba(220,38,38,.85),rgba(185,28,28,.85))}
/* Success icon pulse ring */
.tm-suc-ic{animation:tm-pop .5s ease-out,tm-successPulse 1.5s ease .5s}
/* Panel aurora + floating dots */
.tm-panel{position:relative;overflow:hidden}
.tm-panel::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(16,163,127,.05),rgba(99,102,241,.04),transparent,rgba(236,72,153,.03));background-size:300% 300%;animation:tm-aurora 12s ease infinite;pointer-events:none;border-radius:20px;z-index:0}
.tm-panel>*{position:relative;z-index:1}
/* Panel title shimmer gradient */
.tm-p-title{background:linear-gradient(90deg,#fff 0%,rgba(16,163,127,.8) 45%,rgba(99,102,241,.8) 55%,#fff 100%);background-size:200% 100%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:tm-titleGradient 4s ease infinite}
/* Version badge float */
.tm-p-ver{animation:tm-float 3s ease-in-out infinite}
/* Close button spin on hover */
.tm-md-x{transition:.25s cubic-bezier(.34,1.56,.64,1)}
.tm-md-x:hover{transform:scale(1.1) rotate(90deg)}
/* Separator glass refraction */
.tm-sep{background:linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent);transition:.3s}
/* Status bar glass */
.tm-sbar{backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);background:linear-gradient(135deg,rgba(16,163,127,.85),rgba(14,140,107,.85));border:1px solid rgba(255,255,255,.12)}
/* Button hover glass highlight */
.tm-btn-p:hover{box-shadow:0 4px 20px rgba(16,163,127,.35),inset 0 1px 0 rgba(255,255,255,.15)}
.tm-btn-s:hover{box-shadow:0 4px 16px rgba(0,0,0,.12),inset 0 1px 0 rgba(255,255,255,.08)}
/* Card stagger entrance in accounts */
.tm-ov.show .tm-card{opacity:0;animation:tm-stagger .45s cubic-bezier(.16,1,.3,1) forwards}
.tm-ov.show .tm-card:nth-child(1){animation-delay:.03s}
.tm-ov.show .tm-card:nth-child(2){animation-delay:.06s}
.tm-ov.show .tm-card:nth-child(3){animation-delay:.09s}
.tm-ov.show .tm-card:nth-child(4){animation-delay:.12s}
.tm-ov.show .tm-card:nth-child(5){animation-delay:.15s}
.tm-ov.show .tm-card:nth-child(6){animation-delay:.18s}
.tm-ov.show .tm-card:nth-child(7){animation-delay:.21s}
.tm-ov.show .tm-card:nth-child(8){animation-delay:.24s}
.tm-ov.show .tm-card:nth-child(9){animation-delay:.27s}
.tm-ov.show .tm-card:nth-child(10){animation-delay:.3s}

/* ═══════════════ 移动端适配 ═══════════════ */
@media screen and (max-width:768px){
/* 主容器 - 移动端底部固定（不加!important，允许JS拖动覆盖） */
#tm-app-root{gap:10px}

/* FAB 按钮 - 移动端稍小一点 */
.tm-fab{width:46px;height:46px}
.tm-fab svg{width:20px;height:20px}

/* 面板 - 移动端底部固定弹出 */
.tm-panel{position:fixed!important;bottom:0!important;left:0!important;right:0!important;width:100%!important;max-width:100%!important;border-radius:20px 20px 0 0!important;transform:translateY(100%)!important;transform-origin:bottom center!important;z-index:2147483647}
.tm-panel.show{transform:translateY(0)!important}
.tm-panel::after{content:'';position:absolute;top:8px;left:50%;transform:translateX(-50%);width:36px;height:4px;border-radius:2px;background:rgba(255,255,255,.2);z-index:10}
.tm-p-head{padding:20px 16px 6px}
.tm-p-title{font-size:16px}
.tm-p-body{padding:8px 12px calc(12px + env(safe-area-inset-bottom,0px))}

/* 面板打开时的遮罩 */
.tm-panel-backdrop{display:none;position:fixed;inset:0;background:rgba(0,0,0,.35);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);z-index:2147483646;opacity:0;transition:opacity .3s}
.tm-panel-backdrop.show{display:block;opacity:1}

/* 网格 - 移动端保持3列但缩小间距 */
.tm-g{gap:4px;margin-bottom:6px}
.tm-gi{padding:10px 4px;border-radius:12px;gap:5px}
.tm-gi-ic{width:32px;height:32px;border-radius:8px;font-size:15px}
.tm-gi-lb{font-size:9px}

/* 底部列表项 */
.tm-li{padding:8px 10px;font-size:11px;gap:6px}
.tm-li svg{width:14px;height:14px}

/* 分隔线 */
.tm-sep{margin:3px 8px}

/* 弹窗 overlay */
.tm-ov{align-items:flex-end;padding:0}

/* 弹窗 modal - 移动端底部弹出式 */
.tm-md{width:100%!important;max-width:100vw!important;max-height:92vh!important;border-radius:20px 20px 0 0!important;margin:0!important;transform:translateY(100%) scale(1)!important}
.tm-ov.show .tm-md{transform:translateY(0) scale(1)!important}
.tm-md::before{border-radius:20px 20px 0 0}

/* 弹窗顶部拖拽指示条 */
.tm-md::after{content:'';position:absolute;top:8px;left:50%;transform:translateX(-50%);width:36px;height:4px;border-radius:2px;background:rgba(255,255,255,.2);z-index:10;animation:none!important}

/* 弹窗头部 */
.tm-md-h{padding:18px 16px 10px}
.tm-md-t{font-size:14px}
.tm-md-x{width:32px;height:32px;border-radius:10px;font-size:16px}

/* 弹窗内容区 */
.tm-md-b{padding:12px 14px;max-height:calc(92vh - 120px)!important;-webkit-overflow-scrolling:touch}

/* 弹窗底部 */
.tm-md-f{padding:10px 14px calc(10px + env(safe-area-inset-bottom,0px));gap:6px;flex-wrap:wrap}

/* 表单元素 - 移动端更大的触摸区域 */
.tm-inp{padding:11px 14px;font-size:14px;border-radius:12px}
.tm-lbl{font-size:11px;margin-bottom:5px}
.tm-fld{margin-bottom:12px}
.tm-chk{font-size:13px;gap:10px;padding:4px 0}
.tm-chk input{width:20px;height:20px}

/* 按钮 - 移动端更大触摸区域 */
.tm-btn{padding:10px 16px;font-size:13px;border-radius:12px;min-height:40px}
.tm-btn-sm{padding:8px 12px;font-size:12px;border-radius:10px;min-height:36px}

/* 卡片 - 移动端适配 */
.tm-card{padding:12px;border-radius:14px;margin-bottom:8px}
.tm-card-t{font-size:13px}
.tm-card-sub{font-size:12px}
.tm-card-meta{font-size:11px}
.tm-card-acts{gap:6px;margin-top:10px}
.tm-card-acts .tm-btn{flex:1;justify-content:center;min-width:0;text-align:center;padding:8px 6px}

/* 代码块 */
.tm-code{font-size:11px;padding:10px;border-radius:10px;max-height:120px;word-break:break-all}

/* 提示框 */
.tm-alert{padding:10px;font-size:12px;border-radius:10px}

/* Toast 通知 - 移动端更宽 */
.tm-toast{left:12px!important;right:12px!important;transform:translateX(0) translateY(-20px)!important;max-width:none;border-radius:14px;padding:12px 16px;font-size:13px}
.tm-toast.show{transform:translateX(0) translateY(0)!important}

/* 状态栏 - 移动端更宽 */
.tm-sbar{left:12px!important;right:12px!important;transform:translateX(0)!important;max-width:none;border-radius:12px;padding:10px 14px;font-size:12px}

/* 成功图标 */
.tm-suc-ic{width:56px;height:56px;font-size:26px}
.tm-suc-t{font-size:16px}
.tm-suc-sub{font-size:12px}
.tm-suc-val{max-width:180px;font-size:11px}

/* 空状态 */
.tm-empty{padding:24px 14px;font-size:13px}

/* 收件箱邮件内容 */
#tm-mail-content{max-height:280px!important;padding:12px;font-size:13px}

/* 分页按钮 */
#tm-pg-first,#tm-pg-prev,#tm-pg-next,#tm-pg-last{min-height:34px;padding:6px 10px}

/* 设置页 - 移动端底部按钮区域 */
.tm-md-f .tm-btn{flex:none}

/* 关于页 */
.tm-md[style*="max-width:360px"] .tm-md-b{padding:16px 14px}

/* 账号弹窗底部按钮 - 移动端自动换行 */
#tm-modal-accounts .tm-md-f{flex-wrap:wrap;justify-content:center;gap:6px}
#tm-modal-accounts .tm-md-f .tm-btn{flex:1 1 auto;min-width:0;justify-content:center;text-align:center}

/* 设置弹窗底部按钮 */
#tm-modal-settings .tm-md-f{flex-wrap:wrap;gap:6px}
#tm-modal-settings .tm-md-f .tm-btn{flex:1 1 auto;min-width:0;justify-content:center;text-align:center}

/* 收件箱 - 移动端适配 */
#tm-modal-inbox .tm-md-b{max-height:calc(92vh - 130px)!important}
#tm-inbox-fetch{min-height:36px}
}

/* 更小屏幕适配 (iPhone SE 等) */
@media screen and (max-width:375px){
.tm-fab{width:42px;height:42px}
.tm-fab svg{width:18px;height:18px}
.tm-panel{width:calc(100vw - 16px);max-width:100%}
.tm-g{grid-template-columns:1fr 1fr 1fr;gap:3px}
.tm-gi{padding:8px 3px;gap:4px}
.tm-gi-ic{width:28px;height:28px;font-size:13px;border-radius:7px}
.tm-gi-lb{font-size:8px}
.tm-md-h{padding:16px 12px 8px}
.tm-md-b{padding:10px 12px}
.tm-md-f{padding:8px 12px calc(8px + env(safe-area-inset-bottom,0px));gap:4px}
.tm-inp{padding:10px 12px;font-size:14px}
.tm-btn{padding:9px 12px;font-size:12px;min-height:38px}
.tm-btn-sm{padding:7px 10px;font-size:11px;min-height:34px}
.tm-card-acts{flex-wrap:wrap}
.tm-card-acts .tm-btn{flex:1 1 calc(50% - 3px);min-width:0}
.tm-toast{left:8px!important;right:8px!important;padding:10px 14px;font-size:12px}
.tm-sbar{left:8px!important;right:8px!important;padding:8px 12px;font-size:11px}
}

/* 横屏模式适配 */
@media screen and (max-height:500px) and (orientation:landscape){
.tm-md{max-height:96vh!important}
.tm-md-b{max-height:calc(96vh - 110px)!important}
.tm-fab{width:40px;height:40px}
.tm-fab svg{width:18px;height:18px}
.tm-suc-ic{width:40px;height:40px;font-size:20px;margin-bottom:6px}
.tm-suc-t{font-size:14px}
}

/* 安全区域适配 (刘海屏/底部横条) */
@supports(padding-bottom:env(safe-area-inset-bottom)){
@media screen and (max-width:768px){
.tm-md-f{padding-bottom:calc(10px + env(safe-area-inset-bottom,0px))}
.tm-toast{top:calc(16px + env(safe-area-inset-top,0px))!important}
.tm-sbar{top:calc(16px + env(safe-area-inset-top,0px))!important}
}
}

/* 触摸设备优化 */
@media(hover:none) and (pointer:coarse){
.tm-gi{-webkit-tap-highlight-color:transparent}
.tm-btn{-webkit-tap-highlight-color:transparent}
.tm-card{-webkit-tap-highlight-color:transparent}
.tm-li{-webkit-tap-highlight-color:transparent}
.tm-md-x{-webkit-tap-highlight-color:transparent}
.tm-gi:hover{transform:none;background:rgba(255,255,255,.04);border-color:transparent}
.tm-gi:hover .tm-gi-ic{transform:none;box-shadow:0 2px 8px rgba(0,0,0,.2)}
.tm-gi:active{transform:scale(.95);background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.08)}
.tm-gi:active .tm-gi-ic{transform:scale(1.08)}
.tm-card:hover{border-color:rgba(255,255,255,.08);box-shadow:none;transform:none}
.tm-card:active{border-color:rgba(16,163,127,.35);transform:scale(.98)}
.tm-btn:hover{filter:none;transform:none;box-shadow:none}
.tm-btn:active{transform:scale(.95);filter:brightness(1.1)}
.tm-li:hover{background:transparent;color:rgba(255,255,255,.5);padding-left:12px}
.tm-li:active{background:rgba(255,255,255,.07);color:rgba(255,255,255,.8)}
}
`);

    /* ═══════════════ 工具函数 ═══════════════ */
    function _0x7b(t) { GM_setClipboard(t, 'text'); return !0; }
    const _0x8c = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles', 'Mary', 'Patricia', 'Jennifer', 'Linda', 'Barbara', 'Elizabeth', 'Susan', 'Jessica', 'Sarah', 'Karen', 'Emma', 'Olivia', 'Ava', 'Sophia', 'Isabella', 'Liam', 'Noah', 'Oliver', 'Elijah', 'Lucas'];
    const _0x9d = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris', 'Clark'];
    function _0xae(l = 0x10) { const c = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%'; let p = ''; p += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[Math.floor(Math.random() * 0x1a)]; p += 'abcdefghijklmnopqrstuvwxyz'[Math.floor(Math.random() * 0x1a)]; p += '0123456789'[Math.floor(Math.random() * 0xa)]; p += '!@#$%'[Math.floor(Math.random() * 0x5)]; for (let i = 0x4; i < l; i++) { p += c[Math.floor(Math.random() * c.length)]; } return p.split('').sort(() => Math.random() - 0.5).join(''); }
    function _0xbf() { return { firstName: _0x8c[Math.floor(Math.random() * _0x8c.length)], lastName: _0x9d[Math.floor(Math.random() * _0x9d.length)] }; }
    function _0xc0() { const y = new Date().getFullYear(); const yr = y - 0x12 - Math.floor(Math.random() * 0x1e); const m = Math.floor(Math.random() * 0xc) + 0x1; const d = Math.floor(Math.random() * 0x1c) + 0x1; return { year: yr, month: m, day: d }; }

    /* ═══════════════ NPCmail API ═══════════════ */
    function _0xd1(e, o = {}) { const k = GM_getValue(_0x4e.API_KEY, ''); if (!k) { return Promise.reject(new Error('请先配置 NPCmail 密钥')); } return new Promise((r, j) => { GM_xmlhttpRequest({ method: o.method || 'GET', url: _0x3c + e, headers: { 'X-API-Key': k, 'Content-Type': _0xb('YXBwbGljYXRpb24vanNvbg==') }, data: o.body ? JSON.stringify(o.body) : undefined, onload: function (rs) { try { const d = JSON.parse(rs.responseText); if (rs.status >= 0xc8 && rs.status < 0x12c) { r(d); } else { j(new Error(d.error || d.message || 'HTTP ' + rs.status)); } } catch (x) { j(new Error('JSON 解析失败')); } }, onerror: function (x) { j(new Error('网络请求失败')); } }); }); }
    async function _0xe2() { return await _0xd1(_0xb('L2FwaS9wdWJsaWMvYXBpLWtleS9pbmZv')); }
    async function _0xf3(d = null, p = null) { const b = { count: 0x1, expiryDays: 0x7 }; d && (b.domain = d); p && (b.prefix = p); const r = await _0xd1(_0xb('L2FwaS9wdWJsaWMvYmF0Y2gtY3JlYXRlLWVtYWlscw=='), { method: 'POST', body: b }); if (r.emails && r.emails.length > 0x0) return r.emails[0x0]; throw new Error('创建邮箱失败'); }
    async function _0x115(a) { try { const r = await _0xd1(_0xb('L2FwaS9wdWJsaWMvZXh0cmFjdC1jb2Rlcw=='), { method: 'POST', body: { addresses: [a] } }); console.log('[_0x115] response:', JSON.stringify(r)); if (r && r.length > 0x0 && r[0x0].code) return r[0x0].code; if (r && r.codes && r.codes.length > 0 && r.codes[0].code) return r.codes[0].code; if (r && r.data && r.data.length > 0 && r.data[0].code) return r.data[0].code; return null; } catch (e) { console.error('[_0x115] error:', e); return null; } }
    async function _0x_npcMails(a) { return await _0xd1('/api/public/emails/' + encodeURIComponent(a) + '/messages'); }

    /* ═══════════════ TempMail API ═══════════════ */
    function _0x_tmReq(ep) { return new Promise((r, j) => { GM_xmlhttpRequest({ method: 'GET', url: _0x_TM_API + ep, headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }, timeout: 15000, onload: function (rs) { try { const d = JSON.parse(rs.responseText); if (rs.status >= 200 && rs.status < 300) { r(d); } else { j(new Error('临时邮箱服务请求失败 ' + rs.status)); } } catch (x) { j(new Error('临时邮箱响应解析失败')); } }, onerror: function () { j(new Error('临时邮箱网络错误')); }, ontimeout: function () { j(new Error('临时邮箱请求超时')); } }); }); }
    async function _0x_tmInbox(email, epin) { return await _0x_tmReq('/mails?email=' + encodeURIComponent(email) + '&epin=' + (epin || '')); }
    async function _0x_tmMail(id, email, epin) { return await _0x_tmReq('/mails/' + id + '?email=' + encodeURIComponent(email) + '&epin=' + (epin || '')); }
    async function _0x_tmCode(email, epin) { try { const inbox = await _0x_tmInbox(email, epin); if (!inbox.mail_list || inbox.mail_list.length === 0) return null; const m = inbox.mail_list[0]; const lastId = GM_getValue('tm_last_mail_id', ''); if (lastId === m.mail_id) return null; const det = await _0x_tmMail(m.mail_id, email, epin); const all = (det.text || '') + ' ' + (det.html || '') + ' ' + (det.subject || m.subject || ''); let code = null; const mt = all.match(/\b(\d{6})\b/); if (mt) code = mt[1]; else { const mt2 = all.match(/\b(\d{4,8})\b/); if (mt2) code = mt2[1]; } if (code) { GM_setValue('tm_last_mail_id', m.mail_id); return code; } return null; } catch (e) { console.warn('[TempMail]', e); return null; } }

    /* ═══════════════ Team 后台 API ═══════════════ */
    function _0x_teamReq(baseUrl, method, path, apiKey, body) { return new Promise((r, j) => { const url = baseUrl.replace(/\/+$/, '') + path; GM_xmlhttpRequest({ method: method, url: url, headers: { 'X-API-Key': apiKey, 'Content-Type': 'application/json' }, data: body ? JSON.stringify(body) : undefined, timeout: 120000, onload: function (rs) { try { const d = JSON.parse(rs.responseText); if (rs.status >= 200 && rs.status < 300) { r(d); } else { j(new Error(d.detail || d.message || d.error || 'HTTP ' + rs.status)); } } catch (x) { j(new Error('响应解析失败 (HTTP ' + rs.status + ')')); } }, onerror: function () { j(new Error('网络请求失败，请检查地址')); }, ontimeout: function () { j(new Error('请求超时')); } }); }); }
    async function _0x_pushToTeam() {
        const url = (GM_getValue('tm_team_url', '') || '')
            .trim()
            .replace(/\/+$/, '')
            .replace(/\/external\/push$/i, '')
            .replace(/\/external$/i, '');
        const key = (GM_getValue('tm_team_key', '') || '').trim().replace(/^Bearer\s+/i, '');
        if (!url || !key) throw new Error('请先在设置中配置 Team 后台地址和密钥');

        let token = null;
        try {
            const sr = await fetch(_0xb('L2FwaS9hdXRoL3Nlc3Npb24='));
            const ct = sr.headers.get('content-type');
            if (ct && ct.includes('application/json')) {
                const tk = await sr.json();
                if (tk.accessToken) token = tk.accessToken;
            }
        } catch (e) { }
        if (!token) throw new Error('请先登录 ChatGPT');
        return await _0x_teamReq(url, 'POST', '/external/push', key, { access_token: token });
    }

    async function _0x_doPush() {
        _tmToast('正在推送当前账号...', 'loading');
        try {
            const res = await _0x_pushToTeam();
            if (res && res.success === false) {
                _tmToast(res.message || res.error || '导入失败', 'error', 4500);
            } else {
                const msg = (res && res.message) ? res.message : '导入成功';
                _tmToast(msg, 'success', 3500);
            }
        } catch (e) {
            _tmToast((e && e.message) ? e.message : '推送失败', 'error', 4500);
        }
    }

    /* ═══════════════ 自定义域名 ═══════════════ */
    function _0x_getCDs() { return GM_getValue('tm_custom_domains', []); }
    function _0x_setCDs(d) { GM_setValue('tm_custom_domains', d); }
    function _0x_addCD(d) { d = d.trim().toLowerCase().replace(/^@/, ''); if (!d || !/^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$/.test(d)) return false; const ds = _0x_getCDs(); if (ds.includes(d)) return false; ds.push(d); _0x_setCDs(ds); return true; }
    function _0x_rmCD(d) { _0x_setCDs(_0x_getCDs().filter(x => x !== d)); }
    function _0x_randPfx(n = 12) { const c = 'abcdefghijklmnopqrstuvwxyz0123456789'; let r = c[Math.floor(Math.random() * 26)]; for (let i = 1; i < n; i++)r += c[Math.floor(Math.random() * c.length)]; return r; }
    function _0x_renderCDs() { const el = document.getElementById('tm-cd-list'); if (!el) return; const ds = _0x_getCDs(); if (ds.length === 0) { el.innerHTML = '<div style="font-size:11px;color:#aaa;padding:6px;text-align:center">暂未添加域名</div>'; return; } el.innerHTML = ds.map(d => '<div style="display:flex;align-items:center;justify-content:space-between;padding:5px 8px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);border-radius:8px;margin-bottom:3px"><span style="font-size:11px;font-family:monospace;color:rgba(255,255,255,.8)">' + d + '</span><button class="tm-btn tm-btn-d tm-btn-sm" data-rmcd="' + d + '" style="padding:2px 6px;font-size:10px">✕</button></div>').join(''); el.querySelectorAll('[data-rmcd]').forEach(b => { b.onclick = function () { _0x_rmCD(this.dataset.rmcd); _0x_renderCDs(); }; }); }

    /* ═══════════════ 数据存取 ═══════════════ */
    function _0x126() { return GM_getValue(_0x4e.ACCOUNTS, []); }
    function _0x137(a) { const ac = _0x126(); const i = ac.findIndex(x => x.email === a.email); i >= 0x0 ? ac[i] = { ...ac[i], ...a } : ac.unshift(a); GM_setValue(_0x4e.ACCOUNTS, ac); const _v = GM_getValue(_0x4e.ACCOUNTS, []); if (!_v.find(x => x.email === a.email)) { console.error('[SaveGuard] 保存验证失败，正在重试...'); GM_setValue(_0x4e.ACCOUNTS, ac); const _v2 = GM_getValue(_0x4e.ACCOUNTS, []); if (!_v2.find(x => x.email === a.email)) { try { const bk = JSON.parse(localStorage.getItem('tm_accounts_backup') || '[]'); if (!bk.find(x => x.email === a.email)) bk.unshift(a); localStorage.setItem('tm_accounts_backup', JSON.stringify(bk)); } catch (e) { } console.error('[SaveGuard] 二次保存仍失败，已写入 localStorage 备份'); } } try { localStorage.setItem('tm_accounts_backup', JSON.stringify(GM_getValue(_0x4e.ACCOUNTS, []))); } catch (e) { } _syncPush(a); }
    function _0x148(e) { GM_setValue(_0x4e.ACCOUNTS, _0x126().filter(a => a.email !== e)); }
    function _0x159() { return GM_getValue(_0x4e.AUTO_REG, null); }
    function _0x16a(d) { GM_setValue(_0x4e.AUTO_REG, d); }
    function _0x17b() { return GM_getValue(_0x4e.AUTO_REG_STEP, _0x5f.IDLE); }
    function _0x18c(s) { GM_setValue(_0x4e.AUTO_REG_STEP, s); console.log('[AutoReg] Step:', s); }
    function _0x19d() { GM_deleteValue(_0x4e.AUTO_REG); GM_deleteValue(_0x4e.AUTO_REG_STEP); _0x_regClearGuard(); }

    /* ═══════════════ Workers 云同步 ═══════════════ */
    function _workerReq(method, path, body) { const url = GM_getValue('tm_sync_url', ''); const key = GM_getValue('tm_sync_apikey', ''); if (!url || !key) return Promise.resolve(null); return new Promise((r, j) => { GM_xmlhttpRequest({ method: method, url: url.replace(/\/+$/, '') + path, headers: { 'X-Sync-Key': key, 'Content-Type': 'application/json' }, data: body ? JSON.stringify(body) : undefined, timeout: 15000, onload: function (rs) { try { const d = JSON.parse(rs.responseText); if (rs.status >= 200 && rs.status < 300) { r(d); } else { j(new Error(d.error || 'HTTP ' + rs.status)); } } catch (x) { j(new Error('响应解析失败')); } }, onerror: function () { j(new Error('网络请求失败')); }, ontimeout: function () { j(new Error('请求超时')); } }); }); }
    async function _syncPush(account) { const _su = GM_getValue('tm_sync_url', ''); const _sk = GM_getValue('tm_sync_apikey', ''); if (!_su || !_sk) return; try { await _workerReq('POST', '/api/accounts', { account: account }); console.log('[CloudSync] 已上传:', account.email); } catch (e) { console.warn('[CloudSync] 上传失败:', e.message); } }
    async function _syncPushAll() { const url = GM_getValue('tm_sync_url', ''); const key = GM_getValue('tm_sync_apikey', ''); if (!url || !key) throw new Error('请先在设置中配置云同步地址和密钥'); const ac = _0x126(); if (!ac.length) throw new Error('本地暂无账号'); return await _workerReq('POST', '/api/accounts', { accounts: ac }); }
    async function _syncPull() { const _su = GM_getValue('tm_sync_url', ''); const _sk = GM_getValue('tm_sync_apikey', ''); if (!_su || !_sk) return; try { const r = await _workerReq('GET', '/api/accounts'); if (!r || !r.accounts || !r.accounts.length) return; const remote = r.accounts; const local = _0x126(); let added = 0; const localEmails = new Set(local.map(a => a.email)); for (const ra of remote) { if (!ra.email) continue; if (!localEmails.has(ra.email)) { local.unshift(ra); added++; } else { const li = local.findIndex(x => x.email === ra.email); if (li >= 0) { const la = local[li]; if (ra.status === '注册完成' && la.status !== '注册完成') { local[li] = { ...la, ...ra }; } else if (ra.createdAt && la.createdAt && ra.createdAt > la.createdAt) { local[li] = { ...la, ...ra }; } } } } if (added > 0) { GM_setValue(_0x4e.ACCOUNTS, local); try { localStorage.setItem('tm_accounts_backup', JSON.stringify(local)); } catch (e) { } console.log('[CloudSync] 从云端同步了 ' + added + ' 个新账号'); setTimeout(() => _tmToast('云同步: 恢复了 ' + added + ' 个账号', 'success', 3000), 2500); } else { console.log('[CloudSync] 云端无新账号'); } } catch (e) { console.warn('[CloudSync] 拉取失败:', e.message); } }

    /* ═══════════════ 兜底 & 导入导出 ═══════════════ */
    let _backupChecked = false;
    function _0x_restoreFromBackup() { if (_backupChecked) return; _backupChecked = true; try { const bk = JSON.parse(localStorage.getItem('tm_accounts_backup') || '[]'); if (!bk.length) return; const cur = _0x126(); let count = 0; for (const b of bk) { if (b.email && !cur.find(x => x.email === b.email)) { cur.unshift(b); count++; } } if (count > 0) { GM_setValue(_0x4e.ACCOUNTS, cur); console.log('[SaveGuard] 从备份恢复了 ' + count + ' 个账号'); setTimeout(() => _tmToast('从备份恢复了 ' + count + ' 个丢失账号', 'success', 4000), 2000); } } catch (e) { console.warn('[SaveGuard]', e); } }
    function _0x_exportAccounts() { const ac = _0x126(); if (!ac.length) { alert('暂无账号可导出'); return; } const data = JSON.stringify(ac, null, 2); const blob = new Blob([data], { type: 'application/json' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'chatgpt-accounts-' + new Date().toISOString().slice(0, 10) + '.json'; document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url); _tmToast('已导出 ' + ac.length + ' 个账号', 'success', 2000); }
    function _0x_importAccounts() { const inp = document.createElement('input'); inp.type = 'file'; inp.accept = '.json,.txt,.csv'; inp.onchange = function (e) { const f = e.target.files[0]; if (!f) return; const rd = new FileReader(); rd.onload = function (ev) { try { let arr = []; const txt = ev.target.result.trim(); try { const j = JSON.parse(txt); arr = Array.isArray(j) ? j : [j]; } catch (_) { arr = txt.split('\n').map(l => l.trim()).filter(l => l).map(l => { const p = l.split(/[,\t|;]/); return { email: (p[0] || '').trim(), password: (p[1] || '').trim() }; }); } let added = 0, skipped = 0; const cur = _0x126(); for (const item of arr) { if (!item.email || !item.email.includes('@')) { skipped++; continue; } if (cur.find(x => x.email === item.email)) { skipped++; continue; } _0x137({ email: item.email, password: item.password || '', status: item.status || '导入', createdAt: item.createdAt || new Date().toISOString(), ...item }); added++; } const msg = '导入完成: ' + added + ' 个账号' + (skipped ? ' (跳过' + skipped + '个)' : ''); _tmToast(msg, 'success', 3000); _0xff2(); } catch (ex) { alert('导入失败: ' + ex.message); } }; rd.readAsText(f); }; inp.click(); }
    function _0x_importEmails() { const inp = document.createElement('input'); inp.type = 'file'; inp.accept = '.json,.txt,.csv'; inp.onchange = function (e) { const f = e.target.files[0]; if (!f) return; const rd = new FileReader(); rd.onload = function (ev) { try { let emails = []; const txt = ev.target.result.trim(); try { const j = JSON.parse(txt); if (Array.isArray(j)) emails = j.map(x => typeof x === 'string' ? { email: x } : x); else if (j.email) emails = [j]; else if (j.emails) emails = j.emails.map(x => typeof x === 'string' ? { email: x } : x); } catch (_) { emails = txt.split(/[\n,;]/).map(l => l.trim()).filter(l => l.includes('@')).map(e => ({ email: e })); } let added = 0, skipped = 0; const cur = _0x126(); for (const item of emails) { if (!item.email || !item.email.includes('@')) { skipped++; continue; } if (cur.find(x => x.email === item.email)) { skipped++; continue; } _0x137({ email: item.email, password: item.password || '', status: '邮箱导入', createdAt: new Date().toISOString(), isEmailImport: true, ...item }); added++; } const msg = '导入完成: ' + added + ' 个邮箱' + (skipped ? ' (跳过' + skipped + '个)' : ''); _tmToast(msg, 'success', 3000); _0xff2(); } catch (ex) { alert('导入失败: ' + ex.message); } }; rd.readAsText(f); }; inp.click(); }
    function _0x_exportEmails() { const ac = _0x126(); if (!ac.length) { alert('暂无邮箱可导出'); return; } const emails = ac.map(a => a.email); const blob = new Blob([emails.join('\n')], { type: 'text/plain' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'chatgpt-emails-' + new Date().toISOString().slice(0, 10) + '.txt'; document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url); _tmToast('已导出 ' + emails.length + ' 个邮箱', 'success', 2000); }
    function _0x_fullBackup() { const data = { _meta: { version: '9.1', exportedAt: new Date().toISOString(), type: 'chatgpt-tools-full-backup' }, accounts: _0x126(), settings: { apiKey: GM_getValue(_0x4e.API_KEY, ''), regPrefix: GM_getValue('tm_reg_prefix', ''), regDomain: GM_getValue('tm_reg_domain', ''), useCd: GM_getValue('tm_use_cd', false), customDomains: _0x_getCDs(), tmAddr: GM_getValue('tm_tm_addr', ''), tmEpin: GM_getValue('tm_tm_epin', ''), teamUrl: GM_getValue('tm_team_url', ''), teamKey: GM_getValue('tm_team_key', ''), autoRedirectTeam: GM_getValue(_0x4e.AUTO_REDIRECT_TEAM, false), fabPos: GM_getValue('tm_fab_pos', null) } }; const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'chatgpt-tools-backup-' + new Date().toISOString().slice(0, 10) + '.json'; document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url); _tmToast('已备份全部数据 (' + data.accounts.length + ' 个账号 + 全部设置)', 'success', 2500); }
    function _0x_fullRestore() { const inp = document.createElement('input'); inp.type = 'file'; inp.accept = '.json'; inp.onchange = function (e) { const f = e.target.files[0]; if (!f) return; const rd = new FileReader(); rd.onload = function (ev) { try { const data = JSON.parse(ev.target.result); if (!data._meta || data._meta.type !== 'chatgpt-tools-full-backup') { if (Array.isArray(data) && data.length > 0 && data[0].email) { if (!confirm('检测到这是账号列表文件，包含 ' + data.length + ' 个账号。\n\n是否导入到账号列表？')) return; let added = 0; const cur = _0x126(); for (const item of data) { if (item.email && !cur.find(x => x.email === item.email)) { _0x137(item); added++; } } _tmToast('已导入 ' + added + ' 个账号', 'success', 2500); return; } alert('无效的备份文件格式。\n请选择由「备份全部数据」导出的 .json 文件'); return; } const acCount = data.accounts ? data.accounts.length : 0; const hasSettings = !!data.settings; const info = '备份时间: ' + (data._meta.exportedAt ? new Date(data._meta.exportedAt).toLocaleString() : '未知') + '\n账号数量: ' + acCount + '\n包含设置: ' + (hasSettings ? '是' : '否') + '\n\n⚠️ 恢复将覆盖当前所有数据！确定继续？'; if (!confirm(info)) return; if (data.accounts && Array.isArray(data.accounts)) { GM_setValue(_0x4e.ACCOUNTS, data.accounts); try { localStorage.setItem('tm_accounts_backup', JSON.stringify(data.accounts)); } catch (e) { } } if (data.settings) { const s = data.settings; if (s.apiKey !== undefined) GM_setValue(_0x4e.API_KEY, s.apiKey); if (s.regPrefix !== undefined) GM_setValue('tm_reg_prefix', s.regPrefix); if (s.regDomain !== undefined) GM_setValue('tm_reg_domain', s.regDomain); if (s.useCd !== undefined) GM_setValue('tm_use_cd', s.useCd); if (s.customDomains !== undefined) _0x_setCDs(s.customDomains); if (s.tmAddr !== undefined) GM_setValue('tm_tm_addr', s.tmAddr); if (s.tmEpin !== undefined) GM_setValue('tm_tm_epin', s.tmEpin); if (s.teamUrl !== undefined) GM_setValue('tm_team_url', s.teamUrl); if (s.teamKey !== undefined) GM_setValue('tm_team_key', s.teamKey); if (s.autoRedirectTeam !== undefined) GM_setValue(_0x4e.AUTO_REDIRECT_TEAM, s.autoRedirectTeam); if (s.fabPos !== undefined && s.fabPos) GM_setValue('tm_fab_pos', s.fabPos); } _tmToast('数据恢复成功！' + acCount + ' 个账号 + 全部设置', 'success', 3000); const sm = document.getElementById('tm-modal-settings'); if (sm && sm.classList.contains('show')) { sm.classList.remove('show'); setTimeout(() => _0x76a(), 300); } } catch (ex) { alert('恢复失败: ' + ex.message); } }; rd.readAsText(f); }; inp.click(); }
    let _regUnloadGuard = null;
    function _0x_regSaveGuard() { if (_regUnloadGuard) return; _regUnloadGuard = function () { const d = _0x159(); if (d && d.email) { try { const ac = _0x126(); const i = ac.findIndex(x => x.email === d.email); if (i >= 0) ac[i] = { ...ac[i], status: ac[i].status === '注册完成' ? '注册完成' : '注册中(页面关闭)' }; else ac.unshift({ ...d, status: '注册中(页面关闭)' }); GM_setValue(_0x4e.ACCOUNTS, ac); try { localStorage.setItem('tm_accounts_backup', JSON.stringify(ac)); } catch (e) { } } catch (e) { } } }; window.addEventListener('beforeunload', _regUnloadGuard); }
    function _0x_regClearGuard() { if (_regUnloadGuard) { window.removeEventListener('beforeunload', _regUnloadGuard); _regUnloadGuard = null; } }

    /* ═══════════════ DOM 工具 ═══════════════ */
    function _0x1ae(m) { return new Promise(r => setTimeout(r, m)); }
    function _0x1bf(s, t = 0x2710) { return new Promise((r, j) => { const e = document.querySelector(s); if (e) { r(e); return; } const o = new MutationObserver(() => { const el = document.querySelector(s); if (el) { o.disconnect(); r(el); } }); o.observe(document.body, { childList: !0, subtree: !0 }); setTimeout(() => { o.disconnect(); j(new Error('元素未找到: ' + s)); }, t); }); }
    function _0x1c0(i, v) { i.focus(); const n = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set; n.call(i, v); i.dispatchEvent(new Event('input', { bubbles: !0, composed: !0 })); i.dispatchEvent(new Event('change', { bubbles: !0, composed: !0 })); for (const c of v) { i.dispatchEvent(new KeyboardEvent('keydown', { key: c, bubbles: !0 })); i.dispatchEvent(new KeyboardEvent('keypress', { key: c, bubbles: !0 })); i.dispatchEvent(new KeyboardEvent('keyup', { key: c, bubbles: !0 })); } i.dispatchEvent(new Event('blur', { bubbles: !0 })); i.focus(); }
    async function _0x1d1(e, v) { console.log('[AutoReg] Setting spinbutton:', v); e.focus(); e.click(); await _0x1ae(0xc8); if (!e.textContent.match(/\d/)) { e.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: !0 })); await _0x1ae(0x64); } let m = 0x64; while (m-- > 0x0) { let t = e.textContent || e.getAttribute('aria-valuenow') || ''; let c = parseInt(t.replace(/\D/g, '')); if (isNaN(c)) { e.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: !0 })); await _0x1ae(0x64); continue; } let d = v - c; if (d === 0x0) break; const k = d > 0x0 ? 'ArrowUp' : 'ArrowDown'; e.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: !0 })); await _0x1ae(0x50); } e.setAttribute('aria-valuenow', v); e.dispatchEvent(new Event('change', { bubbles: !0 })); e.dispatchEvent(new Event('blur', { bubbles: !0 })); await _0x1ae(0x64); }
    function _0x1e2(e) { e.click(); e.dispatchEvent(new MouseEvent('click', { bubbles: !0, cancelable: !0 })); }
    function _0x1f3(s, ts) { const es = document.querySelectorAll(s); for (const e of es) { const t = e.textContent.toLowerCase(); for (const x of ts) { if (t.includes(x.toLowerCase())) return e; } } return null; }

    /* ═══════════════ Toast 通知 ═══════════════ */
    let _toastTimer = null;
    function _tmToast(msg, type = 'loading', duration = 0) { let t = document.getElementById('tm-toast'); if (!t) { t = document.createElement('div'); t.id = 'tm-toast'; t.className = 'tm-toast'; document.body.appendChild(t); } if (_toastTimer) { clearTimeout(_toastTimer); _toastTimer = null; } t.className = 'tm-toast ' + type + ' show'; t.innerHTML = (type === 'loading' ? '<div class="sp"></div>' : type === 'success' ? '<span>✅</span>' : '<span>❌</span>') + '<span>' + msg + '</span>'; if (duration > 0) { _toastTimer = setTimeout(() => { t.classList.remove('show'); _toastTimer = null; }, duration); } }
    function _tmToastHide() { const t = document.getElementById('tm-toast'); if (t) t.classList.remove('show'); if (_toastTimer) { clearTimeout(_toastTimer); _toastTimer = null; } }

    /* ═══════════════ 状态栏 ═══════════════ */
    function _0x437() { if (document.getElementById('tm-status-bar')) return; const b = document.createElement('div'); b.id = 'tm-status-bar'; b.className = 'tm-sbar'; b.innerHTML = '<div class="sp"></div><span id="tm-status-text">自动注册中...</span><button class="x" id="tm-stop-reg">✕ 终止</button>'; document.body.appendChild(b); document.getElementById('tm-stop-reg').onclick = _0x98c; }
    function _0x98c() { _0x19d(); _0xa9d(); alert('已终止自动注册'); }
    function _0xbae(t) { const b = document.getElementById('tm-status-bar'); const e = document.getElementById('tm-status-text'); if (b && e) { e.innerText = t; b.classList.add('show'); } }
    function _0xa9d() { const b = document.getElementById('tm-status-bar'); if (b) b.classList.remove('show'); }

    /* ═══════════════ 移动端弹窗滚动锁定 ═══════════════ */
    function _tmModalScrollLock() { const check = () => { const anyOpen = document.querySelector('.tm-ov.show'); document.body.style.overflow = anyOpen ? 'hidden' : ''; }; const obs = new MutationObserver(check); setTimeout(() => { document.querySelectorAll('.tm-ov').forEach(ov => { obs.observe(ov, { attributes: true, attributeFilter: ['class'] }); }); }, 2000); }

    /* ═══════════════ 初始化入口 ═══════════════ */
    function _0x204() { if (document.getElementById(_0xg(0x0))) return; _0x_restoreFromBackup(); _syncPull(); _0x215(); _0x326(); _0x437(); _0x548(); _tmModalScrollLock(); }

    /* ═══════════════ 主面板 ═══════════════ */
    function _0x215() {
        const r = document.createElement('div'); r.id = _0xg(0x0);
        const p = document.createElement('div'); p.className = 'tm-panel';
        p.innerHTML = `
<div class="tm-p-head"><div class="tm-p-title">ChatGPT Tools</div><div class="tm-p-ver">v9.4</div></div>
<div class="tm-p-body">
<div class="tm-g">
<button class="tm-gi" data-act="token"><div class="tm-gi-ic" style="background:linear-gradient(135deg,#059669,#047857)">🔑</div><div class="tm-gi-lb">复制 Token</div></button>
<button class="tm-gi" data-act="pay"><div class="tm-gi-ic" style="background:linear-gradient(135deg,#3b82f6,#2563eb)">💳</div><div class="tm-gi-lb">Plus 支付</div></button>
<button class="tm-gi" data-act="team"><div class="tm-gi-ic" style="background:linear-gradient(135deg,#f59e0b,#d97706)">🔗</div><div class="tm-gi-lb">Team 链接</div></button>
<button class="tm-gi" data-act="register"><div class="tm-gi-ic" style="background:linear-gradient(135deg,#8b5cf6,#7c3aed)">🚀</div><div class="tm-gi-lb">自动注册</div></button>
<button class="tm-gi" data-act="accounts"><div class="tm-gi-ic" style="background:linear-gradient(135deg,#ec4899,#db2777)">📋</div><div class="tm-gi-lb">账号列表</div></button>
<button class="tm-gi" data-act="inbox"><div class="tm-gi-ic" style="background:linear-gradient(135deg,#06b6d4,#0891b2)">📬</div><div class="tm-gi-lb">收件箱</div></button>
<button class="tm-gi" data-act="export"><div class="tm-gi-ic" style="background:linear-gradient(135deg,#f97316,#ea580c)">📦</div><div class="tm-gi-lb">导出对话</div></button>
<button class="tm-gi" data-act="settings"><div class="tm-gi-ic" style="background:linear-gradient(135deg,#6b7280,#4b5563)">⚙️</div><div class="tm-gi-lb">设置</div></button>
</div>
<div class="tm-sep"></div>
<button class="tm-li" data-act="push"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>推送当前账号到 Team</button>
<button class="tm-li" data-act="about"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>关于</button>
<button class="tm-li" data-act="logout" style="color:rgba(239,68,68,.9)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>退出登录</button>
</div>`;
        const fab = document.createElement('button'); fab.className = 'tm-fab'; fab.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>';
        /* 拖动逻辑 */
        let _drag = false, _moved = false, _sx, _sy, _sl, _st, _isTouch = false;
        function _onStart(e) { if (p.classList.contains('show')) return; _drag = true; _moved = false; _isTouch = !!e.touches; const ev = e.touches ? e.touches[0] : e; const rc = r.getBoundingClientRect(); _sx = ev.clientX; _sy = ev.clientY; _sl = rc.left; _st = rc.top; r.classList.add('dragging'); fab.classList.add('dragging'); if (!_isTouch) e.preventDefault(); }
        function _onMove(e) { if (!_drag) return; const ev = e.touches ? e.touches[0] : e; const dx = ev.clientX - _sx, dy = ev.clientY - _sy; if (Math.abs(dx) > 3 || Math.abs(dy) > 3) { _moved = true; e.preventDefault(); } if (!_moved) return; let nl = _sl + dx, nt = _st + dy; nl = Math.max(0, Math.min(nl, window.innerWidth - 52)); nt = Math.max(0, Math.min(nt, window.innerHeight - 52)); r.style.right = 'auto'; r.style.bottom = 'auto'; r.style.left = nl + 'px'; r.style.top = nt + 'px'; }
        function _onEnd(e) { if (!_drag) return; _drag = false; r.classList.remove('dragging'); fab.classList.remove('dragging'); if (_moved) { const rc = r.getBoundingClientRect(); GM_setValue('tm_fab_pos', JSON.stringify({ x: rc.left, y: rc.top })); if (_isTouch) { _moved = false; } else { e.preventDefault(); e.stopPropagation(); } } else if (_isTouch) { _togglePanel(); } }
        fab.addEventListener('mousedown', _onStart); fab.addEventListener('touchstart', _onStart, { passive: true });
        document.addEventListener('mousemove', _onMove); document.addEventListener('touchmove', _onMove, { passive: false });
        document.addEventListener('mouseup', _onEnd); document.addEventListener('touchend', _onEnd);
        /* 移动端遮罩 */
        const _isMobile = () => window.innerWidth <= 768;
        const backdrop = document.createElement('div'); backdrop.className = 'tm-panel-backdrop'; document.body.appendChild(backdrop);
        function _togglePanel(show) { const s = typeof show === 'boolean' ? show : !p.classList.contains('show'); if (s) { p.classList.add('show'); fab.classList.add('open'); if (_isMobile()) { backdrop.classList.add('show'); document.body.style.overflow = 'hidden'; } } else { p.classList.remove('show'); fab.classList.remove('open'); backdrop.classList.remove('show'); document.body.style.overflow = ''; } }
        fab.addEventListener('click', (e) => { e.stopPropagation(); if (_isTouch) return; if (_moved) { _moved = false; return; } _togglePanel(); });
        backdrop.addEventListener('click', () => _togglePanel(false));
        document.addEventListener('click', (e) => { if (!r.contains(e.target) && !backdrop.contains(e.target) && p.classList.contains('show')) _togglePanel(false); });
        r.appendChild(p); r.appendChild(fab); document.body.appendChild(r);
        /* 恢复保存的位置 */
        try { const sp = GM_getValue('tm_fab_pos'); if (sp) { const pos = JSON.parse(sp); r.style.right = 'auto'; r.style.bottom = 'auto'; r.style.left = Math.min(Math.max(0, pos.x), window.innerWidth - 52) + 'px'; r.style.top = Math.min(Math.max(0, pos.y), window.innerHeight - 52) + 'px'; } } catch (e) { }
        p.addEventListener('click', async (e) => { e.stopPropagation(); const item = e.target.closest('[data-act]'); if (!item) return; const act = item.dataset.act; _togglePanel(false); switch (act) { case 'token': _0xcbf(); break; case 'pay': _0xdd0(); break; case 'team': _0xee1(); break; case 'register': _0x659(); break; case 'accounts': _0xff2(); break; case 'inbox': _0x_showInbox(); break; case 'export': _expShowExportDialog(); break; case 'push': _0x_doPush(); break; case 'settings': _0x76a(); break; case 'about': _0x103(); break; case 'logout': _0xLogout(); break; } });
    }

    /* ═══════════════ Modal 创建 ═══════════════ */
    function _0x326() {
        // Pay Modal
        if (!document.getElementById('tm-modal-pay')) {
            const m = document.createElement('div'); m.id = 'tm-modal-pay'; m.className = 'tm-ov'; m.innerHTML = `
<div class="tm-md" style="max-width:400px">
<div class="tm-md-h"><div class="tm-md-t">✅ 生成成功</div><button class="tm-md-x" data-close>✕</button></div>
<div class="tm-md-b">
<div class="tm-alert tm-alert-w">⚠️ 请在无痕模式 + 全局节点下打开</div>
<div class="tm-lbl">支付链接</div>
<div class="tm-code" id="tm-modal-pay-code"></div>
</div>
<div class="tm-md-f"><button class="tm-btn tm-btn-s" data-close>关闭</button><button class="tm-btn tm-btn-p" id="tm-modal-pay-copy">📋 复制</button><button class="tm-btn tm-btn-sm" style="background:rgba(59,130,246,.15);color:rgba(96,165,250,.9);border-color:rgba(59,130,246,.2)" id="tm-modal-pay-open">🔗 打开</button></div>
</div>`; document.body.appendChild(m);
            m.querySelectorAll('[data-close]').forEach(b => b.onclick = () => m.classList.remove('show'));
            document.getElementById('tm-modal-pay-copy').onclick = function () { _0x7b(document.getElementById('tm-modal-pay-code').innerText); this.innerText = '✅ 已复制'; setTimeout(() => this.innerText = '📋 复制', 1200); };
            document.getElementById('tm-modal-pay-open').onclick = function () { window.open(document.getElementById('tm-modal-pay-code').innerText, '_blank'); };
        }

        // Settings Modal
        if (!document.getElementById('tm-modal-settings')) {
            const m = document.createElement('div'); m.id = 'tm-modal-settings'; m.className = 'tm-ov'; m.innerHTML = `
<div class="tm-md" style="max-width:440px">
<div class="tm-md-h"><div class="tm-md-t">⚙️ 设置</div><button class="tm-md-x" data-close>✕</button></div>
<div class="tm-md-b" style="max-height:480px">
<div class="tm-fld"><label class="tm-lbl">NPCmail 密钥</label><input type="text" class="tm-inp" id="tm-settings-apikey" placeholder="输入 NPCmail API 密钥"><div style="font-size:10px;color:rgba(255,255,255,.45);margin-top:4px">API: ${_0x3c}</div></div>
<div style="height:1px;background:rgba(255,255,255,.08);margin:14px 0"></div>
<div class="tm-fld"><label class="tm-lbl">邮箱配置 (可选)</label><input type="text" class="tm-inp" id="tm-settings-reg-prefix" placeholder="邮箱前缀 (留空随机)" style="margin-bottom:6px"><select class="tm-inp tm-sel" id="tm-settings-reg-domain"><option value="">随机域名</option><option value="" disabled>加载中...</option></select></div>
<div style="height:1px;background:rgba(255,255,255,.08);margin:14px 0"></div>
<div class="tm-fld">
<label class="tm-lbl">🌐 自定义域名 + TempMail</label>
<div style="font-size:10px;color:rgba(255,255,255,.45);margin-bottom:6px">CF 邮件路由转发到临时邮箱，无需密钥</div>
<label class="tm-chk" style="margin-bottom:8px"><input type="checkbox" id="tm-settings-use-cd">启用自定义域名注册</label>
<div id="tm-cd-section" style="display:none">
<div style="display:flex;gap:4px;margin-bottom:6px"><input type="text" class="tm-inp" id="tm-cd-input" placeholder="域名 (如 example.com)" style="flex:1"><button class="tm-btn tm-btn-p tm-btn-sm" id="tm-cd-add">添加</button></div>
<div id="tm-cd-list" style="margin-bottom:8px"></div>
<div class="tm-lbl" style="margin-top:8px">📬 TempMail 取件</div>
<input type="text" class="tm-inp" id="tm-settings-tm-addr" placeholder="邮箱 (如 mybox@mailto.plus)" style="margin-bottom:4px">
<input type="text" class="tm-inp" id="tm-settings-tm-epin" placeholder="PIN 码 (没有可留空)">
<div style="font-size:9px;color:rgba(255,255,255,.4);margin-top:3px">支持: ${_0x_TM_DOMAINS.join(', ')}</div>
</div></div>
<div style="height:1px;background:rgba(255,255,255,.08);margin:14px 0"></div>
<div class="tm-fld">
<label class="tm-lbl">🔗 Team 管理后台</label>
<div style="font-size:10px;color:rgba(255,255,255,.45);margin-bottom:6px">配置后可在账号列表中一键推送账号到管理系统</div>
<input type="text" class="tm-inp" id="tm-settings-team-url" placeholder="后台地址 (如 http://127.0.0.1:8008)" style="margin-bottom:4px">
<input type="password" class="tm-inp" id="tm-settings-team-key" placeholder="后台密钥">
</div>
<div style="height:1px;background:rgba(255,255,255,.08);margin:14px 0"></div>
<div class="tm-fld"><label class="tm-chk"><input type="checkbox" id="tm-settings-auto-redirect">注册后自动跳转 Team 短链接</label></div>
<div style="height:1px;background:rgba(255,255,255,.08);margin:14px 0"></div>
<div class="tm-fld">
<label class="tm-lbl">☁️ 云同步 (自动)</label>
<div style="font-size:10px;color:rgba(255,255,255,.45);margin-bottom:6px">输入管理员生成的 API 密钥，账号将自动上传到云端</div>
<input type="text" class="tm-inp" id="tm-settings-sync-url" placeholder="云同步地址 (如 https://xxx.workers.dev)" style="margin-bottom:4px">
<input type="text" class="tm-inp" id="tm-settings-sync-apikey" placeholder="同步密钥 (管理员后台生成)">
<div style="display:flex;gap:4px;margin-top:6px"><button class="tm-btn tm-btn-sm" id="tm-sync-test" style="background:rgba(6,182,212,.15);color:rgba(34,211,238,.9);border-color:rgba(6,182,212,.2);flex:1">🔗 测试连接</button><button class="tm-btn tm-btn-sm" id="tm-sync-push-all" style="background:rgba(168,85,247,.15);color:rgba(192,132,252,.9);border-color:rgba(168,85,247,.2);flex:1">📤 全量上传</button><button class="tm-btn tm-btn-sm" id="tm-sync-pull" style="background:rgba(16,185,129,.15);color:rgba(16,185,129,.9);border-color:rgba(16,185,129,.2);flex:1">📥 拉取</button></div>
</div>
<div style="height:1px;background:rgba(255,255,255,.08);margin:14px 0"></div>
<div class="tm-fld">
<label class="tm-lbl">💾 数据备份与恢复</label>
<div style="font-size:10px;color:rgba(255,255,255,.45);margin-bottom:8px">一键备份所有账号、设置和自定义域名到文件，换浏览器或重装时可恢复</div>
<div style="display:flex;gap:6px"><button class="tm-btn tm-btn-sm" id="tm-backup-export" style="background:rgba(59,130,246,.15);color:rgba(96,165,250,.9);border-color:rgba(59,130,246,.2);flex:1;padding:10px 8px">📦 备份全部数据</button><button class="tm-btn tm-btn-sm" id="tm-backup-import" style="background:rgba(245,158,11,.12);color:rgba(251,191,36,.9);border-color:rgba(245,158,11,.2);flex:1;padding:10px 8px">📂 导入备份</button></div>
</div>
<div id="tm-settings-status" style="display:none;padding:8px 10px;border-radius:6px;font-size:12px;margin-top:12px"></div>
</div>
<div class="tm-md-f"><button class="tm-btn tm-btn-s" data-close>关闭</button><button class="tm-btn tm-btn-s" id="tm-settings-test" style="background:rgba(59,130,246,.15);color:rgba(96,165,250,.9);border-color:rgba(59,130,246,.2)">测试 NPCmail 连接</button><button class="tm-btn tm-btn-s" id="tm-settings-test-team" style="background:rgba(245,158,11,.12);color:rgba(251,191,36,.9);border-color:rgba(245,158,11,.2)">测试 Team</button><button class="tm-btn tm-btn-p" id="tm-settings-save">💾 保存</button></div>
</div>`; document.body.appendChild(m);
            m.querySelectorAll('[data-close]').forEach(b => b.onclick = () => m.classList.remove('show'));
            document.getElementById('tm-settings-test').onclick = async function () { const st = document.getElementById('tm-settings-status'); const k = document.getElementById('tm-settings-apikey').value.trim(); if (!k) { st.style.display = 'block'; st.style.background = 'rgba(239,68,68,.12)'; st.style.color = 'rgba(239,68,68,.9)'; st.innerText = '❌ 请输入密钥'; return; } GM_setValue(_0x4e.API_KEY, k); this.innerText = '测试中...'; try { const i = await _0xe2(); st.style.display = 'block'; st.style.background = 'rgba(16,185,129,.12)'; st.style.color = 'rgba(16,185,129,.9)'; st.innerText = '✅ 连接成功！剩余调用次数: ' + i.remaining_calls; } catch (e) { st.style.display = 'block'; st.style.background = 'rgba(239,68,68,.12)'; st.style.color = 'rgba(239,68,68,.9)'; st.innerText = '❌ ' + e.message; } this.innerText = '测试 NPCmail'; };
            document.getElementById('tm-settings-use-cd').onchange = function () { document.getElementById('tm-cd-section').style.display = this.checked ? 'block' : 'none'; };
            document.getElementById('tm-cd-add').onclick = function () { const v = document.getElementById('tm-cd-input').value; if (_0x_addCD(v)) { document.getElementById('tm-cd-input').value = ''; _0x_renderCDs(); } else { alert('域名格式不正确或已存在'); } };
            document.getElementById('tm-settings-test-team').onclick = async function () { const st = document.getElementById('tm-settings-status'); const url = document.getElementById('tm-settings-team-url').value.trim(); const key = document.getElementById('tm-settings-team-key').value.trim(); if (!url || !key) { st.style.display = 'block'; st.style.background = 'rgba(239,68,68,.12)'; st.style.color = 'rgba(239,68,68,.9)'; st.innerText = '❌ 请输入 Team 后台地址和密钥'; return; } this.innerText = '测试中...'; try { const r = await _0x_teamReq(url, 'GET', '/external/health', key); st.style.display = 'block'; st.style.background = 'rgba(16,185,129,.12)'; st.style.color = 'rgba(16,185,129,.9)'; st.innerText = '✅ Team 后台连接成功！'; } catch (e) { st.style.display = 'block'; st.style.background = 'rgba(239,68,68,.12)'; st.style.color = 'rgba(239,68,68,.9)'; st.innerText = '❌ ' + e.message; } this.innerText = '测试 Team'; };
            document.getElementById('tm-sync-test').onclick = async function () { const st = document.getElementById('tm-settings-status'); const url = document.getElementById('tm-settings-sync-url').value.trim(); const key = document.getElementById('tm-settings-sync-apikey').value.trim(); if (!url || !key) { st.style.display = 'block'; st.style.background = 'rgba(239,68,68,.12)'; st.style.color = 'rgba(239,68,68,.9)'; st.innerText = '❌ 请输入云同步地址和密钥'; return; } this.innerText = '测试中...'; GM_setValue('tm_sync_url', url); GM_setValue('tm_sync_apikey', key); try { const r = await _workerReq('GET', '/health'); if (!r) { throw new Error('无响应，请检查地址是否正确'); } if (r.keyValid === false) { st.style.display = 'block'; st.style.background = 'rgba(251,191,36,.12)'; st.style.color = 'rgba(251,191,36,.9)'; st.innerText = '⚠️ 云端已连接，但密钥无效，请检查'; } else { st.style.display = 'block'; st.style.background = 'rgba(16,185,129,.12)'; st.style.color = 'rgba(16,185,129,.9)'; st.innerText = '✅ 云端连接成功，密钥有效！'; } } catch (e) { st.style.display = 'block'; st.style.background = 'rgba(239,68,68,.12)'; st.style.color = 'rgba(239,68,68,.9)'; st.innerText = '❌ ' + e.message; } this.innerText = '🔗 测试连接'; };
            document.getElementById('tm-sync-push-all').onclick = async function () { const url = document.getElementById('tm-settings-sync-url').value.trim(); const key = document.getElementById('tm-settings-sync-apikey').value.trim(); if (!url || !key) { alert('请先填写云同步地址和密钥'); return; } GM_setValue('tm_sync_url', url); GM_setValue('tm_sync_apikey', key); this.innerText = '上传中...'; try { const r = await _syncPushAll(); const st = document.getElementById('tm-settings-status'); st.style.display = 'block'; st.style.background = 'rgba(16,185,129,.12)'; st.style.color = 'rgba(16,185,129,.9)'; st.innerText = '✅ 全量上传成功！共 ' + r.count + ' 个账号'; _tmToast('全量上传成功！共 ' + r.count + ' 个账号', 'success', 3000); } catch (e) { alert('上传失败: ' + e.message); } this.innerText = '📤 全量上传'; };
            document.getElementById('tm-sync-pull').onclick = async function () { const url = document.getElementById('tm-settings-sync-url').value.trim(); const key = document.getElementById('tm-settings-sync-apikey').value.trim(); if (!url || !key) { alert('请先填写云同步地址和密钥'); return; } GM_setValue('tm_sync_url', url); GM_setValue('tm_sync_apikey', key); this.innerText = '拉取中...'; try { await _syncPull(); const st = document.getElementById('tm-settings-status'); st.style.display = 'block'; st.style.background = 'rgba(16,185,129,.12)'; st.style.color = 'rgba(16,185,129,.9)'; st.innerText = '✅ 拉取完成！'; } catch (e) { alert('拉取失败: ' + e.message); } this.innerText = '📥 拉取'; };
            document.getElementById('tm-settings-save').onclick = function () { GM_setValue(_0x4e.API_KEY, document.getElementById('tm-settings-apikey').value.trim()); GM_setValue(_0x4e.AUTO_REDIRECT_TEAM, document.getElementById('tm-settings-auto-redirect').checked); GM_setValue('tm_reg_prefix', document.getElementById('tm-settings-reg-prefix').value.trim()); GM_setValue('tm_reg_domain', document.getElementById('tm-settings-reg-domain').value); GM_setValue('tm_use_cd', document.getElementById('tm-settings-use-cd').checked); GM_setValue('tm_tm_addr', document.getElementById('tm-settings-tm-addr').value.trim()); GM_setValue('tm_tm_epin', document.getElementById('tm-settings-tm-epin').value.trim()); GM_setValue('tm_team_url', document.getElementById('tm-settings-team-url').value.trim()); GM_setValue('tm_team_key', document.getElementById('tm-settings-team-key').value.trim()); const _oldSyncKey = GM_getValue('tm_sync_apikey', ''); const _newSyncUrl = document.getElementById('tm-settings-sync-url').value.trim(); const _newSyncKey = document.getElementById('tm-settings-sync-apikey').value.trim(); GM_setValue('tm_sync_url', _newSyncUrl); GM_setValue('tm_sync_apikey', _newSyncKey); if (_newSyncKey && _newSyncUrl && _newSyncKey !== _oldSyncKey) { setTimeout(async () => { try { const r = await _syncPushAll(); _tmToast('API密钥已设置，自动上传了 ' + r.count + ' 个账号', 'success', 3000); console.log('[CloudSync] 首次设置密钥，自动全量上传完成'); } catch (e) { console.warn('[CloudSync] 首次全量上传失败:', e.message); } }, 500); } m.classList.remove('show'); };
            document.getElementById('tm-backup-export').onclick = _0x_fullBackup;
            document.getElementById('tm-backup-import').onclick = _0x_fullRestore;
        }

        // Accounts Modal
        if (!document.getElementById('tm-modal-accounts')) {
            const m = document.createElement('div'); m.id = 'tm-modal-accounts'; m.className = 'tm-ov'; m.innerHTML = `
<div class="tm-md" style="max-width:440px">
<div class="tm-md-h"><div class="tm-md-t">📋 账号列表</div><button class="tm-md-x" data-close>✕</button></div>
<div class="tm-md-b" id="tm-accounts-list" style="max-height:380px"></div>
<div class="tm-md-f" style="flex-wrap:wrap;gap:4px"><button class="tm-btn tm-btn-s" data-close>关闭</button><button class="tm-btn tm-btn-sm" id="tm-acc-export" style="background:rgba(59,130,246,.15);color:rgba(96,165,250,.9);border-color:rgba(59,130,246,.2)">📤 导出</button><button class="tm-btn tm-btn-sm" id="tm-acc-import" style="background:rgba(16,185,129,.15);color:rgba(16,185,129,.9);border-color:rgba(16,185,129,.2)">📥 导入</button><button class="tm-btn tm-btn-sm" id="tm-acc-import-email" style="background:rgba(168,85,247,.15);color:rgba(192,132,252,.9);border-color:rgba(168,85,247,.2)">📬 邮箱导入</button><button class="tm-btn tm-btn-sm" id="tm-acc-export-email" style="background:rgba(6,182,212,.12);color:rgba(34,211,238,.9);border-color:rgba(6,182,212,.15)">📧 邮箱导出</button></div>
</div>`; document.body.appendChild(m);
            m.querySelectorAll('[data-close]').forEach(b => b.onclick = () => m.classList.remove('show'));
            document.getElementById('tm-acc-export').onclick = _0x_exportAccounts;
            document.getElementById('tm-acc-import').onclick = _0x_importAccounts;
            document.getElementById('tm-acc-import-email').onclick = _0x_importEmails;
            document.getElementById('tm-acc-export-email').onclick = _0x_exportEmails;
        }

        // Inbox Modal
        if (!document.getElementById('tm-modal-inbox')) {
            const m = document.createElement('div'); m.id = 'tm-modal-inbox'; m.className = 'tm-ov'; m.innerHTML = `
<div class="tm-md" style="max-width:520px">
<div class="tm-md-h"><div class="tm-md-t">📬 收件箱</div><button class="tm-md-x" data-close>✕</button></div>
<div class="tm-md-b" style="max-height:500px">
<div class="tm-fld"><label class="tm-lbl">选择邮箱</label>
<div style="display:flex;gap:6px"><select class="tm-inp tm-sel" id="tm-inbox-email" style="flex:1"><option value="">选择邮箱...</option></select><button class="tm-btn tm-btn-p tm-btn-sm" id="tm-inbox-fetch">📥 获取</button></div></div>
<div id="tm-inbox-list"><div class="tm-empty">📭 选择邮箱后点击获取</div></div>
<div id="tm-inbox-detail" style="display:none"></div>
</div>
<div class="tm-md-f"><button class="tm-btn tm-btn-s" data-close>关闭</button><span id="tm-inbox-count" style="font-size:11px;color:rgba(255,255,255,.4);margin-right:auto;display:flex;align-items:center"></span></div>
</div>`; document.body.appendChild(m);
            m.querySelectorAll('[data-close]').forEach(b => b.onclick = () => m.classList.remove('show'));
            document.getElementById('tm-inbox-fetch').onclick = async function () { const email = document.getElementById('tm-inbox-email').value; if (!email) { alert('请选择邮箱'); return; } this.innerText = '加载中...'; this.disabled = true; document.getElementById('tm-inbox-detail').style.display = 'none'; document.getElementById('tm-inbox-list').style.display = 'block'; document.getElementById('tm-inbox-list').innerHTML = '<div class="tm-empty"><div class="sp" style="width:18px;height:18px;border:2px solid rgba(255,255,255,.15);border-top-color:rgba(255,255,255,.6);border-radius:50%;animation:tm-spin .7s linear infinite;margin:0 auto 8px"></div>正在获取邮件...</div>'; try { const mails = await _0x_fetchAllMails(email); _0x_renderMailList(mails, email); document.getElementById('tm-inbox-count').innerText = mails.length + ' 封邮件'; } catch (e) { document.getElementById('tm-inbox-list').innerHTML = '<div class="tm-empty" style="color:rgba(239,68,68,.8)">❌ ' + e.message + '</div>'; document.getElementById('tm-inbox-count').innerText = ''; } this.innerText = '📥 获取'; this.disabled = false; };
        }

        // About Modal
        if (!document.getElementById('tm-modal-about')) {
            const m = document.createElement('div'); m.id = 'tm-modal-about'; m.className = 'tm-ov'; m.innerHTML = `
<div class="tm-md" style="max-width:360px">
<div class="tm-md-h"><div class="tm-md-t">ℹ️ 关于</div><button class="tm-md-x" data-close>✕</button></div>
<div class="tm-md-b" style="text-align:center">
<div style="width:56px;height:56px;margin:0 auto 12px;border-radius:14px;background:linear-gradient(135deg,#10a37f,#0e8c6b);display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 6px 16px rgba(16,163,127,.3)">⚡</div>
<div style="font-size:18px;font-weight:700;color:rgba(255,255,255,.95);margin-bottom:2px;text-shadow:0 1px 2px rgba(0,0,0,.15)">ChatGPT Tools</div>
<div style="font-size:11px;color:rgba(255,255,255,.45);margin-bottom:16px">v9.4</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:16px;text-align:center">
<div style="padding:8px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);border-radius:10px;font-size:11px;color:rgba(255,255,255,.6)">🔑 Token</div>
<div style="padding:8px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);border-radius:10px;font-size:11px;color:rgba(255,255,255,.6)">💳 Plus</div>
<div style="padding:8px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);border-radius:10px;font-size:11px;color:rgba(255,255,255,.6)">🚀 注册</div>
<div style="padding:8px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);border-radius:10px;font-size:11px;color:rgba(255,255,255,.6)">📦 导出对话</div>
</div>
<a href="https://linux.do/u/npc1/summary" target="_blank" style="display:flex;align-items:center;justify-content:center;gap:6px;padding:10px;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.2);border-radius:10px;color:rgba(16,185,129,.9);text-decoration:none;font-size:12px;font-weight:500;transition:.2s">
👨‍💻 开发者: NPC →</a>
</div>
<div class="tm-md-f"><button class="tm-btn tm-btn-s" data-close>关闭</button></div>
</div>`; document.body.appendChild(m);
            m.querySelectorAll('[data-close]').forEach(b => b.onclick = () => m.classList.remove('show'));
        }

        // Success Modal
        if (!document.getElementById('tm-modal-success')) {
            const m = document.createElement('div'); m.id = 'tm-modal-success'; m.className = 'tm-ov'; m.innerHTML = `
<div class="tm-md" style="max-width:360px;text-align:center">
<div class="tm-md-b" style="padding:24px">
<div class="tm-suc-ic">🎉</div>
<div class="tm-suc-t">注册成功！</div>
<div class="tm-suc-sub">账号已保存到列表</div>
<div class="tm-suc-info">
<div class="tm-suc-row"><span class="tm-suc-lb">邮箱</span><span class="tm-suc-val" id="tm-success-email"></span></div>
<div class="tm-suc-row"><span class="tm-suc-lb">密码</span><span class="tm-suc-val" id="tm-success-password"></span></div>
</div>
<div class="tm-suc-redir" id="tm-suc-redir-wrap">
<div class="tm-suc-redir-txt"><span id="tm-success-countdown">3</span>s 后跳转...</div>
<div class="tm-suc-prog"><div class="tm-suc-prog-bar" id="tm-success-progress-bar"></div></div>
</div>
<div style="display:flex;gap:6px;justify-content:center;margin-top:12px">
<button class="tm-btn tm-btn-d" id="tm-success-cancel">取消</button>
<button class="tm-btn tm-btn-p" id="tm-success-copy">📋 复制</button>
</div>
</div>
</div>`; document.body.appendChild(m);
        }
    }

    /* ═══════════════ 收件箱逻辑 ═══════════════ */
    let _inboxCache = [];
    function _0x_showInbox() {
        const sel = document.getElementById('tm-inbox-email'); sel.innerHTML = '<option value="">选择邮箱...</option>';
        const ac = _0x126(); ac.forEach(a => { const o = document.createElement('option'); o.value = a.email; o.innerText = a.email; if (a.customDomain) o.dataset.cd = '1'; sel.appendChild(o); });
        const tmA = GM_getValue('tm_tm_addr', ''); if (tmA && !ac.find(a => a.email === tmA)) { const o = document.createElement('option'); o.value = '__tm__' + tmA; o.innerText = tmA + ' (临时邮箱)'; o.dataset.cd = '1'; sel.appendChild(o); }
        document.getElementById('tm-inbox-list').innerHTML = '<div class="tm-empty">📭 选择邮箱后点击获取</div>';
        document.getElementById('tm-inbox-list').style.display = 'block';
        document.getElementById('tm-inbox-detail').style.display = 'none';
        document.getElementById('tm-inbox-count').innerText = '';
        _inboxCache = []; document.getElementById('tm-modal-inbox').classList.add('show');
    }

    async function _0x_fetchAllMails(email) {
        const ac = _0x126(); const acc = ac.find(a => a.email === email); const isCD = acc && acc.customDomain; const isTmDirect = email.startsWith('__tm__');
        const tmAddr = GM_getValue('tm_tm_addr', ''); const tmEpin = GM_getValue('tm_tm_epin', '');
        if (isTmDirect || isCD) {
            const useAddr = isTmDirect ? email.replace('__tm__', '') : tmAddr; if (!useAddr) throw new Error('请先在设置中配置 TempMail 取件邮箱');
            const inbox = await _0x_tmInbox(useAddr, tmEpin); if (!inbox.mail_list || inbox.mail_list.length === 0) return [];
            const mails = []; for (const m of inbox.mail_list) { try { const det = await _0x_tmMail(m.mail_id, useAddr, tmEpin); mails.push({ id: m.mail_id, subject: det.subject || m.subject || '(无主题)', from: det.from_mail || m.from_mail || '未知', fromName: det.from_name || m.from_name || '', time: m.time || '', date: det.date || '', text: det.text || '', html: det.html || '', source: 'tempmail' }); } catch (e) { mails.push({ id: m.mail_id, subject: m.subject || '(无主题)', from: m.from_mail || '未知', fromName: m.from_name || '', time: m.time || '', text: '', html: '', source: 'tempmail' }); } }
            _inboxCache = mails; return mails;
        } else {
            try {
                const r = await _0x_npcMails(email); let mails = []; const arr = Array.isArray(r) ? r : (r && r.messages ? r.messages : []); mails = arr.map((m, i) => ({ id: m.id || i, subject: m.subject || '(无主题)', from: m.sender || m.from || '未知', fromName: '', time: m.received_at ? new Date(m.received_at).toLocaleString() : '', date: m.received_at || '', text: m.body || m.text || '', html: m.html || '', isRead: m.is_read || false, source: 'npcmail' }));
                _inboxCache = mails; return mails;
            } catch (e) { throw new Error('获取失败: ' + e.message); }
        }
    }

    function _0x_parseMailHTML(html) { if (!html) return ''; try { const doc = new DOMParser().parseFromString(html, 'text/html'); doc.querySelectorAll('script,style,link,meta').forEach(el => el.remove()); const links = doc.querySelectorAll('a[href]'); links.forEach(a => { a.setAttribute('target', '_blank'); a.setAttribute('rel', 'noopener'); a.style.color = 'rgba(96,165,250,.9)'; }); const imgs = doc.querySelectorAll('img'); imgs.forEach(img => { img.style.maxWidth = '100%'; img.style.height = 'auto'; img.style.borderRadius = '6px'; }); let h = doc.body.innerHTML || ''; h = h.replace(/on\w+\s*=\s*"[^"]*"/gi, ''); h = h.replace(/on\w+\s*=\s*'[^']*'/gi, ''); return h; } catch (e) { return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim(); } }

    function _0x_renderMailList(mails, email) {
        const el = document.getElementById('tm-inbox-list');
        if (!mails || mails.length === 0) { el.innerHTML = '<div class="tm-empty">📭 该邮箱暂无邮件</div>'; return; }
        el.innerHTML = mails.map((m, i) => {
            const sender = m.fromName ? (m.fromName + ' &lt;' + m.from + '&gt;') : m.from; return `
<div class="tm-card" data-mail-view="${i}" style="cursor:pointer">
<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px">
<div class="tm-card-t" style="flex:1">${_0x_escHtml(m.subject)}</div>
<span style="font-size:9px;color:rgba(255,255,255,.3);white-space:nowrap;flex-shrink:0">${m.time || ''}</span>
</div>
<div class="tm-card-sub" style="font-family:inherit">来自: ${sender}</div>
${m.text ? '<div class="tm-card-meta" style="margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100%">' + _0x_escHtml(m.text.substring(0, 80)) + (m.text.length > 80 ? '...' : '') + '</div>' : ''}
</div>`;
        }).join('');
        el.querySelectorAll('[data-mail-view]').forEach(c => { c.onclick = function () { _0x_viewMailDetail(parseInt(this.dataset.mailView)); }; });
    }

    function _0x_escHtml(s) { const d = document.createElement('div'); d.innerText = s; return d.innerHTML; }

    function _0x_viewMailDetail(idx) {
        const m = _inboxCache[idx]; if (!m) return;
        const el = document.getElementById('tm-inbox-detail'); const list = document.getElementById('tm-inbox-list');
        list.style.display = 'none'; el.style.display = 'block';
        const sender = m.fromName ? (m.fromName + ' <' + m.from + '>') : m.from;
        let content = ''; if (m.html) { content = _0x_parseMailHTML(m.html); } else { content = '<pre style="white-space:pre-wrap;word-break:break-word;margin:0;font-family:inherit">' + _0x_escHtml(m.text || '(无内容)') + '</pre>'; }
        el.innerHTML = `
<button class="tm-btn tm-btn-s tm-btn-sm" id="tm-inbox-back" style="margin-bottom:10px">← 返回列表</button>
<div style="margin-bottom:10px">
<div style="font-size:14px;font-weight:700;color:rgba(255,255,255,.95);margin-bottom:6px;line-height:1.4">${_0x_escHtml(m.subject)}</div>
<div style="display:flex;flex-wrap:wrap;gap:4px 12px;font-size:11px;color:rgba(255,255,255,.45)">
<span>👤 ${_0x_escHtml(sender)}</span>
<span>🕐 ${m.time || m.date || ''}</span>
</div>
</div>
<div style="height:1px;background:rgba(255,255,255,.08);margin-bottom:10px"></div>
<div id="tm-mail-content" style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:14px;font-size:12px;color:rgba(255,255,255,.82);line-height:1.7;word-break:break-word;max-height:320px;overflow-y:auto">${content}</div>
<div style="display:flex;gap:6px;margin-top:10px">
<button class="tm-btn tm-btn-s tm-btn-sm" id="tm-mail-copy-text">📋 复制纯文本</button>
${m.html ? '<button class="tm-btn tm-btn-s tm-btn-sm" id="tm-mail-toggle-raw">🔄 切换原始/解析</button>' : ''}
</div>`;
        document.getElementById('tm-inbox-back').onclick = function () { el.style.display = 'none'; list.style.display = 'block'; };
        document.getElementById('tm-mail-copy-text').onclick = function () { const txt = m.text || (m.html ? new DOMParser().parseFromString(m.html, 'text/html').body.textContent : ''); _0x7b(txt); this.innerText = '✅ 已复制'; setTimeout(() => this.innerText = '📋 复制纯文本', 800); };
        const rawBtn = document.getElementById('tm-mail-toggle-raw'); if (rawBtn) { let showRaw = false; rawBtn.onclick = function () { showRaw = !showRaw; const ce = document.getElementById('tm-mail-content'); if (showRaw) { ce.innerText = m.html; ce.style.fontFamily = "'SF Mono',Menlo,monospace"; ce.style.fontSize = '11px'; } else { ce.innerHTML = _0x_parseMailHTML(m.html); ce.style.fontFamily = 'inherit'; ce.style.fontSize = '12px'; } this.innerText = showRaw ? '🔄 切换解析' : '🔄 切换原始'; }; }
    }

    /* ═══════════════ 注册成功弹窗逻辑 ═══════════════ */
    function _0x214(e, pw, oc, cn) { document.getElementById('tm-success-email').innerText = e; document.getElementById('tm-success-password').innerText = pw; const rs = document.getElementById('tm-suc-redir-wrap'); const cb = document.getElementById('tm-success-cancel'); const ce = document.getElementById('tm-success-countdown'); const pb = document.getElementById('tm-success-progress-bar'); const wr = typeof oc === 'function'; rs.style.display = wr ? 'block' : 'none'; cb.innerText = wr ? '取消' : '关闭'; document.getElementById('tm-modal-success').classList.add('show'); let cd = 0x3; let cl = !1; let tm = null; if (wr) { ce.innerText = cd; pb.style.width = '100%'; pb.style.transition = 'none'; setTimeout(() => { pb.style.transition = 'width 3s linear'; pb.style.width = '0%'; }, 0x32); tm = setInterval(() => { if (cl) { clearInterval(tm); return; } cd--; ce.innerText = cd; if (cd <= 0x0) { clearInterval(tm); document.getElementById('tm-modal-success').classList.remove('show'); oc(); } }, 0x3e8); } cb.onclick = function () { cl = !0; if (tm) clearInterval(tm); document.getElementById('tm-modal-success').classList.remove('show'); if (cn) cn(); }; document.getElementById('tm-success-copy').onclick = function () { _0x7b('邮箱: ' + e + '\n密码: ' + pw); this.innerText = '✅ 已复制'; setTimeout(() => this.innerText = '📋 复制', 800); }; }

    /* ═══════════════ Token / Pay / Team ═══════════════ */
    async function _0x325() { const r = await fetch(_0xb('L2FwaS9hdXRoL3Nlc3Npb24=')); if (r.status === 0x193) throw new Error('访问被拒绝 (403)'); const d = await r.json(); if (!d.accessToken) throw new Error('未登录 ChatGPT'); return d.accessToken; }
    async function _0xcbf() { _tmToast('获取 Token...', 'loading'); try { _0x7b(await _0x325()); _tmToast('Token 已复制到剪贴板', 'success', 2000); } catch (e) { _tmToast(e.message, 'error', 3000); } }
    async function _0xdd0() { _tmToast('生成 Plus 支付链接...', 'loading'); try { const tk = await _0x325(); const r = await fetch(_0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9iYWNrZW5kLWFwaS9wYXltZW50cy9jaGVja291dA=='), { method: 'POST', headers: { 'Authorization': 'Bearer ' + tk, 'Content-Type': _0xb('YXBwbGljYXRpb24vanNvbg==') }, body: JSON.stringify({ plan_type: 'plus', checkout_ui_mode: 'hosted', cancel_url: _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS8='), success_url: _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS8=') }) }); const d = await r.json(); if (d.url) { _0x7b(d.url); document.getElementById('tm-modal-pay-code').innerText = d.url; _tmToastHide(); document.getElementById('tm-modal-pay').classList.add('show'); } else throw new Error(d.detail || 'API 错误'); } catch (e) { _tmToast('' + e, 'error', 3000); } }
    async function _0xee1() { _tmToast('生成 Team 链接...', 'loading'); try { const sr = await fetch(_0xb('L2FwaS9hdXRoL3Nlc3Npb24=')); const ct = sr.headers.get('content-type'); if (!ct || !ct.includes(_0xb('YXBwbGljYXRpb24vanNvbg=='))) { _tmToast('请先登录 ChatGPT', 'error', 3000); return; } const tk = await sr.json(); if (!tk.accessToken) { _tmToast('请先登录 ChatGPT', 'error', 3000); return; } const p = { plan_name: 'chatgptteamplan', team_plan_data: { workspace_name: 'MyTeam', price_interval: 'month', seat_quantity: 0x5 }, promo_campaign: { promo_campaign_id: 'team-1-month-free', is_coupon_from_query_param: !0 }, checkout_ui_mode: 'custom' }; const r = await fetch(_0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9iYWNrZW5kLWFwaS9wYXltZW50cy9jaGVja291dA=='), { method: 'POST', headers: { Authorization: 'Bearer ' + tk.accessToken, 'Content-Type': _0xb('YXBwbGljYXRpb24vanNvbg==') }, body: JSON.stringify(p) }); const d = await r.json(); if (d.checkout_session_id) { const su = _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9jaGVja291dC9vcGVuYWlfbGxjLw==') + d.checkout_session_id; _0x7b(su); document.getElementById('tm-modal-pay-code').innerText = su; _tmToastHide(); document.getElementById('tm-modal-pay').classList.add('show'); } else { _tmToast('生成失败：' + (d.detail || '未知错误'), 'error', 3000); } } catch (e) { _tmToast('' + e, 'error', 3000); } }
    async function _0x436(e, pw) { try { const sr = await fetch(_0xb('L2FwaS9hdXRoL3Nlc3Npb24=')); const ct = sr.headers.get('content-type'); if (!ct || !ct.includes(_0xb('YXBwbGljYXRpb24vanNvbg=='))) { _0xa9d(); alert('获取会话失败'); return; } const tk = await sr.json(); if (!tk.accessToken) { _0xa9d(); alert('获取 Token 失败'); return; } _0xbae('生成 Team 短链接...'); const p = { plan_name: 'chatgptteamplan', team_plan_data: { workspace_name: 'MyTeam', price_interval: 'month', seat_quantity: 0x5 }, promo_campaign: { promo_campaign_id: 'team-1-month-free', is_coupon_from_query_param: !0 }, checkout_ui_mode: 'custom' }; const r = await fetch(_0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9iYWNrZW5kLWFwaS9wYXltZW50cy9jaGVja291dA=='), { method: 'POST', headers: { Authorization: 'Bearer ' + tk.accessToken, 'Content-Type': _0xb('YXBwbGljYXRpb24vanNvbg==') }, body: JSON.stringify(p) }); const d = await r.json(); if (d.checkout_session_id) { const su = _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9jaGVja291dC9vcGVuYWlfbGxjLw==') + d.checkout_session_id; _0xa9d(); _0x214(e, pw, () => { window.location.href = su; }, () => { }); } else { _0xa9d(); alert('生成失败'); } } catch (ex) { _0xa9d(); alert('出错：' + ex); } }

    /* ═══════════════ 域名加载 / 设置 / 账号列表 ═══════════════ */
    async function _0x547() { const dd = ['git-hub.email', 'hccc.edu.kg', 'xphdfs.me', 'kiroxubei.tech', 'xpzsd.codes', 'zhurunqi.love', 'geminikey.app', 'geminikey.email', '880070.xyz', '880333.xyz', 'ghukr.cn', '292998.xyz']; let ad = []; try { const d = await _0xd1(_0xb('L2FwaS9wdWJsaWMvZG9tYWlucw==')); if (Array.isArray(d)) ad = d; else if (d && d.domains) ad = d.domains; } catch (e) { console.warn('获取域名失败:', e); } return [...new Set([...ad, ...dd])]; }
    async function _0x76a() { document.getElementById('tm-settings-apikey').value = GM_getValue(_0x4e.API_KEY, ''); document.getElementById('tm-settings-auto-redirect').checked = GM_getValue(_0x4e.AUTO_REDIRECT_TEAM, !1); document.getElementById('tm-settings-reg-prefix').value = GM_getValue('tm_reg_prefix', ''); document.getElementById('tm-settings-team-url').value = GM_getValue('tm_team_url', ''); document.getElementById('tm-settings-team-key').value = GM_getValue('tm_team_key', ''); const ucd = GM_getValue('tm_use_cd', false); document.getElementById('tm-settings-use-cd').checked = ucd; document.getElementById('tm-cd-section').style.display = ucd ? 'block' : 'none'; document.getElementById('tm-settings-tm-addr').value = GM_getValue('tm_tm_addr', ''); document.getElementById('tm-settings-tm-epin').value = GM_getValue('tm_tm_epin', ''); _0x_renderCDs(); document.getElementById('tm-settings-sync-url').value = GM_getValue('tm_sync_url', ''); document.getElementById('tm-settings-sync-apikey').value = GM_getValue('tm_sync_apikey', ''); const sd = GM_getValue('tm_reg_domain', ''); const ds = document.getElementById('tm-settings-reg-domain'); if (ds.options.length <= 0x2) { const dm = await _0x547(); const lo = ds.querySelector('option[value=""]'); if (lo && lo.disabled) lo.remove(); dm.forEach(d => { const dn = typeof d === 'string' ? d : d.domain; if (!ds.querySelector('option[value="' + dn + '"]')) { const o = document.createElement('option'); o.value = dn; o.innerText = dn; ds.appendChild(o); } }); } ds.value = sd || ''; document.getElementById('tm-settings-status').style.display = 'none'; document.getElementById('tm-modal-settings').classList.add('show'); }
    function _0x103() { document.getElementById('tm-modal-about').classList.add('show'); }
    function _0xLogout() { if (!confirm('确定要退出登录吗？')) return; const names = ['__Secure-next-auth.session-token', '__Secure-next-auth.session-token.0', '__Secure-next-auth.session-token.1', '__Secure-next-auth.session-token.2']; let pending = 0, done = 0; function tryReload() { done++; if (done >= pending) location.reload(); } for (const n of names) { pending++; GM_cookie.delete({ name: n, url: 'https://chatgpt.com/' }, tryReload); } if (pending === 0) location.reload(); }
    const _PG_SIZE = 10;
    let _pgCur = 1;
    function _0xff2(page) {
        const ac = _0x126(); const ls = document.getElementById('tm-accounts-list');
        if (ac.length === 0) { ls.innerHTML = '<div class="tm-empty">📭 暂无账号</div>'; document.getElementById('tm-modal-accounts').classList.add('show'); return; }
        const total = ac.length; const pages = Math.ceil(total / _PG_SIZE);
        if (!page) page = 1; if (page < 1) page = 1; if (page > pages) page = pages; _pgCur = page;
        const start = (page - 1) * _PG_SIZE; const end = Math.min(start + _PG_SIZE, total); const slice = ac.slice(start, end);
        let h = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding:0 2px"><span style="font-size:11px;color:rgba(255,255,255,.45)">共 ${total} 个账号</span><span style="font-size:11px;color:rgba(255,255,255,.45)">${page} / ${pages} 页</span></div>`;
        h += slice.map((a, idx) => {
            const i = start + idx; return `
<div class="tm-card">
<div class="tm-card-t">${a.email}</div>
<div class="tm-card-sub">密码: ${a.password}</div>
<div class="tm-card-meta">${a.status || '已创建'} · ${new Date(a.createdAt).toLocaleString()}</div>
<div class="tm-card-acts">
<button class="tm-btn tm-btn-p tm-btn-sm" data-action="copyemail" data-index="${i}">📋 账号</button>
<button class="tm-btn tm-btn-sm" style="background:rgba(168,85,247,.15);color:rgba(192,132,252,.9);border-color:rgba(168,85,247,.2)" data-action="copypwd" data-index="${i}">🔑 密码</button>
<button class="tm-btn tm-btn-sm" style="background:rgba(59,130,246,.15);color:rgba(96,165,250,.9);border-color:rgba(59,130,246,.2)" data-action="code" data-email="${a.email}">📨 验证码</button>
<button class="tm-btn tm-btn-d tm-btn-sm" data-action="del" data-email="${a.email}">🗑️</button>
</div>
</div>`;
        }).join('');
        if (pages > 1) {
            h += `<div style="display:flex;justify-content:center;align-items:center;gap:6px;margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08)">
<button class="tm-btn tm-btn-s tm-btn-sm" id="tm-pg-first" ${page <= 1 ? 'disabled style="opacity:.4;cursor:default"' : ''}>首页</button>
<button class="tm-btn tm-btn-s tm-btn-sm" id="tm-pg-prev" ${page <= 1 ? 'disabled style="opacity:.4;cursor:default"' : ''}>‹ 上一页</button>
<span style="font-size:12px;color:rgba(255,255,255,.7);min-width:40px;text-align:center;font-weight:600">${page}/${pages}</span>
<button class="tm-btn tm-btn-s tm-btn-sm" id="tm-pg-next" ${page >= pages ? 'disabled style="opacity:.4;cursor:default"' : ''}>下一页 ›</button>
<button class="tm-btn tm-btn-s tm-btn-sm" id="tm-pg-last" ${page >= pages ? 'disabled style="opacity:.4;cursor:default"' : ''}>末页</button>
</div>`;
        }
        ls.innerHTML = h;
        if (pages > 1) { const pf = document.getElementById('tm-pg-first'); const pp = document.getElementById('tm-pg-prev'); const pn = document.getElementById('tm-pg-next'); const pl = document.getElementById('tm-pg-last'); if (pf) pf.onclick = () => _0xff2(1); if (pp) pp.onclick = () => _0xff2(_pgCur - 1); if (pn) pn.onclick = () => _0xff2(_pgCur + 1); if (pl) pl.onclick = () => _0xff2(pages); }
        document.getElementById('tm-modal-accounts').classList.add('show');
    }

    /* ═══════════════ 账号操作事件 ═══════════════ */
    document.addEventListener('click', async function (e) { const b = e.target.closest('[data-action]'); if (!b) return; const a = b.dataset.action; if (a === 'copyemail') { const i = parseInt(b.dataset.index); const ac = _0x126()[i]; if (ac) { _0x7b(ac.email); b.innerText = '✅'; setTimeout(() => b.innerText = '📋 账号', 800); } } else if (a === 'copypwd') { const i = parseInt(b.dataset.index); const ac = _0x126()[i]; if (ac) { _0x7b(ac.password); b.innerText = '✅'; setTimeout(() => b.innerText = '🔑 密码', 800); } } else if (a === 'code') { const em = b.dataset.email; try { b.innerText = '...'; const c = await _0x115(em); if (c) { _0x7b(c); alert('验证码: ' + c + '\n已复制'); } else alert('未找到验证码'); } catch (ex) { alert('错误: ' + ex.message); } b.innerText = '📨 验证码'; } else if (a === 'del') { const em = b.dataset.email; if (confirm('确定删除?')) { _0x148(em); _0xff2(); } } });

    /* ═══════════════ 注册流程 (v8.1 原版逻辑 + TempMail 扩展) ═══════════════ */
    async function _0x659() { const ucd = GM_getValue('tm_use_cd', false); const cds = _0x_getCDs(); if (ucd && cds.length > 0) { const tmA = GM_getValue('tm_tm_addr', ''); if (!tmA) { alert('请先在设置中配置 TempMail 取件邮箱'); _0x76a(); return; } try { _0x19d(); _0xbae('清理缓存...'); try { localStorage.clear(); sessionStorage.clear(); } catch (_ce) { } try { document.cookie.split(';').forEach(function (_ck) { var _n = _ck.split('=')[0].trim(); if (!_n) return; document.cookie = _n + '=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/'; document.cookie = _n + '=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/;domain=.chatgpt.com'; document.cookie = _n + '=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/;domain=.openai.com'; document.cookie = _n + '=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/;domain=.auth.openai.com'; }); } catch (_ce) { } await _0x1ae(0x1f4); _0xbae('正在准备自定义域名邮箱...'); const dom = cds[Math.floor(Math.random() * cds.length)]; const pfx = GM_getValue('tm_reg_prefix', '') || _0x_randPfx(12); const email = pfx + '@' + dom; const rd = { email: email, password: _0xae(), ..._0xbf(), birthday: _0xc0(), createdAt: new Date().toISOString(), status: '注册中', customDomain: true, tmAddr: tmA, tmEpin: GM_getValue('tm_tm_epin', '') }; _0x16a(rd); _0x18c(_0x5f.GOTO_SIGNUP); _0x137(rd); _0x_regSaveGuard(); _0xbae('正在跳转注册页面...'); await _0x1ae(0x1f4); window.location.href = _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9hdXRoL2xvZ2lu'); } catch (e) { _0xa9d(); alert('准备失败: ' + e.message); _0x19d(); } return; } const k = GM_getValue(_0x4e.API_KEY, ''); if (!k) { alert('请先配置 NPCmail 密钥或启用自定义域名模式'); _0x76a(); return; } const p = GM_getValue('tm_reg_prefix', ''); const d = GM_getValue('tm_reg_domain', ''); await _0x87b({ prefix: p, domain: d }); }
    async function _0x87b(c = {}) { try { _0x19d(); _0xbae('清理缓存...'); try { localStorage.clear(); sessionStorage.clear(); } catch (_ce) { } try { document.cookie.split(';').forEach(function (_ck) { var _n = _ck.split('=')[0].trim(); if (!_n) return; document.cookie = _n + '=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/'; document.cookie = _n + '=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/;domain=.chatgpt.com'; document.cookie = _n + '=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/;domain=.openai.com'; document.cookie = _n + '=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/;domain=.auth.openai.com'; }); } catch (_ce) { } await _0x1ae(0x1f4); _0xbae('正在创建邮箱...'); const ed = await _0xf3(c.domain || null, c.prefix || null); const rd = { email: ed.address, password: _0xae(), ..._0xbf(), birthday: _0xc0(), createdAt: new Date().toISOString(), status: '注册中' }; _0x16a(rd); _0x18c(_0x5f.GOTO_SIGNUP); _0x137(rd); _0x_regSaveGuard(); _0xbae('正在跳转注册页面...'); await _0x1ae(0x1f4); window.location.href = _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9hdXRoL2xvZ2lu'); } catch (e) { _0xa9d(); alert('创建邮箱失败: ' + e.message); _0x19d(); } }
    async function _0x98d(d) { function _vp(s) { const els = document.querySelectorAll(s); for (const el of els) { const rc = el.getBoundingClientRect(); if (rc.width > 0 && rc.height > 0) { const cs = window.getComputedStyle(el); if (cs.visibility !== 'hidden' && cs.display !== 'none') return el; } } return null; } _0xbae('等待密码框加载...'); let pi = null; let _wt = 0; while (!pi && _wt < 60) { _wt++; var _etp = document.body ? document.body.textContent : ''; if (_etp.includes('糟糕') || _etp.includes('出错了') || _etp.includes('Operation timed out') || _etp.includes('操作超时')) { var _rtp = (d._retries || 0) + 1; if (_rtp <= 5) { _0xbae('检测到错误页面，重试 (' + _rtp + '/5)...'); _0x16a({ ...d, _retries: _rtp }); await _0x1ae(0x5dc); window.location.href = _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9hdXRoL2xvZ2lu'); return; } else { _0xbae('重试次数已达上限'); _0xa9d(); _0x19d(); return; } } _0xbae('等待密码框... (' + _wt + '/60)'); await _0x1ae(0x3e8); pi = _vp('input[type="password"], input[name="password"]'); } if (!pi) { _0xbae('密码框未找到'); return; } _0xbae('正在填写密码...'); await _0x1ae(0x1f4); _0x1c0(pi, d.password); _0x137({ ...d, status: '密码已填写' }); await _0x1ae(0x3e8); let cb = document.querySelector('button[type="submit"]') || _0x1f3('button', ['Continue', '继续', 'Next']); if (cb) { _0x1e2(cb); _0x18c(_0x5f.WAIT_CODE); _0xbae('等待验证码页面...'); let _tw = 0; let _codeReady = false; while (_tw < 60) { _tw++; await _0x1ae(0x3e8); var _etw = document.body ? document.body.textContent : ''; if (_etw.includes('糟糕') || _etw.includes('出错了') || _etw.includes('Operation timed out') || _etw.includes('操作超时')) { var _rtw = (d._retries || 0) + 1; if (_rtw <= 5) { _0xbae('检测到错误页面，重试 (' + _rtw + '/5)...'); _0x16a({ ...d, _retries: _rtw }); await _0x1ae(0x5dc); window.location.href = _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9hdXRoL2xvZ2lu'); return; } else { _0xbae('重试次数已达上限'); _0xa9d(); _0x19d(); return; } } const _ci = document.querySelectorAll('input[type="text"][maxlength="1"]'); const _cs = document.querySelector('input[autocomplete="one-time-code"], input[name="code"]'); if (_ci.length >= 4 || _cs) { _0xbae('验证码页面已加载'); _codeReady = true; break; } _0xbae('等待页面切换... (' + _tw + '/60)'); } if (!_codeReady) { _0xbae('验证码页面未加载'); return; } await _0x1ae(0x7d0); await _0xa9e(d); } }
    async function _0xa9e(d) { _0xbae('等待验证码邮件...'); let c = null; const isTM = d.customDomain && d.tmAddr; for (let i = 0x0; i < 0x3c; i++) { var _eta = document.body ? document.body.textContent : ''; if (_eta.includes('糟糕') || _eta.includes('出错了') || _eta.includes('Operation timed out') || _eta.includes('操作超时')) { var _rta = (d._retries || 0) + 1; if (_rta <= 5) { _0xbae('检测到错误页面，重试 (' + _rta + '/5)...'); _0x16a({ ...d, _retries: _rta }); await _0x1ae(0x5dc); window.location.href = _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9hdXRoL2xvZ2lu'); return; } else { _0xbae('重试次数已达上限'); _0xa9d(); _0x19d(); return; } } _0xbae('等待验证码... (' + (i + 0x1) + '/60)' + (isTM ? ' [TempMail:' + d.tmAddr + ']' : ' [NPCmail:' + d.email + ']')); if (isTM) { c = await _0x_tmCode(d.tmAddr, d.tmEpin || ''); } else { c = await _0x115(d.email); } if (c) { _0xbae('验证码获取成功: ' + c); break; } else { _0xbae('第' + (i + 1) + '次未获取到验证码'); } await _0x1ae(0xbb8); } if (c) { _0x137({ ...d, status: '验证码已获取', verificationCode: c }); _0x16a({ ...d, verificationCode: c }); _0x18c(_0x5f.FILL_CODE); await _0xbaf(c, d); } else { _0x137({ ...d, status: '验证码超时' }); throw new Error('验证码获取超时'); } }
    async function _0xbaf(c, d) { _0xbae('正在填写验证码...'); await _0x1ae(0x3e8); const ci = document.querySelectorAll('input[type="text"][maxlength="1"], input[autocomplete="one-time-code"]'); if (ci.length >= 0x6) { for (let i = 0x0; i < Math.min(c.length, ci.length); i++) { _0x1c0(ci[i], c[i]); await _0x1ae(0x64); } } else { const si = document.querySelector('input[name="code"], input[id*="code"], input[autocomplete="one-time-code"]'); if (si) _0x1c0(si, c); } await _0x1ae(0x3e8); let cb = document.querySelector('button[type="submit"]') || _0x1f3('button', ['Continue', '继续', 'Verify']); if (cb) { _0x1e2(cb); _0x18c(_0x5f.FILL_PROFILE); _0xbae('等待个人信息页面...'); let s = 0x0; let ni = null; const ns = 'input[name="firstName"], input[name="first_name"], input[id="firstName"], input[id="first-name"]'; while (!ni && s < 0x3c) { s++; _0xbae('等待姓名输入框... (' + s + 's)'); await _0x1ae(0x3e8); ni = document.querySelector(ns); if (!ni) ni = document.querySelector('input[name="name"], input[name="fullName"]'); } if (ni) { _0xbae('检测到姓名框...'); await _0x1ae(0x5dc); await _0xcc0(d); } else { _0xbae('超时，请手动填写'); } } }
    async function _0xcc0(d) { _0xbae('填写个人信息...'); await _0x1ae(0x3e8); const ai = document.querySelectorAll('input[type="text"], input:not([type])'); const fi = document.querySelector('input[name="firstName"], input[name="first_name"], input[id*="firstName"], input[id*="first-name"]'); const li = document.querySelector('input[name="lastName"], input[name="last_name"], input[id*="lastName"], input[id*="last-name"]'); if (fi && li) { _0x1c0(fi, d.firstName); _0x1c0(li, d.lastName); } else { const ni = document.querySelector('input[name="name"], input[name="fullName"], input[id*="name"]'); if (ni) _0x1c0(ni, d.firstName + ' ' + d.lastName); else if (ai.length > 0) _0x1c0(ai[0], d.firstName + ' ' + d.lastName); } await _0x1ae(0x1f4); const bd = d.birthday; const sb = document.querySelectorAll('[role="spinbutton"]'); if (sb.length >= 0x3) { await _0x1d1(sb[0], bd.year); await _0x1d1(sb[1], bd.month); await _0x1d1(sb[2], bd.day); } else { const vi = Array.from(document.querySelectorAll('input')).filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && el.type !== 'hidden'; }); if (vi.length > 1) { _0x1c0(vi[1], bd.year + '/' + String(bd.month).padStart(2, '0') + '/' + String(bd.day).padStart(2, '0')); } } await _0x1ae(0x3e8); let cb = document.querySelector('button[type="submit"]') || _0x1f3('button', ['Continue', '继续', 'Agree', '同意']); if (cb) { _0x1e2(cb); const cu = window.location.href; let s = 0; while (window.location.href === cu) { s++; _0xbae('等待页面... (' + s + 's)'); await _0x1ae(0x3e8); if (!document.querySelector('[role="spinbutton"]')) break; } _0x18c(_0x5f.COMPLETE); _0xa9d(); _0x137({ ...d, status: '注册完成' }); _syncPush({ ...d, status: '注册完成' }); _0x19d(); const ar = GM_getValue(_0x4e.AUTO_REDIRECT_TEAM, !1); if (ar) { _0xbae('生成 Team 短链接...'); await _0x1ae(0x5dc); await _0x436(d.email, d.password); } else { _0x214(d.email, d.password, null, null); } } }

    /* ═══════════════ 自动注册主流程 (v8.1 原版) ═══════════════ */
    let _0x548_busy = false;
    async function _0x548() { if (_0x548_busy) return; _0x548_busy = true; try { await _0x548_inner(); } finally { _0x548_busy = false; } }
    async function _0x548_inner() { let st = _0x17b(); const d = _0x159(); if (st === _0x5f.IDLE || !d) return; _0x_regSaveGuard(); const u = window.location.href; const ia = u.includes('auth.openai.com') || u.includes('/auth/'); if (!ia && st !== _0x5f.IDLE && st !== _0x5f.COMPLETE) { _0x18c(_0x5f.COMPLETE); _0xa9d(); _0x137({ ...d, status: '注册完成' }); _syncPush({ ...d, status: '注册完成' }); _0x19d(); const ar = GM_getValue(_0x4e.AUTO_REDIRECT_TEAM, !1); if (ar) { _0xbae('注册完成，生成 Team 短链接...'); await _0x1ae(0x5dc); await _0x436(d.email, d.password); } else { _0x214(d.email, d.password, null, null); } return; } await _0x1ae(0x7d0); var _et = document.body ? document.body.textContent : ''; if (_et.includes('糟糕') || _et.includes('出错了') || _et.includes('Operation timed out') || _et.includes('操作超时')) { var _rt = (d._retries || 0) + 1; if (_rt <= 5) { _0xbae('检测到错误页面，重试 (' + _rt + '/5)...'); _0x16a({ ...d, _retries: _rt }); await _0x1ae(0x5dc); window.location.href = _0xb('aHR0cHM6Ly9jaGF0Z3B0LmNvbS9hdXRoL2xvZ2lu'); return; } else { _0xbae('重试次数已达上限'); _0xa9d(); _0x19d(); return; } } try { function _vis(s) { const els = document.querySelectorAll(s); for (const el of els) { const rc = el.getBoundingClientRect(); const cs = window.getComputedStyle(el); if (rc.width > 0 && rc.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && parseFloat(cs.opacity) > 0) return el; } return null; } const hp = _vis('input[type="password"], input[name="password"]'); const hc = _vis('input[maxlength="1"], input[autocomplete="one-time-code"], input[name="code"]'); const hpi = _vis('input[name="firstName"], input[name="first_name"], input[id*="firstName"]'); if (hpi && st !== _0x5f.FILL_PROFILE) { st = _0x5f.FILL_PROFILE; _0x18c(st); } else if (hp && st === _0x5f.FILL_EMAIL) { st = _0x5f.FILL_PASSWORD; _0x18c(st); } if (st === _0x5f.GOTO_SIGNUP) { _0xbae('准备注册...'); await _0x1ae(0x3e8); const _ei = _vis('input[type="email"], input[name="email"], input[name="username"], #username'); if (_ei) { _0x18c(_0x5f.FILL_EMAIL); _0xbae('填写邮箱...'); await _0x1ae(0x1f4); _0x1c0(_ei, d.email); await _0x1ae(0x3e8); let _cb = document.querySelector('button[type="submit"]') || _0x1f3('button', ['Continue', '继续', 'Next']); if (_cb) { _0x1e2(_cb); _0x18c(_0x5f.FILL_PASSWORD); let _s = 0; let _pi = null; while (!_pi) { _s++; _0xbae('等待... (' + _s + 's)'); await _0x1ae(0x3e8); _pi = _vis('input[type="password"], input[name="password"]'); if (_s >= 60) { _0xbae('超时'); return; } } await _0x98d(d); } return; } else { let sl = document.querySelector('a[href*="signup"], [data-testid="signup-link"]'); if (!sl) { const all = document.querySelectorAll('a, button, div, span, [role="button"], [class*="btn"], [class*="button"], [tabindex]'); for (const el of all) { const txt = (el.textContent || '').trim(); if (/^(sign up|sign up for free|免费注册|create account)$/i.test(txt)) { sl = el; break; } } } if (sl) { _0xbae('点击注册...'); _0x1e2(sl); await _0x1ae(0xbb8); _0x18c(_0x5f.FILL_EMAIL); } else { _0xbae('等待注册入口...'); await _0x1ae(0xbb8); await _0x548(); return; } } } else if (st === _0x5f.FILL_EMAIL) { _0xbae('填写邮箱...'); await _0x1ae(0x3e8); const ei = await _0x1bf('input[type="email"], input[name="email"], input[id*="email"], input[autocomplete="email"], input[inputmode="email"], input[name="username"], #username', 0x3a98); _0x1c0(ei, d.email); await _0x1ae(0x3e8); let cb = document.querySelector('button[type="submit"]') || _0x1f3('button', ['Continue', '继续', 'Next']); if (cb) { _0x1e2(cb); _0x18c(_0x5f.FILL_PASSWORD); let s = 0; let pi = null; while (!pi) { s++; _0xbae('等待... (' + s + 's)'); await _0x1ae(0x3e8); pi = document.querySelector('input[type="password"], input[name="password"]'); if (s >= 0x3c) { _0xbae('超时'); return; } } await _0x98d(d); } } else if (st === _0x5f.FILL_PASSWORD) { if (_vis('input[type="email"], input[name="email"]') && !_vis('input[type="password"]')) { _0xbae('页面状态不匹配，重新开始...'); st = _0x5f.FILL_EMAIL; _0x18c(st); await _0x548(); return; } await _0x98d(d); } else if (st === _0x5f.WAIT_CODE) { if (_vis('input[type="email"], input[name="email"]') && !_vis('input[maxlength="1"], input[autocomplete="one-time-code"]') && !_vis('input[type="password"]')) { _0xbae('页面状态不匹配，重新开始...'); st = _0x5f.FILL_EMAIL; _0x18c(st); await _0x548(); return; } await _0xa9e(d); } else if (st === _0x5f.FILL_CODE) { const ud = _0x159(); if (ud && ud.verificationCode) { await _0xbaf(ud.verificationCode, ud); } else { _0xbae('验证码尚未获取，等待中...'); } } else if (st === _0x5f.FILL_PROFILE) { await _0xcc0(d); } else if (st === _0x5f.COMPLETE) { _0xa9d(); _0x137({ ...d, status: '注册完成' }); _syncPush({ ...d, status: '注册完成' }); _0x19d(); const ar = GM_getValue(_0x4e.AUTO_REDIRECT_TEAM, !1); if (ar) { _0xbae('生成 Team 短链接...'); await _0x1ae(0x5dc); await _0x436(d.email, d.password); } else { _0x214(d.email, d.password, null, null); } } } catch (e) { console.error('[AutoReg]', e); _0xbae('错误: ' + e.message); setTimeout(() => { _0xa9d(); if (confirm('自动注册出错: ' + e.message + '\n\n是否重试？')) { _0x548(); } else { _0x19d(); } }, 0x7d0); } }

    /* ═══════════════ 点击涟漪效果 ═══════════════ */
    document.addEventListener('click', function (e) { const b = e.target.closest('.tm-btn,.tm-gi'); if (!b) return; const rc = b.getBoundingClientRect(); const sz = Math.max(rc.width, rc.height) * 2.5; const x = e.clientX - rc.left - sz / 2; const y = e.clientY - rc.top - sz / 2; const rp = document.createElement('span'); rp.style.cssText = 'position:absolute;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.3) 0%,rgba(255,255,255,.1) 40%,transparent 70%);pointer-events:none;width:' + sz + 'px;height:' + sz + 'px;left:' + x + 'px;top:' + y + 'px;transform:scale(0);opacity:1;animation:tm-rippleOut .65s cubic-bezier(0,.4,.2,1) forwards;z-index:10'; b.style.position || (b.style.position = 'relative'); b.style.overflow = 'hidden'; b.appendChild(rp); setTimeout(() => rp.remove(), 700); });

    setInterval(_0x204, 0x5dc);
    setTimeout(_0x204, 0x3e8);
})();
