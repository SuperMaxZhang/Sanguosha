#!/usr/bin/env python3
"""测试游戏引擎核心功能"""

from engine.game import setup_demo_game
from engine.cards.basic import Slash, Peach
from engine.cards.trick import Dismantle

def test_game():
    print("=" * 50)
    print("测试三国杀游戏引擎")
    print("=" * 50)
    
    # 创建游戏
    game = setup_demo_game()
    print(f"\n游戏初始化成功，共 {len(game.players)} 名玩家")
    
    for i, p in enumerate(game.players):
        print(f"{i+1}. {p}")
    
    # 测试摸牌
    print(f"\n当前玩家: {game.current_player.name}")
    print(f"手牌数: {len(game.current_player.hand)}")
    print("手牌:", [str(c) for c in game.current_player.hand])
    
    # 测试出牌
    if game.current_player.hand:
        card = game.current_player.hand[0]
        print(f"\n尝试使用第一张牌: {card}")
        
        if isinstance(card, Slash):
            # 杀需要目标
            other_players = [p for p in game.players if p != game.current_player]
            if other_players:
                print(f"对 {other_players[0].name} 使用")
                game.use_card(0, [1])
        elif isinstance(card, Peach):
            # 桃
            if game.current_player.hp < game.current_player.max_hp:
                game.use_card(0, [])
        else:
            # 其他牌
            game.use_card(0, [1])
    
    # 测试回合切换
    print("\n切换到下一回合...")
    game.next_turn()
    print(f"当前玩家: {game.current_player.name}")
    print(f"手牌数: {len(game.current_player.hand)}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    test_game()
