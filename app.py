import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import json
import os
import threading
import requests
from datetime import datetime
try:
    import pyperclip
except ImportError:
    pyperclip = None

# 设置现代化主题样式
def setup_modern_style():
    """设置现代化的UI样式"""
    style = ttk.Style()
    # 使用clam主题（在Windows上看起来更现代）
    style.theme_use('clam')
    
    # 自定义字体 - 增大字体
    default_font = ('微软雅黑', 11)
    title_font = ('微软雅黑', 18, 'bold')
    button_font = ('微软雅黑', 11)
    
    # 配置默认字体
    style.configure('.', font=default_font)
    
    # 自定义颜色和样式
    style.configure('Treeview', 
                  rowheight=30,  # 增加行高
                  font=('微软雅黑', 11))  # 表格字体
    style.map('Treeview', 
              background=[('selected', '#4a90d9')],
              foreground=[('selected', 'white')])
    style.configure('Treeview.Heading', 
                  font=('微软雅黑', 12, 'bold'))  # 表头字体
    
    # 按钮样式
    style.configure('TButton', 
                  padding=(12, 8),
                  font=button_font)
    style.configure('Accent.TButton', 
                  foreground='white', 
                  background='#007acc',
                  font=button_font)
    
    # LabelFrame样式
    style.configure('TLabelframe', 
                  font=('微软雅黑', 12, 'bold'))
    style.configure('TLabelframe.Label', 
                  font=('微软雅黑', 12, 'bold'))
    
    # Label样式
    style.configure('TLabel', 
                  font=('微软雅黑', 11))
    
    # Entry样式
    style.configure('TEntry', 
                  font=('微软雅黑', 11),
                  padding=5)
    
    # Combobox样式
    style.configure('TCombobox', 
                  font=('微软雅黑', 11),
                  padding=5)
    
    # Scale样式
    style.configure('TScale', 
                  font=('微软雅黑', 11))
    
    # Scrollbar样式
    style.configure('TScrollbar', 
                  arrowsize=16)

class APIKeyManager:
    def __init__(self):
        self.keys_file = "api_keys.json"
        self.keys = self.load_keys()
    
    def load_keys(self):
        """从文件加载API密钥"""
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载密钥文件出错: {e}")
                return []
        return []
    
    def save_keys(self):
        """保存API密钥到文件"""
        try:
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                json.dump(self.keys, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存密钥文件出错: {e}")
    
    def add_key(self, name, api_key, api_base=None, provider=None, model_type="gpt-3.5-turbo"):
        """添加新的API密钥"""
        # 验证API基础URL格式
        if api_base and not self.is_valid_url(api_base):
            raise ValueError("API基础URL格式不正确，请确保包含协议（如https://）")
        
        # 如果没有提供provider，则尝试从api_base推断
        if provider is None:
            if api_base:
                if "openai.com" in api_base:
                    provider = "OpenAI"
                elif "anthropic.com" in api_base:
                    provider = "Anthropic"
                elif "generativelanguage.googleapis.com" in api_base:
                    provider = "Google AI"
                elif "cohere.ai" in api_base:
                    provider = "Cohere"
                elif "dashscope.aliyuncs.com" in api_base:
                    provider = "通义千问"
                elif "qianfan.baidubce.com" in api_base:
                    provider = "百度千帆"
                elif "hunyuan.cloud.tencent.com" in api_base:
                    provider = "腾讯混元"
                elif "ark.cn-beijing.volces.com" in api_base or "volces.com" in api_base:
                    provider = "字节豆包"
                elif "moonshot.cn" in api_base:
                    provider = "月之暗面"
                elif "minimax.chat" in api_base:
                    provider = "Minimax"
                elif "lingyiwanwu.com" in api_base:
                    provider = "零一万物"
                elif "bigmodel.cn" in api_base:
                    provider = "智谱AI"
                elif "spark-api-open.xf-yun.com" in api_base:
                    provider = "讯飞星火"
                elif "perplexity.ai" in api_base:
                    provider = "Perplexity"
                elif "groq.com" in api_base:
                    provider = "Groq"
                elif "mistral.ai" in api_base:
                    provider = "Mistral AI"
                else:
                    provider = "OpenAI"  # 默认值
            else:
                provider = "OpenAI"  # 默认值
        
        # 为常见provider设置默认api_base
        if not api_base:
            provider_lower = provider.lower()
            if provider_lower in ["openai", "openai"]:
                api_base = "https://api.openai.com/v1"
            elif provider_lower in ["anthropic", "claude", "anthropic claude"]:
                api_base = "https://api.anthropic.com/v1"
            elif provider_lower in ["google ai", "google", "gemini"]:
                api_base = "https://generativelanguage.googleapis.com/v1beta"
            elif provider_lower in ["cohere"]:
                api_base = "https://api.cohere.ai/v1"
            elif provider_lower in ["deepseek"]:
                api_base = "https://api.deepseek.com/v1"
            elif provider_lower in ["qwen", "通义千问", "aliyun百炼", "aliyun"]:
                api_base = "https://dashscope.aliyuncs.com/api/v1"
            elif provider_lower in ["ernie", "百度千帆", "baidu"]:
                api_base = "https://qianfan.baidubce.com/v1"
            elif provider_lower in ["hunyuan", "腾讯混元", "tencent"]:
                api_base = "https://api.hunyuan.cloud.tencent.com/v1"
            elif provider_lower in ["doubao", "字节豆包", "bytedance"]:
                api_base = "https://ark.cn-beijing.volces.com/api/v3"
            elif provider_lower in ["moonshot ai", "moonshot", "月之暗面"]:
                api_base = "https://api.moonshot.cn/v1"
            elif provider_lower in ["minimax"]:
                api_base = "https://api.minimax.chat/v1"
            elif provider_lower in ["yi", "零一万物"]:
                api_base = "https://api.lingyiwanwu.com/v1"
            elif provider_lower in ["glm", "chatglm", "智谱ai", "智谱"]:
                api_base = "https://open.bigmodel.cn/api/paas/v4"
            elif provider_lower in ["spark", "讯飞星火", "xfyun"]:
                api_base = "https://spark-api-open.xf-yun.com/v1"
            elif provider_lower in ["perplexity"]:
                api_base = "https://api.perplexity.ai/"
            elif provider_lower in ["groq"]:
                api_base = "https://api.groq.com/openai/v1"
            elif provider_lower in ["mistral ai", "mistral"]:
                api_base = "https://api.mistral.ai/v1"
            else:
                # 默认使用OpenAI格式的API基础URL
                api_base = "https://api.openai.com/v1"
        
        new_key = {
            "name": name,
            "api_key": api_key,
            "api_base": api_base,
            "provider": provider,
            "model_type": model_type,
            "last_tested": None,
            "is_valid": None,
            "created_at": datetime.now().isoformat()
        }
        self.keys.append(new_key)
        self.save_keys()
    
    def is_valid_url(self, url):
        """检查URL是否符合基本格式"""
        import re
        # 基本的URL格式检查，包括是否包含协议
        pattern = re.compile(
            r'^https?://'  # http:// 或 https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # 可选端口
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return pattern.match(url) is not None
    
    def update_key_status(self, name, is_valid):
        """更新密钥状态"""
        for key in self.keys:
            if key["name"] == name:
                key["is_valid"] = is_valid
                key["last_tested"] = datetime.now().isoformat()
                break
        self.save_keys()

class APIValidator:
    @staticmethod
    def validate_openai_key(api_key, api_base="https://api.openai.com/v1"):
        """验证OpenAI API密钥"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                f"{api_base}/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"验证OpenAI密钥时出错: {e}")
            return False
    
    @staticmethod
    def validate_anthropic_key(api_key):
        """验证Anthropic API密钥"""
        try:
            headers = {
                "x-api-key": api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            # 发送一个最小的请求来测试密钥
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=10
            )
            # 如果返回的是400，说明密钥有效但请求有问题；如果是401，说明密钥无效
            return response.status_code != 401
        except Exception as e:
            print(f"验证Anthropic密钥时出错: {e}")
            return False
    
    @staticmethod
    def validate_google_key(api_key):
        """验证Google AI API密钥"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            # 尝试列出可用的模型
            response = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"验证Google AI密钥时出错: {e}")
            return False
    
    @staticmethod
    def validate_cohere_key(api_key):
        """验证Cohere API密钥"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            # 尝试获取模型列表
            response = requests.get(
                "https://api.cohere.ai/v1/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"验证Cohere密钥时出错: {e}")
            return False
    
    @staticmethod
    def validate_baidu_key(api_key, api_base="https://qianfan.baidubce.com/v1"):
        """验证百度千帆API密钥"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            # 使用简单的模型列表请求来验证
            response = requests.get(
                f"{api_base}/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"验证百度千帆密钥时出错: {e}")
            return False
    
    @staticmethod
    def validate_perplexity_key(api_key):
        """验证Perplexity API密钥"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            # 尝试发送简单请求
            data = {
                "model": "pplx-7b-online",
                "messages": [{"role": "user", "content": "Hello"}]
            }
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            # 401表示密钥无效，其他状态码可能表示密钥有效但请求有问题
            return response.status_code != 401
        except Exception as e:
            print(f"验证Perplexity密钥时出错: {e}")
            return False
    
    @staticmethod
    def validate_groq_key(api_key):
        """验证Groq API密钥"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            # 尝试列出可用模型
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"验证Groq密钥时出错: {e}")
            return False
    
    @staticmethod
    def validate_other_key(api_key, api_base, provider):
        """验证其他类型的API密钥"""
        provider_lower = provider.lower()
        
        # 特殊处理的provider
        if provider_lower in ["ernie", "百度千帆", "baidu"]:
            return APIValidator.validate_baidu_key(api_key, api_base)
        elif provider_lower in ["google ai", "google", "gemini"]:
            return APIValidator.validate_google_key(api_key)
        elif provider_lower in ["cohere"]:
            return APIValidator.validate_cohere_key(api_key)
        elif provider_lower in ["perplexity"]:
            return APIValidator.validate_perplexity_key(api_key)
        elif provider_lower in ["groq"]:
            return APIValidator.validate_groq_key(api_key)
        
        # 对于兼容OpenAI格式的provider，使用OpenAI验证方式
        if provider_lower in [
            "deepseek", "qwen", "通义千问", "aliyun百炼", "aliyun", 
            "hunyuan", "腾讯混元", "tencent", "doubao", "字节豆包", "bytedance",
            "moonshot ai", "moonshot", "月之暗面", "minimax", 
            "yi", "零一万物", "spark", "讯飞星火", "xfyun", "glm", "chatglm", "智谱ai", "智谱",
            "mistral ai", "mistral"
        ]:
            return APIValidator.validate_openai_key(api_key, api_base)
        
        # 其他provider暂时返回True
        return True

class APIClient:
    @staticmethod
    def call_openai_api(api_key, api_base, model, messages, temperature=0.7):
        """调用OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": False  # 简化处理，不使用流式响应
            }
            
            response = requests.post(
                f"{api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"API响应格式异常: {str(result)}"
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
        except Exception as e:
            return f"API调用异常: {str(e)}"
    
    @staticmethod
    def call_baidu_api(api_key, api_base, model, messages, temperature=0.7):
        """调用百度千帆API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # 转换消息格式
            query = ""
            history = []
            for msg in messages:
                if msg["role"] == "user":
                    if query:
                        history.append({"role": "user", "content": query})
                        history.append({"role": "assistant", "content": ""})  # 简化处理
                    query = msg["content"]
                elif msg["role"] == "assistant":
                    if history and history[-1]["role"] == "user":
                        history[-1]["content"] = msg["content"]
            
            data = {
                "model": model,
                "messages": messages,  # 直接使用标准格式
                "temperature": temperature,
                "stream": False
            }
            
            response = requests.post(
                f"{api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
                elif "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"API响应格式异常: {str(result)}"
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
        except Exception as e:
            return f"API调用异常: {str(e)}"
    
    @staticmethod
    def call_google_api(api_key, model, messages, temperature=0.7):
        """调用Google AI API (Gemini)"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            # 转换消息格式为Google Gemini格式
            contents = []
            for msg in messages:
                role = "user" if msg["role"] in ["user", "system"] else "model"  # Google使用user/model角色
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            data = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 2048
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            }
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and result["candidates"]:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                    return f"响应格式异常: {str(result)}"
                else:
                    return f"API响应中无候选答案: {str(result)}"
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
        except Exception as e:
            return f"API调用异常: {str(e)}"
    
    @staticmethod
    def call_cohere_api(api_key, model, messages, temperature=0.7):
        """调用Cohere API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # 将消息转换为适合Cohere的格式
            chat_history = []
            message = ""
            
            for msg in messages:
                if msg["role"] == "user":
                    message = msg["content"]  # 最后一条用户消息作为当前请求
                elif msg["role"] == "assistant":
                    chat_history.append({"role": "CHATBOT", "message": msg["content"]})
                elif msg["role"] == "system":
                    # 将系统消息作为首条用户消息
                    chat_history.append({"role": "USER", "message": msg["content"]})
            
            data = {
                "model": model,
                "message": message,
                "chat_history": chat_history,
                "temperature": temperature
            }
            
            response = requests.post(
                "https://api.cohere.ai/v1/chat",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "text" in result:
                    return result["text"]
                else:
                    return f"API响应格式异常: {str(result)}"
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
        except Exception as e:
            return f"API调用异常: {str(e)}"
    
    @staticmethod
    def call_anthropic_api(api_key, model, messages, temperature=0.7):
        """调用Anthropic API"""
        try:
            headers = {
                "x-api-key": api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # 将标准格式的消息转换为Anthropic格式
            system_msg = ""
            user_msgs = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                elif msg["role"] == "user" or msg["role"] == "assistant":
                    user_msgs.append(msg)
            
            # Anthropic API要求消息必须交替出现
            data = {
                "model": model,
                "max_tokens": 1024,
                "temperature": temperature,
                "messages": user_msgs
            }
            
            if system_msg:
                data["system"] = system_msg
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict):
                    if "completion" in result:
                        return result.get("completion", "")
                    if "content" in result:
                        content = result.get("content")
                        if isinstance(content, list) and content:
                            first = content[0]
                            if isinstance(first, dict):
                                return first.get("text", "")
                            if isinstance(first, str):
                                return first
                        if isinstance(content, str):
                            return content
                    return result.get("text", "") or str(result)
                return str(result)
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
        except Exception as e:
            return f"API调用异常: {str(e)}"

class APIKeyManagerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("大模型API密钥管理器 - 对话测试")
        self.root.geometry("1000x700")
        
        # 设置现代化样式
        setup_modern_style()
        
        self.manager = APIKeyManager()
        self.current_api_key = None
        self.chat_history = []
        
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=2)
        
        # 标题
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="🤖 大模型API密钥管理器", font=("微软雅黑", 20, "bold"))
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(title_frame, text="支持多平台API密钥管理与对话测试", 
                               font=("微软雅黑", 11), foreground="#666666")
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 上半部分：密钥管理区域
        # 左侧表格
        table_frame = ttk.LabelFrame(main_frame, text="🔐 API密钥管理", padding="10")
        table_frame.grid(row=1, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # 表格
        columns = ("name", "model_type", "last_tested", "is_valid")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # 定义列标题
        self.tree.heading("name", text="名称")
        self.tree.heading("model_type", text="模型类型")
        self.tree.heading("last_tested", text="最后测试时间")
        self.tree.heading("is_valid", text="是否有效")
        
        # 设置列宽
        self.tree.column("name", width=150)
        self.tree.column("model_type", width=120)
        self.tree.column("last_tested", width=130)
        self.tree.column("is_valid", width=80)
        
        # 滚动条
        tree_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 按钮框架
        button_frame = ttk.Frame(table_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="➕ 添加密钥", command=self.add_key_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🔍 验证所有", command=self.validate_all_keys).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🔄 刷新", command=self.refresh_table).pack(side=tk.LEFT, padx=2)
        
        # 排序按钮框架
        sort_button_frame = ttk.Frame(table_frame)
        sort_button_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(sort_button_frame, text="🔤 按名称排序", command=lambda: self.sort_table_by_name()).pack(side=tk.LEFT, padx=2)
        ttk.Button(sort_button_frame, text="🤖 按模型类型排序", command=lambda: self.sort_table_by_model()).pack(side=tk.LEFT, padx=2)
        
        # 绑定双击事件以编辑选中的密钥
        self.tree.bind("<Double-1>", self.edit_key_dialog)
        
        # 添加右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📋 复制API密钥", command=self.copy_selected_api_key)
        self.context_menu.add_command(label="🔗 复制API基础URL", command=self.copy_selected_api_base)
        self.context_menu.add_command(label="🏷️ 复制名称", command=self.copy_selected_name)
        self.context_menu.add_command(label="⚙️ 复制完整配置", command=self.copy_selected_full_config)
        self.context_menu.add_separator()  # 分隔线
        self.context_menu.add_command(label="✏️ 编辑名称", command=self.edit_selected_name)
        self.context_menu.add_command(label="🔑 编辑API密钥", command=self.edit_selected_api_key)
        self.context_menu.add_command(label="🌐 编辑API基础URL", command=self.edit_selected_api_base)
        self.context_menu.add_separator()  # 分隔线
        self.context_menu.add_command(label="🗑️ 删除", command=self.delete_selected_key)
        self.context_menu.add_separator()  # 分隔线
        self.context_menu.add_command(label="✅ 设为当前对话密钥", command=self.set_current_key)
        
        # 绑定右键点击事件
        self.tree.bind("<Button-3>", self.show_context_menu)  # Windows/Linux
        self.tree.bind("<Button-2>", self.show_context_menu)  # macOS (通常使用中键)
        
        # 中间控制区域（简化版）
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # 当前密钥选择（简化）
        current_key_frame = ttk.Frame(control_frame)
        current_key_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(current_key_frame, text="🔑 当前密钥:").pack(side=tk.LEFT, padx=(0, 5))
        self.current_key_var = tk.StringVar()
        self.current_key_combo = ttk.Combobox(current_key_frame, textvariable=self.current_key_var, 
                                             values=[], state="readonly", width=25)
        self.current_key_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 参数设置（简化）
        param_frame = ttk.Frame(control_frame)
        param_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(param_frame, text="🌡️ 温度:").pack(side=tk.LEFT, padx=(0, 5))
        self.temp_var = tk.DoubleVar(value=0.7)
        temp_scale = ttk.Scale(param_frame, from_=0.0, to=2.0, variable=self.temp_var, 
                               orient=tk.HORIZONTAL, length=120)
        temp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.temp_label = ttk.Label(param_frame, text="0.7")
        self.temp_label.pack(side=tk.LEFT)
        
        temp_scale.configure(command=lambda v: self.temp_label.config(text=f"{float(v):.1f}"))
        
        # 下半部分：对话区域
        chat_frame = ttk.LabelFrame(main_frame, text="💬 对话测试", padding="10")
        chat_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # 聊天历史显示
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                                      font=("微软雅黑", 11), bg="#f5f5f5")
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 用户输入
        ttk.Label(chat_frame, text="📝 输入:").grid(row=1, column=0, sticky=tk.W)
        self.user_input = scrolledtext.ScrolledText(chat_frame, height=3, wrap=tk.WORD, 
                                                    font=("微软雅黑", 11))
        self.user_input.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 按钮
        button_frame2 = ttk.Frame(chat_frame)
        button_frame2.grid(row=3, column=0, columnspan=2, pady=5)
        button_frame2.columnconfigure(0, weight=1)
        
        send_btn = ttk.Button(button_frame2, text="🚀 发送", command=self.send_message, 
                              style='Accent.TButton')
        send_btn.grid(row=0, column=0, sticky=tk.W)
        
        clear_btn = ttk.Button(button_frame2, text="🗑️ 清空对话", command=self.clear_chat)
        clear_btn.grid(row=0, column=1, padx=(5, 0))
        
        # 绑定回车键发送消息
        self.user_input.bind('<Return>', lambda event: self.send_message())
    
    def refresh_key_list(self):
        """刷新密钥下拉列表"""
        key_names = [key["name"] for key in self.manager.keys]
        self.current_key_combo['values'] = key_names
        
        if self.current_api_key and self.current_api_key.get("name") in key_names:
            self.current_key_var.set(self.current_api_key["name"])
        elif self.current_key_var.get() in key_names:
            selected_name = self.current_key_var.get()
            self.current_api_key = next((k for k in self.manager.keys if k["name"] == selected_name), None)
        elif key_names:
            self.current_key_var.set(key_names[0])
            self.current_api_key = self.manager.keys[0]
        else:
            self.current_key_var.set("")
            self.current_api_key = None
        
        # 解绑可能已存在的事件，然后重新绑定下拉列表选择变化事件
        self.current_key_combo.unbind('<<ComboboxSelected>>')
        self.current_key_combo.bind('<<ComboboxSelected>>', self.on_key_selection_change)
    
    def on_key_selection_change(self, event=None):
        """当下拉列表选择变化时更新当前API密钥"""
        selected_name = self.current_key_var.get()
        if selected_name:
            self.current_api_key = next((k for k in self.manager.keys if k["name"] == selected_name), None)
    
    def set_current_key(self):
        """设置当前对话密钥"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️ 警告", "请先选择一行")
            return
        
        item = self.tree.item(selection[0])
        name = item['values'][0]
        
        for key in self.manager.keys:
            if key["name"] == name:
                self.current_api_key = key
                self.current_key_var.set(name)
                # 同步更新下拉框的选择
                self.current_key_combo.set(name)
                messagebox.showinfo("✅ 成功", f"已设置 '{name}' 为当前对话密钥")
                return
    
    def send_message(self):
        """发送消息到API"""
        if not self.current_api_key:
            selected_name = self.current_key_var.get().strip()
            if selected_name:
                self.current_api_key = next((k for k in self.manager.keys if k["name"] == selected_name), None)
            if not self.current_api_key and self.manager.keys:
                self.current_api_key = self.manager.keys[0]
                self.current_key_var.set(self.current_api_key["name"])
        
        if not self.current_api_key:
            messagebox.showwarning("⚠️ 警告", "请先选择一个API密钥作为当前对话密钥")
            return
        
        user_text = self.user_input.get("1.0", tk.END).strip()
        if not user_text:
            messagebox.showwarning("⚠️ 警告", "请输入要发送的消息")
            return
        
        # 获取温度值
        temperature = self.temp_var.get()
        
        # 添加用户消息到聊天记录
        self.add_to_chat("👤 用户", user_text)
        self.user_input.delete("1.0", tk.END)
        
        # 在新线程中调用API，避免界面冻结
        def api_call_thread():
            # 准备消息历史
            messages = self.chat_history + [{"role": "user", "content": user_text}]
            
            # 根据提供商调用相应API
            provider = self.current_api_key.get("provider", "OpenAI").lower()
            api_key = self.current_api_key["api_key"]
            api_base = self.current_api_key.get("api_base", "https://api.openai.com/v1")
            model = self.current_api_key.get("model_type", "gpt-3.5-turbo")
            
            if provider in ["openai", "openai"]:
                response = APIClient.call_openai_api(api_key, api_base, model, messages, temperature)
            elif provider in ["anthropic", "claude", "anthropic claude"]:
                response = APIClient.call_anthropic_api(api_key, model, messages, temperature)
            elif provider in ["google ai", "google", "gemini"]:
                response = APIClient.call_google_api(api_key, model, messages, temperature)
            elif provider in ["cohere"]:
                response = APIClient.call_cohere_api(api_key, model, messages, temperature)
            elif provider in ["ernie", "百度千帆", "baidu"]:
                response = APIClient.call_baidu_api(api_key, api_base, model, messages, temperature)
            elif provider in [
                "deepseek", "qwen", "通义千问", "aliyun百炼", "aliyun", 
                "hunyuan", "腾讯混元", "tencent", "doubao", "字节豆包", "bytedance",
                "moonshot ai", "moonshot", "月之暗面", "minimax", 
                "yi", "零一万物", "spark", "讯飞星火", "xfyun", "glm", "chatglm", "智谱ai", "智谱",
                "mistral ai", "mistral"
            ]:
                # 这些provider兼容OpenAI格式
                response = APIClient.call_openai_api(api_key, api_base, model, messages, temperature)
            else:
                # 其他provider也尝试OpenAI格式
                response = APIClient.call_openai_api(api_key, api_base, model, messages, temperature)
            
            # 更新UI
            self.root.after(0, lambda: self.add_to_chat("🤖 助手", response))
            
            # 更新使用计数
            # 不再跟踪使用次数
            pass
            self.manager.save_keys()
            self.refresh_table()
        
        thread = threading.Thread(target=api_call_thread, daemon=True)
        thread.start()
    
    def add_to_chat(self, sender, message):
        """添加消息到聊天记录"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        header = f"\n[{timestamp}] {sender}: "
        
        self.chat_display.insert(tk.END, header)
        self.chat_display.insert(tk.END, message)
        self.chat_display.insert(tk.END, "\n" + "-"*50)
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # 更新内部聊天历史
        self.chat_history.append({"role": "user" if sender == "用户" else "assistant", "content": message})
    
    def clear_chat(self):
        """清空聊天记录"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_history = []
    
    def refresh_table(self):
        """刷新表格显示"""
        # 清除现有项目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加密钥数据
        for key in self.manager.keys:
            last_tested = key.get("last_tested", "未测试")
            if last_tested:
                # 格式化时间为更易读的形式
                try:
                    dt = datetime.fromisoformat(last_tested.replace('Z', '+00:00'))
                    last_tested = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            is_valid = "是" if key.get("is_valid") else "否" if key.get("is_valid") is False else "未测试"
            
            self.tree.insert("", tk.END, values=(
                key["name"],
                key["model_type"],
                last_tested,
                is_valid
            ))
        
        # 刷新密钥列表
        self.refresh_key_list()
        
        # 默认按名称排序
        self.sort_table_by_name()
    
    def copy_to_clipboard(self, text, field_name):
        """复制文本到剪贴板"""
        if text:
            if pyperclip:
                try:
                    pyperclip.copy(text)
                    messagebox.showinfo("已复制", f"{field_name}已复制到剪贴板")
                except Exception as e:
                    # 如果pyperclip失败，回退到tkinter clipboard
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
                    messagebox.showinfo("已复制", f"{field_name}已复制到剪贴板")
            else:
                # 如果没有pyperclip，使用tkinter clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                messagebox.showinfo("已复制", f"{field_name}已复制到剪贴板")
        else:
            messagebox.showwarning("警告", f"没有{field_name}可以复制")
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 检查是否有选中项
        selection = self.tree.selection()
        if selection:
            # 尝试获取右键点击的项目
            item = self.tree.identify_row(event.y)
            if item:
                # 选中右键点击的行
                self.tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
    
    def copy_selected_api_key(self):
        """复制选中的API密钥"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一行")
            return
        
        item = self.tree.item(selection[0])
        name = item['values'][0]
        
        # 查找对应的密钥数据
        for key in self.manager.keys:
            if key["name"] == name:
                self.copy_to_clipboard(key["api_key"], "API密钥")
                return
    
    def copy_selected_api_base(self):
        """复制选中的API基础URL"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一行")
            return
        
        item = self.tree.item(selection[0])
        name = item['values'][0]
        
        # 查找对应的密钥数据
        for key in self.manager.keys:
            if key["name"] == name:
                api_base = key.get("api_base")
                if api_base:
                    self.copy_to_clipboard(api_base, "API基础URL")
                else:
                    messagebox.showwarning("警告", "该密钥没有设置API基础URL")
                return
    
    def copy_selected_name(self):
        """复制选中的名称"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一行")
            return
        
        item = self.tree.item(selection[0])
        name = item['values'][0]
        
        self.copy_to_clipboard(name, "名称")
    
    def copy_selected_full_config(self):
        """复制选中的密钥完整配置到剪贴板"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️ 警告", "请先选择一行")
            return
        
        item = self.tree.item(selection[0])
        name = item['values'][0]
        
        # 查找对应的密钥数据
        key_data = None
        for key in self.manager.keys:
            if key["name"] == name:
                key_data = key
                break
        
        if not key_data:
            messagebox.showerror("❌ 错误", "找不到对应的密钥数据")
            return
        
        # 创建完整配置的JSON字符串
        import json
        config_json = json.dumps(key_data, ensure_ascii=False, indent=2)
        
        self.root.clipboard_clear()
        self.root.clipboard_append(config_json)
        messagebox.showinfo("✅ 成功", f"已复制完整配置: {name}")
    
    def edit_selected_name(self):
        """编辑选中的名称"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️ 警告", "请先选择一行")
            return
        
        item = self.tree.item(selection[0])
        old_name = item['values'][0]
        
        # 查找对应的密钥数据
        key_to_edit = None
        for key in self.manager.keys:
            if key["name"] == old_name:
                key_to_edit = key
                break
        
        if not key_to_edit:
            return
        
        # 创建编辑对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ 编辑名称")
        dialog.geometry("450x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示对话框
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx()+50, self.root.winfo_rooty()+50))
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 名称输入框
        ttk.Label(main_frame, text="🏷️ 新的名称:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=10)
        name_entry = ttk.Entry(main_frame, width=40, font=("微软雅黑", 11))
        name_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky=(tk.W, tk.E))
        name_entry.insert(0, old_name)
        name_entry.select_range(0, tk.END)  # 选中所有文本，方便编辑
        
        # 配置列权重
        main_frame.columnconfigure(1, weight=1)
        
        def update_name():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("❌ 错误", "名称不能为空")
                return
            
            # 检查新名称是否已存在
            for key in self.manager.keys:
                if key["name"] == new_name and new_name != old_name:
                    messagebox.showerror("❌ 错误", f"名称 '{new_name}' 已存在，请选择其他名称")
                    return
            
            # 更新密钥数据
            key_to_edit["name"] = new_name
            self.manager.save_keys()
            self.refresh_table()
            dialog.destroy()
            messagebox.showinfo("✅ 成功", "名称已更新")
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="💾 保存", command=update_name, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_selected_api_key(self):
        """编辑选中的API密钥"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️ 警告", "请先选择一行")
            return
        
        item = self.tree.item(selection[0])
        name = item['values'][0]
        
        # 查找对应的密钥数据
        key_to_edit = None
        for key in self.manager.keys:
            if key["name"] == name:
                key_to_edit = key
                break
        
        if not key_to_edit:
            return
        
        # 创建编辑对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("🔑 编辑API密钥")
        dialog.geometry("500x180")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示对话框
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx()+50, self.root.winfo_rooty()+50))
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # API密钥输入框
        ttk.Label(main_frame, text="🔑 新的API密钥:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=10)
        key_entry = ttk.Entry(main_frame, width=40, show="*", font=("微软雅黑", 11))
        key_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky=(tk.W, tk.E))
        key_entry.insert(0, key_to_edit["api_key"])
        
        # 配置列权重
        main_frame.columnconfigure(1, weight=1)
        
        def update_key():
            new_api_key = key_entry.get().strip()
            if not new_api_key:
                messagebox.showerror("❌ 错误", "API密钥不能为空")
                return
            
            # 更新密钥数据
            key_to_edit["api_key"] = new_api_key
            self.manager.save_keys()
            self.refresh_table()
            dialog.destroy()
            messagebox.showinfo("✅ 成功", "API密钥已更新")
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="💾 保存", command=update_key, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_selected_api_base(self):
        """编辑选中的API基础URL"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️ 警告", "请先选择一行")
            return
        
        item = self.tree.item(selection[0])
        name = item['values'][0]
        
        # 查找对应的密钥数据
        key_to_edit = None
        for key in self.manager.keys:
            if key["name"] == name:
                key_to_edit = key
                break
        
        if not key_to_edit:
            return
        
        # 创建编辑对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("🌐 编辑API基础URL")
        dialog.geometry("500x180")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示对话框
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx()+50, self.root.winfo_rooty()+50))
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # API基础URL输入框
        ttk.Label(main_frame, text="🌐 新的API基础URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=10)
        base_entry = ttk.Entry(main_frame, width=40, font=("微软雅黑", 11))
        base_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky=(tk.W, tk.E))
        if key_to_edit.get("api_base"):
            base_entry.insert(0, key_to_edit["api_base"])
        
        # 配置列权重
        main_frame.columnconfigure(1, weight=1)
        
        def update_base():
            new_api_base = base_entry.get().strip() or None
            
            # 更新密钥数据
            key_to_edit["api_base"] = new_api_base
            self.manager.save_keys()
            self.refresh_table()
            dialog.destroy()
            messagebox.showinfo("✅ 成功", "API基础URL已更新")
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="💾 保存", command=update_base, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_selected_key(self):
        """删除选中的密钥"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️ 警告", "请先选择一行")
            return
        
        item = self.tree.item(selection[0])
        name = item['values'][0]
        
        # 确认删除
        if messagebox.askyesno("⚠️ 确认删除", f"确定要删除密钥 '{name}' 吗？\n此操作无法撤销！"):
            # 从列表中移除密钥
            self.manager.keys = [key for key in self.manager.keys if key["name"] != name]
            self.manager.save_keys()
            self.refresh_table()
            messagebox.showinfo("✅ 成功", f"密钥 '{name}' 已删除")
    
    def add_key_dialog(self):
        """添加密钥对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ 添加API密钥")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示对话框
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx()+50, self.root.winfo_rooty()+50))
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表单字段
        ttk.Label(main_frame, text="🔑 名称:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        name_entry = ttk.Entry(main_frame, width=40, font=("微软雅黑", 11))
        name_entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(main_frame, text="🔑 API密钥:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        key_entry_frame = ttk.Frame(main_frame)
        key_entry_frame.grid(row=1, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        
        key_entry = ttk.Entry(key_entry_frame, width=30, show="*", font=("微软雅黑", 11))
        key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        copy_key_btn = ttk.Button(key_entry_frame, text="📋", width=3, 
                                  command=lambda: self.copy_to_clipboard(key_entry.get(), "API密钥"))
        copy_key_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(main_frame, text="🌐 API基础URL (可选):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        base_entry_frame = ttk.Frame(main_frame)
        base_entry_frame.grid(row=2, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        
        base_entry = ttk.Entry(base_entry_frame, width=30, font=("微软雅黑", 11))
        base_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        copy_base_btn = ttk.Button(base_entry_frame, text="📋", width=3,
                                   command=lambda: self.copy_to_clipboard(base_entry.get(), "API基础URL"))
        copy_base_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 隐藏提供商选择，使用内部默认值
        provider_var = tk.StringVar(value="OpenAI")
        
        ttk.Label(main_frame, text="🧠 模型类型:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        model_var = tk.StringVar(value="gpt-3.5-turbo")
        model_entry = ttk.Entry(main_frame, textvariable=model_var, font=("微软雅黑", 11))
        model_entry.grid(row=4, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        
        # 配置列权重以实现响应式布局
        main_frame.columnconfigure(1, weight=1)
        
        def save_key():
            name = name_entry.get().strip()
            api_key = key_entry.get().strip()
            api_base = base_entry.get().strip() or None
            model_type = model_var.get()
            
            if not name or not api_key:
                messagebox.showerror("❌ 错误", "名称和API密钥不能为空")
                return
            
            # 检查名称是否已存在
            for key in self.manager.keys:
                if key["name"] == name:
                    messagebox.showerror("❌ 错误", f"名称 '{name}' 已存在，请选择其他名称")
                    return
            
            try:
                # 添加新密钥（不传递provider参数，让系统自动推断）
                self.manager.add_key(name, api_key, api_base, model_type=model_type)
                self.refresh_table()
                dialog.destroy()
                messagebox.showinfo("✅ 成功", f"API密钥 '{name}' 已添加")
            except ValueError as e:
                messagebox.showerror("❌ 错误", str(e))
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="💾 保存", command=save_key, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_key_dialog(self, event):
        """编辑密钥对话框"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        name = item['values'][0]
        
        # 找到对应的密钥数据
        key_data = None
        for key in self.manager.keys:
            if key["name"] == name:
                key_data = key
                break
        
        if not key_data:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ 编辑API密钥")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示对话框
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx()+50, self.root.winfo_rooty()+50))
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表单字段
        ttk.Label(main_frame, text="🏷️ 名称:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        name_entry = ttk.Entry(main_frame, width=35, font=("微软雅黑", 11))
        name_entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        name_entry.insert(0, key_data["name"])
        name_entry.config(state="disabled")  # 名称不允许修改
        
        ttk.Label(main_frame, text="🔑 API密钥:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        key_entry_frame = ttk.Frame(main_frame)
        key_entry_frame.grid(row=1, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        
        key_entry = ttk.Entry(key_entry_frame, width=30, show="*", font=("微软雅黑", 11))
        key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        key_entry.insert(0, key_data["api_key"])
        
        copy_key_btn = ttk.Button(key_entry_frame, text="📋", width=3,
                                  command=lambda: self.copy_to_clipboard(key_entry.get(), "API密钥"))
        copy_key_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(main_frame, text="🌐 API基础URL (可选):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        base_entry_frame = ttk.Frame(main_frame)
        base_entry_frame.grid(row=2, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        
        base_entry = ttk.Entry(base_entry_frame, width=30, font=("微软雅黑", 11))
        base_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if key_data.get("api_base"):
            base_entry.insert(0, key_data["api_base"])
        
        copy_base_btn = ttk.Button(base_entry_frame, text="📋", width=3,
                                   command=lambda: self.copy_to_clipboard(base_entry.get(), "API基础URL"))
        copy_base_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 隐藏提供商选择，使用内部默认值
        provider_var = tk.StringVar(value=key_data.get("provider", "OpenAI"))
        
        ttk.Label(main_frame, text="🧠 模型类型:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        model_var = tk.StringVar(value=key_data.get("model_type", "gpt-3.5-turbo"))
        model_entry = ttk.Entry(main_frame, textvariable=model_var, font=("微软雅黑", 11))
        model_entry.grid(row=4, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        
        # 配置列权重以实现响应式布局
        main_frame.columnconfigure(1, weight=1)
        
        def update_key():
            api_key = key_entry.get().strip()
            api_base = base_entry.get().strip() or None
            model_type = model_var.get()
            
            if not api_key:
                messagebox.showerror("❌ 错误", "请输入API密钥")
                return
            
            # 验证API基础URL格式
            if api_base and not self.manager.is_valid_url(api_base):
                messagebox.showerror("❌ 错误", "API基础URL格式不正确，请确保包含协议（如https://）")
                return
            
            # 更新密钥数据
            for key in self.manager.keys:
                if key["name"] == name:
                    key["api_key"] = api_key
                    key["api_base"] = api_base
                    # 根据api_base自动推断provider
                    if api_base:
                        if "openai.com" in api_base:
                            key["provider"] = "OpenAI"
                        elif "anthropic.com" in api_base:
                            key["provider"] = "Anthropic"
                        elif "generativelanguage.googleapis.com" in api_base:
                            key["provider"] = "Google AI"
                        elif "cohere.ai" in api_base:
                            key["provider"] = "Cohere"
                        elif "dashscope.aliyuncs.com" in api_base:
                            key["provider"] = "通义千问"
                        elif "qianfan.baidubce.com" in api_base:
                            key["provider"] = "百度千帆"
                        elif "hunyuan.cloud.tencent.com" in api_base:
                            key["provider"] = "腾讯混元"
                        elif "ark.cn-beijing.volces.com" in api_base or "volces.com" in api_base:
                            key["provider"] = "字节豆包"
                        elif "moonshot.cn" in api_base:
                            key["provider"] = "月之暗面"
                        elif "minimax.chat" in api_base:
                            key["provider"] = "Minimax"
                        elif "lingyiwanwu.com" in api_base:
                            key["provider"] = "零一万物"
                        elif "bigmodel.cn" in api_base:
                            key["provider"] = "智谱AI"
                        elif "spark-api-open.xf-yun.com" in api_base:
                            key["provider"] = "讯飞星火"
                        elif "perplexity.ai" in api_base:
                            key["provider"] = "Perplexity"
                        elif "groq.com" in api_base:
                            key["provider"] = "Groq"
                        elif "mistral.ai" in api_base:
                            key["provider"] = "Mistral AI"
                        else:
                            key["provider"] = key.get("provider", "OpenAI")  # 保持原provider或使用默认值
                    key["model_type"] = model_type
                    break
            
            self.manager.save_keys()
            self.refresh_table()
            dialog.destroy()
            messagebox.showinfo("✅ 成功", f"API密钥 '{name}' 已更新")
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="🔄 更新", command=update_key, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ 删除", command=lambda: self.delete_key(name, dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_key(self, name, dialog):
        """删除密钥"""
        if messagebox.askyesno("⚠️ 确认删除", f"确定要删除密钥 '{name}' 吗？\n此操作无法撤销！"):
            self.manager.keys = [key for key in self.manager.keys if key["name"] != name]
            self.manager.save_keys()
            self.refresh_table()
            dialog.destroy()
            messagebox.showinfo("✅ 成功", f"密钥 '{name}' 已删除")
    
    def validate_single_key(self, key_info):
        """验证单个密钥"""
        name = key_info["name"]
        api_key = key_info["api_key"]
        api_base = key_info.get("api_base")
        provider = key_info.get("provider", "OpenAI")
        model_type = key_info["model_type"]
        
        is_valid = False
        if provider.lower() in ["openai", "openai"]:
            is_valid = APIValidator.validate_openai_key(api_key, api_base)
        elif provider.lower() in ["anthropic", "claude"]:
            is_valid = APIValidator.validate_anthropic_key(api_key)
        else:
            is_valid = APIValidator.validate_other_key(api_key, api_base, provider)
        
        # 更新密钥状态
        self.manager.update_key_status(name, is_valid)
        
        return name, is_valid
    
    def validate_all_keys(self):
        """验证所有密钥"""
        if not self.manager.keys:
            messagebox.showinfo("提示", "没有密钥需要验证")
            return
        
        # 在新线程中验证，避免阻塞UI
        def validation_thread():
            total = len(self.manager.keys)
            for i, key in enumerate(self.manager.keys):
                # 更新进度
                progress = int((i + 1) / total * 100)
                print(f"验证进度: {progress}% ({i+1}/{total})")
                
                self.validate_single_key(key)
            
            # 刷新UI
            self.root.after(0, self.refresh_table)
        
        thread = threading.Thread(target=validation_thread, daemon=True)
        thread.start()
    
    def sort_table_by_name(self):
        """按名称排序表格"""
        # 获取所有项目并按名称排序
        items = [(self.tree.set(k, "name"), k) for k in self.tree.get_children('')]
        items.sort(key=lambda x: x[0].lower())  # 忽略大小写排序
        
        # 重新排列项目
        for index, (_, k) in enumerate(items):
            self.tree.move(k, '', index)
    
    def sort_table_by_model(self):
        """按模型类型排序表格"""
        # 获取所有项目并按模型类型排序
        items = [(self.tree.set(k, "model_type"), k) for k in self.tree.get_children('')]
        items.sort(key=lambda x: x[0].lower())  # 忽略大小写排序
        
        # 重新排列项目
        for index, (_, k) in enumerate(items):
            self.tree.move(k, '', index)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = APIKeyManagerApp()
    app.run()