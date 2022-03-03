import pygame as pg

class Tree(pg.sprite.Sprite):
    
    def __init__(self, init_x: int, init_y: int):
        
        super().__init__()

        self.size = self.width, self.height = 5, 5
        self.x, self.y = init_x, init_y
        self.pos = [self.x, self.y]

        self.rect = pg.Rect((0, 0), self.size)
        self.rect.center = self.pos