class Hero:
    """武将基类"""
    def __init__(self, name: str, force: str, hp: int, skills=None):
        self.name = name
        self.force = force  # 势力：wei, shu, wu, qun
        self.hp = hp
        self.skills = skills or []
    
    def __repr__(self):
        return f"<Hero {self.name} {self.force} HP:{self.hp}>"


class Skill:
    """技能基类"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def can_trigger(self, player, game, event_name, **kwargs):
        """是否可以触发"""
        return False
    
    def trigger(self, player, game, **kwargs):
        """触发技能效果"""
        pass


# ========== 武将技能实现 ==========

class JianXiong(Skill):
    """奸雄（曹操）：当你受到伤害后，你可以获得对你造成伤害的牌"""
    def __init__(self):
        super().__init__(" 奸雄", "当你受到伤害后，获得造成伤害的牌")
    
    def can_trigger(self, player, game, event_name, **kwargs):
        return event_name == "damage_taken"
    
    def trigger(self, player, game, **kwargs):
        damage_card = kwargs.get('damage_card')
        if damage_card:
            player.hand.append(damage_card)
            game.log(f"{player.name} 发动【奸雄】，获得了造成伤害的牌")


class PaoXiao(Skill):
    """哆哮（张飞）：出牌阶段，你使用【杀】无次数限制"""
    def __init__(self):
        super().__init__("哆哮", "出牌阶段，你使用【杀】无次数限制")
    
    def can_trigger(self, player, game, event_name, **kwargs):
        return event_name == "check_slash_limit"
    
    def trigger(self, player, game, **kwargs):
        # 哆哮：移除杀的次数限制
        return True  # 返回true表示可以使用


class LongDan(Skill):
    """龙胆（赵云）：你可以将【杀】当【闪】、【闪】当【杀】使用或打出"""
    def __init__(self):
        super().__init__(" 龙胆", "你可以将【杀】当【闪】、【闪】当【杀】使用")


class GuanXing(Skill):
    """观星（诸葛亮）：准备阶段，你可以观看牌堆顶的X张牌"""
    def __init__(self):
        super().__init__("观星", "准备阶段，观看牌堆顶的牌")


class QingNang(Skill):
    """青囊（华佗）：出牌阶段，你可以弃置一张手牌，令一名角色回复1点体力"""
    def __init__(self):
        super().__init__(" 青囊", "弃置一张手牌，令一名角色回复1点体力")


class WuShuang(Skill):
    """无双（吕布）：锁定技，当你使用【杀】指定一名角色为目标后，该角色需依次使用两张【闪】才能抵消"""
    def __init__(self):
        super().__init__("无双", "使用【杀】时，目标需出两张【闪】")


# ========== 标准版武将 ==========

class CaoCao(Hero):
    """曹操 - 奸雄"""
    def __init__(self):
        skills = [JianXiong()]
        super().__init__(" 曹操", "wei", 4, skills)


class LiuBei(Hero):
    """刘备 - 仁德"""
    def __init__(self):
        super().__init__("刘备", "shu", 4)


class SunQuan(Hero):
    """孙权 - 制衡"""
    def __init__(self):
        super().__init__("孙权", "wu", 4)


class GuanYu(Hero):
    """关羽 - 武圣"""
    def __init__(self):
        super().__init__("关羽", "shu", 4)


class ZhangFei(Hero):
    """张飞 - 哆哮"""
    def __init__(self):
        skills = [PaoXiao()]
        super().__init__(" 张飞", "shu", 4, skills)


class ZhaoYun(Hero):
    """赵云 - 龙胆"""
    def __init__(self):
        skills = [LongDan()]
        super().__init__(" 赵云", "shu", 4, skills)


class ZhugeLiang(Hero):
    """诸葛亮 - 观星、空城"""
    def __init__(self):
        skills = [GuanXing()]
        super().__init__(" 诸葛亮", "shu", 3, skills)


class HuaTuo(Hero):
    """华佗 - 急救、青囊"""
    def __init__(self):
        skills = [QingNang()]
        super().__init__(" 华佗", "qun", 3, skills)


class LvBu(Hero):
    """吕布 - 无双"""
    def __init__(self):
        skills = [WuShuang()]
        super().__init__(" 吕布", "qun", 4, skills)


# 可选武将列表
STANDARD_HEROES = [
    CaoCao, LiuBei, SunQuan, GuanYu, ZhangFei, 
    ZhaoYun, ZhugeLiang, HuaTuo, LvBu
]


def get_random_heroes(n=4):
    """随机获取n个武将"""
    import random
    hero_classes = random.sample(STANDARD_HEROES, min(n, len(STANDARD_HEROES)))
    return [cls() for cls in hero_classes]
