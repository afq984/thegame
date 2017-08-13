from thegame import Client, Ability


class IClient(Client):
    def action(self, hero, polygons, heroes, bullets):
        print("I'm", hero)
        print(
            f'level: {hero.level}',
            f'experience: {hero.experience}/{hero.experience_to_level_up}'
        )
        print("I'm surrounded by these polygons:", polygons)
        print("I'm surrounded by these heroes:", heroes)
        print("I'm surrounded by these bullets:", bullets)
        print('-' * 79)
        if polygons:
            self.shoot_at(*polygons[0].position)


IClient.main()
