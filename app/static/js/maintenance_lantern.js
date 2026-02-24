(function () {
    // 动态添加样式
    const style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = `
        .deng-box {
            position: fixed;
            top: -30px;
            left: 10px;
            z-index: 9999;
            pointer-events: none;
            overflow: visible;
        }

        .deng-box1 {
            position: fixed;
            top: -30px;
            right: 10px;
            z-index: 9999;
            pointer-events: none;
            overflow: visible;
        }

        .deng-box1 .deng,
        .deng {
            position: relative;
            width: 170px;
            height: 128px;
            margin: 64px;
            background: #d8000f;
            background: rgba(216, 0, 15, 0.8);
            border-radius: 50% 50%;
            -webkit-transform-origin: 50% -100px;
            -webkit-animation: swing 3s infinite ease-in-out;
            box-shadow: -5px 5px 50px 4px rgba(250, 108, 0, 1);
        }

        .deng-box1 .deng {
            -webkit-animation: swing 5s infinite ease-in-out;
            box-shadow: -5px 5px 30px 4px rgba(252, 144, 61, 1);
        }

        .deng-a {
            width: 100px;
            height: 90px;
                width: 142px;
                height: 128px;
            border-radius: 50% 50%;
                margin: 16px 10px 10px 10px;
        }

        .deng-b {
            width: 45px;
            height: 90px;
                width: 64px;
                height: 128px;
                margin: -6px 10px 10px 37px;
            border: 2px solid #dc8f03;
        }

        .xian {
            position: absolute;
            top: -44px;
            left: 50%;
            transform: translateX(-50%);
            width: 3px;
            height: 44px;
            background: linear-gradient(180deg, #f7c24f 0%, #dc8f03 100%);
            border-radius: 999px;
            box-shadow: 0 0 6px rgba(220, 143, 3, 0.45);
        }

        .xian:before {
            content: "";
            position: absolute;
            top: -6px;
            left: 50%;
            transform: translateX(-50%);
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #ffd978 0%, #dc8f03 72%);
        }

        .shui-a {
            position: relative;
            width: 5px;
            height: 20px;
            margin: -5px 0 0 59px;
                margin: -5px 0 0 83px;
            -webkit-transform-origin: 50% -45px;
            background: #ffa500;
            border-radius: 0 0 5px 5px;
        }

        .shui-b {
            position: absolute;
            top: 14px;
            left: -2px;
            width: 10px;
            height: 10px;
            background: #dc8f03;
            border-radius: 50%;
        }

        .shui-c {
            position: absolute;
            top: 18px;
            left: -2px;
            width: 10px;
            height: 35px;
            background: #ffa500;
            border-radius: 0 0 0 5px;
        }

        .deng:before {
            position: absolute;
            top: -8px;
            left: 42px;
            height: 14px;
            width: 86px;
            content: " ";
            display: block;
            z-index: 999;
            border-radius: 5px 5px 0 0;
            border: solid 1px #dc8f03;
            background: linear-gradient(to right, #dc8f03, #ffa500, #dc8f03, #ffa500, #dc8f03);
        }

        .deng:after {
            position: absolute;
            bottom: -8px;
            left: 15px;
            height: 14px;
            width: 86px;
            content: " ";
            display: block;
            margin-left: 28px;
            border-radius: 0 0 5px 5px;
            border: solid 1px #dc8f03;
            background: linear-gradient(to right, #dc8f03, #ffa500, #dc8f03, #ffa500, #dc8f03);
        }

        .deng-t {
            font-family: 华文行楷, Arial, Lucida Grande, Tahoma, sans-serif;
            font-size: 4.4rem;
            color: #dc8f03;
            font-weight: bold;
            line-height: 120px;
            text-align: center;
        }

        @-webkit-keyframes swing {
            0% {
                -webkit-transform: rotate(-10deg);
            }
            50% {
                -webkit-transform: rotate(10deg);
            }
            100% {
                -webkit-transform: rotate(-10deg);
            }
        }
    `;
    document.head.appendChild(style);

    // 动态添加灯笼的 HTML
    const createLantern = (boxClass, text) => {
        const box = document.createElement('div');
        box.className = boxClass;

        const deng = document.createElement('div');
        deng.className = 'deng';

        const xian = document.createElement('div');
        xian.className = 'xian';

        const dengA = document.createElement('div');
        dengA.className = 'deng-a';

        const dengB = document.createElement('div');
        dengB.className = 'deng-b';

        const dengT = document.createElement('div');
        dengT.className = 'deng-t';
        dengT.innerText = text;

        const shuiA = document.createElement('div');
        shuiA.className = 'shui shui-a';

        const shuiC = document.createElement('div');
        shuiC.className = 'shui-c';

        const shuiB = document.createElement('div');
        shuiB.className = 'shui-b';

        dengB.appendChild(dengT);
        dengA.appendChild(dengB);
        shuiA.appendChild(shuiC);
        shuiA.appendChild(shuiB);
        deng.appendChild(xian);
        deng.appendChild(dengA);
        deng.appendChild(shuiA);
        box.appendChild(deng);

        document.body.appendChild(box);
    };

    // 创建灯笼1 (春)
    createLantern('deng-box', '春');

    // 创建灯笼2 (节)
    createLantern('deng-box1', '节');
})();
