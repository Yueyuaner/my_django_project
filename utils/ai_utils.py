import requests
import json
from django.conf import settings


def generate_data_summary(data, title="数据总结"):
    """调用OpenRouter API（带详细日志+代理+容错）"""
    # ==================== 1. 基础配置（必须改！） ====================
    API_KEY = settings.OPENROUTER_API_KEY
    # ① 替换成你的代理（比如Clash/梯子的本地代理，通常是127.0.0.1:7890）
    PROXY = {
        "http": "http://127.0.0.1:7897",
        "https": "http://127.0.0.1:7897",
    }
    # ② 模型名必须带提供商前缀（OpenRouter强制要求）
    MODEL_NAME = "openai/gpt-3.5-turbo"
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    # ==================== 2. 前置检查 ====================
    if not API_KEY:
        return "[错误1] 未配置API密钥！请在settings.py里设置OPENROUTER_API_KEY"
    if not PROXY["http"]:
        return "[错误2] 未配置代理！国内必须加代理才能访问OpenRouter"

    # ==================== 3. 构建请求 ====================
    prompt = f"""请总结以下{title}数据，用简洁明了的自然语言描述关键信息：
    数据：{json.dumps(data, ensure_ascii=False)}
    要求：1. 突出核心指标 2. 指出明显趋势 3. 保持专业简洁 4. 不超过300字
    """
    request_data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # ==================== 4. 调用API（带详细日志） ====================
    try:
        print(f"[调试] 开始调用OpenRouter | 模型：{MODEL_NAME} | 代理：{PROXY}")
        # 核心：加代理+超时+详细日志
        response = requests.post(
            API_URL,
            headers=headers,
            json=request_data,
            timeout=20,  # 延长超时时间
            proxies=proxies,  # 关键：代理访问
            verify=False,  # 忽略SSL证书错误（部分代理需要）
        )
        print(f"[调试] HTTP状态码：{response.status_code}")
        print(f"[调试] 响应内容：{response.text[:500]}")  # 打印前500字

        # 检查HTTP状态
        response.raise_for_status()

        # 解析结果
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    # ==================== 5. 精准错误提示（复制日志给我看） ====================
    except requests.exceptions.ProxyError:
        return "[错误3] 代理配置错误！请检查代理地址（比如7890端口是否正确），或确认梯子已开启"
    except requests.exceptions.ConnectTimeout:
        return "[错误4] 连接超时！代理无效/梯子未开/OpenRouter服务器故障"
    except requests.exceptions.SSLError:
        return "[错误5] SSL证书错误！已加verify=False，若仍报错请换代理"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return "[错误6] 密钥无效！检查OPENROUTER_API_KEY是否复制完整（无空格/换行）"
        elif e.response.status_code == 404:
            return "[错误7] 模型名错误！请确认模型名是openai/gpt-3.5-turbo（带前缀）"
        elif e.response.status_code == 429:
            return "[错误8] 限流！OpenRouter免费额度用完/请求太频繁"
        else:
            return f"[错误9] HTTP错误 {e.response.status_code}：{e.response.text[:200]}"
    except Exception as e:
        return f"[终极错误] 未知问题：{str(e)}（复制这个错误给我）"