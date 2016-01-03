#coding:utf-8
import re
import platform

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QApplication, QMessageBox, QFileDialog, QWidget, QDialog,
    QLabel, QLineEdit, QTextEdit, QRadioButton, QToolButton, QPushButton, QTextBrowser,
	QButtonGroup, QFrame, QListWidget, QListWidgetItem, QTabWidget,
    QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem)

from PyQt5.QtCore import *
from threading import Thread
from Queue import Queue
from time import sleep
from datetime import datetime
from client import TcpClient


class UserDataBox(QWidget):
    def __init__(self):
        QDialog.__init__(self)

        userDataJson = [
            ["user1", u"用户1", "127.0.0.1", "54321"],
            # ["user233333", u"红红火火", "127.0.0.1", "54321"],
            # ["user233333", u"红红火火", "127.0.0.1", "54321"],
            # ["user233333", u"红红火火", "127.0.0.1", "54321"],
            # ["user233333", u"红红火火", "127.0.0.1", "54321"],
            # ["user233333", u"红红火火", "127.0.0.1", "54321"],
        ]

        userNum = len(userDataJson)

        self.resize(450, 60+43*userNum)
        self.setWindowTitle(u'在线用户列表')

        self.MyTable = QTableWidget(userNum, 4)
        self.MyTable.setHorizontalHeaderLabels(['用户名','昵称','IP','开放端口'])

        for index,userData in enumerate(userDataJson):
            newItem = QTableWidgetItem(userData[0])
            newItem.setTextAlignment(Qt.AlignHCenter |  Qt.AlignVCenter)
            self.MyTable.setItem(index, 0, newItem)

            newItem = QTableWidgetItem(userData[1])
            newItem.setTextAlignment(Qt.AlignHCenter |  Qt.AlignVCenter)
            self.MyTable.setItem(index, 1, newItem)

            newItem = QTableWidgetItem(userData[2])
            newItem.setTextAlignment(Qt.AlignHCenter |  Qt.AlignVCenter)
            self.MyTable.setItem(index, 2, newItem)

            newItem = QTableWidgetItem(userData[3])
            newItem.setTextAlignment(Qt.AlignHCenter |  Qt.AlignVCenter)
            self.MyTable.setItem(index, 3, newItem)

        self.MyTable.resizeColumnsToContents()   # 将列调整到跟内容大小相匹配
        self.MyTable.resizeRowsToContents()      # 将行大小调整到跟内容的大小相匹配

        layout = QHBoxLayout()
        layout.addWidget(self.MyTable)
        self.setLayout(layout)


class MainWindow(QWidget):
    # 声明信号 不能放init中
    add_format_text_to_group_chat_signal = pyqtSignal(dict)


    def closeEvent(self, QCloseEvent):
        print u"程序退出"
        self.__thread_killer = True
        self.client.finish()
        print "关闭client"
        self.recv_client.finish()
        print "关闭recv_client"



    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
#        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("MINET")
        self.resize(500, 300)

        # 创建窗口部件
        self.widget_frame = QLabel()

        # 窗口标题
        self.title_fram = QLabel()
        self.title = QLabel('MINET')
        self.title.setAlignment(Qt.AlignCenter)
        self.title_fram.setFixedHeight(100)

        # 登录部分

        self.login_btn_fram = QLabel()
        self.login_input_fram = QLabel()
        self.username_lab = QLabel("用户名：")
        self.password_lab = QLabel("密码：")
        self.nickname_lab = QLabel("昵称：")
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.nickname_edit = QLineEdit()
        self.type_select_login = QRadioButton('登录')
        self.type_select_register = QRadioButton('注册')
        self.login_btn = QPushButton('登录')
        self.register_btn = QPushButton('注册')
        self.login_btn.setFixedWidth(100)
        self.register_btn.setFixedWidth(100)

        # 显示详细聊天部分
        self.tabView = QTabWidget()
        self.group_chat = QTextBrowser()
        self.P2P_chat = QTextBrowser()
        self.tabView.addTab(self.group_chat, '群聊')
        self.tabView.addTab(self.P2P_chat, 'P2P聊天')

        self.chat_msg_edit = QTextEdit()
        self.send_msg_btn = QPushButton('发送')
        self.chat_msg_edit.setMaximumHeight(80)
        self.chat_msg_edit.setPlaceholderText("有什么想说的？")


        # 布局
        # 标题部分
        self.__layout_title = QHBoxLayout()
        self.__layout_title.addWidget(self.title)
        self.title_fram.setLayout(self.__layout_title)

        # 登录部分
        self.login_input_layout = QGridLayout()
        self.login_input_layout.addWidget(self.username_lab, 0, 0, 1, 1)
        self.login_input_layout.addWidget(self.password_lab, 1, 0, 1, 1)
        self.login_input_layout.addWidget(self.nickname_lab, 2, 0, 1, 1)
        self.login_input_layout.addWidget(self.username_edit, 0, 1, 1, 3);
        self.login_input_layout.addWidget(self.password_edit, 1, 1, 1, 3);
        self.login_input_layout.addWidget(self.nickname_edit, 2, 1, 1, 3);
        self.login_input_layout.addWidget(self.type_select_login, 3, 1, 1, 2);
        self.login_input_layout.addWidget(self.type_select_register, 3, 2, 1, 2);
        self.login_input_layout.setContentsMargins(0, 0, 0, 0)

        self.login_btn_layout = QHBoxLayout()
        self.login_btn_layout.addWidget(self.login_btn)
        self.login_btn_layout.addWidget(self.register_btn)
        self.login_btn_layout.setContentsMargins(0, 0, 0, 0)

        self.login_input_fram.setFixedHeight(100)
        self.login_input_fram.setLayout(self.login_input_layout)
        self.login_btn_fram.setLayout(self.login_btn_layout)


        # 登录部分widget
        self.login_layout = QVBoxLayout()
        self.login_layout.addWidget(self.login_input_fram)
        self.login_layout.addWidget(self.login_btn_fram)

        self.login_widget = QLabel()
        self.login_widget.setLayout(self.login_layout)

        # 聊天部分widget
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addWidget(self.tabView)
        self.chat_layout.addWidget(self.chat_msg_edit)
        self.chat_layout.addWidget(self.send_msg_btn)

        self.chat_widget = QLabel()
        self.chat_widget.setLayout(self.chat_layout)

        # 顶部层
        self.top_layout = QVBoxLayout()
        self.top_layout.addWidget(self.title_fram)
        self.top_layout.addWidget(self.login_widget)
        self.top_layout.addWidget(self.chat_widget)
        self.top_layout.setSpacing(10)

        self.widget_frame.setLayout(self.top_layout)

        self.layout_fram = QGridLayout()
        self.layout_fram.addWidget(self.widget_frame, 0, 0, 1, 1)
        self.layout_fram.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_fram)

        # set object name
        self.widget_frame.setObjectName('frame')
        self.title.setObjectName('title')
        self.tabView.setObjectName('tabView')
        self.group_chat.setObjectName('group_chat')
        self.P2P_chat.setObjectName('P2P_chat')
        self.chat_msg_edit.setObjectName('chat_msg_edit')
        self.username_lab.setObjectName('username_lab')
        self.password_lab.setObjectName('password_lab')
        self.nickname_lab.setObjectName('nickname_lab')

        self.setStyleSheet(
            '#username_lab, #password_lab, #nickname_lab{'
                'color: white;'
            '}'
            '#frame{'
                'border-image: url(Images/bg);'
            '}'
            '#title{'
                'color: white;'
                'font-size: 20pt;'
            '}'
            '#open_tool{'
                'color: black;'
            '}'
            '#mode_fram{'
                # 'border-top: 1px solid rgba(20, 20, 20, 100);'
                # 'border-bottom: 1px solid rgba(20, 20, 20, 100);'
                'background: rgba(200, 200, 200, 40);'
            '}'
            '#ln_open_tool, #ln_path{'
                'border-top-left-radius:    2px;'
                'border-bottom-left-radius: 2px;'
            '}'
            '#ln_pattern{'
                'border-radius: 2px;'
            '}'
            '#state{'
                'background: rgba(200, 200, 200, 40);'
                'border-radius: 2px;'
                'padding: 1px;'
                'color: rgb(240, 240, 240);'
            '}'
            'QTabBar::tab {'
                'border: 0;'
                'width:  100px;'
                'height: 20px;'
                'margin: 0 2px 0 0;'        # top right bottom left
                # 'border-top-left-radius: 5px;'
                # 'border-top-right-radius: 5px;'
                'color: rgb(200, 255, 255;);'
            '}'
            'QTabBar::tab:selected{'
                'background: rgba(25, 255, 255, 40);'
                'border-left: 1px solid rgba(255, 255, 255, 200);'
                'border-top: 1px solid rgba(255, 255, 255, 200);'
                'border-right: 1px solid rgba(255, 255, 255, 200);'
            '}'
            'QTabWidget:pane {'
                'border: 1px solid rgba(255, 255, 255, 200);'
                'background: rgba(0, 0, 0, 80);'
            '}'
            '#group_chat, #P2P_chat{'
                'background: rgba(0, 0, 0, 0);'
                'color: white;'
                'border: 0;'
            '}'
            '#chat_msg_edit{'
                'background: rgba(0, 0, 0, 40);'
                'border: 1px solid rgba(220, 220, 220, 200);'
                'color: white;'
                'height: 10px;'
            '}'
            'QRadioButton{'
                'background: rgba(0, 0, 0, 0);'
                'color: white;'
            '}'
            'QLineEdit{'
                'background: rgba(0, 0, 0, 40);'
                'border: 1px solid rgba(220, 220, 220, 200);'
                'color: white;'
                'height: 20px;'
            '}'
            'QPushButton{'
                'background: rgba(0, 0, 0, 100);'
                'border-radius: 15px;'
                'height: 25px;'
                'color: white;'
            '}'
            'QPushButton::hover{'
                'background: rgba(0, 0, 0, 150);'
            '}'
            'QToolButton{'
                'background: rgba(100, 100, 100, 100);'
                'color: white;'
                'border-top-right-radius:    2px;'
                'border-bottom-right-radius: 2px;'
            '}'
            'QToolButton::hover{'
                'background: rgba(0, 0, 0, 150);'
            '}'
            )

        self.login_btn.setShortcut(Qt.Key_Return)

        # 关联 信号/槽
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        self.send_msg_btn.clicked.connect(self.send_msg)
        self.chat_msg_edit.textChanged.connect(self.detect_return)
        self.type_select_register.toggled.connect(self.toggle_register)
        self.type_select_login.toggled.connect(self.toggle_login)

        # 绑定信号
        self.add_format_text_to_group_chat_signal.connect(self.add_format_text_to_group_chat)

        # 线程间共享数据队列
        queue_size = 10000
        self.__queue_result = Queue(queue_size)
        self.__queue_error = Queue(queue_size)

        # 强制结束子线程
        self.__thread_killer = False

        self.chat_widget.hide()
        self.type_select_login.click()
        # self.chat_layout_widgets = [self.tabView, self.chat_msg_edit, self.send_msg_btn]
        # self.login_layout_widgets = [self.login_btn_fram, self.login_input_fram]

        self.client = TcpClient(self)
        self.recv_client = TcpClient(self, is_recv_boardcast=True)
        #self.start_recv_msg()


        # 显示新窗口
        self.tableViewWindow = UserDataBox()
        self.tableViewWindow.show()

    # 检测回车，检测到就发送
    def detect_return(self):
        content = self.chat_msg_edit.toPlainText()
        # print "%r" % content
        if content.endswith('\n'):
            self.send_msg_btn.click()


    #　切换到注册页
    def toggle_register(self):
        self.login_btn.hide()
        self.register_btn.show()
        self.nickname_lab.show()
        self.nickname_edit.show()


    #　切换到登录页
    def toggle_login(self):
        self.login_btn.show()
        self.register_btn.hide()
        self.nickname_lab.hide()
        self.nickname_edit.hide()


    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        print "username:"+username
        print "password:"+password
        try:
            assert self.client.login(username, password)
            assert self.recv_client.login(username, password)
            QMessageBox.information(
                self,
                "提示",
                "登录成功！",
                QMessageBox.Yes)
            if self.chat_widget.isHidden():
                self.login_widget.hide()
                self.chat_widget.show()
                self.resize(1000, 800)
            else:
                self.chat_widget.hide()
                self.resize(500, 300)
            self.start_recv_msg()
        except Exception, e:
            print e
            QMessageBox.warning(
                self,
                "提示",
                "登录失败！",
                QMessageBox.Yes)


    def register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        nickname = self.nickname_edit.text()
        print "username:"+username
        print "password:"+password
        print "nickname:"+nickname
        try:
            assert self.client.register(username, password, nickname)
            QMessageBox.information(
                self,
                "提示",
                "注册完成！",
                QMessageBox.Yes)
            # 转到登录页
            self.type_select_login.click()
        except Exception, e:
            print e
            QMessageBox.warning(
                self,
                "提示",
                "注册失败！",
                QMessageBox.Yes)


    def add_format_text_to_group_chat(self, jdata):
        time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        text = jdata.get("content", "")
        nickname = jdata.get("nickname", "")
        msg = "%s %s\n%s\n" % (nickname, time, text)
        self.group_chat.setText("%s%s"%(self.group_chat.toPlainText(), msg))
        self.group_chat.moveCursor(self.group_chat.textCursor().End)


    def add_format_text_to_P2P_chat(self, jdata):
        time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        text = jdata.get("content", "")
        nickname = jdata.get("nickname", "")
        msg = "%s %s\n%s\n" % (nickname, time, text)
        self.P2P_chat.setText("%s%s"%(self.group_chat.toPlainText(), msg))
        self.P2P_chat.moveCursor(self.P2P_chat.textCursor().End)


    def send_msg(self):
        currentWidgetName = self.tabView.currentWidget().objectName()
        raw_content = self.chat_msg_edit.toPlainText()
        # 内容后面统一换行
        if not raw_content.endswith('\n'):
            raw_content += '\n'
        content = raw_content.replace('\n', '\\n')
        self.chat_msg_edit.clear()

        if currentWidgetName == 'group_chat':
            try:
                assert self.client.broadcast(content)
                jdata = {"content": raw_content, "nickname": u"自己"}
                self.add_format_text_to_group_chat(jdata)
            except Exception, e:
                print "send_msg:", e
                QMessageBox.warning(
                    self,
                    "提示",
                    "发送失败！",
                    QMessageBox.Yes)
        else:
            jdata = {"content": raw_content, "nickname": u"自己"}
            self.add_format_text_to_P2P_chat(jdata)


    def start_recv_msg(self):
        def start():
            while True:
                if self.__thread_killer:
                    print "停止接收信息"
                    return True
                jdata = self.recv_client.receive_one_msg()
                if jdata.keys() == ['content', 'nickname', 'user', 'time']:
                    #self.add_format_text_to_group_chat(jdata['content'])
                    self.add_format_text_to_group_chat_signal.emit(jdata)
                    print jdata['nickname'], "发来消息：", jdata['content']
        self.recv_msg_thread = Thread(target=start)
        self.recv_msg_thread.start()
        return True


# 程序入口
if __name__ == '__main__':
    import sys
    translator = QTranslator()
    translator.load('/home/bill/Qt5.5.1/5.5/gcc_64/translations/qt_zh_CN.qm')
    app = QApplication(sys.argv)
    app.installTranslator(translator)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
