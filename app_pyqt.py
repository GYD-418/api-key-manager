import sys
import json
import os
import time
import requests
import threading
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QComboBox, QTextEdit, QMessageBox, QHeaderView, QFrame,
    QDialog, QFormLayout, QDialogButtonBox, QSplitter, QGroupBox,
    QSlider, QCheckBox, QAction, QMenuBar, QMenu, QStatusBar,
    QTreeWidget, QTreeWidgetItem, QScrollArea, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QMimeData
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QBrush, QClipboard
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

class APIKeyManager:
    def __init__(self):
        self.keys_file = "api_keys.json"
        self.keys = self.load_keys()
    
    def load_keys(self):
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载密钥文件出错: {e}")
                return []
        return []
    
    def save_keys(self):
        try:
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                json.dump(self.keys, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存密钥文件出错: {e}")
    
    def add_key(self, name, api_key, api_base=None, provider=None, model_type="gpt-3.5-turbo"):
        if provider is None and api_base:
            if "openai.com" in api_base:
                provider = "OpenAI"
            elif "anthropic.com" in api_base:
                provider = "Anthropic"
            elif "dashscope.aliyuncs.com" in api_base:
                provider = "通义千问"
            elif "qianfan.baidubce.com" in api_base:
                provider = "百度千帆"
            elif "hunyuan.cloud.tencent.com" in api_base:
                provider = "腾讯混元"
            elif "ark.cn-beijing.volces.com" in api_base:
                provider = "字节豆包"
            elif "moonshot.cn" in api_base:
                provider = "月之暗面"
            elif "deepseek.com" in api_base:
                provider = "DeepSeek"
            else:
                provider = "OpenAI"
        elif not provider:
            provider = "OpenAI"
        
        if not api_base:
            provider_lower = provider.lower()
            if "openai" in provider_lower:
                api_base = "https://api.openai.com/v1"
            elif "anthropic" in provider_lower:
                api_base = "https://api.anthropic.com"
            elif "qwen" in provider_lower or "通义" in provider_lower:
                api_base = "https://dashscope.aliyuncs.com/api/v1"
            elif "deepseek" in provider_lower:
                api_base = "https://api.deepseek.com/v1"
            else:
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
    
    def update_key_status(self, name, is_valid):
        for key in self.keys:
            if key["name"] == name:
                key["is_valid"] = is_valid
                key["last_tested"] = datetime.now().isoformat()
                break
        self.save_keys()
    
    def delete_key(self, name):
        self.keys = [k for k in self.keys if k["name"] != name]
        self.save_keys()
    
    def update_key(self, old_name, name, api_key, api_base, model_type, provider):
        for key in self.keys:
            if key["name"] == old_name:
                key["name"] = name
                key["api_key"] = api_key
                key["api_base"] = api_base
                key["model_type"] = model_type
                key["provider"] = provider
                break
        self.save_keys()


class APIKeyManagerApp(QMainWindow):
    
    validation_complete_signal = pyqtSignal()
    validation_progress_signal = pyqtSignal(int, bool, int)
    
    def __init__(self):
        super().__init__()
        self.manager = APIKeyManager()  # API密钥管理器实例
        self.current_api_key = None    # 当前选中的API密钥
        self.chat_history = []         # 对话历史
        self.init_ui()
        self.refresh_table()
        
        # 连接验证信号
        self.validation_progress_signal.connect(self.update_validation_progress)
        self.validation_complete_signal.connect(self.on_validation_complete)
    
    def init_ui(self):
        # ==================== 窗口基本设置 ====================
        self.setWindowTitle("🤖 大模型API密钥管理器")  # 窗口标题
        self.setGeometry(100, 100, 1400, 850)  # 窗口位置和大小 (x, y, width, height)
        
        # ==================== 界面布局设置 ====================
        # 设置深色主题
        self.set_dark_theme()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 水平分割 (左右各占一半)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧 - 密钥管理面板 (各占一半)
        left_widget = self.create_key_manager_panel()
        main_layout.addWidget(left_widget, 1)  # stretch=1 表示占1份
        
        # 右侧 - 对话测试面板 (各占一半)
        right_widget = self.create_chat_panel()
        main_layout.addWidget(right_widget, 1)  # stretch=1 表示占1份
        
        # 状态栏显示
        self.statusBar().showMessage("就绪")  # 底部状态栏
    
    # ==================== 主题和样式设置 ====================
    def set_dark_theme(self):
        """设置深色主题调色板"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(dark_palette)
        
        # ==================== 消息框样式 ====================
        self.dark_message_style = """
            QMessageBox {
                background-color: #2b2b2b;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                padding: 8px 20px;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4a4a4a;
            }
        """
        
        # ==================== CSS样式表 ====================
        # 设置所有控件的样式，包括颜色、字体、边框等
        self.setStyleSheet("""
            /* 主窗口背景 */
            QMainWindow { background-color: #2b2b2b; }
            
            /* 按钮样式 - 背景深灰、白色文字、圆角 */
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                padding: 18px 35px;  /* 内边距: 上下18px, 左右35px */
                border-radius: 4px;   /* 圆角 */
                font-size: 18px;      /* 字体大小 */
                font-weight: bold;    /* 加粗 */
            }
            QPushButton:hover { background-color: #4a4a4a; border: 1px solid #2a82da; }
            QPushButton:pressed { background-color: #2a82da; }
            QPushButton#primary { background-color: #2a82da; border: none; }
            
            /* 输入框样式 - 背景深色、白色文字 */
            QLineEdit, QTextEdit, QComboBox {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #555;
                padding: 12px;       /* 内边距 */
                border-radius: 3px;    /* 圆角 */
                font-size: 16px;      /* 字体大小 */
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #2a82da; }
            
            /* 表格样式 */
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;  /* 交替行颜色 */
                gridline-color: #3a3a3a;              /* 网格线颜色 */
                color: white;
                font-size: 20px;
            }
            QTableWidget::item { padding: 20px; }
            QTableWidget::item:selected { background-color: #2a82da; }
            
            /* 表头样式 */
            QHeaderView::section {
                background-color: #3a3a3a;
                color: white;
                padding: 20px;
                border: none;
                font-weight: bold;
                font-size: 20px;
            }
            
            /* 标签样式 */
            QLabel { color: white; }
            
            /* 分组框样式 */
            QGroupBox {
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            
            /* 菜单栏样式 */
            QMenuBar { background-color: #2b2b2b; color: white; }
            QMenuBar::item:selected { background-color: #3a3a3a; }
            QMenu { background-color: #2b2b2b; color: white; border: 1px solid #555; }
            QMenu::item:selected { background-color: #2a82da; }
            
            /* 状态栏样式 */
            QStatusBar { background-color: #2b2b2b; color: white; }
            
            /* Tab控件样式 */
            QTabWidget::pane { border: 1px solid #555; background-color: #1e1e1e; }
            QTabBar::tab { background-color: #2b2b2b; color: white; padding: 8px 16px; border: 1px solid #555; }
            QTabBar::tab:selected { background-color: #2a82da; }
            
            /* 滚动条样式 */
            QScrollBar:vertical { background-color: #2b2b2b; width: 12px; }
            QScrollBar::handle:vertical { background-color: #555; min-height: 20px; border-radius: 6px; }
            QScrollBar:horizontal { background-color: #2b2b2b; height: 12px; }
            QScrollBar::handle:horizontal { background-color: #555; min-width: 20px; border-radius: 6px; }
            
            /* 树形控件样式 */
            QTreeWidget { background-color: #1e1e1e; color: white; border: none; }
            QTreeWidget::item:selected { background-color: #2a82da; }
            
            /* 滑块样式 */
            QSlider::groove:horizontal { height: 6px; background: #3a3a3a; border-radius: 3px; }
            QSlider::handle:horizontal { width: 16px; margin: -5px 0; background: #2a82da; border-radius: 8px; }  /* 滑块手柄宽度16px，margin用于居中 */
        """)
    
    def eventFilter(self, obj, event):
        """事件过滤器：处理回车发送消息"""
        if obj == self.user_input and event.type() == event.KeyPress:
            # Enter键发送消息（不带Shift）
            if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                self.send_message()
                return True  # 阻止默认换行行为
            # Shift+Enter 允许换行
            elif event.key() == Qt.Key_Return and event.modifiers() & Qt.ShiftModifier:
                return False  # 允许默认换行行为
        return super().eventFilter(obj, event)
    
    def show_dark_message(self, msg_type, title, message):
        """显示深色主题的消息框"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(self.dark_message_style)
        
        if msg_type == "information":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "critical":
            msg_box.setIcon(QMessageBox.Critical)
        
        msg_box.exec_()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("📁 文件")
        
        refresh_action = QAction("🔄 刷新", self)
        refresh_action.triggered.connect(self.refresh_table)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("❌ 退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("✏️ 编辑")
        
        add_action = QAction("➕ 添加密钥", self)
        add_action.triggered.connect(self.add_key_dialog)
        edit_menu.addAction(add_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("❓ 帮助")
        
        about_action = QAction("ℹ️ 关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    # ==================== 左侧面板：API密钥管理 ====================
    def create_key_manager_panel(self):
        """创建左侧API密钥管理面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)  # 边距: 左上右下
        
        # 标题
        title = QLabel("🔐 API密钥管理")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["名称", "模型类型", "最后测试", "有效"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.cellDoubleClicked.connect(self.edit_key_dialog)
        
        # 增大表格字体和行高
        self.table.setStyleSheet("""
            QTableWidget { 
                font-size: 20px; 
            }
            QTableWidget::item { 
                padding: 18px; 
                height: 45px;
            }
            QHeaderView::section {
                font-size: 20px;
                font-weight: bold;
                padding: 12px;
            }
        """)
        
        layout.addWidget(self.table)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ 添加")
        add_btn.setMinimumHeight(55)
        add_btn.setStyleSheet("font-size: 18px; font-weight: bold;")
        add_btn.clicked.connect(self.add_key_dialog)
        btn_layout.addWidget(add_btn)
        
        validate_btn = QPushButton("🔍 验证所有")
        validate_btn.setMinimumHeight(55)
        validate_btn.setStyleSheet("font-size: 18px; font-weight: bold;")
        validate_btn.clicked.connect(self.validate_all_keys)
        btn_layout.addWidget(validate_btn)
        
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setMinimumHeight(55)
        refresh_btn.setStyleSheet("font-size: 18px; font-weight: bold;")
        refresh_btn.clicked.connect(self.refresh_table)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # 排序按钮
        sort_layout = QHBoxLayout()
        
        sort_name_btn = QPushButton("🔤 按名称")
        sort_name_btn.setMinimumHeight(50)
        sort_name_btn.setStyleSheet("font-size: 17px;")
        sort_name_btn.clicked.connect(lambda: self.sort_table(0))
        sort_layout.addWidget(sort_name_btn)
        
        sort_model_btn = QPushButton("🤖 按模型")
        sort_model_btn.setMinimumHeight(50)
        sort_model_btn.setStyleSheet("font-size: 17px;")
        sort_model_btn.clicked.connect(lambda: self.sort_table(1))
        sort_layout.addWidget(sort_model_btn)
        
        sort_layout.addStretch()
        layout.addLayout(sort_layout)
        
        return widget
    
    # ==================== 右侧面板：对话测试 ====================
    def create_chat_panel(self):
        """创建右侧对话测试面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)  # 边距: 左上右下
        
        # 标题
        title = QLabel("💬 对话测试")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # 密钥选择和参数
        config_group = QGroupBox("⚙️ 配置")
        config_group.setStyleSheet("QGroupBox { color: white; font-size: 20px; }")
        config_layout = QFormLayout(config_group)
        
        # 密钥选择
        self.key_combo = QComboBox()
        self.key_combo.setMinimumWidth(300)
        self.key_combo.setMinimumHeight(45)
        self.key_combo.setStyleSheet("font-size: 20px;")
        
        key_label = QLabel("🔑 当前密钥:")
        key_label.setStyleSheet("font-size: 20px; color: #cccccc;")
        config_layout.addRow(key_label, self.key_combo)
        
        # 温度
        temp_layout = QHBoxLayout()
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(0)
        self.temp_slider.setMaximum(20)
        self.temp_slider.setValue(7)
        self.temp_label = QLabel("0.7")
        self.temp_label.setFixedWidth(30)
        self.temp_label.setStyleSheet("font-size: 20px;")
        self.temp_slider.valueChanged.connect(lambda v: self.temp_label.setText(f"{v/10:.1f}"))
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_label)
        
        temp_label = QLabel("🌡️ 温度:")
        temp_label.setStyleSheet("font-size: 20px; color: #cccccc;")
        config_layout.addRow(temp_label, temp_layout)
        
        layout.addWidget(config_group)
        
        # 对话显示
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("对话内容将显示在这里...")
        self.chat_display.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.chat_display, 3)
        
        # 输入区域
        input_layout = QVBoxLayout()
        
        self.user_input = QTextEdit()
        self.user_input.setPlaceholderText("输入您的问题...")
        self.user_input.setMaximumHeight(100)
        self.user_input.setStyleSheet("font-size: 20px;")
        self.user_input.installEventFilter(self)  # 安装事件过滤器，支持回车发送
        input_layout.addWidget(self.user_input)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        send_btn = QPushButton("🚀 发送")
        send_btn.setObjectName("primary")
        send_btn.clicked.connect(self.send_message)
        btn_layout.addWidget(send_btn)
        
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self.clear_chat)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        input_layout.addLayout(btn_layout)
        
        layout.addLayout(input_layout)
        
        return widget
    
    # ==================== 右键菜单 ====================
    def show_context_menu(self, position):
        """显示右键菜单"""
        # 确保右键点击的行被选中
        item = self.table.itemAt(position)
        if item:
            self.table.setCurrentCell(item.row(), item.column())
        
        # 检查是否选中了行
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #2a82da;
                color: white;
            }
        """)
        
        copy_name = QAction("📋 复制名称", self)
        copy_name.triggered.connect(self.copy_selected_name)
        menu.addAction(copy_name)
        
        copy_key = QAction("🔑 复制API密钥", self)
        copy_key.triggered.connect(self.copy_selected_api_key)
        menu.addAction(copy_key)
        
        copy_config = QAction("⚙️ 复制完整配置", self)
        copy_config.triggered.connect(self.copy_selected_full_config)
        menu.addAction(copy_config)
        
        copy_url = QAction("🔗 复制API URL", self)
        copy_url.triggered.connect(self.copy_selected_url)
        menu.addAction(copy_url)
        
        menu.addSeparator()
        
        rename = QAction("✏️ 修改名称", self)
        rename.triggered.connect(self.rename_key_dialog)
        menu.addAction(rename)
        
        menu.addSeparator()
        
        set_current = QAction("✅ 设为当前密钥", self)
        set_current.triggered.connect(self.set_current_key)
        menu.addAction(set_current)
        
        menu.addSeparator()
        
        edit = QAction("✏️ 编辑", self)
        edit.triggered.connect(self.edit_key_dialog)
        menu.addAction(edit)
        
        delete = QAction("🗑️ 删除", self)
        delete.triggered.connect(self.delete_selected_key)
        menu.addAction(delete)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))
    
    # ==================== 刷新表格 ====================
    def refresh_table(self):
        """刷新表格显示"""
        self.table.setRowCount(0)
        
        for key in self.manager.keys:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            name_item = QTableWidgetItem(key["name"])
            model_item = QTableWidgetItem(key.get("model_type", ""))
            
            last_tested = key.get("last_tested", "")
            if last_tested:
                try:
                    dt = datetime.fromisoformat(last_tested.replace('Z', '+00:00'))
                    last_tested = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            time_item = QTableWidgetItem(last_tested)
            
            is_valid = key.get("is_valid")
            response_time = key.get("response_time", 0)
            if is_valid is True:
                valid_item = QTableWidgetItem(f"✅ {response_time}ms")
                valid_item.setForeground(QBrush(QColor(0, 200, 0)))
            elif is_valid is False:
                valid_item = QTableWidgetItem("❌")
                valid_item.setForeground(QBrush(QColor(255, 80, 80)))
            else:
                valid_item = QTableWidgetItem("⏳")
            
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, model_item)
            self.table.setItem(row, 2, time_item)
            self.table.setItem(row, 3, valid_item)
        
        # 更新下拉列表
        key_names = [key["name"] for key in self.manager.keys]
        self.key_combo.clear()
        self.key_combo.addItems(key_names)
        
        # 排序
        self.sort_table(0)
    
    def sort_table(self, column):
        self.table.sortItems(column, Qt.AscendingOrder)
    
    def add_key_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("添加API密钥")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: white;
                font-size: 20px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #555;
                padding: 10px;
                border-radius: 3px;
                font-size: 20px;
            }
            QLineEdit:focus {
                border: 1px solid #2a82da;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        
        layout = QFormLayout(dialog)
        
        input_style = "font-size: 20px; background-color: #1e1e1e; color: white; border: 1px solid #555; padding: 10px; border-radius: 3px;"
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("例如: my-openai-key")
        name_input.setStyleSheet(input_style)
        layout.addRow("🏷️ 名称:", name_input)
        
        key_input = QLineEdit()
        key_input.setPlaceholderText("sk-...")
        key_input.setEchoMode(QLineEdit.Password)
        key_input.setStyleSheet(input_style)
        layout.addRow("🔑 API密钥:", key_input)
        
        base_input = QLineEdit()
        base_input.setPlaceholderText("https://api.openai.com/v1 (可选)")
        base_input.setStyleSheet(input_style)
        layout.addRow("🌐 API基础URL:", base_input)
        
        model_input = QLineEdit()
        model_input.setText("gpt-3.5-turbo")
        model_input.setStyleSheet(input_style)
        layout.addRow("🤖 模型类型:", model_input)
        
        provider_input = QLineEdit()
        provider_input.setText("OpenAI")
        provider_input.setStyleSheet(input_style)
        layout.addRow("🏢 提供商:", provider_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            api_key = key_input.text().strip()
            api_base = base_input.text().strip() or None
            model_type = model_input.text().strip()
            provider = provider_input.text().strip()
            
            if not name or not api_key:
                QMessageBox.warning(self, "错误", "名称和API密钥不能为空")
                return
            
            # 检查名称重复
            for key in self.manager.keys:
                if key["name"] == name:
                    QMessageBox.warning(self, "错误", f"名称 '{name}' 已存在")
                    return
            
            try:
                self.manager.add_key(name, api_key, api_base, provider, model_type)
                self.refresh_table()
                self.show_dark_message("information", "成功", f"API密钥 '{name}' 已添加")
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
    
    def edit_key_dialog(self, row=None, col=None):
        if row is None:
            current_row = self.table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "警告", "请先选择一行")
                return
            row = current_row
        
        name = self.table.item(row, 0).text()
        
        # 查找密钥数据
        key_data = None
        for key in self.manager.keys:
            if key["name"] == name:
                key_data = key
                break
        
        if not key_data:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑: {name}")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: white;
                font-size: 20px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #555;
                padding: 10px;
                border-radius: 3px;
                font-size: 20px;
            }
            QLineEdit:focus {
                border: 1px solid #2a82da;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        
        layout = QFormLayout(dialog)
        
        input_style = "font-size: 20px; background-color: #1e1e1e; color: white; border: 1px solid #555; padding: 10px; border-radius: 3px;"
        
        name_input = QLineEdit(key_data["name"])
        name_input.setStyleSheet(input_style)
        layout.addRow("🏷️ 名称:", name_input)
        
        key_input = QLineEdit(key_data["api_key"])
        key_input.setEchoMode(QLineEdit.Password)
        key_input.setStyleSheet(input_style)
        layout.addRow("🔑 API密钥:", key_input)
        
        base_input = QLineEdit(key_data.get("api_base", ""))
        base_input.setStyleSheet(input_style)
        layout.addRow("🌐 API基础URL:", base_input)
        
        model_input = QLineEdit(key_data.get("model_type", "gpt-3.5-turbo"))
        model_input.setStyleSheet(input_style)
        layout.addRow("🤖 模型类型:", model_input)
        
        provider_input = QLineEdit(key_data.get("provider", "OpenAI"))
        provider_input.setStyleSheet(input_style)
        layout.addRow("🏢 提供商:", provider_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            old_name = name  # 保存旧名称
            new_name = name_input.text().strip()
            api_key = key_input.text().strip()
            api_base = base_input.text().strip() or None
            model_type = model_input.text().strip()
            provider = provider_input.text().strip()
            
            if not new_name:
                QMessageBox.warning(self, "错误", "名称不能为空")
                return
            
            if not api_key:
                QMessageBox.warning(self, "错误", "API密钥不能为空")
                return
            
            # 检查新名称是否已存在（排除自己）
            if new_name != old_name:
                for key in self.manager.keys:
                    if key["name"] == new_name:
                        QMessageBox.warning(self, "错误", f"名称 '{new_name}' 已存在")
                        return
            
            self.manager.update_key(old_name, new_name, api_key, api_base, model_type, provider)
            self.refresh_table()
            self.key_combo.refresh()
            self.show_dark_message("information", "成功", f"API密钥 '{new_name}' 已更新")
    
    def delete_selected_key(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一行")
            return
        
        name = self.table.item(current_row, 0).text()
        
        reply = QMessageBox.question(self, "确认删除", f"确定要删除密钥 '{name}' 吗?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.manager.delete_key(name)
            self.refresh_table()
            self.show_dark_message("information", "成功", f"密钥 '{name}' 已删除")
    
    def copy_selected_name(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            name = self.table.item(current_row, 0).text()
            clipboard = QApplication.clipboard()
            clipboard.setText(name)
            self.statusBar().showMessage(f"已复制名称: {name}", 2000)
    
    def copy_selected_api_key(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            name = self.table.item(current_row, 0).text()
            for key in self.manager.keys:
                if key["name"] == name:
                    clipboard = QApplication.clipboard()
                    clipboard.setText(key["api_key"])
                    self.statusBar().showMessage(f"已复制API密钥: {name}", 2000)
                    break
    
    def copy_selected_full_config(self):
        """复制选中的配置（仅模型类型、密钥、URL）"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            name = self.table.item(current_row, 0).text()
            for key in self.manager.keys:
                if key["name"] == name:
                    # 只保留模型类型、密钥、URL
                    config = {
                        "model_type": key.get("model_type", ""),
                        "api_key": key.get("api_key", ""),
                        "api_base": key.get("api_base", "")
                    }
                    config_json = json.dumps(config, ensure_ascii=False, indent=2)
                    clipboard = QApplication.clipboard()
                    clipboard.setText(config_json)
                    self.statusBar().showMessage(f"已复制配置: {name}", 2000)
                    break
    
    def copy_selected_url(self):
        """复制选中的API URL"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            name = self.table.item(current_row, 0).text()
            for key in self.manager.keys:
                if key["name"] == name:
                    api_base = key.get("api_base", "")
                    clipboard = QApplication.clipboard()
                    clipboard.setText(api_base)
                    self.statusBar().showMessage(f"已复制API URL: {api_base}", 2000)
                    break
    
    def set_current_key(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一行")
            return
        
        name = self.table.item(current_row, 0).text()
        for key in self.manager.keys:
            if key["name"] == name:
                self.current_api_key = key
                self.key_combo.setCurrentText(name)
                self.statusBar().showMessage(f"已设置当前密钥: {name}", 2000)
                return
    
    def rename_key_dialog(self):
        """修改密钥名称"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一行")
            return
        
        old_name = self.table.item(current_row, 0).text()
        
        # 查找密钥数据
        key_data = None
        for key in self.manager.keys:
            if key["name"] == old_name:
                key_data = key
                break
        
        if not key_data:
            return
        
        # 创建修改名称对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("修改名称")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog { background-color: #2b2b2b; }
            QLabel { color: white; font-size: 14px; }
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #4a4a4a; }
        """)
        
        layout = QFormLayout(dialog)
        
        name_label = QLabel("新名称:")
        name_input = QLineEdit(old_name)
        name_input.setStyleSheet("font-size: 14px;")
        layout.addRow(name_label, name_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            new_name = name_input.text().strip()
            if not new_name:
                QMessageBox.warning(self, "错误", "名称不能为空")
                return
            
            if new_name == old_name:
                return
            
            # 检查新名称是否已存在
            for key in self.manager.keys:
                if key["name"] == new_name:
                    QMessageBox.warning(self, "错误", f"名称 '{new_name}' 已存在")
                    return
            
            # 更新密钥名称
            try:
                self.manager.update_key(old_name, new_name, key_data["api_key"], 
                                       key_data.get("api_base"), 
                                       key_data.get("model_type"),
                                       key_data.get("provider"))
                self.refresh_table()
                self.key_combo.refresh()
                self.show_dark_message("information", "成功", f"名称已修改为 '{new_name}'")
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
    
    def validate_all_keys(self):
        if not self.manager.keys:
            self.show_dark_message("information", "提示", "没有密钥需要验证")
            return
        
        self.statusBar().showMessage("正在验证密钥...")
        
        def validation_thread():
            for i, key in enumerate(self.manager.keys):
                is_valid, response_time = self.validate_key(key)
                key["is_valid"] = is_valid
                key["last_tested"] = datetime.now().isoformat()
                key["response_time"] = response_time if is_valid else 0
                
                # 通过信号更新UI
                self.validation_progress_signal.emit(i, is_valid, response_time)
            
            self.manager.save_keys()
            self.validation_complete_signal.emit()
        
        thread = threading.Thread(target=validation_thread, daemon=True)
        thread.start()
    
    def update_validation_progress(self, index, is_valid, response_time):
        """在主线程中更新验证进度"""
        if is_valid:
            self.table.item(index, 3).setText(f"✅ {response_time}ms")
            self.table.item(index, 3).setForeground(QBrush(QColor(0, 200, 0)))
        else:
            self.table.item(index, 3).setText("❌")
            self.table.item(index, 3).setForeground(QColor(255, 80, 80))
    
    def on_validation_complete(self):
        """验证完成时的回调"""
        self.statusBar().showMessage("验证完成", 3000)
    
    def validate_key(self, key):
        try:
            api_base = key.get("api_base", "https://api.openai.com/v1")
            api_key = key["api_key"]
            
            headers = {"Authorization": f"Bearer {api_key}"}
            start_time = time.time()
            response = requests.get(f"{api_base}/models", headers=headers, timeout=10)
            response_time = int((time.time() - start_time) * 1000)
            return response.status_code == 200, response_time
        except:
            return False, 0
    
    def send_message(self):
        if not self.current_api_key:
            # 尝试从下拉框获取
            current_text = self.key_combo.currentText()
            if current_text:
                for key in self.manager.keys:
                    if key["name"] == current_text:
                        self.current_api_key = key
                        break
        
        if not self.current_api_key:
            QMessageBox.warning(self, "警告", "请先选择一个API密钥")
            return
        
        user_text = self.user_input.toPlainText().strip()
        if not user_text:
            QMessageBox.warning(self, "警告", "请输入要发送的消息")
            return
        
        self.chat_display.append(f"<b style='color: #2a82da'>你:</b> {user_text}")
        self.user_input.clear()
        self.chat_display.append("<b style='color: #888'>助手:</b> ")
        
        # 滚动到底部
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
        
        self.statusBar().showMessage("正在发送请求...")
        
        def api_thread():
            try:
                api_base = self.current_api_key.get("api_base", "https://api.openai.com/v1")
                api_key = self.current_api_key["api_key"]
                model = self.current_api_key.get("model_type", "gpt-3.5-turbo")
                temperature = self.temp_slider.value() / 10
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                messages = [{"role": "user", "content": user_text}]
                
                data = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature
                }
                
                response = requests.post(
                    f"{api_base}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    assistant_text = result["choices"][0]["message"]["content"]
                    
                    # 更新UI
                    cursor = self.chat_display.textCursor()
                    cursor.movePosition(cursor.End)
                    cursor.insertHtml(f"<b style='color: #50fa7b'>助手:</b> {assistant_text.replace(chr(10), '<br>')}")
                    self.chat_display.append("")
                else:
                    error_text = f"错误: {response.status_code} - {response.text}"
                    cursor = self.chat_display.textCursor()
                    cursor.movePosition(cursor.End)
                    cursor.insertHtml(f"<b style='color: #ff5555'>助手:</b> {error_text}")
                    self.chat_display.append("")
                
                self.statusBar().showMessage("就绪")
                
            except Exception as e:
                cursor = self.chat_display.textCursor()
                cursor.movePosition(cursor.End)
                cursor.insertHtml(f"<b style='color: #ff5555'>助手:</b> 错误: {str(e)}")
                self.chat_display.append("")
                self.statusBar().showMessage("错误", 3000)
        
        thread = threading.Thread(target=api_thread, daemon=True)
        thread.start()
    
    def clear_chat(self):
        self.chat_display.clear()
    
    def show_about(self):
        QMessageBox.about(self, "关于", 
                         "<h3>大模型API密钥管理器</h3>"
                         "<p>支持多平台API密钥管理与对话测试</p>"
                         "<p>版本: 2.0 (PyQt5)</p>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("微软雅黑", 14))
    window = APIKeyManagerApp()
    window.show()
    sys.exit(app.exec_())