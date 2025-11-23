class Player:
    def __init__(self, name: str, hp: int = 4, hero=None, is_ai=False, role="player"):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.hand = []
        self.equip = []
        self.judge_area = []
        self.hero = hero  # 武将
        self.is_alive = True
        self.is_ai = is_ai  # 是否是AI玩家
        self.role = role  # 身份：lord(主公), loyalist(忠丸), rebel(反贼), traitor(内奸)
        # 回合状态
        self.slash_used_this_turn = False

    def draw(self, deck, n: int = 1):
        for _ in range(n):
            card = deck.draw()
            if card:
                self.hand.append(card)

    def use_card(self, card, targets, game):
        """使用一张牌"""
        if card not in self.hand:
            print(f"错误：{card} 不在手牌中")
            return False
        
        if not card.can_use(self, game):
            print(f"错误：不能使用 {card}")
            return False
        
        # 从手牌移除
        self.hand.remove(card)
        
        # 触发UI显示动画（在执行效果之前）
        target_player = targets[0] if targets else None
        game.emit_event("card_used", source=self, card=card, target=target_player)
        
        # 执行效果
        card.use(self, targets, game)
        
        # 进入弃牌堆
        game.deck.discard(card)
        
        # 效果执行后再次触发事件，用于刷新UI
        game.emit_event("card_effect_done", source=self, card=card, target=target_player)
        
        return True

    def reset_turn(self):
        """重置回合状态"""
        self.slash_used_this_turn = False

    def __repr__(self):
        return f"<Player {self.name} hp={self.hp}/{self.max_hp} hand={len(self.hand)}>"
