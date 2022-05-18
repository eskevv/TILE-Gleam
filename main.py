import pygame, sys, random
import tgl

class Collidable(pygame.Rect):
   def __init__(self, type_block: str, rect: pygame.Rect):
      self.collision_type = type_block
      self.x = rect.x
      self.y = rect.y
      self.w = rect.w
      self.h = rect.h

class GameTile:
   def __init__(self, tile: tgl.Tile):
      self.rect = pygame.Rect(tile.rect)
      self.image = tmx_images[tile.img_id]
      self.offset_x = self.get_offsets()
      self.x_pos = tile.pos[0] + self.offset_x
      self.y_pos = tile.pos[1]
      self.layer_name = tile.layer_name
      self.layer_order = tile.layer_order

      self.frame_data = tile.frame_data
      self.max_frame = self.frame_setup()
      self.frame_index = 0
      self.frame_time = 0

   def get_offsets(self):
      if (tile.layer_name== 'coins'):
         return 10
      return 0

   def frame_setup(self):
      if self.frame_data != None:
         return len(self.frame_data) - 1
      return 0

   def update(self, time):
      if self.frame_data != None:
         self.animate(time)

   def animate(self, time, ):
      frame = self.frame_data[self.frame_index]
      frame_img = frame[0]
      frame_duration = frame[1]
      self.image = tmx_images[frame_img]

      self.frame_time += time
      if self.frame_time >= frame_duration:
         self.frame_time = 0
         self.frame_index += 1
         if self.frame_index > self.max_frame:
            self.frame_index = 0

class Cloud(GameTile):
   def __init__(self, tile : tgl.Tile):
      super().__init__(tile)
      self.type = tile.img_id
      self.width = tmx_images[self.type].get_width()
      self.height = tmx_images[self.type].get_height()
      self.speed = self.get_speed()
      self.y_pos += random.randint (-300, 300)


   def get_speed(self):
      if self.type == '1.png':
         return random.randint(2, 3) * 0.1
      return random.randint(1, 1) * 0.3

   def update(self, time):
      super().update(time)

      self.x_pos += self.speed
      
      if self.x_pos > 3900:
         self.x_pos = 0 - (self.width + random.randint(200, 1000))
         self.y_pos = self.y_pos + random.randint(-1, 1)
         if self.y_pos > SCREEN[1] / 2:
            self.y_pos -= self.height
         if self.y_pos < -self.height + 100:
            self.y_pos += 50

class Entity():
   def __init__(self, pos: tuple[int, int]) -> None:
      self.x_pos = pos[0]
      self.y_pos = pos[1]
      self.on_ground = False
      self.on_ceiling = False
      self.collider = None

      self.image = None
      self.image_direction = 'Right'
      self.flipped = False
      self.frame_time = 0
      self.frame_index = 0
      self.frame_duration = 0
      self.max_frame = 0
      self.repeat = True

      self.current_action = None
      self.collider_offsets = None
      self.delta_speed = [0, 0]
      self.speed = [0, 0]
      self.turn_around = False

      # const properties
      self.GRAVITY = 7
      self.MAX_DX = 2

   def set_action(self, action):
      if self.current_action != action:
         self.current_action = action
         self.frame_index = 0
         self.image = image_database[action][0]
         self.max_frame = len(image_database[action]) - 1
         self.frame_time = 0

   def get_collider(self):
      x = self.x_pos - self.collider_offsets[0]
      y = self.y_pos - self.collider_offsets[1]
      w = self.image.get_width() + self.collider_offsets[0]
      h = self.image.get_height() + self.collider_offsets[1]
      return pygame.Rect(x, y, w, h)

   def check_colliding(self, types: list[str]):
      self.collider.x += self.delta_speed[0]
      for type_of in types:
         for block in collisions:
            if type_of == block.collision_type:
               if self.collider.colliderect(block):
                  if self.delta_speed[0] > 0:
                     self.collider.right = block.left
                  elif self.delta_speed[0] < 0:
                     self.collider.left = block.right
                  if self.turn_around:
                     self.speed[0] = -self.speed[0]
                  self.delta_speed[0] = 0
      
      self.collider.y += self.delta_speed[1]
      for type_of in types:
         for block in collisions:
            if type_of == block.collision_type:
               if self.collider.colliderect(block):
                  if self.delta_speed[1] > 0:
                     self.collider.bottom = block.top
                     self.on_ground = True
                  if self.delta_speed[1] < 0:
                     self.collider.top = block.bottom
                     self.on_ceiling = True
                  self.delta_speed[1] = 0

      if self.on_ground and self.delta_speed[1] < 0 or self.delta_speed[1] >= 1:
         self.on_ground = False
      if self.on_ceiling and self.delta_speed[1] > self.speed[1]:
         self.on_ceiling = False

   def animate(self, time) -> None:
      self.image = image_database[self.current_action][self.frame_index]
      if self.flipped == True:
         self.image = pygame.transform.flip(self.image, True, False)

      self.frame_time += time
      if self.frame_time >= animation_durations[self.current_action][self.frame_index]:
         self.frame_time = 0
         self.frame_index += 1
         if self.frame_index > self.max_frame:
            if self.repeat:
               self.frame_index = 0
            else:
               self.frame_index -= 1
   
   def move_collider(self):
      self.delta_speed[0] += self.speed[0]
      self.delta_speed[1] += self.speed[1]

      if self.delta_speed[1] > self.GRAVITY:
         self.delta_speed[1] = self.GRAVITY
      if self.delta_speed[0] > self.MAX_DX:
         self.delta_speed[0] = self.MAX_DX
      if self.delta_speed[0] < -self.MAX_DX:
         self.delta_speed[0] = -self.MAX_DX
      
      if self.delta_speed[0] > 0 and self.image_direction == 'left':
         self.flipped = True
      elif self.delta_speed[0] > 0 and self.image_direction == 'right':
         self.flipped = False
      elif self.delta_speed[0] < 0 and self.image_direction == 'right':
         self.flipped = True
      elif self.delta_speed[0] < 0 and self.image_direction == 'left':
         self.flipped = False

   def get_status(self):
      if self.delta_speed[1]  < 0:
         return 'jump'
      elif self.delta_speed[1] > 1:
         return 'fall'
      elif self.delta_speed[1] >= 0 and self.on_ground == False:
         return 'jump'
      else:
         if self.delta_speed[0] != 0:
            return 'run'
         else:
            return 'idle'

class FishMan(Entity):
   def __init__(self, pos: tuple[int, int]) -> None:
      self.spawn_offsets = (0, 64 - image_database['enemy_run'][0].get_height())
      self.new_pos = (pos[0], pos[1] + self.spawn_offsets[1])
      super().__init__(self.new_pos)

      self.collider_offsets = (-20, -10)
      self.turn_around = True
      self.image_direction = 'left'
      self.set_action('enemy_run')
      self.collider = self.get_collider()
      self.speed = [0.2, 0.15]
   
   def update(self, time):
      self.move_collider()
      self.check_colliding(['terrain', 'constraint'])
      self.animate(time)
      self.x_pos = self.collider.x + self.collider_offsets[0] / 2 
      self.y_pos = self.collider.y + self.collider_offsets[1]
      
class Player(Entity):
   def __init__(self, pos: tuple[int, int]) -> None:
      super().__init__(pos)

      self.collider_offsets = (-20, 0)
      self.set_action('player_idle')
      self.collider = self.get_collider()
      self.turn_around = False
      self.speed = [0, 0.55]
      self.MAX_DX = 4.6
      self.image_direction = 'right'

   def get_input(self):
      keys = pygame.key.get_pressed()

      if keys[pygame.K_RIGHT]:
         if self.on_ground:
            self.speed[0] = 1
         else:
            self.speed[0] = 0.5
      elif keys[pygame.K_LEFT]:
         if self.on_ground:
            self.speed[0] = -1
         else:
            self.speed[0] = -0.5
      else:
         if self.on_ground:
            self.speed[0] = 0
            self.delta_speed[0] = 0
         else:
            self.speed[0] = 0

      if keys[pygame.K_c] and self.on_ground:
         self.jump()

   def jump(self):
      self.delta_speed[1] = -11.8

   def check_actions(self):
      status = self.get_status()
      self.repeat = True
      if status == 'jump':
         self.set_action('player_jump')
         self.repeat = False
      if status == 'fall':
         self.set_action('player_fall')
         self.repeat = False
      if status == 'run':
         self.set_action('player_run')
      if status == 'idle':
         self.set_action('player_idle')

   def player_logs(self, time):
      global log_time
      log_time += time
      if log_time >= 300:
         # print(f'{self.get_status()} | OnGround:{self.on_ground} | dy: {self.delta_speed[1]}')
         print(f'{self.get_status()} | SpeedX:{self.speed[0]} | dx: {self.delta_speed[0]}')
         log_time = 0

   def update(self, time):
      self.get_input()
      self.move_collider()
      self.check_colliding(['terrain'])
      self.check_actions()
      self.animate(time)

      self.x_pos = self.collider.x + self.collider_offsets[0] / 2 
      self.y_pos = self.collider.y + self.collider_offsets[1]

      if self.flipped == False:
         self.x_pos += 10
      if self.flipped == True:
         self.x_pos -= 10
      if self.flipped == True and self.on_ground == False:
         self.x_pos += 18
      if self.flipped == True and self.get_status() == 'fall':
         self.x_pos -= 18
      self.player_logs(time)

def get_images(path: str, count: int) -> dict[str, pygame.Surface]:
   image_frames = []
   for image_id in range(count):
      animation_name = path.split('/')[-1] + f'_{image_id}'
      img_file = pygame.image.load(path + '/' + animation_name + '.png')
      image_frames.append(img_file)

   return image_frames

def add_animation(path: str, name: str, durations: list[int], count: int):
   image_database[name] = get_images(path, count)
   animation_durations[name] = durations

   if count > len(durations):
      for i in range(count - 1):
         animation_durations[name].append(durations[0])

def camera_update():
   player.update(frame_time)
   scroll[0] += (player.collider.x - scroll[0] - SCREEN[0] / 2) / 20

   if scroll[0] < 0:
      scroll[0] = 0
   if scroll[0] > 3840 - SCREEN[0]:
      scroll[0] = 3840 - SCREEN[0]

# Pygame Window
pygame.init()
SCREEN = (1400, 650)
SCALE = 1
RESOLUTION = (SCREEN[0] / SCALE, SCREEN[1] / SCALE)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SCREEN)
display = pygame.Surface(RESOLUTION)
tmx_map = tgl.load_map('./world/level_0/level_0.tmx')
tmx_images = tmx_map.load_images()
all_tiles = tmx_map.load_tiles()
frame_time = 25
log_time = 0

image_database = {}
animation_durations: dict[str, list[int]] = {}

enemy_run_durations = [180]
player_run_durations = [160]
player_idle_durations = [180]
player_jump_durations = [130]
player_fall_durations = [130]
add_animation('./graphics/enemy/run', 'enemy_run', enemy_run_durations, 6)
add_animation('./graphics/character/run', 'player_run', player_run_durations, 6)
add_animation('./graphics/character/idle', 'player_idle', player_idle_durations, 5)
add_animation('./graphics/character/jump', 'player_jump', player_idle_durations, 3)
add_animation('./graphics/character/fall', 'player_fall', player_idle_durations, 1)

world_tiles : list[GameTile] = []
bg_tiles : list[GameTile] = []
enemies : list[GameTile] = []
entities : list[Entity] = []
collisions : list[Collidable] = []

player = Player((1000, 400))
scroll = [player.x_pos - SCREEN[0] / 2, 0]

for tile in all_tiles:
   if tile.layer_name == 'bg_clouds':
      continue
   if tile.layer_name == 'bg_palms':
      continue
   if tile.layer_name == 'background':
      continue
   if tile.layer_name == 'enemies':
      continue
   if tile.layer_name == 'constraints':
      continue
   world_tiles.append(GameTile(tile))

for tile in all_tiles:
   if tile.layer_name == 'bg_clouds':
      bg_tiles.append(Cloud(tile))
   if tile.layer_name == 'background':
      bg_tiles.append(GameTile(tile))
   if tile.layer_name == 'bg_palms':
      bg_tiles.append(GameTile(tile))
   if tile.layer_name == 'enemies':
      enemies.append(GameTile(tile))
   if tile.layer_name == 'terrain':
      constraint = pygame.Rect(tile.pos[0], tile.pos[1], 64, 64)
      collisions.append(Collidable('terrain', constraint))
   if tile.layer_name == 'constraints':
      constraint = pygame.Rect(tile.pos[0], tile.pos[1], 64, 64)
      collisions.append(Collidable('constraint', constraint))

for tile in enemies:
   pos = (tile.x_pos, tile.y_pos)
   entities.append(FishMan(pos))

while True:
   # Event loop
   close_window = False
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         close_window = True
      if event.type == pygame.KEYDOWN:
         if event.key == pygame.K_ESCAPE:
            close_window = True
      if close_window:
         pygame.quit()
         sys.exit()

   camera_update()
   
   #Display drawing
   display.fill('grey12')

   for bg in bg_tiles:
      if bg.x_pos > player.collider.x + SCREEN[0] or bg.x_pos < player.x_pos - SCREEN[0]:
         continue
      bg.update(frame_time)
      pos = (int(bg.x_pos) - int(scroll[0]), int(bg.y_pos))
      display.blit(bg.image, pos, bg.rect)

   for tile in world_tiles:
      if tile.x_pos > player.collider.x + SCREEN[0] or tile.x_pos < player.x_pos - SCREEN[0]:
         continue
      tile.update(frame_time)
      pos = (int(tile.x_pos) - int(scroll[0]), int(tile.y_pos))
      display.blit(tile.image, pos, tile.rect)

   for entity in entities:
      if entity.x_pos > player.collider.x + SCREEN[0] or entity.x_pos < player.x_pos - SCREEN[0]:
         continue
      entity.update(frame_time)
      pos = int(entity.x_pos) - int(scroll[0]), int(entity.y_pos)
      display.blit(entity.image, pos)
      entity_rects = pygame.Rect(entity.collider.x - scroll[0], pos[1], entity.collider.w, entity.collider.h)
      pygame.draw.rect(display, 'green', entity_rects, 2, 8)

   display.blit(player.image, (player.x_pos - int(scroll[0]), player.y_pos))
   
   # collider debugging
   # pygame.draw.rect(display, 'gray7', player.collider, 2)
   # for block in collisions:
   #    pygame.draw.rect(display, 'blue', block, 3)

   screen.blit(pygame.transform.scale(display, SCREEN), (0, 0))

   #Display Refresh
   pygame.display.update()
   clock.tick(60)