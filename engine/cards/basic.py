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
        # 检查是否装备了诸葛连弩
        has_zhuge = False
        for eq in player.equip:
            if hasattr(eq, 'name') and eq.name == "诸葛连弩":
                has_zhuge = True
                break
        
        # 检查是否有哆哮技能
        has_paoxiao = False
        if player.hero and player.hero.skills:
            for skill in player.hero.skills:
                if skill.can_trigger(player, game, "check_slash_limit"):
                    has_paoxiao = True
                    game.log(f"{player.name} 发动【{skill.name}】，可以无限使用【杀】")
                    break
        
        # 检查次数限制
        if not (has_paoxiao or has_zhuge):
            # 正常情况：出牌阶段限一次
            if hasattr(player, 'slash_used_this_turn') and player.slash_used_this_turn:
                return False
        
        return True

    def use(self, player, targets, game):
        if not targets:
            # 没有目标，把牌放回手牌
            player.hand.append(self)
            return
        target = targets[0]
        
        # 检查距离：在使用杀之前先检查是否在攻击范围内
        attack_range = player.get_attack_range() if hasattr(player, 'get_attack_range') else 1
        dist = game.distance(player, target) if hasattr(game, 'distance') else 1
        
        if dist > attack_range:
            game.log(f"{player.name} 对 {target.name} 使用【杀】失败：目标超出攻击范围（距离 {dist}，范围 {attack_range}）")
            # 把牌放回手牌，不标记为已使用
            player.hand.append(self)
            return
        
        # 目标需要出闪抵消
        game.emit_event("slash_used", source=player, target=target, card=self)
        
        # 检查是否装备诸葛连弩
        has_zhuge = any(hasattr(eq, 'name') and eq.name == "诸葛连弩" for eq in player.equip)
        
        # 使用响应系统请求闪的响应
        game.log(f"{player.name} 对 {target.name} 使用了【杀】{' (诸葛连弩)' if has_zhuge else ''}（距离 {dist}，范围 {attack_range}）")
        responded = game.response_system.request_response(
            request_type="dodge_slash",
            source_player=player,
            target_player=target,
            context={"damage_card": self, "source_player": player}
        )
        
        # 处理响应结果
        if responded is None:
            # 人类玩家：等待UI响应，不在此结算
            if not has_zhuge:
                player.slash_used_this_turn = True
            return
        elif responded:  # 有闪，抵消攻击
            game.log(f"{target.name} 使用了【闪】抵消了攻击")
        else:  # 没有闪，造成伤害
            target.hp -= 1
            game.log(f"{target.name} 受到了1点伤害，剩余体力: {target.hp}")
            
            # 触发受伤技能（如奸雄）
            if target.hero and target.hero.skills:
                for skill in target.hero.skills:
                    if skill.can_trigger(target, game, "damage_taken", damage_card=self, source=player):
                        skill.trigger(target, game, damage_card=self, source=player)
            
            # 立即检查是否死亡
            game.check_death(target)
        
        # 诸葛连弩不设置slash_used_this_turn
        if not has_zhuge:
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
