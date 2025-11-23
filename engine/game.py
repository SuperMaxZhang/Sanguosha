from engine.deck import Deck
from engine.player import Player
from engine.events import EventBus
from engine.hero import get_random_heroes
from engine.ai import AIController
from engine.response import ResponseSystem


def get_role_config(player_count):
    """获取不同人数的身份配置"""
    configs = {
        2: ["lord", "rebel"],  # 1主 + 1反
        3: ["lord", "loyalist", "rebel"],  # 1主 + 1忠 + 1反
        4: ["lord", "loyalist", "rebel", "rebel"],  # 1主 + 1忠 + 2反
        5: ["lord", "loyalist", "rebel", "rebel", "traitor"],  # 1主 + 1忠 + 2反 + 1内
        6: ["lord", "loyalist", "rebel", "rebel", "rebel", "traitor"],  # 1主 + 1忠 + 3反 + 1内
        7: ["lord", "loyalist", "loyalist", "rebel", "rebel", "rebel", "traitor"],  # 1主 + 2忠 + 3反 + 1内
        8: ["lord", "loyalist", "loyalist", "rebel", "rebel", "rebel", "rebel", "traitor"],  # 1主 + 2忠 + 4反 + 1内
    }
    return configs.get(player_count, configs[4])


class Game:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.deck.build_standard()  # 使用完整牌堆
        self.turn_index = 0
        self.current_player = self.players[self.turn_index]
        self.event_bus = EventBus()
        self.phase = "idle"  # idle, prepare, judge, draw, play, discard
        self.log_callback = None  # UI日志回调
        
        # AI控制器
        self.ai_controllers = {}
        for player in self.players:
            if player.is_ai:
                self.ai_controllers[player] = AIController(player, self)
        
        # 响应系统
        self.response_system = ResponseSystem(self)
        
        # 发初始手牌
        for p in self.players:
            p.draw(self.deck, 4)
        
        # 第一个回合开始
        self.start_turn()
    
    def set_log_callback(self, callback):
        """设置UI日志回调函数"""
        self.log_callback = callback
    
    def log(self, message):
        """记录日志，同时输出到终端和UI"""
        print(message)
        if self.log_callback:
            self.log_callback(message)

    def emit_event(self, event_name, **kwargs):
        """发送事件"""
        self.event_bus.emit(event_name, game=self, **kwargs)

    def start_turn(self):
        """开始一个新回合（准备-判定-摘牌-出牌-弃牌）"""
        self.log(f"\n===== {self.current_player.name} 的回合 =====")
        
        # 1. 准备阶段
        self.phase = "prepare"
        self.log(f"[准备阶段]")
        self.emit_event("prepare_phase", player=self.current_player)
        # TODO: 触发观星等准备阶段技能
        
        # 2. 判定阶段
        self.phase = "judge"
        self.log(f"[判定阶段]")
        self.emit_event("judge_phase", player=self.current_player)
        # TODO: 处理延时锦囊（乐不思蜀、闪电等）
        
        # 3. 摘牌阶段
        self.phase = "draw"
        self.log(f"[摘牌阶段]")
        self.current_player.draw(self.deck, 2)
        self.log(f"{self.current_player.name} 摘了2张牌")
        self.emit_event("draw_phase", player=self.current_player)
        
        # 4. 出牌阶段
        self.phase = "play"
        self.log(f"[出牌阶段]")
        self.emit_event("play_phase", player=self.current_player)
        
        # 如果是AI玩家，自动执行
        if self.current_player.is_ai:
            self.ai_play_turn()

    def use_card(self, card_index, target_indices=None):
        """当前玩家使用手牌"""
        if card_index < 0 or card_index >= len(self.current_player.hand):
            return False
        
        card = self.current_player.hand[card_index]
        targets = []
        if target_indices:
            for idx in target_indices:
                if 0 <= idx < len(self.players):
                    targets.append(self.players[idx])
        
        return self.current_player.use_card(card, targets, self)

    def next_turn(self):
        """结束当前回合，进入下一个玩家的回合"""
        # 弃牌阶段：手牌数不能超过体力值
        discard_count = len(self.current_player.hand) - self.current_player.hp
        if discard_count > 0:
            self.log(f"{self.current_player.name} 需要弃置 {discard_count} 张牌")
            
            if self.current_player.is_ai:
                # AI自动弃牌：弃置最后的牌
                discarded_cards = []
                for _ in range(discard_count):
                    if len(self.current_player.hand) > 0:
                        card = self.current_player.hand.pop()
                        self.deck.discard(card)
                        discarded_cards.append(card.name)
                self.log(f"{self.current_player.name} 弃置了：{', '.join(discarded_cards)}")
            else:
                # 玩家需要选择弃牌，触发事件
                self.emit_event("discard_phase", player=self.current_player, count=discard_count)
                # 注意：UI会处理这个事件，不在这里自动弃牌
                return  # 等待UI处理完毕后调用finish_turn
        
        # 如果不需要弃牌，直接结束回合
        self.finish_turn()
    
    def finish_turn(self):
        """完成回合结束，切换到下一个玩家"""
        # 检查玩家是否死亡
        if self.current_player.hp <= 0:
            self.current_player.is_alive = False
            self.log(f">>> {self.current_player.name} 阵亡了！<<<")
        
        # 重置回合状态
        self.current_player.reset_turn()
        
        # 切换玩家
        self.turn_index = (self.turn_index + 1) % len(self.players)
        self.current_player = self.players[self.turn_index]
        
        # 跳过已死亡的玩家
        attempts = 0
        while not self.current_player.is_alive and attempts < len(self.players):
            self.turn_index = (self.turn_index + 1) % len(self.players)
            self.current_player = self.players[self.turn_index]
            attempts += 1
        
        # 检查游戏是否结束
        alive_players = self.get_alive_players()
        if len(alive_players) <= 1:
            if len(alive_players) == 1:
                self.log(f"\n\n★★★ 游戏结束！{alive_players[0].name} 获胜！★★★")
            else:
                self.log(f"\n\n游戏结束！")
            self.phase = "game_over"
            return
        
        self.phase = "idle"
        
        # 开始新回合
        self.start_turn()
    
    def discard_cards(self, card_indices):
        """弃置指定的牌（由UI调用）"""
        # 按索引从大到小排序，避免删除时索引错乱
        card_indices = sorted(card_indices, reverse=True)
        discarded_cards = []
        
        for idx in card_indices:
            if 0 <= idx < len(self.current_player.hand):
                card = self.current_player.hand.pop(idx)
                self.deck.discard(card)
                discarded_cards.append(card.name)
        
        if discarded_cards:
            self.log(f"{self.current_player.name} 弃置了：{', '.join(discarded_cards)}")
        
        # 继续完成回合
        self.finish_turn()
    
    def distance(self, a: Player, b: Player):
        """距离计算：环形最短距离 + 装备修正（+1马、-1马）"""
        try:
            n = len(self.players)
            ia = next(i for i, p in enumerate(self.players) if p is a)
            ib = next(i for i, p in enumerate(self.players) if p is b)
            d = abs(ia - ib)
            base_dist = min(d, n - d)
            
            # 装备修正
            # a的-1马：计算与a的距离-1
            for eq in a.equip:
                if hasattr(eq, 'equip_type') and eq.equip_type == "minus_horse":
                    base_dist -= 1
                    break
            
            # b的+1马：计算与b的距离+1
            for eq in b.equip:
                if hasattr(eq, 'equip_type') and eq.equip_type == "plus_horse":
                    base_dist += 1
                    break
            
            return max(1, base_dist)  # 距离最小为1
        except StopIteration:
            return 999
    def ai_play_turn(self):
        """执行AI回合"""
        ai = self.ai_controllers.get(self.current_player)
        if ai:
            ai.play_turn()
    
    def get_alive_players(self):
        """获取所有存活的玩家"""
        return [p for p in self.players if p.is_alive]
    
    def check_game_over(self):
        """检查游戏是否结束，返回获胜方"""
        alive_players = self.get_alive_players()
        
        # 没有活人了
        if len(alive_players) == 0:
            return "draw"  # 平局
        
        # 只剩1个人
        if len(alive_players) == 1:
            return alive_players[0].role
        
        # 检查各身份是否还活着
        lord_alive = any(p.is_alive and p.role == "lord" for p in self.players)
        rebels_alive = any(p.is_alive and p.role == "rebel" for p in self.players)
        
        # 主公死了
        if not lord_alive:
            # 如果还有反贼，反贼胜
            if rebels_alive:
                return "rebel"
            # 如果只剩内奸，内奸胜
            return "traitor"
        
        # 主公活着，反贼全灭
        if not rebels_alive:
            # 如果还有内奸，继续游戏
            traitors_alive = any(p.is_alive and p.role == "traitor" for p in self.players)
            if traitors_alive:
                return None  # 游戏继续
            # 反贼全灭且无内奸，主忠胜
            return "lord"
        
        # 游戏继续
        return None
    
    def announce_winner(self, winner_role):
        """宣布获胜者"""
        role_names = {
            "lord": "主公和忠臣",
            "loyalist": "主公和忠臣",
            "rebel": "反贼",
            "traitor": "内奸",
            "draw": "无人"
        }
        
        winner_name = role_names.get(winner_role, "未知")
        
        if winner_role == "draw":
            self.log(f"\n\n★★★ 游戏结束！平局！★★★")
        else:
            self.log(f"\n\n★★★ 游戏结束！{winner_name}获胜！★★★")
            
            # 显示获胜玩家
            winners = [p for p in self.players if p.is_alive and (p.role == winner_role or (winner_role == "lord" and p.role == "loyalist"))]
            if winners:
                winner_list = ", ".join([p.name for p in winners])
                self.log(f"获胜玩家：{winner_list}")
        
        self.phase = "game_over"
    
    def check_death(self, player):
        """检查玩家是否死亡，立即处理"""
        if player.hp <= 0 and player.is_alive:
            # TODO: 这里应该让玩家选择是否使用桃，简化为自动使用
            # 检查是否有桃
            from engine.cards.basic import Peach
            peach_index = None
            for i, card in enumerate(player.hand):
                if isinstance(card, Peach):
                    peach_index = i
                    break
            
            if peach_index is not None:
                # 自动使用桃
                self.log(f"{player.name} 体力归零，自动使用【桃】救命！")
                peach = player.hand.pop(peach_index)
                player.hp = min(player.hp + 1, player.max_hp)
                self.deck.discard(peach)
            else:
                # 死亡
                player.is_alive = False
                self.log(f">>> {player.name} 阵亡了！<<<")
                
                # 检查游戏是否结束
                winner_role = self.check_game_over()
                if winner_role is not None:
                    self.announce_winner(winner_role)


def setup_demo_game():
    """4人局：1个玩家 + 3个AI"""
    heroes = get_random_heroes(4)
    players = [
        Player(f"{heroes[0].name}", heroes[0].hp, heroes[0], is_ai=False),  # 玩家
        Player(f"{heroes[1].name}", heroes[1].hp, heroes[1], is_ai=True),   # AI
        Player(f"{heroes[2].name}", heroes[2].hp, heroes[2], is_ai=True),   # AI
        Player(f"{heroes[3].name}", heroes[3].hp, heroes[3], is_ai=True),   # AI
    ]
    return Game(players)
