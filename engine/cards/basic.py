class Card:
    def __init__(self, name: str, suit: str = "♠", rank: str = "A"):
        self.name = name
        self.suit = suit  # ♠ ♥ ♣ ♦
        self.rank = rank  # A 2-10 J Q K
        self.card_type = "basic"  # basic, trick, equip

    def can_use(self, player, game):
        """是否可以使用这张牌"""
        return True

    def use(self, player, targets, game):
        """使用这张牌"""
        pass

    def __repr__(self):
        return f"<{self.suit}{self.rank} {self.name}>"


class Slash(Card):
    def __init__(self, suit="♠", rank="A"):
        super().__init__("杀", suit, rank)

    def can_use(self, player, game):
        # 检查是否有哆哮技能
        has_paoxiao = False
        if player.hero and player.hero.skills:
            for skill in player.hero.skills:
                if skill.can_trigger(player, game, "check_slash_limit"):
                    has_paoxiao = True
                    game.log(f"{player.name} 发动【{skill.name}】，可以无限使用【杀】")
                    break
        
        if has_paoxiao:
            return True  # 哆哮：无次数限制
        
        # 正常情况：出牌阶段限一次
        if hasattr(player, 'slash_used_this_turn'):
            return not player.slash_used_this_turn
        return True

    def use(self, player, targets, game):
        if not targets:
            return
        target = targets[0]
        # 目标需要出闪抵消
        game.emit_event("slash_used", source=player, target=target, card=self)
        
        # 检查目标是否有闪（简化：自动出闪）
        from engine.cards.basic import Dodge
        dodge_index = None
        for i, card in enumerate(target.hand):
            if isinstance(card, Dodge):
                dodge_index = i
                break
        
        if dodge_index is not None:
            # 自动使用闪
            dodge_card = target.hand.pop(dodge_index)
            game.deck.discard(dodge_card)
            game.log(f"{target.name} 使用了【闪】抵消了攻击")
            game.emit_event("dodge_used", source=target, card=dodge_card, against=player)
        else:
            # 没有闪，造成伤害
            target.hp -= 1
            game.log(f"{player.name} 对 {target.name} 使用了【杀】，造成1点伤害")
            
            # 立即检查是否死亡
            game.check_death(target)
        
        player.slash_used_this_turn = True


class Dodge(Card):
    def __init__(self, suit="♠", rank="A"):
        super().__init__("闪", suit, rank)


class Peach(Card):
    def __init__(self, suit="♠", rank="A"):
        super().__init__("桃", suit, rank)

    def can_use(self, player, game):
        # 体力未满时可用
        return player.hp < player.max_hp

    def use(self, player, targets, game):
        player.hp = min(player.hp + 1, player.max_hp)
        game.log(f"{player.name} 使用了【桃】，回复1点体力")
        game.emit_event("peach_used", player=player, card=self)
