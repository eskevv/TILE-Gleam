# TILE-Gleam
## Tiled parser for XML in Python (originally for quick results in pygame) - unoptimized

I made this to improve my python skills when i started with Python
[using a couple of my own string functions]

### Supports:
- Animated tiles
- Multiple layers
- Layer ordering
- Compact tile data in single list


### Example scenario:
1) load the map
2) load the images
3) load the tiles
4) append data as needed to your custom tiles list
```
import tgl

class GameTile:
  def __init__(...):
    ...

tmx_map = tgl.load_map('./world/level_0/level_0.tmx')
tmx_images = tmx_map.load_images()
all_tiles = tmx_map.load_tiles()

world_tiles : list[GameTile] = []

for tile in all_tiles:
  if tile.layer_name == 'bg_clouds':
    world_tiles.append(GameTile(tile))
```
