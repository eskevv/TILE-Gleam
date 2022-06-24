# TILE-Gleam
## Tiled parser for XML in Python (originally for quick results in pygame) - unoptimized

Originally made to improve my python skills
[using a couple of my own string functions]

### Supports:
- Animated tiles
- Multiple layers
- Layer ordering
- Compact tile data in single list


### Example use:
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
