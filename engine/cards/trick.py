from engine.cards.basic import Card


class TrickCard(Card):
    def __init__(self, name: str, suit: str = "♠", rank: str = "A"):
        super().__init__(name, suit, rank)
        self.card_type = "trick"


class Dismantle(TrickCard):
    """过河拆桥"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("过河拆桥", suit, rank)

    def use(self, player, targets, game):
        if not targets:
            return
        target = targets[0]
        if target.hand:
            # 简化：弃置第一张手牌
            card = target.hand.pop(0)
            game.deck.discard(card)
            game.log(f"{player.name} 使用【过河拆桥】弃置了 {target.name} 的一张牌")


class Snatch(TrickCard):
    """顺手牵羊"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("顺手牵羊", suit, rank)

    def use(self, player, targets, game):
        if not targets:
            return
        target = targets[0]
        if target.hand:
            card = target.hand.pop(0)
            player.hand.append(card)
            game.log(f"{player.name} 使用【顺手牵羊】获得了 {target.name} 的一张牌")


class ExNihilo(TrickCard):
    """无中生有"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("无中生有", suit, rank)

    def use(self, player, targets, game):
        player.draw(game.deck, 2)
        game.log(f"{player.name} 使用【无中生有】摸了2张牌")


class Duel(TrickCard):
    """决斗"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("决斗", suit, rank)

    def use(self, player, targets, game):
        if not targets:
            return
        target = targets[0]
        # 简化：直接造成1点伤害
        target.hp -= 1
        game.log(f"{player.name} 对 {target.name} 使用【决斗】，造成1点伤害")
        
        # 立即检查是否死亡
        game.check_death(target)
