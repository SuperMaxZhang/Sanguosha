from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, 
    QVBoxLayout, QPushButton, QTextEdit, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from ui.table.scene import GameView
from ui.dialogs import HeroSelectDialog, RoleSelectDialog
from engine.game import Game, setup_demo_game
from engine.player import Player
from engine.hero import get_random_heroes


class MainWindow(QMainWindow):
    def __init__(self, game: Game, selected_role: str, player_hero):
        super().__init__()
        self.setWindowTitle("三国杀 - 单机版")
        self.resize(1200, 800)
        self.game = game

        central = QWidget()
        main_layout = QHBoxLayout(central)

        # 主视图（牌桌）
        self.view = GameView(self.game)
        main_layout.addWidget(self.view, stretch=2)

        # 右侧区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 游戏信息
        info_label = QLabel("游戏信息")
        right_layout.addWidget(info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        right_layout.addWidget(self.info_text)
        
        # 操作按钮
        btn_label = QLabel("操作")
        right_layout.addWidget(btn_label)
        
        self.btn_use = QPushButton("出牌 (U)")
        self.btn_end = QPushButton("结束回合 (E)")
        self.btn_restart = QPushButton("重新开始 (R)")
        right_layout.addWidget(self.btn_use)
        right_layout.addWidget(self.btn_end)
        right_layout.addWidget(self.btn_restart)
        
        # 日志
        log_label = QLabel("游戏日志")
        right_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        right_layout.addWidget(self.log_text)
        
        main_layout.addWidget(right_widget, stretch=1)
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
        # 显示身份选择对话框
        role_dialog = RoleSelectDialog(self)
        if role_dialog.exec():
            selected_role = role_dialog.get_selected_role()
        else:
            selected_role = "lord"
        
        # 显示武将选择对话框
        hero_dialog = HeroSelectDialog(self)
        if hero_dialog.exec():
            player_hero = hero_dialog.get_selected_hero()
        else:
            player_hero = get_random_heroes(1)[0]
        
        # 主公体力+1
        player_hp = player_hero.hp + 1 if selected_role == "lord" else player_hero.hp
        
        # 创建新游戏
        ai_heroes = get_random_heroes(3)
        ai_roles = ["loyalist", "rebel", "rebel"]  # 1忠臣2反
        
        players = [
            Player(player_hero.name, player_hp, player_hero, is_ai=False, role=selected_role),
            Player(ai_heroes[0].name, ai_heroes[0].hp, ai_heroes[0], is_ai=True, role=ai_roles[0]),
            Player(ai_heroes[1].name, ai_heroes[1].hp, ai_heroes[1], is_ai=True, role=ai_roles[1]),
            Player(ai_heroes[2].name, ai_heroes[2].hp, ai_heroes[2], is_ai=True, role=ai_roles[2]),
        ]
        
        self.game = Game(players)
        self.view.game = self.game
        self.log_text.clear()
        
        # 重新设置日志回调
        self.game.set_log_callback(self.log)
        self.game.event_bus.on("card_used", self.on_card_used_event)
        self.game.event_bus.on("card_effect_done", self.on_card_effect_done)
        self.game.event_bus.on("dodge_used", self.on_dodge_used_event)
        
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
        else:
            super().keyPressEvent(event)


def run_app():
    app = QApplication([])
    
    # 显示选择对话框
    role_dialog = RoleSelectDialog()
    if role_dialog.exec():
        selected_role = role_dialog.get_selected_role()
    else:
        selected_role = "lord"
    
    hero_dialog = HeroSelectDialog()
    if hero_dialog.exec():
        player_hero = hero_dialog.get_selected_hero()
    else:
        player_hero = get_random_heroes(1)[0]
    
    # 主公体力+1
    player_hp = player_hero.hp + 1 if selected_role == "lord" else player_hero.hp
    
    # 创建游戏
    ai_heroes = get_random_heroes(3)
    ai_roles = ["loyalist", "rebel", "rebel"]
    
    players = [
        Player(player_hero.name, player_hp, player_hero, is_ai=False, role=selected_role),
        Player(ai_heroes[0].name, ai_heroes[0].hp, ai_heroes[0], is_ai=True, role=ai_roles[0]),
        Player(ai_heroes[1].name, ai_heroes[1].hp, ai_heroes[1], is_ai=True, role=ai_roles[1]),
        Player(ai_heroes[2].name, ai_heroes[2].hp, ai_heroes[2], is_ai=True, role=ai_roles[2]),
    ]
    
    game = Game(players)
    window = MainWindow(game, selected_role, player_hero)
    window.show()
    app.exec()
