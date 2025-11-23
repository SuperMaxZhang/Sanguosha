from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsTextItem, 
    QGraphicsRectItem, QGraphicsItem
)
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtCore import Qt, QRectF


class CardItem(QGraphicsRectItem):
    """可交互的卡牌图形项"""
    def __init__(self, card, x, y, width=80, height=110):
        super().__init__(0, 0, width, height)
        self.card = card
        self.setPos(x, y)
        self.width = width
        self.height = height
        self.selected = False
        
        # 样式
        self.setBrush(QBrush(QColor(255, 250, 240)))
        self.setPen(QPen(QColor(100, 100, 100), 2))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        # 卡牌文本
        self.text = QGraphicsTextItem(self)
        font = QFont("Arial", 12, QFont.Bold)
        self.text.setFont(font)
        self.update_text()
        
    def update_text(self):
        # 显示花色、点数和牌名
        text = f"{self.card.suit}{self.card.rank}\n{self.card.name}"
        self.text.setPlainText(text)
        # 居中
        bounds = self.text.boundingRect()
        self.text.setPos(
            (self.width - bounds.width()) / 2,
            (self.height - bounds.height()) / 2
        )
        # 颜色：红色花色用红字
        if self.card.suit in ["♥", "♦"]:
            self.text.setDefaultTextColor(QColor(200, 0, 0))
        else:
            self.text.setDefaultTextColor(QColor(0, 0, 0))
    
    def mousePressEvent(self, event):
        self.selected = not self.selected
        if self.selected:
            self.setBrush(QBrush(QColor(255, 255, 150)))
        else:
            self.setBrush(QBrush(QColor(255, 250, 240)))
        super().mousePressEvent(event)


class PlayerPanel(QGraphicsRectItem):
    """玩家信息面板"""
    def __init__(self, player, x, y, width=150, height=120):
        super().__init__(0, 0, width, height)
        self.player = player
        self.setPos(x, y)
        self.width = width
        self.height = height
        self.selected = False
        
        self.setBrush(QBrush(QColor(230, 230, 250)))
        self.setPen(QPen(QColor(100, 100, 100), 2))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        self.text = QGraphicsTextItem(self)
        self.text.setPos(5, 5)
        
        # 血量显示（红色爱心）
        self.hp_items = []
        
        self.update_display()
    
    def update_display(self):
        # 获取身份显示
        role_symbols = {
            "lord": "主",  # 主公
            "loyalist": "忠",  # 忠臣
            "rebel": "反",  # 反贼
            "traitor": "内"  # 内奸
        }
        role_symbol = role_symbols.get(self.player.role, "")
        
        # 获取技能显示
        skill_text = ""
        if self.player.hero and self.player.hero.skills:
            skill_names = [skill.name for skill in self.player.hero.skills]
            if skill_names:
                skill_text = "\n" + " ".join(skill_names)
        
        # 更新文本
        name_suffix = " (电脑)" if self.player.is_ai else " (你)"
        hero_name = f" - {self.player.hero.name}" if self.player.hero else ""
        role_display = f" [{role_symbol}]" if role_symbol else ""
        info = f"{self.player.name}{hero_name}{role_display}{name_suffix}\n手牌: {len(self.player.hand)}{skill_text}"
        self.text.setPlainText(info)
        
        # 如果死亡，变灰
        if not self.player.is_alive:
            self.setBrush(QBrush(QColor(180, 180, 180)))
            info += "\n☠ 已阵亡"
            self.text.setPlainText(info)
            self.text.setDefaultTextColor(QColor(100, 100, 100))
        
        # 清除旧的血量显示
        for item in self.hp_items:
            if item.scene():
                item.scene().removeItem(item)
        self.hp_items.clear()
        
        # 绘制血量（红色爱心）
        heart_size = 18
        start_y = 70  # 增加Y位置，给技能留空间
        for i in range(self.player.max_hp):
            heart = QGraphicsTextItem(self)
            if i < self.player.hp:
                heart.setPlainText("♥")  # 实心
                heart.setDefaultTextColor(QColor(220, 20, 60))
            else:
                heart.setPlainText("♡")  # 空心
                heart.setDefaultTextColor(QColor(150, 150, 150))
            
            font = QFont("Arial", 16, QFont.Bold)
            heart.setFont(font)
            heart.setPos(5 + i * heart_size, start_y)
            self.hp_items.append(heart)
    
    def update_text(self):
        self.update_display()
    
    def mousePressEvent(self, event):
        self.selected = not self.selected
        if self.selected:
            self.setBrush(QBrush(QColor(255, 200, 200)))
        else:
            self.setBrush(QBrush(QColor(230, 230, 250)))
        super().mousePressEvent(event)


class GameView(QGraphicsView):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setSceneRect(0, 0, 900, 700)
        
        self.player_panels = []
        self.hand_cards = []
        self.center_card_item = None  # 中间显示的牌
        
        self.refresh()
    
    def show_card_in_center(self, card, source_player, target_player=None):
        """在牌桌中间显示出牌动画"""
        # 清除之前的牌和定时器
        if hasattr(self, '_clear_timer') and self._clear_timer:
            self._clear_timer.stop()
            self._clear_timer = None
        
        if self.center_card_item:
            try:
                if self.center_card_item.scene():
                    self.scene.removeItem(self.center_card_item)
            except RuntimeError:
                pass  # 对象已被删除
            self.center_card_item = None
        
        if hasattr(self, '_center_text_item') and self._center_text_item:
            try:
                if self._center_text_item.scene():
                    self.scene.removeItem(self._center_text_item)
            except RuntimeError:
                pass
            self._center_text_item = None
        
        if hasattr(self, '_arrow_item') and self._arrow_item:
            try:
                if self._arrow_item.scene():
                    self.scene.removeItem(self._arrow_item)
            except RuntimeError:
                pass
            self._arrow_item = None
        
        # 创建中心区域的大牌
        center_x, center_y = 380, 280
        self.center_card_item = CardItem(card, center_x, center_y, width=120, height=160)
        self.scene.addItem(self.center_card_item)
        
        # 添加描述文本
        desc_text = f"{source_player.name} 使用 【{card.name}】"
        if target_player:
            desc_text = f"{source_player.name} → {target_player.name}"
        
        self._center_text_item = QGraphicsTextItem(desc_text)
        self._center_text_item.setPos(center_x - 20, center_y - 35)
        font = QFont("Arial", 14, QFont.Bold)
        self._center_text_item.setFont(font)
        self._center_text_item.setDefaultTextColor(QColor(255, 100, 0))
        self.scene.addItem(self._center_text_item)
        
        # 如果有目标，绘制箭头
        if target_player:
            self._draw_arrow(source_player, target_player)
        
        # 定时清除（2秒后）
        from PySide6.QtCore import QTimer
        self._clear_timer = QTimer()
        self._clear_timer.setSingleShot(True)
        self._clear_timer.timeout.connect(self._clear_center_card)
        self._clear_timer.start(2000)
    
    def _draw_arrow(self, source_player, target_player):
        """绘制从源玩家到目标玩家的箭头"""
        from PySide6.QtCore import QPointF, QLineF
        from PySide6.QtGui import QPen, QPolygonF
        import math
        
        # 找到玩家面板位置
        source_panel = None
        target_panel = None
        for panel in self.player_panels:
            if panel.player == source_player:
                source_panel = panel
            if panel.player == target_player:
                target_panel = panel
        
        if not source_panel or not target_panel:
            return
        
        # 计算中心点
        source_center = QPointF(
            source_panel.x() + source_panel.width / 2,
            source_panel.y() + source_panel.height / 2
        )
        target_center = QPointF(
            target_panel.x() + target_panel.width / 2,
            target_panel.y() + target_panel.height / 2
        )
        
        # 绘制箭头
        line = QLineF(source_center, target_center)
        pen = QPen(QColor(255, 0, 0), 3)
        pen.setStyle(Qt.DashLine)
        
        self._arrow_item = self.scene.addLine(line, pen)
        
        # 绘制箭头三角形
        angle = math.atan2(line.dy(), line.dx())
        arrow_size = 15
        
        arrow_p1 = target_center - QPointF(
            math.cos(angle - math.pi / 6) * arrow_size,
            math.sin(angle - math.pi / 6) * arrow_size
        )
        arrow_p2 = target_center - QPointF(
            math.cos(angle + math.pi / 6) * arrow_size,
            math.sin(angle + math.pi / 6) * arrow_size
        )
        
        arrow_head = QPolygonF([target_center, arrow_p1, arrow_p2])
        arrow_head_item = self.scene.addPolygon(arrow_head, pen, QBrush(QColor(255, 0, 0)))
        
        # 保存箭头以便清除
        if not hasattr(self, '_arrow_items'):
            self._arrow_items = []
        self._arrow_items.append(arrow_head_item)
    
    def _clear_center_card(self):
        """清除中心区域的牌"""
        if self.center_card_item:
            try:
                if self.center_card_item.scene():
                    self.scene.removeItem(self.center_card_item)
            except RuntimeError:
                pass  # 对象已被删除
            self.center_card_item = None
        
        if hasattr(self, '_center_text_item') and self._center_text_item:
            try:
                if self._center_text_item.scene():
                    self.scene.removeItem(self._center_text_item)
            except RuntimeError:
                pass
            self._center_text_item = None
        
        if hasattr(self, '_arrow_item') and self._arrow_item:
            try:
                if self._arrow_item.scene():
                    self.scene.removeItem(self._arrow_item)
            except RuntimeError:
                pass
            self._arrow_item = None
        
        if hasattr(self, '_arrow_items') and self._arrow_items:
            for item in self._arrow_items:
                try:
                    if item.scene():
                        self.scene.removeItem(item)
                except RuntimeError:
                    pass
            self._arrow_items = []

    def refresh(self):
        # 停止并清理中心牌的定时器
        if hasattr(self, '_clear_timer') and self._clear_timer:
            self._clear_timer.stop()
            self._clear_timer = None
        
        self.center_card_item = None
        if hasattr(self, '_center_text_item'):
            self._center_text_item = None
        if hasattr(self, '_arrow_item'):
            self._arrow_item = None
        if hasattr(self, '_arrow_items'):
            self._arrow_items = []
        
        self.scene.clear()
        self.player_panels.clear()
        self.hand_cards.clear()
        
        # 圆环布局展示所有玩家
        radius = 200
        cx, cy = 450, 250
        import math
        n = len(self.game.players)
        
        for i, p in enumerate(self.game.players):
            angle = 2 * math.pi * i / max(n, 1) - math.pi / 2  # 从顶部开始
            x = cx + radius * math.cos(angle) - 75
            y = cy + radius * math.sin(angle) - 40
            
            panel = PlayerPanel(p, x, y)
            self.scene.addItem(panel)
            self.player_panels.append(panel)
            
            # 标记当前玩家
            if p is self.game.current_player:
                panel.setPen(QPen(QColor(255, 100, 100), 4))
        
        # 底部显示当前玩家的手牌
        current = self.game.current_player
        start_x = 50
        y = 550
        for i, card in enumerate(current.hand):
            card_item = CardItem(card, start_x + i * 90, y)
            self.scene.addItem(card_item)
            self.hand_cards.append(card_item)
        
        # 显示提示信息
        info_text = QGraphicsTextItem(f"当前阶段: {self.game.phase}  |牌堆剩余: {len(self.game.deck.cards)}")
        info_text.setPos(50, 20)
        font = QFont("Arial", 12)
        info_text.setFont(font)
        self.scene.addItem(info_text)
    
    def get_selected_card_index(self):
        """获取选中的手牌索引"""
        for i, card_item in enumerate(self.hand_cards):
            if card_item.selected:
                return i
        return None
    
    def get_selected_target_indices(self):
        """获取选中的目标玩家索引列表"""
        indices = []
        for i, panel in enumerate(self.player_panels):
            if panel.selected:
                indices.append(i)
        return indices
    
    def clear_selections(self):
        """清除所有选中状态"""
        for card_item in self.hand_cards:
            if card_item.selected:
                card_item.selected = False
                card_item.setBrush(QBrush(QColor(255, 250, 240)))
        for panel in self.player_panels:
            if panel.selected:
                panel.selected = False
                panel.setBrush(QBrush(QColor(230, 230, 250)))
