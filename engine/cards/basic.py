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
        
        # 使用响应系统请求闪的响应
        game.log(f"{player.name} 对 {target.name} 使用了【杀】")
        responded = game.response_system.request_response(
            request_type="dodge_slash",
            source_player=player,
            target_player=target,
            context={"damage_card": self}
        )
        
        # 处理响应结果
        if responded is None:
            # 人类玩家：等待UI响应，不在此结算
            player.slash_used_this_turn = True
            return
        elif responded:  # 有闪，抵消攻击
            game.log(f"{target.name} 使用了【闪】抵消了攻击")
        else:  # 没有闪，造成伤害
            # 距离限制：若超出攻击范围，不造成伤害（保险）
            try:
                attack_range = player.get_attack_range() if hasattr(player, 'get_attack_range') else 1
                dist = game.distance(player, target) if hasattr(game, 'distance') else 1
                if dist > attack_range:
                    game.log(f"目标超出攻击范围（距离 {dist}，范围 {attack_range}），攻击未生效")
                    player.slash_used_this_turn = True
                    return
            except Exception:
                pass
            
            target.hp -= 1
            game.log(f"{target.name} 受到了1点伤害，剩余体力: {target.hp}")
            
            # 触发受伤技能（如奸雄）
            if target.hero and target.hero.skills:
                for skill in target.hero.skills:
                    if skill.can_trigger(target, game, "damage_taken", damage_card=self, source=player):
                        skill.trigger(target, game, damage_card=self, source=player)
            
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
