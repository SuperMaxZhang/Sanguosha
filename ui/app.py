from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, 
    QVBoxLayout, QPushButton, QTextEdit, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from ui.table.scene import GameView
from ui.dialogs import HeroSelectDialog, RoleSelectDialog, DiscardDialog, PlayerCountDialog, HeroInfoDialog
from ui.response_dialog import ResponseDialog
from engine.game import Game, setup_demo_game, get_role_config
from engine.player import Player
from engine.hero import get_random_heroes


class MainWindow(QMainWindow):
    def __init__(self, game: Game, selected_role: str, player_hero):
        super().__init__()
        self.setWindowTitle("三国杀 - 单机版")
        self.resize(1200, 800)
        self.game = game

        central = QWidget()
        main_layout = QVBoxLayout(central)  # 改为垂直布局
        
        # 上部区域：牵桌 + 右侧信息
        top_layout = QHBoxLayout()
        
        # 主视图（牌桌）
        self.view = GameView(self.game)
        top_layout.addWidget(self.view, stretch=2)

        # 右侧区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 游戏信息
        info_label = QLabel("游戏信息")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        right_layout.addWidget(info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        right_layout.addWidget(self.info_text)
        
        # 重新开始按钮放在右侧
        self.btn_restart = QPushButton("🔄 重新开始")
        self.btn_restart.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:pressed {
                background-color: #e65100;
            }
        """)
        right_layout.addWidget(self.btn_restart)
        
        # 日志
        log_label = QLabel("游戏日志")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; margin-top: 10px;")
        right_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        right_layout.addWidget(self.log_text)
        
        top_layout.addWidget(right_widget, stretch=1)
        main_layout.addLayout(top_layout)
        
        # 底部区域：操作按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        # 出牌按钮
        self.btn_use = QPushButton("⚔️ 出牌 (U)")
        self.btn_use.setFixedSize(140, 50)
        self.btn_use.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: 2px solid #45a049;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5CBF60, stop:1 #4CAF50);
                border: 2px solid #4CAF50;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #357a38);
            }
        """)
        bottom_layout.addWidget(self.btn_use)
        
        # 结束回合按钮
        self.btn_end = QPushButton("⏸️ 结束回合 (E)")
        self.btn_end.setFixedSize(140, 50)
        self.btn_end.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: 2px solid #1976D2;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #2196F3);
                border: 2px solid #2196F3;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1565C0, stop:1 #0D47A1);
            }
        """)
        bottom_layout.addWidget(self.btn_end)
        
        bottom_layout.addStretch()
        
        # 添加底部边距
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)
        bottom_widget.setStyleSheet("""
            QWidget {
                background-color: #fafafa;
                border-top: 2px solid #ddd;
                padding: 10px;
            }
        """)
        main_layout.addWidget(bottom_widget)
        
        self.setCentralWidget(central)

        # 绑定事件
        self.btn_use.clicked.connect(self.on_use_card)
        self.btn_end.clicked.connect(self.on_end)
        self.btn_restart.clicked.connect(self.on_restart)
        
        # 初始化显示
        self.update_info()
        
        # 设置游戏日志回调
        self.game.set_log_callback(self.log)
        
        # 监听出牌事件，在中间显示
        self.game.event_bus.on("card_used", self.on_card_used_event)
        # 监听效果完成事件，刷新界面
        self.game.event_bus.on("card_effect_done", self.on_card_effect_done)
        # 监听出闪事件
        self.game.event_bus.on("dodge_used", self.on_dodge_used_event)
        # 监听响应请求（如被杀需要出闪）
        self.game.event_bus.on("response_request", self.on_response_request)
        
        self.log("游戏开始！")
        self.log(f"你的身份：{self._get_role_name(selected_role)}")
        self.log(f"你的武将：{player_hero.name}")
        self.log(f"当前玩家：{self.game.current_player.name}")
        
        # 如果第一个玩家是AI，自动切换到玩家回合
        if self.game.current_player.is_ai:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(500, self.auto_play_ai_turns)

    def on_card_used_event(self, source, card, target, **kwargs):
        """处理出牌事件，在中间显示"""
        # 先刷新界面，再显示动画
        self.view.refresh()
        self.update_info()
        # 使用QTimer延迟显示，确保界面已经刷新
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.view.show_card_in_center(card, source, target))
    
    def on_card_effect_done(self, source, card, target, **kwargs):
        """卡牌效果执行完成，刷新UI显示最新状态"""
        # 延迟刷新，让动画显示一段时间后再更新
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2100, lambda: (
            self.view.refresh(),
            self.update_info()
        ))
    
    def on_dodge_used_event(self, source, card, against, **kwargs):
        """处理出闪事件，显示闪的动画"""
        # 在杀的动画之后稍微延迟显示闪
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.view.show_card_in_center(card, source, None))
    
    def on_discard_phase(self, player, count, **kwargs):
        """处理弃牌阶段"""
        # 显示弃牌对话框
        dialog = DiscardDialog(player, count, self)
        if dialog.exec():
            selected_indices = dialog.get_selected_indices()
            # 调用游戏引擎的弃牌方法
            self.game.discard_cards(selected_indices)
            
            # 刷新界面
            self.view.refresh()
            self.update_info()
            
            # 检查游戏是否结束
            if self.game.phase == "game_over":
                return
            
            self.log(f"轮到 {self.game.current_player.name} 的回合")
            
            # 如果AI回合自动结束，继续切换直到玩家回合
            self.auto_play_ai_turns()
    
    def on_response_request(self, request, **kwargs):
        """响应请求事件：弹出响应对话框"""
        # 仅在人类玩家需要响应时弹框
        if request.target_player.is_ai:
            return
        dialog = ResponseDialog(request, self)
        if dialog.exec():
            selected_index = dialog.get_selected_index()
        else:
            selected_index = None
        # 将选择结果交给响应系统处理
        self.game.response_system.handle_response(selected_index)
        # 处理后刷新界面
        self.view.refresh()
        self.update_info()
    
    def log(self, message):
        """添加日志"""
        self.log_text.append(message)
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

    def update_info(self):
        """更新游戏信息"""
        info = f"当前玩家：{self.game.current_player.name}\n"
        info += f"阶段：{self.game.phase}\n"
        info += f"牌堆剩余：{len(self.game.deck.cards)}\n"
        info += f"弃牌堆：{len(self.game.deck.discards)}\n"
        if not self.game.current_player.is_ai:
            info += f"\n提示：点击手牌和目标后\n点击'出牌'按钮"
        self.info_text.setText(info)

        
    def on_use_card(self):
        """出牌：使用选中的手牌对选中的目标"""
        if self.game.phase == "game_over":
            self.log("游戏已结束，请点击'重新开始'开启新局")
            return
        
        if self.game.current_player.is_ai:
            self.log("现在是电脑回合，请等待...")
            return
        
        card_index = self.view.get_selected_card_index()
        if card_index is None:
            self.log("请先选择一张手牌！")
            return
        
        # 检查索引是否有效
        if card_index >= len(self.game.current_player.hand):
            self.log("手牌索引无效，请重新选择")
            self.view.clear_selections()
            self.view.refresh()
            return
        
        target_indices = self.view.get_selected_target_indices()
        card = self.game.current_player.hand[card_index]
        
        success = self.game.use_card(card_index, target_indices)
        
        # 不在这里刷新，由事件回调处理
        if success:
            self.view.clear_selections()
        else:
            self.log(f"无法使用 {card.name}！")

    def on_end(self):
        if self.game.phase == "game_over":
            self.log("游戏已结束，请点击'重新开始'开启新局")
            return
        
        if self.game.current_player.is_ai:
            self.log("现在是电脑回合，请等待...")
            return
        
        self.log(f"{self.game.current_player.name} 结束回合")
        self.log("=" * 30)
        self.game.next_turn()
        
        # 检查游戏是否结束
        if self.game.phase == "game_over":
            self.view.refresh()
            self.update_info()
            return
        
        self.log(f"轮到 {self.game.current_player.name} 的回合")
        self.view.refresh()
        self.update_info()
        
        # 如果AI回合自动结束，继续切换直到玩家回合
        self.auto_play_ai_turns()
    
    def auto_play_ai_turns(self):
        """自动执行AI回合，直到轮到玩家"""
        import time
        from PySide6.QtCore import QTimer
        
        if self.game.current_player.is_ai:
            # 等待一下让玩家看到AI操作
            QTimer.singleShot(800, self.continue_ai_turn)
    
    def continue_ai_turn(self):
        """继续AI回合"""
        if self.game.current_player.is_ai and self.game.phase != "game_over":
            self.log(f"{self.game.current_player.name} (电脑)结束回合")
            self.log("=" * 30)
            self.game.next_turn()
            
            # 检查游戏是否结束
            if self.game.phase == "game_over":
                self.view.refresh()
                self.update_info()
                return
            
            self.log(f"轮到 {self.game.current_player.name} 的回合")
            self.view.refresh()
            self.update_info()
            
            # 递归检查是否还是AI
            self.auto_play_ai_turns()
    
    def on_restart(self):
        """重新开始游戏"""
        # 1. 选择人数
        count_dialog = PlayerCountDialog(self)
        if count_dialog.exec():
            player_count = count_dialog.get_player_count()
        else:
            player_count = 4
        
        # 2. 选择身份（传入人数）
        role_dialog = RoleSelectDialog(player_count, self)
        if role_dialog.exec():
            selected_role = role_dialog.get_selected_role()
        else:
            selected_role = "lord"
        
        # 3. 选择武将
        hero_dialog = HeroSelectDialog(self)
        if hero_dialog.exec():
            player_hero = hero_dialog.get_selected_hero()
        else:
            player_hero = get_random_heroes(1)[0]
        
        # 获取身份配置
        all_roles = get_role_config(player_count)
        
        # 从所有身份中移除玩家选择的身份，剩下的分配给AI
        ai_roles = all_roles.copy()
        ai_roles.remove(selected_role)
        
        # 如果玩家是主公，体力+1
        player_hp = player_hero.hp + 1 if selected_role == "lord" else player_hero.hp
        
        # 创建新游戏
        ai_count = player_count - 1
        ai_heroes = get_random_heroes(ai_count)
        
        players = [Player(player_hero.name, player_hp, player_hero, is_ai=False, role=selected_role)]
        
        # 添加AI玩家
        for i in range(ai_count):
            ai_hp = ai_heroes[i].hp
            # 如果这个AI是主公，体力+1
            if ai_roles[i] == "lord":
                ai_hp += 1
            players.append(Player(ai_heroes[i].name, ai_hp, ai_heroes[i], is_ai=True, role=ai_roles[i]))
        
        self.game = Game(players)
        self.view.game = self.game
        self.log_text.clear()
        
        # 重新设置日志回调
        self.game.set_log_callback(self.log)
        self.game.event_bus.on("card_used", self.on_card_used_event)
        self.game.event_bus.on("card_effect_done", self.on_card_effect_done)
        self.game.event_bus.on("dodge_used", self.on_dodge_used_event)
        self.game.event_bus.on("discard_phase", self.on_discard_phase)
        # 监听响应请求（如被杀需要出闪）
        self.game.event_bus.on("response_request", self.on_response_request)
        
        self.log("游戏重新开始！")
        self.log(f"你的身份：{self._get_role_name(selected_role)}")
        self.log(f"你的武将：{player_hero.name}")
        self.log(f"当前玩家：{self.game.current_player.name}")
        self.view.refresh()
        self.update_info()
        
        # 如果第一个玩家是AI，自动切换到玩家回合
        if self.game.current_player.is_ai:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(500, self.auto_play_ai_turns)
    
    def _get_role_name(self, role):
        """获取身份中文名"""
        role_names = {
            "lord": "主公",
            "loyalist": "忠臣",
            "rebel": "反贼",
            "traitor": "内奸"
        }
        return role_names.get(role, "未知")
    
    def keyPressEvent(self, event):
        """快捷键支持"""
        if event.key() == Qt.Key_U:
            self.on_use_card()
        elif event.key() == Qt.Key_E:
            self.on_end()
        elif event.key() == Qt.Key_R:
            self.on_restart()
        elif event.key() == Qt.Key_H:
            self.show_hero_info()
        else:
            super().keyPressEvent(event)
    
    def show_hero_info(self):
        """显示武将信息对话框"""
        dialog = HeroInfoDialog(self)
        dialog.exec()


def run_app():
    app = QApplication([])
    
    # 1. 选择人数
    count_dialog = PlayerCountDialog()
    if count_dialog.exec():
        player_count = count_dialog.get_player_count()
    else:
        player_count = 4
    
    # 2. 选择身份（传入人数）
    role_dialog = RoleSelectDialog(player_count)
    if role_dialog.exec():
        selected_role = role_dialog.get_selected_role()
    else:
        selected_role = "lord"
    
    # 3. 选择武将
    hero_dialog = HeroSelectDialog()
    if hero_dialog.exec():
        player_hero = hero_dialog.get_selected_hero()
    else:
        player_hero = get_random_heroes(1)[0]
    
    # 获取身份配置
    all_roles = get_role_config(player_count)
    
    # 从所有身份中移除玩家选择的身份，剩下的分配给AI
    ai_roles = all_roles.copy()
    ai_roles.remove(selected_role)
    
    # 如果玩家是主公，体力+1
    player_hp = player_hero.hp + 1 if selected_role == "lord" else player_hero.hp
    
    # 创建游戏
    ai_count = player_count - 1
    ai_heroes = get_random_heroes(ai_count)
    
    players = [Player(player_hero.name, player_hp, player_hero, is_ai=False, role=selected_role)]
    
    # 添加AI玩家
    for i in range(ai_count):
        ai_hp = ai_heroes[i].hp
        # 如果这个AI是主公，体力+1
        if ai_roles[i] == "lord":
            ai_hp += 1
        players.append(Player(ai_heroes[i].name, ai_hp, ai_heroes[i], is_ai=True, role=ai_roles[i]))
    
    game = Game(players)
    window = MainWindow(game, selected_role, player_hero)
    window.show()
    app.exec()
