# System Window Detector（Windows 系统窗口检测器）

A small Windows GUI utility for inspecting browser-window/process signatures and, when explicitly enabled, Chrome/Edge remote-debugging tabs.

本项目使用 Python + PyQt5 提供图形界面，当前主要用于识别指定的战斧浏览器（AxBrowser）窗口，并尝试连接本机 Chrome DevTools 调试端口查看标签页信息。

## 当前功能状态

| 检测入口 | 当前状态 | 说明 |
| --- | --- | --- |
| Win32 窗口检测 | 已实现 | 读取可见窗口的标题、窗口类、进程路径等信息，并按 AxBrowser 特征进行匹配 |
| 浏览器调试端口 | 已实现基础流程 | 尝试连接 `127.0.0.1:9222`，读取 Chrome/Edge 的标签页标题与 URL；需要浏览器已开启调试端口 |
| NDIS 网络驱动方案 | **未实现** | 当前界面仅显示需要额外驱动，不能视为可用检测功能 |
| 内存特征扫描 | **未实现** | 当前界面仅显示尚需配置，不能视为可用检测功能 |

## 环境要求

- Windows 10/11
- Python 环境
- 依赖项见 [requirements.txt](./requirements.txt)
- 部分窗口检查操作需要管理员权限
- 调试端口检测需要已启动并开放本地调试端口的 Chrome/Edge；仅连接你自己有权检查的浏览器实例

## 安装与运行

```powershell
git clone https://github.com/change979666/window-detector.git
cd window-detector
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python window_detector.py
```

如程序提示管理员权限，请确认运行环境和权限后再继续。不要在不受你管理的设备上启用调试端口或检查进程信息。

## 实现说明与限制

- Win32 检测依赖窗口标题、窗口类及进程路径等特征，浏览器版本或安装目录变化可能影响匹配结果。
- 调试端口模式依赖 Selenium 与相应浏览器驱动环境；如果连接失败，请先检查浏览器是否以调试参数启动。
- NDIS 与内存扫描选项目前只是预留入口，不会执行底层网络驱动拦截或真正的内存扫描。
- 仓库中的 [功能介绍.md](./功能介绍.md) 包含扩展技术思路；其中的示例/规划不能等同于已经交付的程序功能。

## License

MIT License. See [LICENSE](./LICENSE).
