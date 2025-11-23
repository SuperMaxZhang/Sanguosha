"""简单AI控制器"""
import random
from engine.cards.basic import Slash, Peach, Dodge
from engine.cards.trick import Dismantle, Snatch, ExNihilo, Duel


class AIController:
    """AI玩家控制器"""
    
    def __init__(self, player, game):
        self.player = player
        self.game = game
    
    def play_turn(self):
        """执行一个完整的AI回合"""
        self.game.log(f"[AI] {self.player.name} 开始思考...")
        
        # 出牌阶段：尝试使用手牌
        while True:
            action = self.decide_action()
            if not action:
                break
            
            card_index, targets = action
            success = self.game.use_card(card_index, targets)
            if not success:
                break
        
        self.game.log(f"[AI] {self.player.name} 结束出牌")
    
    def decide_action(self):
        """决定下一步行动：返回 (card_index, target_indices) 或 None"""
        if not self.player.hand:
            return None
        
        # 策略优先级：
        # 1. 体力低时使用桃
        # 2. 使用无中生有摸牌
        # 3. 使用过河拆桥/顺手牵羊控场
        # 4. 使用杀攻击
        # 5. 使用决斗
        
        # 1. 优先回血
        if self.player.hp < self.player.max_hp:
            for i, card in enumerate(self.player.hand):
                if isinstance(card, Peach) and card.can_use(self.player, self.game):
                    return (i, [])
        
        # 2. 使用无中生有摸牌
        for i, card in enumerate(self.player.hand):
            if isinstance(card, ExNihilo):
                return (i, [])
        
        # 3. 使用控场锦囊
        for i, card in enumerate(self.player.hand):
            if isinstance(card, (Dismantle, Snatch)):
                target = self.select_control_target()
                if target is not None:
                    return (i, [target])
        
        # 4. 使用杀攻击
        for i, card in enumerate(self.player.hand):
            if isinstance(card, Slash) and card.can_use(self.player, self.game):
                target = self.select_attack_target()
                if target is not None:
                    return (i, [target])
        
        # 5. 使用决斗
        for i, card in enumerate(self.player.hand):
            if isinstance(card, Duel):
                target = self.select_attack_target()
                if target is not None:
                    return (i, [target])
        
        return None
    
    def select_attack_target(self):
        """选择攻击目标：优先血量低的"""
        other_players = [(i, p) for i, p in enumerate(self.game.players) 
                        if p != self.player and p.is_alive]
        
        if not other_players:
            return None
        
        # 优先攻击血量最低的
        other_players.sort(key=lambda x: x[1].hp)
        return other_players[0][0]
    
    def select_control_target(self):
        """选择控制目标：优先手牌多的"""
        other_players = [(i, p) for i, p in enumerate(self.game.players) 
                        if p != self.player and p.is_alive and len(p.hand) > 0]
        
        if not other_players:
            return None
        
        # 优先选择手牌最多的
        other_players.sort(key=lambda x: len(x[1].hand), reverse=True)
        return other_players[0][0]
