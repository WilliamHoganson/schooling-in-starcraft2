from loguru import logger

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units


# pylint: disable=W0231
class ZealotPred(BotAI):

    def __init__(self):
        # Initialize inherited class
        self.proxy_built = False

    
    # pylint: disable=R0912
    async def on_step(self, iteration):
        if(self.units(UnitTypeId.ZEALOT).amount == 0):
            if(iteration<=1):
                print("making zealots")
                hatch: Unit = self.townhalls[0]
                p=Point2 = hatch.position.towards(self.game_info.map_center, 40)
                await self._client.debug_create_unit([[UnitTypeId.ZEALOT, 4, p, 1]])
        if self.units(UnitTypeId.ZEALOT).amount >= 1:
            for zealot in self.units(UnitTypeId.ZEALOT).ready.idle:
                targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                if targets:
                    target = targets.closest_to(zealot)
                    zealot.attack(target)
                else:
                    zealot.attack(self.enemy_start_locations[0].towards(self.game_info.map_center,40))
        if(self.units(UnitTypeId.ZEALOT).amount == 0):
            if(iteration>1):
                print(iteration)
                await self.client.leave()
def main():
    run_game(
        maps.get("AcropolisLE"),
        [Bot(Race.Protoss, ZealotPred()), Computer(Race.Protoss, Difficulty.Easy)],
        realtime=False,
    )


if __name__ == "__main__":
    main()
