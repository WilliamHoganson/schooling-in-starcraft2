from cProfile import run
import numpy as np
from loguru import logger

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race, Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer, Human
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units


# pylint: disable=W0231
class ZergControl(BotAI):

    def __init__(self):
        self.on_end_called = False
        self.kcoh=1
        self.kall=1
        self.num_lings=26

    async def on_start(self):
        self.client.game_step = 2


    async def start(self, iteration):
        if(self.units(UnitTypeId.ZERGLING).amount == 0):
            if(iteration<=1):
                print("making zerglings")
                
                hatch: Unit = self.townhalls[0]
                p=Point2 = hatch.position.towards(self.game_info.map_center, 50)
                await self._client.debug_create_unit([[UnitTypeId.ZERGLING, self.num_lings, p, 2]])
        count=0
        for zergling in self.units(UnitTypeId.ZERGLING):
            count=count+1
        if (count<self.num_lings):
            print("number of zerglings killed:")
            print(self.num_lings-count)
                

    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("(glhf)")
        else:
            await self.start(iteration)
   
        

    async def on_end(self, game_result: Result):
        
        self.on_end_called = True
        logger.info(f"{self.time_formatted} On end was called")


def main():
    run_game(
        maps.get("AcropolisLE"),
        #[Bot(Race.Zerg, ZergRushBot()), Human(Race.Protoss)],
        
        [Human(Race.Protoss),Bot(Race.Zerg, ZergControl())], # runs a pre-made computer agent, zerg race, with a hard difficulty.
        realtime=True,
        save_replay_as="Pvz.SC2Replay",
    )


if __name__ == "__main__":
    main()
