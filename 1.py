import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
from openai import OpenAI

# 配置
default = """
我一下告诉你的内容你要转成md格式 不需要任何解释
"""
default = str(default)

client = OpenAI(
    api_key="sk-zX6J7qGloURSGzscRg7O3xIdQYhT8mQI1Z4adKxPfkmjAzMd",
    base_url="https://api.moonshot.cn/v1"
)

models_list = ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
moonshot = 2

messages = [
    {"role": "system", "content": default}
]

def clear_history():
    global messages
    messages = [
        {"role": "system", "content": default}
    ]

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("聊天应用")
        self.setGeometry(100, 100, 800, 600)

        # 创建主窗口的中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # 输入框
        self.input_text = QTextEdit(self)
        self.input_text.setPlaceholderText("请输入内容...")
        self.input_text.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.input_text)

        # 输出框
        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("输出内容将显示在这里...")
        self.output_text.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.output_text)

        # 按钮
        self.send_button = QPushButton("发送", self)
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.clear_button = QPushButton("清空历史", self)
        self.clear_button.clicked.connect(self.clear_history)
        self.layout.addWidget(self.clear_button)

        self.copy_button = QPushButton("复制输出", self)
        self.copy_button.clicked.connect(self.copy_output)
        self.layout.addWidget(self.copy_button)

        # 定时器，用于实时更新输出
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_output)

        self.streaming = False
        self.streaming_output = ""
        self.streaming_chunk_index = 0

    def send_message(self):
        content = self.input_text.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "警告", "请输入内容！")
            return

        self.input_text.clear()
        self.streaming = True
        self.streaming_chunk_index = 0
        self.streaming_output = ""

        try:
            global messages
            messages.append({"role": "user", "content": content})
            response = client.chat.completions.create(
                model=models_list[moonshot],
                messages=messages,
                temperature=0.1,
                stream=True  # 开启流式输出
            )

            # 将流式输出的内容存储到 self.streaming_output
            for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    self.streaming_output += delta.content
            self.timer.start(50)  # 每 50 毫秒更新一次输出
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生错误：{e}")
            self.streaming = False

    def update_output(self):
        if self.streaming:
            # 每次更新一部分内容
            chunk_size = 10  # 每次更新的字符数
            chunk = self.streaming_output[self.streaming_chunk_index:self.streaming_chunk_index + chunk_size]
            self.output_text.append(chunk)
            self.streaming_chunk_index += chunk_size

            # 如果所有内容都已更新完毕
            if self.streaming_chunk_index >= len(self.streaming_output):
                self.streaming = False
                self.timer.stop()
        else:
            self.timer.stop()

    def clear_history(self):
        clear_history()
        self.output_text.clear()
        QMessageBox.information(self, "提示", "对话历史已清空。")

    def copy_output(self):
        output = self.output_text.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(output)
        QMessageBox.information(self, "提示", "输出内容已复制到剪贴板。")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec())