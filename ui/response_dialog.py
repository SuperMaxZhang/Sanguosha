from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class ResponseDialog(QDialog):
    """响应选择对话框（例如：是否出闪）"""
    def __init__(self, request, parent=None):
        super().__init__(parent)
        self.setWindowTitle("响应请求")
        self.setMinimumWidth(380)
        self.request = request
        self.selected_index = None
        
        layout = QVBoxLayout(self)
        
        title = QLabel(f"{request.source_player.name} 对 {request.target_player.name} 使用了【{request.context.get('damage_card').name if request.context and request.context.get('damage_card') else '牌'}】")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        tip = QLabel("请选择是否使用响应牌：")
        tip.setStyleSheet("color: #666;")
        layout.addWidget(tip)
        
        # 列出可用的响应牌
        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.SingleSelection)
        
        # 填充手牌中符合条件的响应牌
        from engine.cards.basic import Dodge, Peach, Slash
        player = request.target_player
        for i, card in enumerate(player.hand):
            if request.request_type == "dodge_slash" and isinstance(card, Dodge):
                item = QListWidgetItem(f"{card.suit}{card.rank}  {card.name}")
                item.setData(Qt.UserRole, i)
                self.list.addItem(item)
            elif request.request_type == "peach_dying" and isinstance(card, Peach):
                item = QListWidgetItem(f"{card.suit}{card.rank}  {card.name}")
                item.setData(Qt.UserRole, i)
                self.list.addItem(item)
            elif request.request_type == "slash_duel" and isinstance(card, Slash):
                item = QListWidgetItem(f"{card.suit}{card.rank}  {card.name}")
                item.setData(Qt.UserRole, i)
                self.list.addItem(item)
        layout.addWidget(self.list)
        
        btns = QHBoxLayout()
        use_btn = QPushButton("使用")
        cancel_btn = QPushButton("不响应")
        btns.addWidget(use_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)
        
        use_btn.clicked.connect(self.on_use)
        cancel_btn.clicked.connect(self.on_cancel)
    
    def on_use(self):
        item = self.list.currentItem()
        if item:
            self.selected_index = item.data(Qt.UserRole)
        self.accept()
    
    def on_cancel(self):
        self.selected_index = None
        self.accept()
    
    def get_selected_index(self):
        return self.selected_index
