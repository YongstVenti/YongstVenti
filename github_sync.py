import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
from datetime import datetime
import ctypes
import sys


class GitSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Sync Tool")
        self.root.geometry("500x400")
        self.root.resizable(True, True)

        # 窗口置顶
        self.root.attributes('-topmost', True)

        # Git 路径
        self.git_path = "git"

        # 颜色主题
        self.bg_color = "#1e1e2e"
        self.fg_color = "#cdd6f4"
        self.accent_color = "#89b4fa"
        self.success_color = "#a6e3a1"
        self.warning_color = "#f9e2af"
        self.error_color = "#f38ba8"
        self.terminal_bg = "#181825"
        self.terminal_fg = "#a6adc8"

        self.setup_ui()
        self.log("程序已启动...")
        self.log("点击「检查状态」获取仓库状态")

    def setup_ui(self):
        # 整体背景
        self.root.configure(bg=self.bg_color)

        # 标题栏区域
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(fill="x", pady=(15, 10))

        title_label = tk.Label(title_frame, text="GitHub Sync Tool", font=("Segoe UI", 18, "bold"),
                               bg=self.bg_color, fg=self.accent_color)
        title_label.pack(side="left", padx=20)

        # 状态指示灯
        self.status_dot = tk.Label(title_frame, text="●", font=("Segoe UI", 14),
                                   bg=self.bg_color, fg=self.warning_color)
        self.status_dot.pack(side="right", padx=20)
        self.status_text = tk.Label(title_frame, text="未同步", font=("Segoe UI", 10),
                                     bg=self.bg_color, fg=self.fg_color)
        self.status_text.pack(side="right", padx=5)

        # 分隔线
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=20)

        # 仓库路径
        path_frame = tk.Frame(self.root, bg=self.bg_color)
        path_frame.pack(fill="x", padx=20, pady=15)

        ttk.Label(path_frame, text="📁 仓库路径:", font=("Segoe UI", 10),
                  background=self.bg_color, foreground=self.fg_color).pack(side="left")

        self.path_entry = tk.Entry(path_frame, font=("Segoe UI", 10), width=35,
                                    bg=self.terminal_bg, fg=self.fg_color,
                                    insertbackground=self.accent_color, relief="flat")
        self.path_entry.insert(0, "D:/heart-abyss")
        self.path_entry.pack(side="left", padx=10, ipady=2)

        browse_btn = tk.Button(path_frame, text="浏览", font=("Segoe UI", 9),
                               bg=self.accent_color, fg=self.bg_color,
                               relief="flat", cursor="hand2", command=self.browse_folder)
        browse_btn.pack(side="left")

        # 按钮区
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=10)

        buttons = [
            ("检查状态", self.check_status, "#89b4fa"),
            ("拉取 ↓", self.pull_changes, "#f9e2af"),
            ("推送 ↑", self.push_changes, "#a6e3a1"),
        ]

        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 10, "bold"),
                            bg=color, fg=self.bg_color, relief="flat",
                            cursor="hand2", command=cmd, width=10, height=2)
            btn.pack(side="left", padx=5)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=c, fg=self.bg_color))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c, fg=self.bg_color))

        # 新增：一键同步按钮
        sync_frame = tk.Frame(self.root, bg=self.bg_color)
        sync_frame.pack(pady=5)

        sync_btn = tk.Button(sync_frame, text="🔄 一键拉取并更新", font=("Segoe UI", 11, "bold"),
                             bg="#cba6f7", fg=self.bg_color, relief="flat",
                             cursor="hand2", command=self.sync_all, width=20, height=2)
        sync_btn.pack()

        # 终端显示区
        terminal_frame = tk.Frame(self.root, bg=self.terminal_bg)
        terminal_frame.pack(fill="both", expand=True, padx=20, pady=(10, 15))

        terminal_label = tk.Label(terminal_frame, text="终端输出", font=("Segoe UI", 9),
                                   bg=self.terminal_bg, fg=self.terminal_fg, anchor="w")
        terminal_label.pack(fill="x", padx=10, pady=(8, 5))

        self.terminal = scrolledtext.ScrolledText(terminal_frame, font=("Consolas", 10),
                                                   bg=self.terminal_bg, fg=self.terminal_fg,
                                                   insertbackground=self.accent_color,
                                                   relief="flat", state="disabled",
                                                   wrap="word")
        self.terminal.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 设置终端文本标签
        self.terminal.tag_config("info", foreground=self.fg_color)
        self.terminal.tag_config("success", foreground=self.success_color)
        self.terminal.tag_config("warning", foreground=self.warning_color)
        self.terminal.tag_config("error", foreground=self.error_color)
        self.terminal.tag_config("time", foreground=self.terminal_fg)

    def browse_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def log(self, msg, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.terminal.configure(state="normal")
        self.terminal.insert("end", f"[{timestamp}] ", "time")
        self.terminal.insert("end", f"{msg}\n", level)
        self.terminal.see("end")
        self.terminal.configure(state="disabled")

    def run_git(self, args, cwd=None):
        if cwd is None:
            cwd = self.path_entry.get()
        cmd = [self.git_path] + args
        try:
            # Windows 下隐藏黑窗
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                                    timeout=60, startupinfo=startupinfo)
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "操作超时"
        except Exception as e:
            return -1, "", str(e)

    def check_status(self):
        def worker():
            self.log("正在检查仓库状态...")
            self.root.after(0, lambda: self.status_dot.config(fg=self.warning_color))
            self.root.after(0, lambda: self.status_text.config(text="检查中..."))

            # 获取 remote
            code, stdout, stderr = self.run_git(["remote", "-v"])
            if code != 0 or not stdout:
                self.log(f"未找到远程仓库: {stderr}", "error")
                self.root.after(0, lambda: self.status_text.config(text="无远程仓库"))
                return

            # fetch 远程
            self.run_git(["fetch"])

            # 获取状态
            code, stdout, stderr = self.run_git(["status", "-sb"])
            if code == 0:
                lines = stdout.split('\n')
                if lines:
                    branch_line = lines[0]
                    ahead = branch_line.count('ahead')
                    behind = branch_line.count('behind')

                    if ahead > 0 and behind > 0:
                        self.log(f"📤 本地有 {ahead} 个提交未推送 | 📥 云端有 {behind} 个更新未拉取", "warning")
                        self.root.after(0, lambda: self.status_dot.config(fg=self.warning_color))
                        self.root.after(0, lambda: self.status_text.config(text=f"待同步({ahead+behind})"))
                    elif ahead > 0:
                        self.log(f"📤 本地有 {ahead} 个提交未推送", "warning")
                        self.root.after(0, lambda: self.status_dot.config(fg=self.warning_color))
                        self.root.after(0, lambda: self.status_text.config(text=f"待推送({ahead})"))
                    elif behind > 0:
                        self.log(f"📥 云端有 {behind} 个更新未拉取", "warning")
                        self.root.after(0, lambda: self.status_dot.config(fg=self.warning_color))
                        self.root.after(0, lambda: self.status_text.config(text=f"待拉取({behind})"))
                    else:
                        self.log("✅ 已同步，无待处理更改", "success")
                        self.root.after(0, lambda: self.status_dot.config(fg=self.success_color))
                        self.root.after(0, lambda: self.status_text.config(text="已同步"))
            else:
                self.log(f"检查失败: {stderr}", "error")

        threading.Thread(target=worker, daemon=True).start()

    def push_changes(self):
        def worker():
            self.log("正在推送...", "info")
            code, stdout, stderr = self.run_git(["push"])
            if code == 0:
                self.log("✅ 推送成功!", "success")
            else:
                self.log(f"❌ 推送失败: {stderr}", "error")
            self.root.after(0, self.check_status)

        threading.Thread(target=worker, daemon=True).start()

    def pull_changes(self):
        def worker():
            self.log("正在拉取...", "info")
            code, stdout, stderr = self.run_git(["pull", "--rebase"])
            if code == 0:
                self.log("✅ 拉取成功!", "success")
            else:
                self.log(f"❌ 拉取失败: {stderr}", "error")
            self.root.after(0, self.check_status)

        threading.Thread(target=worker, daemon=True).start()

    def sync_all(self):
        """一键拉取并更新"""
        def worker():
            repo_path = self.path_entry.get()
            self.log("=" * 40, "info")
            self.log("🔄 开始一键同步...", "info")

            # 1. 先 fetch 获取远程最新状态
            self.log("📥 正在获取远程更新...", "info")
            code, stdout, stderr = self.run_git(["fetch", "--all"])
            if code != 0:
                self.log(f"⚠️ fetch 失败（可能无远程仓库）: {stderr}", "warning")

            # 2. 检查本地是否有未提交的修改
            code, status_stdout, stderr = self.run_git(["status", "--porcelain"])
            has_local_changes = bool(status_stdout.strip())

            if has_local_changes:
                # 3. 如果有未提交修改，先添加并提交
                self.log("📝 检测到本地有修改，正在提交...", "info")
                code, stdout, stderr = self.run_git(["add", "-A"])
                if code == 0:
                    # 自动生成提交信息
                    commit_msg = f"sync: 自动同步更新 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    code, stdout, stderr = self.run_git(["commit", "-m", commit_msg])
                    if code == 0:
                        self.log(f"✅ 提交成功: {commit_msg}", "success")
                    else:
                        self.log(f"⚠️ 提交失败: {stderr}", "warning")
                        self.root.after(0, self.check_status)
                        return

            # 4. 拉取远程更新（rebase 模式）
            self.log("📥 正在拉取远程更新...", "info")
            code, stdout, stderr = self.run_git(["pull", "--rebase", "--autostash"])
            if code == 0:
                self.log("✅ 拉取成功!", "success")
            else:
                # 如果 rebase 失败，尝试普通 pull
                self.log("⚠️ rebase 模式失败，尝试普通拉取...", "warning")
                code, stdout, stderr = self.run_git(["pull"])
                if code != 0:
                    self.log(f"❌ 拉取失败: {stderr}", "error")
                    self.root.after(0, self.check_status)
                    return

            # 5. 推送本地更新
            self.log("📤 正在推送本地更新...", "info")
            code, stdout, stderr = self.run_git(["push"])
            if code == 0:
                self.log("✅ 推送成功!", "success")
                self.log("🎉 同步完成! 请在 GitHub 网页刷新查看", "success")
            else:
                self.log(f"❌ 推送失败: {stderr}", "error")

            self.root.after(0, self.check_status)

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("GitHub Sync Tool")

    # Windows: 设置 App ID
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("github-sync-tool")
    except:
        pass

    app = GitSyncApp(root)
    root.mainloop()