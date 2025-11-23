from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QButtonGroup, QRadioButton, QGroupBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from engine.hero import STANDARD_HEROES


class HeroSelectDialog(QDialog):
    """武将选择对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择你的武将")
        self.setMinimumWidth(500)
        self.selected_hero = None
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("请选择你要扮演的武将：")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # 武将列表
        self.hero_group = QButtonGroup(self)
        
        for i, hero_class in enumerate(STANDARD_HEROES):
            hero = hero_class()
            btn = QRadioButton(f"{hero.name} ({hero.force}) - {hero.hp}血")
            self.hero_group.addButton(btn, i)
            layout.addWidget(btn)
            
            if i == 0:
                btn.setChecked(True)
        
        # 确认按钮
        confirm_btn = QPushButton("确认选择")
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)
    
    def get_selected_hero(self):
        """获取选中的武将"""
        index = self.hero_group.checkedId()
        if index >= 0:
            return STANDARD_HEROES[index]()
        return STANDARD_HEROES[0]()


class RoleSelectDialog(QDialog):
    """身份选择对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择你的身份")
        self.setMinimumWidth(400)
        self.selected_role = "player"
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("请选择你的游戏身份：")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # 身份说明
        desc = QLabel(
            "• 主公：需要消灭所有反贼和内奸\n"
            "• 忠臣：保护主公，协助主公获胜\n"
            "• 反贼：目标是击杀主公\n"
            "• 内奸：最后存活者获胜"
        )
        desc.setStyleSheet("color: #666; margin: 10px;")
        layout.addWidget(desc)
        
        # 身份按钮
        self.role_group = QButtonGroup(self)
        
        roles = [
            ("主公", "lord", "红色，公开身份，体力+1"),
            ("忠臣", "loyalist", "黄色，保护主公"),
            ("反贼", "rebel", "绿色，击杀主公"),
            ("内奸", "traitor", "蓝色，最后存活"),
        ]
        
        for i, (name, role, desc) in enumerate(roles):
            btn = QRadioButton(f"{name} - {desc}")
            self.role_group.addButton(btn, i)
            layout.addWidget(btn)
            
            if role == "lord":
                btn.setChecked(True)
        
        # 确认按钮
        confirm_btn = QPushButton("确认选择")
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)
    
    def get_selected_role(self):
        """获取选中的身份"""
        roles = ["lord", "loyalist", "rebel", "traitor"]
        index = self.role_group.checkedId()
        return roles[index] if 0 <= index < len(roles) else "lord"


class DiscardDialog(QDialog):
    """弃牌选择对话框"""
    def __init__(self, player, discard_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("弃牌阶段")
        self.setMinimumSize(400, 500)
        self.player = player
        self.discard_count = discard_count
        self.selected_cards = []
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel(f"你的体力：{player.hp}  手牌数：{len(player.hand)}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #d32f2f;")
        layout.addWidget(title)
        
        # 说明
        desc = QLabel(f"请选择 {discard_count} 张牌弃置：")
        desc.setStyleSheet("font-size: 14px; margin: 10px 0;")
        layout.addWidget(desc)
        
        # 手牌列表
        self.card_list = QListWidget()
        self.card_list.setSelectionMode(QListWidget.MultiSelection)
        self.card_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #ff5252;
                color: white;
            }
        """)
        
        for i, card in enumerate(player.hand):
            item = QListWidgetItem(f"{card.suit}{card.rank} {card.name}")
            item.setData(Qt.UserRole, i)  # 存储索引
            self.card_list.addItem(item)
        
        layout.addWidget(self.card_list)
        
        # 选中提示
        self.status_label = QLabel(f"已选择：0 / {discard_count}")
        self.status_label.setStyleSheet("font-size: 13px; color: #666; margin: 5px 0;")
        layout.addWidget(self.status_label)
        
        self.card_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        confirm_btn = QPushButton("确认弃牌")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c62828;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        confirm_btn.clicked.connect(self.on_confirm)
        self.confirm_btn = confirm_btn
        confirm_btn.setEnabled(False)
        
        btn_layout.addWidget(confirm_btn)
        layout.addLayout(btn_layout)
    
    def on_selection_changed(self):
        selected_items = self.card_list.selectedItems()
        count = len(selected_items)
        self.status_label.setText(f"已选择：{count} / {self.discard_count}")
        self.confirm_btn.setEnabled(count == self.discard_count)
    
    def on_confirm(self):
        selected_items = self.card_list.selectedItems()
        if len(selected_items) == self.discard_count:
            self.selected_cards = [item.data(Qt.UserRole) for item in selected_items]
            self.accept()
    
    def get_selected_indices(self):
        return self.selected_cards
