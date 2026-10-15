import sys
import win32gui
import win32process
import psutil
import re
import ctypes
import os
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QTextEdit, QComboBox, 
                           QLabel, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新运行程序"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

class WorkerSignals(QObject):
    """定义信号类，用于线程间通信"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(str)

class WindowDetector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统窗口检测器")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # 创建检测方法选择下拉框
        method_layout = QHBoxLayout()
        method_label = QLabel("选择检测方法:")
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Win32多维度检测",
            "调试端口直连",
            "NDIS网络驱动方案",
            "内存特征扫描"
        ])
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        layout.addLayout(method_layout)
        
        # 创建开始检测按钮
        self.detect_button = QPushButton("开始检测")
        self.detect_button.clicked.connect(self.start_detection)
        layout.addWidget(self.detect_button)
        
        # 创建结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        # 显示当前权限状态
        self.status_label = QLabel()
        self.update_status_label()
        layout.addWidget(self.status_label)
        
        # 创建进度标签
        self.progress_label = QLabel("就绪")
        layout.addWidget(self.progress_label)
        
        # 初始化信号
        self.signals = WorkerSignals()
        self.signals.result.connect(self.update_result)
        self.signals.error.connect(self.show_error)
        self.signals.finished.connect(self.detection_finished)
        
    def update_status_label(self):
        """更新状态标签显示当前权限状态"""
        if is_admin():
            self.status_label.setText("当前状态：已获取管理员权限")
            self.status_label.setStyleSheet("color: green")
        else:
            self.status_label.setText("当前状态：未获取管理员权限，部分功能可能受限")
            self.status_label.setStyleSheet("color: red")
            
    def start_detection(self):
        """根据选择的检测方法执行相应的检测"""
        method = self.method_combo.currentText()
        self.result_text.clear()
        self.detect_button.setEnabled(False)
        self.progress_label.setText("正在检测...")
        
        # 检查是否需要管理员权限
        if method in ["Win32多维度检测", "NDIS网络驱动方案", "内存特征扫描"] and not is_admin():
            reply = QMessageBox.question(self, "权限提示", 
                                       "此检测方法需要管理员权限，是否以管理员身份重新启动程序？",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                run_as_admin()
                return
        
        # 在新线程中执行检测
        thread = threading.Thread(target=self.run_detection, args=(method,))
        thread.daemon = True
        thread.start()
        
    def run_detection(self, method):
        """在新线程中执行检测"""
        try:
            if method == "Win32多维度检测":
                self.win32_detection()
            elif method == "调试端口直连":
                self.debug_port_detection()
            elif method == "NDIS网络驱动方案":
                self.ndis_detection()
            elif method == "内存特征扫描":
                self.memory_detection()
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()
            
    def update_result(self, text):
        """更新结果显示"""
        self.result_text.append(text)
        
    def show_error(self, error_msg):
        """显示错误信息"""
        QMessageBox.critical(self, "错误", error_msg)
        
    def detection_finished(self):
        """检测完成后的处理"""
        self.detect_button.setEnabled(True)
        self.progress_label.setText("检测完成")
            
    def win32_detection(self):
        """实现Win32多维度检测方法"""
        try:
            windows = self.get_all_windows()
            self.signals.result.emit("=== Win32多维度检测结果 ===\n")
            for win in windows:
                if self.is_axbrowser_window(win):
                    self.signals.result.emit(f"检测到战斧浏览器窗口：\n{win}\n")
        except Exception as e:
            raise Exception(f"Win32检测失败：{str(e)}")
            
    def debug_port_detection(self):
        """实现调试端口直连检测方法"""
        try:
            self.signals.result.emit("=== 调试端口检测结果 ===\n")
            self.signals.result.emit("正在尝试连接调试端口...\n")
            
            # 检查Chrome是否在运行
            chrome_running = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in ['chrome.exe', 'msedge.exe']:
                    chrome_running = True
                    break
                    
            if not chrome_running:
                self.signals.result.emit("未检测到Chrome浏览器运行，请先启动浏览器并启用调试模式\n")
                return
                
            # 尝试连接调试端口
            try:
                from selenium.webdriver.chrome.options import Options
                from selenium import webdriver
                
                options = Options()
                options.debugger_address = "127.0.0.1:9222"
                
                driver = webdriver.Chrome(options=options)
                tabs = []
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    tabs.append({
                        "title": driver.title,
                        "url": driver.current_url,
                        "handle_id": handle
                    })
                driver.quit()
                
                for tab in tabs:
                    self.signals.result.emit(f"标签页：{tab}\n")
            except Exception as e:
                self.signals.result.emit(f"连接调试端口失败：{str(e)}\n")
                self.signals.result.emit("请确保浏览器已启用调试模式：\n")
                self.signals.result.emit("1. 关闭所有Chrome浏览器窗口\n")
                self.signals.result.emit("2. 使用以下命令启动浏览器：\n")
                self.signals.result.emit("   chrome.exe --remote-debugging-port=9222\n")
        except Exception as e:
            raise Exception(f"调试端口检测失败：{str(e)}")
            
    def ndis_detection(self):
        """实现NDIS网络驱动检测方法"""
        try:
            self.signals.result.emit("=== NDIS网络驱动检测结果 ===\n")
            self.signals.result.emit("此功能需要安装NDIS驱动，当前未实现\n")
            self.signals.result.emit("如需使用此功能，请联系开发者获取驱动安装包\n")
        except Exception as e:
            raise Exception(f"NDIS检测失败：{str(e)}")
            
    def memory_detection(self):
        """实现内存特征扫描检测方法"""
        try:
            self.signals.result.emit("=== 内存特征扫描结果 ===\n")
            self.signals.result.emit("此功能需要额外配置，当前未实现\n")
            self.signals.result.emit("如需使用此功能，请联系开发者获取配置说明\n")
        except Exception as e:
            raise Exception(f"内存扫描失败：{str(e)}")
            
    def get_all_windows(self):
        """获取所有窗口的三维特征"""
        windows = []
        
        def callback(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = psutil.Process(pid)
                    window_info = {
                        "hwnd": hwnd,
                        "title": win32gui.GetWindowText(hwnd),
                        "class": win32gui.GetClassName(hwnd),
                        "exe_path": proc.exe(),
                        "process_name": proc.name(),
                        "cmdline": " ".join(proc.cmdline())
                    }
                    windows.append(window_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return True
        
        win32gui.EnumWindows(callback, None)
        return windows
        
    def is_axbrowser_window(self, window_info):
        """通过多维度特征矩阵验证窗口身份"""
        AXBROWSER_FINGERPRINT = {
            "process_patterns": [
                r".*\\战斧浏览器\\application\\axbrowser\.exe$",
                r"^(axbrowser|axbrowser|axbrowser_turbo)\.exe$"
            ],
            "window_class": [
                "Chrome_WidgetWin_1",
                "AxBrowser_WindowClass"
            ]
        }
        
        # 检查进程路径
        path_match = any(
            re.search(pattern, window_info["exe_path"], re.I)
            for pattern in AXBROWSER_FINGERPRINT["process_patterns"]
        )
        
        # 检查窗口类
        class_match = any(
            cls == window_info["class"]
            for cls in AXBROWSER_FINGERPRINT["window_class"]
        )
        
        return path_match or class_match

if __name__ == "__main__":
    # 检查并请求管理员权限
    if not is_admin():
        run_as_admin()
        sys.exit()
        
    app = QApplication(sys.argv)
    window = WindowDetector()
    window.show()
    sys.exit(app.exec_()) 