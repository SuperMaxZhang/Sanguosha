"""装备牌系统：武器、防具、坐骑"""
from engine.cards.basic import Card


class EquipCard(Card):
    """装备牌基类"""
    def __init__(self, name: str, suit: str = "♠", rank: str = "A", equip_type: str = "weapon", description: str = ""):
        super().__init__(name, suit, rank)
        self.card_type = "equip"
        self.equip_type = equip_type  # weapon, armor, plus_horse, minus_horse
        self.description = description  # 装备能力说明
    
    def can_use(self, player, game):
        """装备牌总是可以使用"""
        return True
    
    def use(self, player, targets, game):
        """装备到玩家装备区"""
        # 检查是否已有同类型装备
        old_equip = None
        for eq in player.equip:
            if hasattr(eq, 'equip_type') and eq.equip_type == self.equip_type:
                old_equip = eq
                break
        
        # 替换旧装备
        if old_equip:
            player.equip.remove(old_equip)
            game.deck.discard(old_equip)
            game.log(f"{player.name} 替换了【{old_equip.name}】")
        
        # 从手牌中移除（注意：这里需要在Player.use_card中已经移除）
        # 装备到装备区（不进入弃牌堆，而是放入equip）
        player.equip.append(self)
        game.log(f"{player.name} 装备了【{self.name}】")


# ========== 武器牌 ==========

class ZhuGeLianNu(EquipCard):
    """诸葛连弩 - 攻击范围1，可无限次使用【杀】"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("诸葛连弩", suit, rank, "weapon", "攻击范围1，无限出杀")
        self.attack_range = 1


class QingGangJian(EquipCard):
    """青傕剑 - 攻击范围2，无视防具"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("青傕剑", suit, rank, "weapon", "攻击范围2，无视防具")
        self.attack_range = 2


class ZhangBaSheMao(EquipCard):
    """丈八蛇矛 - 攻击范围3"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("丈八蛇矛", suit, rank, "weapon", "攻击范围3")
        self.attack_range = 3


class GuanShiFu(EquipCard):
    """贯石斧 - 攻击范围3"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("贯石斧", suit, rank, "weapon")
        self.attack_range = 3


class FangTianHuaJi(EquipCard):
    """方天画戟 - 攻击范围4"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("方天画戟", suit, rank, "weapon")
        self.attack_range = 4


class QiLinGong(EquipCard):
    """麒麟弓 - 攻击范围5"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("麒麟弓", suit, rank, "weapon")
        self.attack_range = 5


# ========== 防具牌 ==========

class BaGuaZhen(EquipCard):
    """八卦阵 - 可以进行判定代替【闪】"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("八卦阵", suit, rank, "armor", "被杀时可判定，红色视为闪")


class RenWangDun(EquipCard):
    """仁王盾 - 黑色【杀】对你无效"""
    def __init__(self, suit="♠", rank="A"):
        super().__init__("仁王盾", suit, rank, "armor", "黑色杀无效")


# ========== 坐骑牌 ==========

class PlusHorse(EquipCard):
    """+1马 - 其他角色计算与你的距离+1"""
    def __init__(self, name: str, suit: str = "♠", rank: str = "A"):
        super().__init__(name, suit, rank, "plus_horse", "防御距离+1")


class MinusHorse(EquipCard):
    """-1马 - 你计算与其他角色的距离-1"""
    def __init__(self, name: str, suit: str = "♠", rank: str = "A"):
        super().__init__(name, suit, rank, "minus_horse", "攻击距离-1")


# 具体坐骑

class ChiTu(PlusHorse):
    """赤兔 +1马"""
    def __init__(self, suit="♥", rank="5"):
        super().__init__("赤兔", suit, rank)


class DaWan(PlusHorse):
    """大宛 +1马"""
    def __init__(self, suit="♠", rank="13"):
        super().__init__("大宛", suit, rank)


class ZiXing(PlusHorse):
    """紫骍 +1马"""
    def __init__(self, suit="♦", rank="13"):
        super().__init__("紫骍", suit, rank)


class ZhuaHuangFeiDian(MinusHorse):
    """爪黄飞电 -1马"""
    def __init__(self, suit="♥", rank="13"):
        super().__init__("爪黄飞电", suit, rank)


class JueYing(MinusHorse):
    """绝影 -1马"""
    def __init__(self, suit="♠", rank="5"):
        super().__init__("绝影", suit, rank)


class DiLu(MinusHorse):
    """的卢 -1马"""
    def __init__(self, suit="♣", rank="5"):
        super().__init__("的卢", suit, rank)
