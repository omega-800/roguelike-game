from turtle import position
from xml.sax.handler import EntityResolver
from ursina import *
from random import Random
from ursina.hit_info import HitInfo

app = Ursina()
random = Random()

window.borderless = False
window.color = color.smoke
camera.orthographic = True
camera.fov = 10



#roomNr = 5
#roomX = 10
#roomY = 3

#ground = Entity(model='cube', scale_x=roomX, scale_y=roomY, scale_z=10, collider='box', color=color.black, origin_y=-1)

class Bullet(Entity):
    
    def __init__(self, **kwargs):
        super().__init__()
        self.model='cube'
        self.scale=.1
        self.color=color.black
        self.collider='box'
        self.damage = 1
        self.speed = 6
    
    def update(self):
        global player
      
        self.direction = player.direction.normalized()

        origin = self.world_position + (self.up*.5)
        hit_info = raycast(origin, self.direction, ignore=(self,player), distance=.52, debug=True)
        
        if not hit_info.hit:
            self.position += self.direction * self.speed * time.dt
   
class Player(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.model='cube'
        self.collider = 'box'
        self.texture='player'   
        self.health = 4
        self.damage = 1
        self.speed = 5

    def input(self, key):
        if key == 'q':
            self.speed += .1
        if key == 'e':
            bullet = Entity()                             
            bullet.animate_position(player.world_position+(bullet.up*500), duration=2)
            destroy(bullet, delay=2)  

    def update(self):
        self.direction = Vec3(
            self.up * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        origin = self.world_position + (self.up*.5)
        hit_info = raycast(origin, self.direction, ignore=(self,), distance=.52, debug=False)

        if not hit_info.hit:
            self.position += self.direction * self.speed * time.dt
            self.color=color.green
        else:
            #if hit_info.entity == enemy:
            #    health -= 1
            self.color=color.red                                                                                                                                                          

player = Player()
camera.add_script(SmoothFollow(target=player, offset=[0,0,-10], speed=10))
   
class Enemy(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.model='cube'
        self.collider = 'box'
        self.texture='enemy'
        
    health = 1
    damage = 1
    speed = 2

    def update(self):
        if(self.health > 0):
            self.direction = (player.position - self.position).normalized()

            origin = self.world_position + (self.up*.5)
            hit_info = raycast(origin, self.direction, ignore=(self,), distance=.52, debug=True)

            if not hit_info.hit:
                self.position += self.direction * self.speed * time.dt
    

quad = load_model('quad', use_deepcopy=True)

level_parent = Entity(model=Mesh(vertices=[], uvs=[]), texture='brick')
def make_level(texture):
    # destroy every child of the level parent.
    # This doesn't do anything the first time the level is generated, but if we want to update it several times
    # this will ensure it doesn't just create a bunch of overlapping entities.
    [destroy(c) for c in level_parent.children]

    for y in range(texture.height):
        collider = None
        for x in range(texture.width):
            col = texture.get_pixel(x,y)

            # If it's black, it's solid, so we'll place a tile there.
            if col == color.black:
                level_parent.model.vertices += [Vec3(*e) + Vec3(x+.5,y+.5,0) for e in quad.generated_vertices] # copy the quad model, but offset it with Vec3(x+.5,y+.5,0)
                level_parent.model.uvs += quad.uvs
                # Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), color=color.gray, texture='white_cube', visible=True)
                if not collider:
                    collider = Entity(parent=level_parent, position=(x,y), model='quad', origin=(-.5,-.5), collider='box', visible=False)
                else:
                    # instead of creating a new collider per tile, stretch the previous collider right.
                    collider.scale_x += 1
            else:
                collider = None

            # If it's green, we'll place the player there. Store this in player.start_position so we can reset the plater position later.
            if col == color.green:
                player.start_position = (x, y)
                player.position = player.start_position
            
            if col == color.red:
                enemy = Enemy()
                enemy.start_position = (x, y)
                enemy.position = enemy.start_position

    level_parent.model.generate()

make_level(load_texture('level_texture'))   # generate the level

def update():
    
    if(held_keys['x']):
        #ground.color = color.random_color()
        player.color = color.random_color()
        window.color = color.random_color()


app.run()