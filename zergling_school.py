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
class ZergSchoolBot(BotAI):

    def __init__(self):
        self.on_end_called = False
        #set coefficients and number of zerglings
        self.kcoh=2
        self.kall=1
        self.num_lings=26

    async def on_start(self):
        self.client.game_step = 2
    #gets the school together and away from base for testing (unused)
    async def school(self, iteration):
        
        hatch: Unit = self.townhalls[0]
        p=Point2 = hatch.position.towards(self.game_info.map_center, 50)
        for zergling in self.units(UnitTypeId.ZERGLING):
            zergling.move(p)
    #implementing boids algorithm variation
    async def flock(self, iteration):
        count=0
        #go through each zergling in the flock
        for zergling in self.units(UnitTypeId.ZERGLING):
            count=count+1
        #report zergling deaths
        if (count<self.num_lings):
            print("number of zerglings killed:")
            print(self.num_lings-count)
        #for each zergling in the flock
        for zergling in self.units(UnitTypeId.ZERGLING):
            neighbors_attacking=0
            #list of enemy zealots
            enemy_zealots= self.enemy_units(UnitTypeId.ZEALOT)
            #list of friendly zerglings
            my_zerglings = self.units(UnitTypeId.ZERGLING)
            #find neighboring friendly zerglings within distance d
            d=3
            close_zerglings = my_zerglings.closer_than(d, zergling)
            #current position and orientation
            pos=zergling.position
            orientation=zergling.facing
            #make empty sums
            cohesionsum=pos
            cohesionsum=cohesionsum-pos
            alignmentsum=orientation
            alignmentsum=alignmentsum-orientation
            collisionsum=cohesionsum
            num_neighbors=0
            enemy=False
            damaged=False
            #check for zergling damage
            if (zergling.health< zergling.health_max*.6):
                damaged=True
            attacking=False
          
            #for each neighbor
            for neighbor in close_zerglings:
                #see how many are attacking
                if neighbor.is_attacking:
                    neighbors_attacking=neighbors_attacking+1
                num_neighbors=num_neighbors+1
                #get neighbor position and neighbor velocity
                neighbor_pos=neighbor.position
                neighbor_orientation= neighbor.facing
                #incrememnt sums
                cohesionsum=cohesionsum+(neighbor_pos-pos)
                alignmentsum=alignmentsum+(neighbor_orientation-orientation)
                collisionsum=collisionsum+(pos-neighbor_pos)
             #get position of nearest zealot
            if len(enemy_zealots)>=1:
                closest_zealot=pos.closest(enemy_zealots)
                close_zealots=enemy_zealots.closer_than(3,zergling)
                if len(close_zealots)>=1:
                    enemy=True
                    zealot_pos=closest_zealot.position
                    dist_to_z=zergling.distance_to(zealot_pos)
                    #check how close the zealot is, and whether the zergling is damaged. If not damaged, and zealot is close, attack
                    if(dist_to_z<1.5 and damaged==False):
                        targets=(self.enemy_units.filter(lambda unit: unit.can_be_attacked))
                        target=targets.closest_to(zergling)
                        zergling.attack(target)
                        attacking=True
                    #if two neighbors minimum are attacking and zergling is undamaged, also attack
                    if (neighbors_attacking>2) and (damaged == False):
                        targets=(self.enemy_units.filter(lambda unit: unit.can_be_attacked))
                        target=targets.closest_to(zergling)
                        zergling.attack(target)
                        attacking=True
                        
            #get average cohesion point tomove towards
            avg_from_cohesion=Point2=pos+np.array([cohesionsum[0]/num_neighbors,cohesionsum[1]/num_neighbors])-pos
            cohesion_point=Point2= pos.towards(avg_from_cohesion,1,False)
            #get average alignment point to move towards
            alighnmentsum=alignmentsum/num_neighbors
            temp_alignment_point=Point2= pos+np.array([np.cos(alignmentsum),np.sin(alignmentsum)])
            alignment_point=Point2=pos.towards(temp_alignment_point,1,False)
            #get point we want the swarm to stay near
            hatch: Unit = self.townhalls[0]
            p=Point2 = hatch.position.towards(self.game_info.map_center, 50)
            to_p=Point2=pos.towards(p,3,False)
            #dist from the point we wish to stay at
            dist_from_p=zergling.distance_to(p)
            #coefficient for staying nearby
            stay_coeff=2+dist_from_p/4
            #coefficient for fearing enemies
            fear_coeff=.05
            #check for damage and increase fear if damaged
            if damaged==True:
                damaged_percent=(1-zergling.health/zergling.health_max)*2
                fear_coeff=fear_coeff+damaged_percent
            n=self.kall+self.kcoh+stay_coeff
            if(attacking==False) or damaged ==True:
                #check for enemies
                if(enemy==True):
                    #point to run towards
                    run_pt=Point2=pos.towards(zealot_pos,-1,False)
                    n=n+fear_coeff
                    final_point=Point2=pos+np.array([(self.kcoh*cohesion_point[0]+self.kall*alignment_point[0]+stay_coeff*to_p[0] + fear_coeff*run_pt[0])/n,(self.kcoh*cohesion_point[1]+self.kall*alignment_point[1]+stay_coeff*to_p[1]+run_pt[1])/(n)])-pos
                else:
                    final_point=Point2=pos+np.array([(self.kcoh*cohesion_point[0]+self.kall*alignment_point[0]+stay_coeff*to_p[0])/n,(self.kcoh*cohesion_point[1]+self.kall*alignment_point[1]+stay_coeff*to_p[1])/(n)])-pos
                super_final_point=pos.towards((final_point),1,False)
            
                zergling.move(super_final_point)
            
                

    #on start of game
    async def start(self, iteration):
        if(self.units(UnitTypeId.ZERGLING).amount == 0):
            if(iteration<=1):
                print("making zerglings")
                hatch: Unit = self.townhalls[0]
                #spawn num_lings number of zerglings and begin schooling
                p=Point2 = hatch.position.towards(self.game_info.map_center, 50)
                await self._client.debug_create_unit([[UnitTypeId.ZERGLING, self.num_lings, p, 2]])
            #if we run out of zerglings, surrender and report the time
            else:
                if (iteration>=550):
                    print(iteration)
                    await self.client.leave()
        else:
            await self.flock(iteration)

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
        
        [Human(Race.Protoss),Bot(Race.Zerg, ZergSchoolBot())], # runs a pre-made computer agent, zerg race, with a hard difficulty.
        realtime=True,
        save_replay_as="Pvz.SC2Replay",
    )


if __name__ == "__main__":
    main()
