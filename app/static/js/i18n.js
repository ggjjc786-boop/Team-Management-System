/**
 * i18n - 中/英/俄 三语切换
 */
(function() {
    var LANGS = {
        zh: { label: '中文', flag: '🇨🇳' },
        en: { label: 'English', flag: '🇬🇧' },
        ru: { label: 'Русский', flag: '🇷🇺' }
    };

    var T = {
        zh: {
            // === 通用 ===
            'site_title': 'GPT Team 兑换',
            'site_subtitle': '✨ 新春喜迎 · 使用兑换码加入 ChatGPT Team ✨',
            'newyear_chip': '🐴 马年大吉',
            'remaining_spots': '剩余车位:',
            'close': '关闭',
            'back_to_redeem': '返回兑换页',
            'email_label': '邮箱地址',
            'email_placeholder': '请输入您的邮箱地址',
            'email_help': '邀请将发送到此邮箱，请确保可正常接收',
            'loading': '加载中...',
            'network_error': '网络错误，请稍后重试',
            'invalid_email': '请输入有效的邮箱地址',

            // === 兑换页 ===
            'freespot_banner_text': '免费车位',
            'freespot_banner_desc': '无需兑换码，直接上车',
            'tab_redeem': '兑换码兑换',
            'tab_warranty': '质保查询',
            'redeem_title': '输入兑换信息',
            'redeem_sub': '填写邮箱和兑换码，即可加入 ChatGPT Team',
            'code_label': '兑换码',
            'code_placeholder': '请输入兑换码',
            'verify_btn': '验证并兑换',
            'select_team': '选择 Team',
            'btn_back': '返回',
            'btn_auto_select': '自动选择',
            'fill_all': '请填写完整信息',
            'redeeming': '正在兑换...',
            'verify_code': '验证兑换码',
            'members': '成员',
            'expires': '到期:',
            'no_team': '没有可用的 Team',
            'redeem_success': '兑换成功!',
            'joined_team': '您已成功加入 Team',
            'team_name_label': '🏠 Team 名称',
            'email_addr_label': '📧 邮箱地址',
            'expire_label': '📅 到期时间',
            'invite_sent': '✉️ 邀请邮件已发送到您的邮箱，请查收并按照邮件指引接受邀请。',
            'redeem_again': '再次兑换',
            'redeem_fail': '兑换失败',
            'btn_retry': '返回重试',
            'btn_restart': '重新开始',

            // === 质保 ===
            'warranty_title': '质保查询',
            'warranty_sub': '封号后可凭原兑换码重新加入 Team',
            'warranty_tip': '如果您使用<strong>质保兑换码</strong>加入的 Team 被封号，可以在质保期内重复使用原兑换码重新加入。',
            'warranty_code_placeholder': '请输入您的兑换码',
            'warranty_query_btn': '查询质保状态',

            // === 免费车位页 ===
            'freespot_page_title': '免费车位',
            'freespot_subtitle': '✨ 无需兑换码 · 填写邮箱即可直接上车 ✨',
            'freespot_card_title': '可用免费车位',
            'freespot_card_sub': '选择一个车位，输入邮箱即可加入 ChatGPT Team',
            'freespot_no_spots': '当前暂无可用免费车位',
            'freespot_redirecting': '正在为您跳转至候车室...',
            'freespot_avail': '个空位',
            'freespot_join': '上车',
            'freespot_load_fail': '加载失败，请稍后重试',
            'freespot_enter_email': '请先输入邮箱地址',
            'freespot_joining': '加入中...',
            'freespot_join_fail': '加入失败',
            'freespot_join_success': '加入成功！',
            'freespot_check_email': '请前往邮箱查收 ChatGPT Team 邀请链接',

            // === 候车室 ===
            'waiting_page_title': '候车室',
            'waiting_subtitle': '✨ 当前暂无可用免费车位，请耐心等待 ✨',
            'waiting_title': '候车室',
            'waiting_recheck': '重新检查车位',
            'waiting_count_prefix': '当前',
            'waiting_count_suffix': '人正在候车',
            'waiting_desc': '当前所有免费车位已满，留下邮箱后有车位会通知您',
            'waiting_email_label': '您的邮箱',
            'waiting_email_help': '车位开放时会向此邮箱发送通知',
            'waiting_join_btn': '加入候车室',
            'waiting_joined': '已加入候车室',
            'waiting_joined_detail': '有车位开放时会通过邮件通知您，请留意收件箱',
            'waiting_tip_title': '温馨提示',
            'waiting_tip_1': '加入候车室后，有车位开放会收到邮件通知',
            'waiting_tip_2': '收到通知后请尽快前往免费车位页面上车',
            'waiting_tip_3': '也可以使用兑换码直接兑换，无需等待',
            'waiting_enter_email': '请输入邮箱地址',
            'waiting_joining': '加入中...',
            'waiting_join_fail': '加入失败'
        },
        en: {
            'site_title': 'GPT Team Redeem',
            'site_subtitle': '✨ Use a redemption code to join ChatGPT Team ✨',
            'newyear_chip': '🐴 Happy New Year',
            'remaining_spots': 'Spots left:',
            'close': 'Close',
            'back_to_redeem': 'Back to Redeem',
            'email_label': 'Email Address',
            'email_placeholder': 'Enter your email address',
            'email_help': 'The invitation will be sent to this email',
            'loading': 'Loading...',
            'network_error': 'Network error, please try again later',
            'invalid_email': 'Please enter a valid email address',

            'freespot_banner_text': 'Free Spots',
            'freespot_banner_desc': 'No code needed, join directly',
            'tab_redeem': 'Redeem Code',
            'tab_warranty': 'Warranty',
            'redeem_title': 'Enter Redemption Info',
            'redeem_sub': 'Enter email and code to join ChatGPT Team',
            'code_label': 'Redemption Code',
            'code_placeholder': 'Enter redemption code',
            'verify_btn': 'Verify & Redeem',
            'select_team': 'Select Team',
            'btn_back': 'Back',
            'btn_auto_select': 'Auto Select',
            'fill_all': 'Please fill in all fields',
            'redeeming': 'Redeeming...',
            'verify_code': 'Verify Code',
            'members': 'members',
            'expires': 'Expires:',
            'no_team': 'No available Team',
            'redeem_success': 'Redeemed Successfully!',
            'joined_team': 'You have joined the Team',
            'team_name_label': '🏠 Team Name',
            'email_addr_label': '📧 Email',
            'expire_label': '📅 Expires',
            'invite_sent': '✉️ An invitation email has been sent. Please check your inbox and follow the instructions.',
            'redeem_again': 'Redeem Again',
            'redeem_fail': 'Redemption Failed',
            'btn_retry': 'Go Back',
            'btn_restart': 'Start Over',

            'warranty_title': 'Warranty Check',
            'warranty_sub': 'Re-join Team with original code if banned',
            'warranty_tip': 'If your Team was banned, you can re-use your <strong>warranty code</strong> to rejoin during the warranty period.',
            'warranty_code_placeholder': 'Enter your redemption code',
            'warranty_query_btn': 'Check Warranty',

            'freespot_page_title': 'Free Spots',
            'freespot_subtitle': '✨ No code needed · Just enter email to join ✨',
            'freespot_card_title': 'Available Free Spots',
            'freespot_card_sub': 'Pick a spot and enter email to join ChatGPT Team',
            'freespot_no_spots': 'No free spots available',
            'freespot_redirecting': 'Redirecting to waiting room...',
            'freespot_avail': 'spots left',
            'freespot_join': 'Join',
            'freespot_load_fail': 'Failed to load, please try again',
            'freespot_enter_email': 'Please enter your email first',
            'freespot_joining': 'Joining...',
            'freespot_join_fail': 'Failed to join',
            'freespot_join_success': 'Joined successfully!',
            'freespot_check_email': 'Check your email for the ChatGPT Team invitation',

            'waiting_page_title': 'Waiting Room',
            'waiting_subtitle': '✨ No free spots available, please wait ✨',
            'waiting_title': 'Waiting Room',
            'waiting_recheck': 'Recheck Spots',
            'waiting_count_prefix': '',
            'waiting_count_suffix': 'people waiting',
            'waiting_desc': 'All free spots are taken. Leave your email and we\'ll notify you when spots open.',
            'waiting_email_label': 'Your Email',
            'waiting_email_help': 'You\'ll be notified at this email when spots open',
            'waiting_join_btn': 'Join Waiting Room',
            'waiting_joined': 'Joined waiting room',
            'waiting_joined_detail': 'You\'ll receive an email notification when spots become available',
            'waiting_tip_title': 'Tips',
            'waiting_tip_1': 'You\'ll get an email when free spots open up',
            'waiting_tip_2': 'Act fast after receiving the notification',
            'waiting_tip_3': 'You can also use a redemption code directly',
            'waiting_enter_email': 'Please enter your email',
            'waiting_joining': 'Joining...',
            'waiting_join_fail': 'Failed to join'
        },
        ru: {
            'site_title': 'GPT Team Активация',
            'site_subtitle': '✨ Используйте код для вступления в ChatGPT Team ✨',
            'newyear_chip': '🐴 С Новым Годом',
            'remaining_spots': 'Осталось мест:',
            'close': 'Закрыть',
            'back_to_redeem': 'Назад',
            'email_label': 'Электронная почта',
            'email_placeholder': 'Введите ваш email',
            'email_help': 'Приглашение будет отправлено на этот адрес',
            'loading': 'Загрузка...',
            'network_error': 'Ошибка сети, попробуйте позже',
            'invalid_email': 'Введите корректный email',

            'freespot_banner_text': 'Свободные места',
            'freespot_banner_desc': 'Без кода, присоединяйтесь сразу',
            'tab_redeem': 'Активация кода',
            'tab_warranty': 'Гарантия',
            'redeem_title': 'Введите данные',
            'redeem_sub': 'Введите email и код для вступления в ChatGPT Team',
            'code_label': 'Код активации',
            'code_placeholder': 'Введите код активации',
            'verify_btn': 'Активировать',
            'select_team': 'Выберите Team',
            'btn_back': 'Назад',
            'btn_auto_select': 'Авто выбор',
            'fill_all': 'Заполните все поля',
            'redeeming': 'Активация...',
            'verify_code': 'Проверить код',
            'members': 'участников',
            'expires': 'Истекает:',
            'no_team': 'Нет доступных Team',
            'redeem_success': 'Успешно активировано!',
            'joined_team': 'Вы успешно вступили в Team',
            'team_name_label': '🏠 Название Team',
            'email_addr_label': '📧 Email',
            'expire_label': '📅 Истекает',
            'invite_sent': '✉️ Приглашение отправлено на вашу почту. Проверьте входящие и следуйте инструкциям.',
            'redeem_again': 'Активировать ещё',
            'redeem_fail': 'Ошибка активации',
            'btn_retry': 'Назад',
            'btn_restart': 'Начать заново',

            'warranty_title': 'Проверка гарантии',
            'warranty_sub': 'Повторное вступление при бане по исходному коду',
            'warranty_tip': 'Если ваш Team был заблокирован, вы можете повторно использовать <strong>гарантийный код</strong> в течение гарантийного срока.',
            'warranty_code_placeholder': 'Введите ваш код активации',
            'warranty_query_btn': 'Проверить гарантию',

            'freespot_page_title': 'Свободные места',
            'freespot_subtitle': '✨ Без кода · Введите email и присоединяйтесь ✨',
            'freespot_card_title': 'Доступные места',
            'freespot_card_sub': 'Выберите место и введите email для вступления',
            'freespot_no_spots': 'Нет свободных мест',
            'freespot_redirecting': 'Перенаправление в зал ожидания...',
            'freespot_avail': 'мест свободно',
            'freespot_join': 'Занять',
            'freespot_load_fail': 'Ошибка загрузки, попробуйте позже',
            'freespot_enter_email': 'Сначала введите email',
            'freespot_joining': 'Присоединение...',
            'freespot_join_fail': 'Не удалось присоединиться',
            'freespot_join_success': 'Успешно!',
            'freespot_check_email': 'Проверьте почту для приглашения в ChatGPT Team',

            'waiting_page_title': 'Зал ожидания',
            'waiting_subtitle': '✨ Нет свободных мест, пожалуйста, подождите ✨',
            'waiting_title': 'Зал ожидания',
            'waiting_recheck': 'Проверить места',
            'waiting_count_prefix': '',
            'waiting_count_suffix': 'чел. ожидают',
            'waiting_desc': 'Все места заняты. Оставьте email — мы уведомим вас, когда места появятся.',
            'waiting_email_label': 'Ваш email',
            'waiting_email_help': 'Уведомление придёт на этот адрес',
            'waiting_join_btn': 'Встать в очередь',
            'waiting_joined': 'Вы в очереди',
            'waiting_joined_detail': 'Вы получите email-уведомление, когда появятся свободные места',
            'waiting_tip_title': 'Подсказки',
            'waiting_tip_1': 'Вы получите email при появлении свободных мест',
            'waiting_tip_2': 'Действуйте быстро после получения уведомления',
            'waiting_tip_3': 'Также можно использовать код активации напрямую',
            'waiting_enter_email': 'Введите email',
            'waiting_joining': 'Присоединение...',
            'waiting_join_fail': 'Не удалось присоединиться'
        }
    };

    // 获取/设置语言
    function getLang() {
        return localStorage.getItem('app_lang') || 'zh';
    }
    function setLang(lang) {
        if (!T[lang]) return;
        localStorage.setItem('app_lang', lang);
        applyLang(lang);
    }

    // 翻译函数
    function t(key) {
        var lang = getLang();
        return (T[lang] && T[lang][key]) || (T.zh && T.zh[key]) || key;
    }

    // 应用翻译到页面
    function applyLang(lang) {
        if (!lang) lang = getLang();
        // data-i18n → textContent
        document.querySelectorAll('[data-i18n]').forEach(function(el) {
            var key = el.getAttribute('data-i18n');
            var val = (T[lang] && T[lang][key]) || (T.zh && T.zh[key]);
            if (val) el.textContent = val;
        });
        // data-i18n-html → innerHTML
        document.querySelectorAll('[data-i18n-html]').forEach(function(el) {
            var key = el.getAttribute('data-i18n-html');
            var val = (T[lang] && T[lang][key]) || (T.zh && T.zh[key]);
            if (val) el.innerHTML = val;
        });
        // data-i18n-placeholder → placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el) {
            var key = el.getAttribute('data-i18n-placeholder');
            var val = (T[lang] && T[lang][key]) || (T.zh && T.zh[key]);
            if (val) el.placeholder = val;
        });
        // data-i18n-title → title
        document.querySelectorAll('[data-i18n-title]').forEach(function(el) {
            var key = el.getAttribute('data-i18n-title');
            var val = (T[lang] && T[lang][key]) || (T.zh && T.zh[key]);
            if (val) el.title = val;
        });
        // 更新切换按钮文本
        var switcherLabel = document.getElementById('langSwitcherLabel');
        if (switcherLabel && LANGS[lang]) {
            switcherLabel.textContent = LANGS[lang].flag;
        }
        // 更新激活状态
        document.querySelectorAll('.lang-option').forEach(function(opt) {
            opt.classList.toggle('active', opt.getAttribute('data-lang') === lang);
        });
        // html lang
        document.documentElement.lang = lang === 'zh' ? 'zh-CN' : lang;
    }

    // 创建语言切换器 UI
    function createSwitcher() {
        var wrapper = document.createElement('div');
        wrapper.className = 'lang-switcher';
        wrapper.innerHTML =
            '<button class="lang-switcher-btn" id="langSwitcherBtn" onclick="window._toggleLangMenu()">' +
            '<span id="langSwitcherLabel">🇨🇳</span></button>' +
            '<div class="lang-menu" id="langMenu">' +
            '<div class="lang-option" data-lang="zh" onclick="window._setLang(\'zh\')">🇨🇳 中文</div>' +
            '<div class="lang-option" data-lang="en" onclick="window._setLang(\'en\')">🇬🇧 English</div>' +
            '<div class="lang-option" data-lang="ru" onclick="window._setLang(\'ru\')">🇷🇺 Русский</div>' +
            '</div>';
        document.body.appendChild(wrapper);
    }

    window._toggleLangMenu = function() {
        var menu = document.getElementById('langMenu');
        if (menu) menu.classList.toggle('show');
    };

    window._setLang = function(lang) {
        setLang(lang);
        var menu = document.getElementById('langMenu');
        if (menu) menu.classList.remove('show');
    };

    // 点击外部关闭菜单
    document.addEventListener('click', function(e) {
        var switcher = document.querySelector('.lang-switcher');
        if (switcher && !switcher.contains(e.target)) {
            var menu = document.getElementById('langMenu');
            if (menu) menu.classList.remove('show');
        }
    });

    // 暴露全局
    window.t = t;
    window.getLang = getLang;
    window.setLang = setLang;
    window.applyLang = applyLang;

    // 初始化
    document.addEventListener('DOMContentLoaded', function() {
        createSwitcher();
        applyLang(getLang());
    });
})();
