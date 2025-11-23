import random
from engine.cards.basic import Slash, Dodge, Peach
from engine.cards.trick import Dismantle, Snatch, ExNihilo, Duel
from engine.cards.equip import (
    ZhuGeLianNu, QingGangJian, ZhangBaSheMao,
    BaGuaZhen, RenWangDun,
    ChiTu, DaWan, ZiXing, ZhuaHuangFeiDian, JueYing, DiLu
)


class Deck:
    def __init__(self):
        self.cards = []
        self.discards = []

    def build_basic(self):
        """标准版基本牌：杀30、闪15、桃8"""
        suits = ["♠", "♥", "♣", "♦"]
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        
        cards = []
        # 杀 30张
        for i in range(30):
            cards.append(Slash(suits[i % 4], ranks[i % 13]))
        # 闪 15张
        for i in range(15):
            cards.append(Dodge(suits[i % 4], ranks[i % 13]))
        # 桃 8张
        for i in range(8):
            cards.append(Peach(suits[i % 4], ranks[i % 13]))
        
        self.cards = cards
        random.shuffle(self.cards)

    def build_standard(self):
        """标准版完整牌堆：基本牌53 + 锦囊35 + 装妇9"""
        self.build_basic()
        
        # 添加锦囊牌
        tricks = []
        # 过河拆桥 6张
        for i in range(6):
            tricks.append(Dismantle("♠" if i < 3 else "♣", str(i + 3)))
        # 顺手牵羊 5张
        for i in range(5):
            tricks.append(Snatch("♠" if i < 3 else "♦", str(i + 3)))
        # 无中生有 4张
        for i in range(4):
            tricks.append(ExNihilo("♥", str(i + 7)))
        # 决斗 3张
        for i in range(3):
            tricks.append(Duel("♠" if i < 2 else "♣", str(i + 1)))
        
        self.cards.extend(tricks)
        
        # 添加装备牌
        equips = []
        # 武器 3张
        equips.append(ZhuGeLianNu("♦", "A"))
        equips.append(QingGangJian("♠", "6"))
        equips.append(ZhangBaSheMao("♠", "12"))
        # 防具 2张
        equips.append(BaGuaZhen("♠", "2"))
        equips.append(RenWangDun("♣", "2"))
        # +1马 3张
        equips.append(ChiTu("♥", "5"))
        equips.append(DaWan("♠", "13"))
        equips.append(ZiXing("♦", "13"))
        # -1马 3张
        equips.append(ZhuaHuangFeiDian("♥", "13"))
        equips.append(JueYing("♠", "5"))
        equips.append(DiLu("♣", "5"))
        
        self.cards.extend(equips)
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            # 牌堆耗尽，洗入弃牌堆
            self.cards = self.discards
            self.discards = []
            random.shuffle(self.cards)
        return self.cards.pop()

    def discard(self, card):
        self.discards.append(card)
