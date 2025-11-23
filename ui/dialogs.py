from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QButtonGroup, QRadioButton, QGroupBox, QListWidget, QListWidgetItem, QSlider
)
from PySide6.QtCore import Qt
from engine.hero import STANDARD_HEROES


class PlayerCountDialog(QDialog):
    """人数选择对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择游戏人数")
        self.setMinimumWidth(500)
        self.player_count = 4
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("请选择游戏人数：")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 人数滑块
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("2人"))
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(2)
        self.slider.setMaximum(8)
        self.slider.setValue(4)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.slider)
        
        slider_layout.addWidget(QLabel("8人"))
        layout.addLayout(slider_layout)
        
        # 当前选择显示
        self.current_label = QLabel("4 人")
        self.current_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #2196F3;
            margin: 20px;
            qproperty-alignment: AlignCenter;
        """)
        layout.addWidget(self.current_label)
        
        # 身份配置说明
        self.config_label = QLabel()
        self.config_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 8px;
            margin: 10px 0;
        """)
        layout.addWidget(self.config_label)
        
        # 初始化显示
        self.update_config_display(4)
        
        # 快捷按钮
        quick_layout = QHBoxLayout()
        quick_label = QLabel("快速选择：")
        quick_layout.addWidget(quick_label)
        
        for count in [2, 4, 5, 8]:
            btn = QPushButton(f"{count}人")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e3f2fd;
                    border: 2px solid #2196F3;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #2196F3;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, c=count: self.set_count(c))
            quick_layout.addWidget(btn)
        
        quick_layout.addStretch()
        layout.addLayout(quick_layout)
        
        # 确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)
    
    def on_slider_changed(self, value):
        self.player_count = value
        self.current_label.setText(f"{value} 人")
        self.update_config_display(value)
    
    def set_count(self, count):
        self.slider.setValue(count)
    
    def update_config_display(self, count):
        configs = {
            2: "🀄 1主公 + 1反贼  (经典对决)",
            3: "🀄 1主公 + 1忠臣 + 1反贼",
            4: "🀄 1主公 + 1忠臣 + 2反贼  (标准局)",
            5: "🀄 1主公 + 1忠臣 + 2反贼 + 1内奸",
            6: "🀄 1主公 + 1忠臣 + 3反贼 + 1内奸",
            7: "🀄 1主公 + 2忠臣 + 3反贼 + 1内奸",
            8: "🀄 1主公 + 2忠臣 + 4反贼 + 1内奸  (满人局)"
        }
        self.config_label.setText(configs.get(count, ""))
    
    def get_player_count(self):
        return self.player_count


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
    def __init__(self, player_count=4, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择你的身份")
        self.setMinimumWidth(400)
        self.selected_role = "lord"
        self.player_count = player_count
        
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
        
        # 根据人数决定可选身份
        all_roles = [
            ("主公", "lord", "红色，公开身份，体力+1"),
            ("忠臣", "loyalist", "黄色，保护主公"),
            ("反贼", "rebel", "绿色，击杀主公"),
            ("内奸", "traitor", "蓝色，最后存活"),
        ]
        
        # 根据人数禁用某些身份
        if player_count == 2:
            # 2人局：只能选主公或反贼
            available_roles = ["lord", "rebel"]
        elif player_count == 3:
            # 3人局：只能选主公、忠臣或反贼
            available_roles = ["lord", "loyalist", "rebel"]
        elif player_count == 4:
            # 4人局：没有内奸
            available_roles = ["lord", "loyalist", "rebel"]
        else:
            # 5人及以上：所有身份都可选
            available_roles = ["lord", "loyalist", "rebel", "traitor"]
        
        for i, (name, role, desc_text) in enumerate(all_roles):
            btn = QRadioButton(f"{name} - {desc_text}")
            
            # 如果该身份不可用，禁用按钮
            if role not in available_roles:
                btn.setEnabled(False)
                btn.setStyleSheet("color: #ccc;")
            
            self.role_group.addButton(btn, i)
            layout.addWidget(btn)
            
            # 默认选中第一个可用的身份
            if role == available_roles[0]:
                btn.setChecked(True)
        
        # 确认按钮
        confirm_btn = QPushButton("确认选择")
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)
    
    def get_selected_role(self):
        """获取选中的身份"""
        roles = ["lord", "loyalist", "rebel", "traitor"]
        index = self.role_group.checkedId()
        selected = roles[index] if 0 <= index < len(roles) else "lord"
        
        # 再次检查该身份是否在当前人数配置中
        from engine.game import get_role_config
        all_roles = get_role_config(self.player_count)
        if selected in all_roles:
            return selected
        else:
            # 如果不在，返回第一个可用身份
            return all_roles[0]


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
