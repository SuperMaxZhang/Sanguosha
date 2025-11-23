"""响应机制系统 - 处理玩家对特定事件的响应（如出闪、求桃等）"""


class ResponseRequest:
    """响应请求"""
    def __init__(self, request_type, source_player, target_player, context=None):
        """
        request_type: 响应类型（dodge_slash, peach_dying, wuxie等）
        source_player: 发起响应请求的玩家（如使用杀的玩家）
        target_player: 需要响应的玩家（如被杀的玩家）
        context: 额外上下文信息（如造成的伤害牌）
        """
        self.request_type = request_type
        self.source_player = source_player
        self.target_player = target_player
        self.context = context or {}
        self.response_card = None  # 响应使用的牌
        self.responded = False  # 是否已响应


class ResponseSystem:
    """响应系统管理器"""
    
    def __init__(self, game):
        self.game = game
        self.pending_request = None  # 当前待处理的响应请求
    
    def request_response(self, request_type, source_player, target_player, context=None):
        """
        请求响应
        返回 True 表示响应成功，False 表示未响应或响应失败
        """
        request = ResponseRequest(request_type, source_player, target_player, context)
        self.pending_request = request
        
        if target_player.is_ai:
            # AI自动响应
            return self._ai_auto_response(request)
        else:
            # 玩家手动响应 - 触发UI事件
            self.game.emit_event("response_request", request=request)
            # 注意：实际响应由 UI 调用 handle_response 处理
            return None  # 等待UI处理
    
    def handle_response(self, card_index=None):
        """
        处理玩家的响应选择
        card_index: 响应使用的牌索引，None表示不响应
        """
        if not self.pending_request:
            return False
        
        request = self.pending_request
        player = request.target_player
        
        # 检查是否可以使用八卦阵
        if request.request_type == "dodge_slash" and card_index is None:
            has_bagua = any(hasattr(eq, 'name') and eq.name == "八卦阵" for eq in player.equip)
            if has_bagua:
                # 八卦阵：进行判定，红色视为闪
                judge_card = self.game.deck.draw()
                self.game.log(f"{player.name} 发动【八卦阵】，判定牌为 {judge_card.suit}{judge_card.rank}")
                self.game.deck.discard(judge_card)
                
                if judge_card.suit in ["♥", "♦"]:  # 红色
                    self.game.log(f"判定成功，视为使用了【闪】")
                    request.responded = True
                    self.pending_request = None
                    return True
                else:
                    self.game.log(f"判定失败")
                    # 继续执行下面的伤害结算
        
        if card_index is not None and 0 <= card_index < len(player.hand):
            card = player.hand[card_index]
            
            # 验证卡牌是否有效
            if self._validate_response_card(request, card):
                # 使用响应牌
                player.hand.remove(card)
                self.game.deck.discard(card)
                request.response_card = card
                request.responded = True
                
                self.game.log(f"{player.name} 使用了【{card.name}】进行响应")
                self.game.emit_event("response_used", request=request, card=card)
                
                self.pending_request = None
                return True
        
        # 不响应或响应无效
        request.responded = False
        self.game.log(f"{player.name} 没有响应")
        
        # 如果是被【杀】请求闪但未响应，则结算伤害
        if request.request_type == "dodge_slash":
            source = request.source_player
            target = request.target_player
            
            # 检查仁王盾：黑色杀无效
            has_renwang = any(hasattr(eq, 'name') and eq.name == "仁王盾" for eq in target.equip)
            damage_card = request.context.get("damage_card")
            if has_renwang and damage_card and damage_card.suit in ["♠", "♣"]:
                self.game.log(f"{target.name} 的【仁王盾】生效，黑色【杀】无效")
                self.pending_request = None
                return False
            
            target.hp -= 1
            self.game.log(f"{target.name} 受到1点伤害，剩余体力: {target.hp}")
            # 检查死亡
            self.game.check_death(target)
        
        self.pending_request = None
        return False
    
    def _validate_response_card(self, request, card):
        """验证响应牌是否有效"""
        from engine.cards.basic import Dodge, Peach, Slash
        
        if request.request_type == "dodge_slash":
            # 响应杀：需要闪
            return isinstance(card, Dodge)
        elif request.request_type == "bagua_judge":
            # 八卦阵判定：无需卡牌（由判定系统处理）
            return False
        elif request.request_type == "peach_dying":
            # 濒死求桃：需要桃
            return isinstance(card, Peach)
        elif request.request_type == "slash_duel":
            # 决斗响应：需要杀
            return isinstance(card, Slash)
        
        return False
    
    def _ai_auto_response(self, request):
        """AI自动响应逻辑"""
        from engine.cards.basic import Dodge, Peach, Slash
        
        player = request.target_player
        
        # 根据请求类型查找对应的响应牌
        response_card_index = None
        
        if request.request_type == "dodge_slash":
            # 检查是否装备八卦阵
            has_bagua = any(hasattr(eq, 'name') and eq.name == "八卦阵" for eq in player.equip)
            if has_bagua:
                # 八卦阵：进行判定，红色视为闪
                judge_card = self.game.deck.draw()
                self.game.log(f"{player.name} 发动【八卦阵】，判定牌为 {judge_card.suit}{judge_card.rank}")
                self.game.deck.discard(judge_card)
                
                if judge_card.suit in ["♥", "♦"]:  # 红色
                    self.game.log(f"判定成功，视为使用了【闪】")
                    request.responded = True
                    self.pending_request = None
                    return True
                else:
                    self.game.log(f"判定失败")
                    # 继续查找手牌中的闪
            
            # 查找闪
            for i, card in enumerate(player.hand):
                if isinstance(card, Dodge):
                    response_card_index = i
                    break
        
        elif request.request_type == "peach_dying":
            # 查找桃
            for i, card in enumerate(player.hand):
                if isinstance(card, Peach):
                    response_card_index = i
                    break
        
        elif request.request_type == "slash_duel":
            # 查找杀
            for i, card in enumerate(player.hand):
                if isinstance(card, Slash):
                    response_card_index = i
                    break
        
        # 处理AI响应
        if response_card_index is not None:
            card = player.hand.pop(response_card_index)
            self.game.deck.discard(card)
            request.response_card = card
            request.responded = True
            
            self.game.log(f"{player.name} 使用了【{card.name}】进行响应")
            self.game.emit_event("response_used", request=request, card=card)
            
            self.pending_request = None
            return True
        else:
            # 没有对应的响应牌
            request.responded = False
            self.game.log(f"{player.name} 没有响应")
            self.pending_request = None
            return False
    
    def cancel_pending_request(self):
        """取消当前待处理的响应请求"""
        if self.pending_request:
            self.pending_request.responded = False
            self.pending_request = None
