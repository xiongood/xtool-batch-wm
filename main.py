import os
import sys
import traceback

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QFileDialog, QPushButton
from PIL import Image, ImageDraw, ImageFont
from Watermark import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow


class Constants:
    TRANSPARENCY = 128


class MyApp(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化界面

        # 连接按钮的点击信号到槽函数
        self.pushButton_in = QPushButton('选择输入文件夹', self)
        self.pushButton_in.resize(self.pushButton_in.sizeHint())
        self.pushButton_in.move(6, 6)
        self.pushButton_in.clicked.connect(self.openFolderDialogIn)

        # 连接按钮的点击信号到槽函数
        self.pushButton_out = QPushButton('选择输出文件夹', self)
        self.pushButton_out.resize(self.pushButton_out.sizeHint())
        self.pushButton_out.move(6, 36)
        self.pushButton_out.clicked.connect(self.openFolderDialogOut)
        # 修改透明度
        # 默认透明度50%
        self.horizontalSlider.setValue(50)
        self.horizontalSlider.valueChanged.connect(self.onSliderValueChanged)
        # 开始
        self.pushButtonStart.clicked.connect(self.do)

        # 设置文件夹路径只读
        self.lineEdit.setReadOnly(True)
        self.lineEdit_2.setReadOnly(True)
        self.textEdit.setReadOnly(True)

    # 打开输入文件夹
    @pyqtSlot()
    def openFolderDialogIn(self):
        # 显示文件夹选择对话框
        folder_selected = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_selected:
            # 在这里处理文件夹路径，比如显示在 lineEdit 中或进行其他操作
            self.lineEdit.setText(folder_selected)

    # 打开输出文件夹
    @pyqtSlot()
    def openFolderDialogOut(self):
        # 显示文件夹选择对话框
        folder_selected = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_selected:
            # 在这里处理文件夹路径，比如显示在 lineEdit 中或进行其他操作
            self.lineEdit_2.setText(folder_selected)

    # 修改透明度方法
    def onSliderValueChanged(self, value):
        # 每当滑块的值改变时，这个函数会被调用
        self.label_5.setText(str(value + 1) + "%")
        Constants.TRANSPARENCY = 255 * ((value + 1) / 100)
        Constants.TRANSPARENCY = int(Constants.TRANSPARENCY)

    def do(self):
        try:
            # 按钮置灰
            self.pushButtonStart.setEnabled(False)
            self.pushButton_out.setEnabled(False)
            self.pushButton_in.setEnabled(False)
            # 清空日志
            self.textEdit.clear()
            x = self.lineEditX.text()
            y = self.lineEditY.text()
            if len(x) == 0 or len(y) == 0:
                self.textEdit.append("水印位置不能为空！")
                return

            inputPath = self.lineEdit.text()
            if len(inputPath) == 0:
                self.textEdit.append("输入文件夹不能为空！")
                return

            outputPath = self.lineEdit_2.text()
            if len(outputPath) == 0:
                self.textEdit.append("输出文件夹不能为空！")
                return

            text = self.lineEditText.text()
            if len(text) == 0:
                self.textEdit.append("水印文字不能为空！")
                return

            color = self.comboBoxColor.currentText()
            fontSize = self.lineEditSize.text()

            # 开始处理图片
            self.textEdit.append("开始处理图片文件……")
            file_names = self.get_file_names(inputPath)
            if len(file_names) == 0:
                self.textEdit.append("文件夹为空！")
                return
            for file_name in file_names:
                # 判断文件类型
                suffixNames = file_name.split('.')
                suffixName = suffixNames[1]
                if suffixName == "jpg" or suffixName == "jpeg" or suffixName == "png":
                    self.textEdit.append("开始处理：" + file_name)
                else:
                    self.textEdit.append(file_name + "文件格式错误，已经跳过！")
                    continue

                # 开始添加水印
                # 打开图片
                image = Image.open(inputPath + "/" + file_name)
                # 获取图片的宽度和高度
                width, height = image.size

                # 创建一个新的Image对象，作为水印图层
                watermark = Image.new('RGBA', (width, height), (255, 255, 255, 0))

                # 在水印图层上绘制文本
                draw = ImageDraw.Draw(watermark)
                font = ImageFont.truetype("simkai.ttf", int(fontSize))  # 设置字体和大小

                text_position = (int(y),int(x))

                # 最后一个255 是透明度，如果写128就是50%的透明度
                # 设置颜色
                if color == "白色":
                    draw.text(text_position, text, font=font, fill=(255, 255, 255, Constants.TRANSPARENCY))
                elif color == "红色":
                    draw.text(text_position, text, font=font, fill=(255, 0, 0, Constants.TRANSPARENCY))
                elif color == "蓝色":
                    draw.text(text_position, text, font=font, fill=(0, 0, 255, Constants.TRANSPARENCY))
                elif color == "绿色":
                    draw.text(text_position, text, font=font, fill=(0, 255, 0, Constants.TRANSPARENCY))
                elif color == "黑色":
                    draw.text(text_position, text, font=font, fill=(0, 0, 0, Constants.TRANSPARENCY))
                elif color == "黄色":
                    draw.text(text_position, text, font=font, fill=(255, 255, 0, Constants.TRANSPARENCY))
                else:  # 默认白色
                    draw.text(text_position, text, font=font, fill=(255, 255, 255, Constants.TRANSPARENCY))

                # 将水印图层叠加到原始图片上
                watermarked_image = Image.alpha_composite(image.convert('RGBA'), watermark)

                # 将图片转换为RGB模式，再保存为JPEG格式
                watermarked_image = watermarked_image.convert("RGB")
                watermarked_image.save(outputPath + "/" + file_name)
                self.textEdit.append(file_name + "处理完成！")
        except Exception as e:
            # 当异常被捕获时执行的代码块
            error_message = f"发生了一个异常: {e}\n{traceback.format_exc()}"
            print(error_message)
            self.textEdit.append(error_message)
        finally:
            self.textEdit.append("全部处理成功！")
            # 按钮恢复
            self.pushButtonStart.setEnabled(True)
            self.pushButton_out.setEnabled(True)
            self.pushButton_in.setEnabled(True)

    # 打开输入文件夹
    def get_file_names(self, inputPath):
        return [f for f in os.listdir(inputPath) if os.path.isfile(os.path.join(inputPath, f))]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()  # 创建应用实例
    ex.show()  # 显示窗口
    sys.exit(app.exec_())  # 进入应用的主循环
