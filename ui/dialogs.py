from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QButtonGroup, QRadioButton, QGroupBox
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
