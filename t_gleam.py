from gc import collect
import sys, pygame
from string_utils import st

class Tileset:
   def __init__(self, data : dict[str, str]):
      self.firstgid = data['firstgid']
      self.name = data['name']
      self.width = data['width']
      self.height = data['height']
      self.tile_count = data['tile_count']
      self.columns = data['columns']
      self.source = data['source']
      self.img_src = data['img_src']
      self.tile_width = data['tile_width']
      self.tile_height = data['tile_height']
      self.data_full = data['data_full']

class TiledLayer:
   def __init__(self, data):
      self.id = data['id']
      self.name = data['name']
      self.width = data['width']
      self.height = data['height']
      self.encoding = data['encoding']
      self.layer = data['layer']

class Tile:
   def __init__(self, pos, img_id, rect, layer, frames:list[list] = None):
      self.pos = pos
      self.img_id = img_id
      self.rect = rect
      self.layer_name = layer[0]
      self.layer_order = layer[1]
      self.frame_data = frames

class TiledMap:
   def __init__(self, path):
      self.directory = self.get_directory(path)
      self.content = open(path).read()
      self.tile_width = int(self.parse_property(self.content, 'tilewidth'))
      self.tile_height = int(self.parse_property(self.content, 'tileheight'))
      self.layers = self.add_layers()
      self.layer_info = self.store_layers()
      self.tileset_ids = self.add_gids()
      self.tilesets = self.add_tilesets()
      self.mapped_tiles = self.layer_setup()
      self.tile_data = self.setup_tiles()
   
   def store_layers(self) -> dict[str, int]:
      layer_orders = {}
      for layer in self.layers:
         layer_orders[layer.name] = layer.layer
      
      # print(layer_orders)

      return layer_orders

   def count_before(self, data:str, search:str):
      look_for = '<layer id='
      stop_index = data.find(search)
      count = data.count(look_for, 0, stop_index)

      

      # index = st.iterate_with(data, look_for, 0) + len(look_for)
      # count = 0
      # while index < stop_index:
      #    count += 1
      #    index = st.iterate_with(data, look_for, index) + len(data) - len(search)
      
      return count

   def collect_layer(self, data):
      values = {}
      
      values['id'] = self.parse_property(data, 'id')
      values['name'] = self.parse_property(data, 'name')
      values['width'] = self.parse_property(data, 'width')
      values['height'] = self.parse_property(data, 'height')
      values['encoding'] = self.parse_encoding(data, 'csv')
      values['layer'] = self.count_before(self.content, data) + 1

      return values

   def parse_property(self, data, property):
      value = st.string_within(data, f'{property}="', '"')
      indexes = st.find_between(value, '"', '"', 1)
      start = indexes[0]
      finish = indexes[1] + 1
      return value[start:finish]

   def parse_encoding(self, data, property):
      value = st.string_within(data, f'"{property}">', '<')
      indexes = st.find_between(value, '>', '<', 1)
      start = indexes[0]
      finish = indexes[1] + 1
      return value[start:finish]

   def add_layers(self) -> list[TiledLayer]:
      layers = []

      for layer in self.get_datatrees(self.content, 'layer', '</'):
         layer_data = self.collect_layer(layer)
         layers.append(TiledLayer(layer_data))

      return layers

   def get_imgsrc(self, raw_source, tileset_data):
      tsx = raw_source.split('/')[-1]
      tsx_source_index = raw_source.find(tsx)
      tsx_source = raw_source[0:tsx_source_index]
      return self.directory + tsx_source + tileset_data

   def get_datatrees(self, data, tree, end):
      trees = []
      indexes = st.find_between(data, f'<{tree} ', end, 0, 0)
      while indexes[1] != -1:
         tree_data = st.string_inside(data, indexes)
         trees.append(tree_data)
         indexes = st.find_between(data, f'<{tree} ', end, 0, indexes[1] + 1)

      return trees

   def get_allsrc(self, data, first_path) -> list[str]:
      sources = []
      trees = self.get_datatrees(data, 'image', '/>')
      
      for source in trees:
         img_path = self.parse_property(source, 'source')
         complete_source = self.get_imgsrc(first_path, img_path)
         sources.append(complete_source)

      return sources 

   def add_tilesets(self) -> list[Tileset]:
      all_tilesets = []

      for tileset in self.find_tilesets():
         tileset_data = self.collect_tsx(tileset)
         all_tilesets.append(Tileset(tileset_data))

      return all_tilesets

   def get_layer(self, number):
      for layer in self.layers:
         if layer.id == str(number):
            return layer
      return TiledLayer(None)

   def get_tileset(self, firstgid):
      for tileset in self.tilesets:
         if tileset.firstgid == str(firstgid):
            return tileset
      return Tileset(None)

   def tileset_index(self, id):
      for tileset in self.tilesets:
         if tileset.id == str(id):
            return tileset
      return Tileset(None)

   def string_tileset(self, gid):
      tileset_data = st.string_within(self.content, f'<tileset firstgid="{gid}"', '/>')

      if tileset_data != None:
         return tileset_data
      return f'Error: gid #{gid} doesn\'t exist or is not a starting gid'

   def load_images(self) -> dict[str, pygame.Surface]:
      images = {}
      for i in self.get_images():
         image_id = i[0]
         image = pygame.image.load(i[1]).convert_alpha()
         images[image_id] = image
      
      return images

   def read_tsx(self, path):
      data = open(self.directory + path).read()
      return st.string_within(data, '<tileset', '</tileset>')

   def collect_tsx(self, data):
      values = {}
      tsx_path = self.parse_property(data, 'source')
      tsx_data = self.read_tsx(tsx_path)

      values['source'] = tsx_path
      values['img_src'] = self.get_allsrc(tsx_data, tsx_path)
      values['firstgid'] = self.parse_property(data, 'firstgid')
      values['name'] = self.parse_property(tsx_data, 'name')
      values['tile_width'] = self.parse_property(tsx_data, 'tilewidth')
      values['tile_height'] = self.parse_property(tsx_data, 'tileheight')
      values['tile_count'] = self.parse_property(tsx_data, 'tilecount')
      values['columns'] = self.parse_property(tsx_data, 'columns')
      values['width'] = self.parse_property(tsx_data, 'width')
      values['height'] = self.parse_property(tsx_data, 'height')
      values['data_full'] = tsx_data

      return values

   def find_tilesets(self):
      search_with = '<tileset firstgid="'
      tilesets = []

      indexes = st.find_between(self.content, search_with, '>', 0, 0)
      while indexes[1] != -1:
         data = st.string_inside(self.content, indexes)
         tilesets.append(data)
         indexes = st.find_between(self.content, search_with, '>', 0, indexes[1] + 1)

      return tilesets

   def get_directory(self, path):
      sect = path.split('/')[-1]
      trim_at = path.find(sect)
      return path[0:trim_at]

   def add_gids(self):
      set_ids = []
      for tileset in self.find_tilesets():
         set_id = self.parse_property(tileset, 'firstgid')
         set_ids.append(set_id)
      
      return set_ids

   def get_firstgid(self, gid):
      current_id = 1
      for s in self.tileset_ids:
         if gid >= int(s):
            current_id = s
      return current_id
   
   def get_srcrect(self, img_id, tile_size, image_size):
      x_pos = (img_id * tile_size[0]) % image_size[0]
      y_pos = int(img_id * tile_size[0] / image_size[0]) * tile_size[1]
      return (x_pos, y_pos, tile_size[0], tile_size[1])

   def get_tileproperties(self, gid, pos, layer):
      first_gid = self.get_firstgid(gid)
      tileset = self.get_tileset(first_gid)
      tile_id = gid - int(first_gid)
      img_trees = self.get_datatrees(tileset.data_full, 'image', '/>')
      tile_trees = self.get_datatrees(tileset.data_full, 'tile', '</tile>')
      coords = (pos[0] * self.tile_width, pos[1] * self.tile_height)

      id_list = []
      for tree in img_trees:
         img_id = self.parse_property(tree, 'source').split('/')[-1]
         id_list.append(img_id)

      images = 0
      for tree in img_trees:
         max_w = int(self.parse_property(tree, 'width'))
         max_h = int(self.parse_property(tree, 'height'))
         tile_w = int(self.parse_property(tileset.data_full, 'tilewidth'))
         tile_h = int(self.parse_property(tileset.data_full, 'tileheight'))
         img_id = self.parse_property(tree, 'source').split('/')[-1]

         if tile_id == images and len(img_trees) > 1:
            frames = []
            tile_data = tile_trees[tile_id]
            animation_data = st.string_within(tile_data, '<animation>', '</animation>')
            if animation_data != None:
               frame_trees = self.get_datatrees(animation_data, 'frame', '/>')
               for frame in range(len(frame_trees)):
                  frames.append([])
                  frame_id = self.parse_property(frame_trees[frame], 'tileid')
                  frame_img = id_list[int(frame_id)]
                  duration = self.parse_property(frame_trees[frame], 'duration')
                  frames[frame] = [frame_img, int(duration)]
            offset_y = self.tile_height - max_h
            if not frames:
               frames = None
            return Tile((coords[0], coords[1] + offset_y), img_id, (0, 0, max_w, max_h), layer, frames)

         elif len(img_trees) == 1:
            offset_y = self.tile_height - tile_h
            rect = self.get_srcrect(tile_id, (tile_w, tile_h) ,(max_w, max_h))
            return Tile((coords[0], coords[1] + offset_y), img_id, rect, layer)
         images += 1

      return Tile(coords, 'none', (0, 0, 0, 0), layer)

   def layer_setup(self) -> dict[str,TiledLayer]:
      every_layer = {}
      for layer in self.layers:
         width = int(layer.width)
         height = int(layer.height)
         encoding = layer.encoding
         name = layer.name
         world = []

         skips = 0
         for y in range(height):
            world.append([])
            for x in range(width):
               raw_value = ''
               location = y * width + x

               while encoding[location + skips] != ',':
                  raw_value += encoding[location + skips]
                  if location + skips >= len(encoding) - 1:
                     break
                  skips += 1
               
               world[y].append(raw_value)

         every_layer[name] = world

      return every_layer

   def get_map(self, name : str) -> dict[str:Tile]:
      return self.mapped_tiles[name]

   def setup_tiles(self):
      tile_setup = {}

      for tile_map in self.mapped_tiles:
         working_map = self.mapped_tiles[tile_map]
         new_map = []
         for row in range(len(working_map)):
            for cell in range(len(working_map[row])):
               gid = int(working_map[row][cell])
               if gid == 0:
                  continue
               pos = (cell, row)
               layer_info = [tile_map, self.layer_info[tile_map]]
               tile = self.get_tileproperties(gid, pos, layer_info)
               new_map.append(tile)

         tile_setup[tile_map] = new_map
      return tile_setup

   def get_tiles(self, name : str) -> list[Tile]:
      return self.tile_data[name]

   def get_images(self) -> list[list[str]]:
      image_ids = []
      image_index = 0

      for t in range(len(self.tilesets)):
         sources = self.tilesets[t].img_src
         for source in sources:
            image_ids.append([])
            image_ids[image_index].append(source.split('/')[-1])
            image_ids[image_index].append(source)
            image_index += 1

      return image_ids

   def load_tiles(self) -> list[Tile]:
      all_tiles = []
      collected_layers = 0

      # while collected_layers != len(self.layers):
      for layer in self.tile_data:
         tiles = self.get_tiles(layer)
         for tile in tiles:
            all_tiles.append(tile)
            # if self.layer_info[layer] == collected_layers + 1:
            #    collected_layers += 1
      
      return all_tiles

def load_map(path):
   return TiledMap(path)