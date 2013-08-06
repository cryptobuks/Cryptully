from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QSplitter
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QWidget

import qtUtils

from utils import constants
from utils import utils


class QChatWidget(QWidget):
    def __init__(self, connectionManager, parent=None):
        QWidget.__init__(self, parent)

        self.connectionManager = connectionManager
        self.isDisabled = False

        self.chatLog = QTextEdit()
        self.chatLog.setReadOnly(True)

        self.chatInput = QTextEdit()
        self.chatInput.textChanged.connect(self.chatInputTextChanged)

        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.sendMessage)

        # Set the min height for the chatlog and a matching fixed height for the send button
        chatInputFontMetrics = QFontMetrics(self.chatInput.font())
        self.chatInput.setMinimumHeight(chatInputFontMetrics.lineSpacing() * 3)
        self.sendButton.setFixedHeight(chatInputFontMetrics.lineSpacing() * 3)

        hbox = QHBoxLayout()
        hbox.addWidget(self.chatInput)
        hbox.addWidget(self.sendButton)

        # Put the chatinput and send button in a wrapper widget so they may be added to the splitter
        chatInputWrapper = QWidget()
        chatInputWrapper.setLayout(hbox)
        chatInputWrapper.setMinimumHeight(chatInputFontMetrics.lineSpacing() * 3.7)

        # Put the chat log and chat input into a splitter so the user can resize them at will
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.chatLog)
        splitter.addWidget(chatInputWrapper)
        splitter.setSizes([int(parent.height()), 1])

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)


    def chatInputTextChanged(self):
        if str(self.chatInput.toPlainText())[-1:] == '\n':
            self.sendMessage()


    def sendMessage(self):
        if self.isDisabled:
            return

        text = str(self.chatInput.toPlainText())[:-1]

        # Don't send empty messages
        if text == '':
            return

        # Add the message to the message queue to be sent
        self.connectionManager.getClient(self.nick).sendChatMessage(text)

        # Clear the chat input
        self.chatInput.clear()

        self.appendMessage(text, constants.SENDER)


    def showNowChattingMessage(self, nick):
        self.nick = nick
        self.appendMessage("You are now securely chatting with " + self.nick + " :)",
                           constants.SERVICE, showTimestampAndNick=False)

        self.appendMessage("It's a good idea to verify the communcation is secure by selecting "
                           "\"verify key integrity\" in the options menu.", constants.SERVICE, showTimestampAndNick=False)


    def appendMessage(self, message, source, showTimestampAndNick=True):
        color = self.__getColor(source)

        if showTimestampAndNick:
            timestamp = '<font color="' + color + '">(' + utils.getTimestamp() + ') <strong>' + \
                        (self.connectionManager.nick if source == constants.SENDER else self.nick) + \
                        ':</strong></font> '
        else:
            timestamp = ''

        # If the user has scrolled up (current value != maximum), do not move the scrollbar
        # to the bottom after appending the message
        shouldScroll = True
        scrollbar = self.chatLog.verticalScrollBar()
        if scrollbar.value() != scrollbar.maximum() and source != constants.SENDER:
            shouldScroll = False

        self.chatLog.append(timestamp + message)

        # Move the vertical scrollbar to the bottom of the chat log
        if shouldScroll:
            scrollbar.setValue(scrollbar.maximum())


    def __getColor(self, source):
        if source == constants.SENDER:
            if qtUtils.isLightTheme:
                return '#0000CC'
            else:
                return '#6666FF'
        elif source == constants.RECEIVER:
            if qtUtils.isLightTheme:
                return '#CC0000'
            else:
                return '#CC3333'
        else:
            if qtUtils.isLightTheme:
                return '#000000'
            else:
                return '#FFFFFF'


    def disable(self):
        self.isDisabled = True
        self.chatInput.setReadOnly(True)


    def enable(self):
        self.isDisabled = False
        self.chatInput.setReadOnly(False)
