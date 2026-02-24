"""
代理管理服务
支持 SS / VMess / Trojan / VLESS 代理格式解析、订阅链接获取、Xray 子进程管理
"""
import asyncio
import base64
import json
import logging
import os
import subprocess
import tempfile
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, unquote, parse_qs

import httpx

logger = logging.getLogger(__name__)


# ==================== 数据模型 ====================

class ProxyNode:
    """代理节点（通用，支持所有协议）"""

    def __init__(
        self,
        name: str,
        protocol: str,
        server: str,
        port: int,
        raw_url: str = "",
        # SS 字段
        method: str = "",
        password: str = "",
        # VMess 字段
        uuid: str = "",
        alter_id: int = 0,
        security: str = "auto",
        # 传输层
        network: str = "tcp",
        tls: str = "",
        sni: str = "",
        host: str = "",
        path: str = "",
        # Trojan
        # (用 password 字段)
        # VLESS
        flow: str = "",
        encryption: str = "none",
        # 额外
        extra: dict = None,
    ):
        self.name = name
        self.protocol = protocol  # ss / vmess / trojan / vless
        self.server = server
        self.port = port
        self.raw_url = raw_url
        self.method = method
        self.password = password
        self.uuid = uuid
        self.alter_id = alter_id
        self.security = security
        self.network = network
        self.tls = tls
        self.sni = sni
        self.host = host
        self.path = path
        self.flow = flow
        self.encryption = encryption
        self.extra = extra or {}

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "protocol": self.protocol,
            "server": self.server,
            "port": self.port,
            "method": self.method,
            "password": self.password,
            "uuid": self.uuid,
            "alter_id": self.alter_id,
            "security": self.security,
            "network": self.network,
            "tls": self.tls,
            "sni": self.sni,
            "host": self.host,
            "path": self.path,
            "flow": self.flow,
            "encryption": self.encryption,
            "raw_url": self.raw_url,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ProxyNode":
        return cls(
            name=d.get("name", ""),
            protocol=d.get("protocol", ""),
            server=d.get("server", ""),
            port=d.get("port", 0),
            method=d.get("method", ""),
            password=d.get("password", ""),
            uuid=d.get("uuid", ""),
            alter_id=d.get("alter_id", 0),
            security=d.get("security", "auto"),
            network=d.get("network", "tcp"),
            tls=d.get("tls", ""),
            sni=d.get("sni", ""),
            host=d.get("host", ""),
            path=d.get("path", ""),
            flow=d.get("flow", ""),
            encryption=d.get("encryption", "none"),
            raw_url=d.get("raw_url", ""),
            extra=d.get("extra", {}),
        )


# ==================== Base64 工具 ====================

def _b64_decode(s: str) -> str:
    """Base64 解码（自动补全 padding）"""
    s = s.strip()
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    try:
        return base64.urlsafe_b64decode(s).decode("utf-8", errors="replace")
    except Exception:
        try:
            return base64.b64decode(s).decode("utf-8", errors="replace")
        except Exception:
            return ""


# ==================== 协议解析器 ====================

def parse_ss_url(url: str) -> Optional[ProxyNode]:
    """解析 SS URL (SIP002 / Legacy / Plain)"""
    url = url.strip()
    if not url.startswith("ss://"):
        return None
    try:
        name = ""
        if "#" in url:
            url, name = url.rsplit("#", 1)
            name = unquote(name)
        body = url[5:]

        if "@" in body:
            user_info, server_part = body.rsplit("@", 1)
            if "?" in server_part:
                server_part = server_part.split("?")[0]
            if ":" in server_part:
                server, port_str = server_part.rsplit(":", 1)
                port = int(port_str)
            else:
                return None
            decoded = _b64_decode(user_info)
            if ":" in decoded:
                method, password = decoded.split(":", 1)
            elif ":" in user_info:
                method, password = user_info.split(":", 1)
                method = unquote(method)
                password = unquote(password)
            else:
                return None
        else:
            decoded = _b64_decode(body)
            if "@" not in decoded:
                return None
            user_info, server_part = decoded.rsplit("@", 1)
            if ":" not in user_info or ":" not in server_part:
                return None
            method, password = user_info.split(":", 1)
            server, port_str = server_part.rsplit(":", 1)
            port = int(port_str)

        if not name:
            name = f"{server}:{port}"
        return ProxyNode(
            name=name, protocol="ss", server=server.strip(), port=port,
            method=method.strip(), password=password.strip(), raw_url=url,
        )
    except Exception as e:
        logger.warning(f"解析 SS URL 失败: {e}")
        return None


def parse_vmess_url(url: str) -> Optional[ProxyNode]:
    """解析 VMess URL: vmess://BASE64(JSON)"""
    url = url.strip()
    if not url.startswith("vmess://"):
        return None
    try:
        body = url[8:]
        decoded = _b64_decode(body)
        if not decoded:
            return None
        cfg = json.loads(decoded)

        return ProxyNode(
            name=cfg.get("ps", "") or cfg.get("remark", "") or f"{cfg.get('add')}:{cfg.get('port')}",
            protocol="vmess",
            server=cfg.get("add", ""),
            port=int(cfg.get("port", 0)),
            uuid=cfg.get("id", ""),
            alter_id=int(cfg.get("aid", 0)),
            security=cfg.get("scy", "auto") or "auto",
            network=cfg.get("net", "tcp") or "tcp",
            tls=cfg.get("tls", ""),
            sni=cfg.get("sni", ""),
            host=cfg.get("host", ""),
            path=cfg.get("path", ""),
            raw_url=url,
            extra={"type": cfg.get("type", "none")},
        )
    except Exception as e:
        logger.warning(f"解析 VMess URL 失败: {e}")
        return None


def parse_trojan_url(url: str) -> Optional[ProxyNode]:
    """解析 Trojan URL: trojan://password@server:port?params#name"""
    url = url.strip()
    if not url.startswith("trojan://"):
        return None
    try:
        name = ""
        if "#" in url:
            url, name = url.rsplit("#", 1)
            name = unquote(name)
        parsed = urlparse(url)
        password = unquote(parsed.username or "")
        server = parsed.hostname or ""
        port = parsed.port or 443
        params = parse_qs(parsed.query)

        if not name:
            name = f"{server}:{port}"
        return ProxyNode(
            name=name, protocol="trojan", server=server, port=port,
            password=password,
            network=params.get("type", ["tcp"])[0],
            tls="tls",
            sni=params.get("sni", [server])[0],
            host=params.get("host", [""])[0],
            path=params.get("path", [""])[0],
            raw_url=url,
        )
    except Exception as e:
        logger.warning(f"解析 Trojan URL 失败: {e}")
        return None


def parse_vless_url(url: str) -> Optional[ProxyNode]:
    """解析 VLESS URL: vless://uuid@server:port?params#name"""
    url = url.strip()
    if not url.startswith("vless://"):
        return None
    try:
        name = ""
        if "#" in url:
            url, name = url.rsplit("#", 1)
            name = unquote(name)
        parsed = urlparse(url)
        uuid = unquote(parsed.username or "")
        server = parsed.hostname or ""
        port = parsed.port or 443
        params = parse_qs(parsed.query)

        if not name:
            name = f"{server}:{port}"
        return ProxyNode(
            name=name, protocol="vless", server=server, port=port,
            uuid=uuid,
            encryption=params.get("encryption", ["none"])[0],
            network=params.get("type", ["tcp"])[0],
            tls=params.get("security", [""])[0],
            sni=params.get("sni", [server])[0],
            host=params.get("host", [""])[0],
            path=params.get("path", [""])[0],
            flow=params.get("flow", [""])[0],
            raw_url=url,
            extra={"fp": params.get("fp", [""])[0], "pbk": params.get("pbk", [""])[0],
                    "sid": params.get("sid", [""])[0]},
        )
    except Exception as e:
        logger.warning(f"解析 VLESS URL 失败: {e}")
        return None


def parse_ssr_url(url: str) -> Optional[ProxyNode]:
    """解析 SSR URL: ssr://BASE64(server:port:protocol:method:obfs:b64pass/?params)"""
    url = url.strip()
    if not url.startswith("ssr://"):
        return None
    try:
        body = url[6:]
        decoded = _b64_decode(body)
        if not decoded:
            return None

        main_part = decoded.split("/?")[0]
        parts = main_part.split(":")
        if len(parts) < 6:
            return None

        server = parts[0]
        port = int(parts[1])
        ssr_protocol = parts[2]
        method = parts[3]
        obfs = parts[4]
        password = _b64_decode(parts[5])

        # 从查询参数中获取名称
        name = f"{server}:{port}"
        if "/?" in decoded:
            param_str = decoded.split("/?")[1]
            params = parse_qs(param_str)
            if "remarks" in params:
                name = _b64_decode(params["remarks"][0]) or name

        return ProxyNode(
            name=name, protocol="ss", server=server, port=port,
            method=method, password=password, raw_url=url,
            extra={"ssr_protocol": ssr_protocol, "obfs": obfs},
        )
    except Exception as e:
        logger.warning(f"解析 SSR URL 失败: {e}")
        return None


def parse_node_url(url: str) -> Optional[ProxyNode]:
    """统一解析入口，自动识别协议"""
    url = url.strip()
    if url.startswith("vmess://"):
        return parse_vmess_url(url)
    elif url.startswith("vless://"):
        return parse_vless_url(url)
    elif url.startswith("trojan://"):
        return parse_trojan_url(url)
    elif url.startswith("ss://"):
        return parse_ss_url(url)
    elif url.startswith("ssr://"):
        return parse_ssr_url(url)
    return None


# ==================== Clash YAML 解析 ====================

def _parse_clash_proxy(p: dict) -> Optional[ProxyNode]:
    """解析 Clash YAML 中的单个 proxy 节点"""
    try:
        ptype = (p.get("type") or "").lower()
        name = p.get("name", "")
        server = str(p.get("server", ""))
        port = int(p.get("port", 0))

        if not server or not port:
            return None

        if ptype == "vmess":
            ws_opts = p.get("ws-opts") or p.get("ws-opt") or {}
            ws_headers = ws_opts.get("headers") or {}
            network = p.get("network", "tcp") or "tcp"
            return ProxyNode(
                name=name, protocol="vmess", server=server, port=port,
                uuid=p.get("uuid", ""),
                alter_id=int(p.get("alterId", 0)),
                security=p.get("cipher", "auto") or "auto",
                network=network,
                tls="tls" if p.get("tls") else "",
                sni=p.get("servername", "") or p.get("sni", ""),
                host=ws_headers.get("Host", "") or ws_headers.get("host", ""),
                path=ws_opts.get("path", ""),
                extra={"type": p.get("type", "")},
            )

        elif ptype == "vless":
            ws_opts = p.get("ws-opts") or {}
            ws_headers = ws_opts.get("headers") or {}
            network = p.get("network", "tcp") or "tcp"
            reality_opts = p.get("reality-opts") or {}
            tls_val = ""
            if reality_opts:
                tls_val = "reality"
            elif p.get("tls"):
                tls_val = "tls"
            return ProxyNode(
                name=name, protocol="vless", server=server, port=port,
                uuid=p.get("uuid", ""),
                encryption="none",
                network=network,
                tls=tls_val,
                sni=p.get("servername", "") or p.get("sni", ""),
                host=ws_headers.get("Host", "") or ws_headers.get("host", ""),
                path=ws_opts.get("path", ""),
                flow=p.get("flow", ""),
                extra={
                    "fp": p.get("client-fingerprint", ""),
                    "pbk": reality_opts.get("public-key", ""),
                    "sid": reality_opts.get("short-id", ""),
                },
            )

        elif ptype == "trojan":
            ws_opts = p.get("ws-opts") or {}
            ws_headers = ws_opts.get("headers") or {}
            network = p.get("network", "tcp") or "tcp"
            return ProxyNode(
                name=name, protocol="trojan", server=server, port=port,
                password=p.get("password", ""),
                network=network,
                tls="tls",
                sni=p.get("sni", "") or p.get("servername", "") or server,
                host=ws_headers.get("Host", "") or ws_headers.get("host", ""),
                path=ws_opts.get("path", ""),
            )

        elif ptype == "ss":
            return ProxyNode(
                name=name, protocol="ss", server=server, port=port,
                method=p.get("cipher", "") or p.get("method", ""),
                password=p.get("password", ""),
            )

        elif ptype == "ssr":
            return ProxyNode(
                name=name, protocol="ss", server=server, port=port,
                method=p.get("cipher", "") or p.get("method", ""),
                password=p.get("password", ""),
                extra={
                    "ssr_protocol": p.get("protocol", ""),
                    "obfs": p.get("obfs", ""),
                },
            )

        elif ptype == "hysteria2" or ptype == "hysteria":
            return ProxyNode(
                name=name, protocol="hysteria2", server=server, port=port,
                password=p.get("password", "") or p.get("auth-str", ""),
                tls="tls",
                sni=p.get("sni", "") or server,
                extra={"type": ptype},
            )

        else:
            logger.debug(f"跳过不支持的 Clash 节点类型: {ptype}")
            return None

    except Exception as e:
        logger.warning(f"解析 Clash 节点失败: {e}")
        return None


def parse_clash_config(text: str) -> List[ProxyNode]:
    """解析 Clash YAML 配置文件，提取 proxies 列表"""
    import yaml

    nodes: List[ProxyNode] = []
    try:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            return nodes

        proxies = data.get("proxies") or []
        for p in proxies:
            if not isinstance(p, dict):
                continue
            node = _parse_clash_proxy(p)
            if node:
                nodes.append(node)

    except Exception as e:
        logger.warning(f"解析 Clash YAML 失败: {e}")

    return nodes


# ==================== 订阅获取 ====================

async def fetch_subscription(subscription_url: str) -> List[ProxyNode]:
    """
    获取代理订阅链接，解析出所有支持的节点
    自动识别格式: base64 编码 URL 列表 / Clash YAML 配置

    Args:
        subscription_url: 订阅 URL

    Returns:
        节点列表
    """
    nodes: List[ProxyNode] = []

    # 按优先级尝试多个 User-Agent（不同机场对 UA 敏感）
    user_agents = [
        "clash-verge/v1.3.8",
        "ClashForWindows/0.20.39",
        "ClashX/1.118.0",
        "ClashForAndroid/2.5.12",
    ]

    last_error = None
    for ua in user_agents:
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                resp = await client.get(subscription_url, headers={"User-Agent": ua})
                resp.raise_for_status()
                raw = resp.text.strip()

            nodes = _parse_raw_subscription(raw)
            if nodes:
                logger.info(f"使用 UA '{ua}' 成功获取到节点")
                break
            logger.info(f"UA '{ua}' 获取到 0 个节点,尝试下一个...")
        except Exception as e:
            last_error = e
            logger.warning(f"UA '{ua}' 请求失败: {e},尝试下一个...")
            continue

    if not nodes and last_error:
        logger.error(f"所有 UA 均获取失败,最后错误: {last_error}")
        raise last_error

    proto_counts: dict = {}
    for n in nodes:
        proto_counts[n.protocol] = proto_counts.get(n.protocol, 0) + 1
    summary = ", ".join(f"{p}: {c}" for p, c in proto_counts.items())
    logger.info(f"订阅解析完成: 共 {len(nodes)} 个节点 ({summary})")

    return nodes


def _parse_raw_subscription(raw: str) -> List[ProxyNode]:
    """尝试各种格式解析订阅内容"""
    nodes: List[ProxyNode] = []

    # 1) 检测是否为 Clash YAML 格式
    if ("proxies:" in raw or "Proxy:" in raw):
        parsed = parse_clash_config(raw)
        if parsed:
            logger.info("检测到 Clash YAML 格式订阅")
            return parsed

    # 2) 尝试 base64 解码
    decoded = _b64_decode(raw)
    if decoded and ("\n" in decoded or "://" in decoded):
        text = decoded.strip()
    else:
        text = raw

    # 2a) 解码后可能也是 Clash YAML
    if ("proxies:" in text or "Proxy:" in text):
        parsed = parse_clash_config(text)
        if parsed:
            logger.info("检测到 base64 编码的 Clash YAML 格式订阅")
            return parsed

    # 2b) 按行解析 URL 列表
    for line in text.splitlines():
        line = line.strip()
        if not line or "://" not in line:
            continue
        node = parse_node_url(line)
        if node:
            nodes.append(node)

    return nodes


# ==================== Xray 配置生成 ====================

def _build_xray_config(node: ProxyNode, local_port: int) -> dict:
    """
    根据节点信息生成 Xray JSON 配置

    Args:
        node: 代理节点
        local_port: 本地 SOCKS5 监听端口

    Returns:
        Xray 配置字典
    """
    # 入站: 本地 SOCKS5
    inbound = {
        "tag": "socks-in",
        "port": local_port,
        "listen": "127.0.0.1",
        "protocol": "socks",
        "settings": {"auth": "noauth", "udp": True},
    }

    # 出站: 根据协议构建
    outbound = _build_outbound(node)

    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [inbound],
        "outbounds": [outbound],
    }

    return config


def _build_outbound(node: ProxyNode) -> dict:
    """根据节点协议构建 Xray outbound"""

    if node.protocol == "vmess":
        outbound = {
            "tag": "proxy",
            "protocol": "vmess",
            "settings": {
                "vnext": [{
                    "address": node.server,
                    "port": node.port,
                    "users": [{
                        "id": node.uuid,
                        "alterId": node.alter_id,
                        "security": node.security or "auto",
                    }],
                }],
            },
        }

    elif node.protocol == "vless":
        user = {
            "id": node.uuid,
            "encryption": node.encryption or "none",
        }
        if node.flow:
            user["flow"] = node.flow
        outbound = {
            "tag": "proxy",
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": node.server,
                    "port": node.port,
                    "users": [user],
                }],
            },
        }

    elif node.protocol == "trojan":
        outbound = {
            "tag": "proxy",
            "protocol": "trojan",
            "settings": {
                "servers": [{
                    "address": node.server,
                    "port": node.port,
                    "password": node.password,
                }],
            },
        }

    elif node.protocol == "ss":
        outbound = {
            "tag": "proxy",
            "protocol": "shadowsocks",
            "settings": {
                "servers": [{
                    "address": node.server,
                    "port": node.port,
                    "method": node.method,
                    "password": node.password,
                }],
            },
        }

    else:
        outbound = {
            "tag": "proxy",
            "protocol": "shadowsocks",
            "settings": {
                "servers": [{
                    "address": node.server,
                    "port": node.port,
                    "method": node.method or "aes-256-gcm",
                    "password": node.password,
                }],
            },
        }

    # 传输层设置
    stream = {}
    net = node.network or "tcp"
    stream["network"] = net

    if net == "ws":
        ws_settings = {}
        if node.path:
            ws_settings["path"] = node.path
        if node.host:
            ws_settings["headers"] = {"Host": node.host}
        stream["wsSettings"] = ws_settings

    elif net == "grpc":
        stream["grpcSettings"] = {
            "serviceName": node.path or "",
        }

    elif net == "h2" or net == "http":
        stream["network"] = "http"
        h2 = {}
        if node.path:
            h2["path"] = node.path
        if node.host:
            h2["host"] = [node.host]
        stream["httpSettings"] = h2

    # TLS 设置
    if node.tls in ("tls", "1", "true"):
        stream["security"] = "tls"
        tls_settings = {"allowInsecure": True}
        if node.sni:
            tls_settings["serverName"] = node.sni
        fp = node.extra.get("fp", "")
        if fp:
            tls_settings["fingerprint"] = fp
        stream["tlsSettings"] = tls_settings

    elif node.tls == "reality":
        stream["security"] = "reality"
        reality = {}
        if node.sni:
            reality["serverName"] = node.sni
        fp = node.extra.get("fp", "")
        if fp:
            reality["fingerprint"] = fp
        pbk = node.extra.get("pbk", "")
        if pbk:
            reality["publicKey"] = pbk
        sid = node.extra.get("sid", "")
        if sid:
            reality["shortId"] = sid
        stream["realitySettings"] = reality

    outbound["streamSettings"] = stream
    return outbound


# ==================== Xray 进程管理 ====================

class SSLocalManager:
    """
    管理 Xray 子进程，提供本地 SOCKS5 代理
    支持 SS / VMess / Trojan / VLESS 等所有 Xray 支持的协议
    """

    LOCAL_PORT = 1081

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._current_node: Optional[ProxyNode] = None
        self._config_path: Optional[str] = None
        self._lock = asyncio.Lock()

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def current_node(self) -> Optional[ProxyNode]:
        return self._current_node

    @property
    def local_proxy_url(self) -> Optional[str]:
        if self.is_running:
            return f"socks5://127.0.0.1:{self.LOCAL_PORT}"
        return None

    async def start(self, node: ProxyNode) -> bool:
        """
        启动 Xray 连接到指定节点

        Args:
            node: 代理节点

        Returns:
            是否启动成功
        """
        async with self._lock:
            await self._stop_internal()

            try:
                # 生成 Xray 配置
                config = _build_xray_config(node, self.LOCAL_PORT)

                # 写入临时配置文件
                fd, config_path = tempfile.mkstemp(suffix=".json", prefix="xray_")
                with os.fdopen(fd, "w") as f:
                    json.dump(config, f, indent=2)
                self._config_path = config_path

                cmd = ["xray", "run", "-c", config_path]

                logger.info(f"启动 Xray: [{node.protocol}] {node.name} ({node.server}:{node.port})")

                self._process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # 等待检查是否立即失败
                await asyncio.sleep(1.5)

                if self._process.poll() is not None:
                    stderr = self._process.stderr.read().decode() if self._process.stderr else ""
                    logger.error(f"Xray 启动后立即退出: {stderr[:500]}")
                    self._cleanup_config()
                    self._process = None
                    return False

                self._current_node = node
                logger.info(f"Xray 已启动,本地代理: socks5://127.0.0.1:{self.LOCAL_PORT}")
                return True

            except FileNotFoundError:
                logger.error("xray 未安装,请确保 Xray-core 已安装")
                self._cleanup_config()
                return False
            except Exception as e:
                logger.error(f"启动 Xray 失败: {e}")
                self._cleanup_config()
                return False

    async def stop(self):
        """停止 Xray"""
        async with self._lock:
            await self._stop_internal()

    async def _stop_internal(self):
        """内部停止方法（不加锁）"""
        if self._process is not None:
            try:
                self._process.terminate()
                try:
                    self._process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait(timeout=2)
            except Exception as e:
                logger.warning(f"停止 Xray 异常: {e}")
            finally:
                self._process = None
                self._current_node = None
                self._cleanup_config()
                logger.info("Xray 已停止")

    def _cleanup_config(self):
        """清理临时配置文件"""
        if self._config_path and os.path.exists(self._config_path):
            try:
                os.remove(self._config_path)
            except Exception:
                pass
            self._config_path = None

    def status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "running": self.is_running,
            "local_proxy": self.local_proxy_url,
            "current_node": self._current_node.to_dict() if self._current_node else None,
        }


# 全局实例
ss_local_manager = SSLocalManager()
