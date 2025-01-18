import os, csv
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

___version___ = "0.1" # 2023

# Initialize 'Minecraft' app using 'Ursina' Engine
minecraft_app = Ursina()

# All Block Textures
sand_block_texture = load_texture('assets/graphic/Sand.png')
stone_block_texture = load_texture('assets/graphic/Stone_Block.png')
stone_brick_texture = load_texture('assets/graphic/Stone_Brick.png')
wood_plank_texture = load_texture('assets/graphic/Wood_Plank.jpg')
leaves_texture = load_texture('assets/graphic/Leaves.png')
obsidian_texture = load_texture('assets/graphic/Obsidian.png')
sponge_texture = load_texture('assets/graphic/Sponge.jpg')
gold_ore_block_texture = load_texture('assets/graphic/Gold_Ore_Block.png')
diamond_ore_block_texture = load_texture('assets/graphic/Diamond_Ore_Block.png')
emerald_ore_block_texture = load_texture('assets/graphic/Emerald_Ore_Block.png')

# Sky Texture
sky_texture = load_texture('assets/graphic/Sky.png')

# Block Placing/ Destroying Sound
block_sound = Audio('assets/sound/Block_Sound.mp3', loop = False, autoplay = False)

# Player 'WASD' Movement Sound
player_movement_sound = Audio('assets/sound/Player_Movement_Sound.mp3', loop = True, autoplay = False)

# By Declaration of 'Block Choice Variable' and by default block was 'Stone Block'
block_choice = 'Stone Block'

# List to store block data
blocks = []
GAME_FILE = os.path.join(os.path.dirname(__file__), 'games/game.csv')

# Save function
def save_blocks():
    with open(GAME_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        for block in blocks:
            writer.writerow(block)
    print("Game saved.")

# Load function
def load_blocks():
    global blocks
    try:
        with open(GAME_FILE, 'r') as file:  # Sjednocení cesty
            reader = csv.reader(file)
            for row in reader:
                x, y, z, b = map(int, row)
                blocks.append([x, y, z, b])
                texture_map = {
                    1: stone_block_texture,
                    2: sand_block_texture,
                    3: stone_brick_texture,
                    4: wood_plank_texture,
                    5: leaves_texture,
                    6: obsidian_texture,
                    7: sponge_texture,
                    8: gold_ore_block_texture,
                    9: diamond_ore_block_texture,
                    0: emerald_ore_block_texture
                }
                texture = texture_map.get(b, stone_block_texture)  # Default to stone block if type not found
                Voxel(position=(x, y, z), texture=texture)
        print("Game loaded.")
    except FileNotFoundError:
        print("No save file found.")

# Clear function
def clear_blocks():
    global blocks
    for block in blocks[:]:  # Create a copy of the list to safely iterate while modifying
        for entity in scene.entities:
            if (int(entity.position.x), int(entity.position.y), int(entity.position.z)) == tuple(block[:3]):
                destroy(entity)
    blocks.clear()
    print("All blocks cleared.")

# Restore function
def restore_player():
    player_position = (dimension // 2, 2, dimension // 2)
    minecraft_player.position = player_position
    print("Player restored to center.")

# Declare 'update()' function for the 'Choice of Block' and 'Hand Movements' Functionalities
def update():
    global block_choice
    if held_keys['1']:
        block_choice = 'Stone Block'
    if held_keys['2']:
        block_choice = 'Sand Block'
    if held_keys['3']:
        block_choice = 'Stone Brick'
    if held_keys['4']:
        block_choice = 'Wood Plank'
    if held_keys['5']:
        block_choice = 'Leaves'
    if held_keys['6']:
        block_choice = 'Obsidian'
    if held_keys['7']:
        block_choice = 'Sponge'
    if held_keys['8']:
        block_choice = 'Gold Ore Block'
    if held_keys['9']:
        block_choice = 'Diamond Ore Block'
    if held_keys['0']:
        block_choice = 'Emerald Ore Block'

    # Hand Movement Part
    """
    if held_keys['left mouse'] or held_keys['right mouse']:
        player_hand.active()
    else:
        player_hand.passive()
    """    
  
    # 'WASD' Movement Sound of Player 
    if not (held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']):
        player_movement_sound.play()
    if (held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']):
        pass

    # Save, Load, Clear, and Restore Handling
    if held_keys['s']:
        save_blocks()
    if held_keys['l']:
        load_blocks()
    if held_keys['c']:
        clear_blocks()
    if held_keys['r']:
        restore_player()

''' 'Minecraft' is a game based on 'Blocks' which is also known as 'Voxel'. 
So, we have declared 'Voxel' class for 'Block' Manipulation in game. '''
class Voxel(Button):
    def __init__(self, position = (0, 0, 0), texture = sand_block_texture):
        super().__init__(
            parent = scene,
            position = position,
            model = 'cube',
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.gray
        )

    # Declaration of 'input()' function for 'onClick()' operations such as 'Place Block', 'Remove Block'
    def input(self, key):
        if self.hovered:
            # Press 'Left Click' to 'Place Block' 
            if key == 'left mouse down':
                # Play Block placing Sound
                block_sound.play()

                # Place Block according to your Choice
                if block_choice == 'Stone Block':
                    voxel = Voxel(position=self.position + mouse.normal, texture=stone_block_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 1])
                elif block_choice == 'Sand Block':
                    voxel = Voxel(position=self.position + mouse.normal, texture=sand_block_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 2])
                elif block_choice == 'Stone Brick':
                    voxel = Voxel(position=self.position + mouse.normal, texture=stone_brick_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 3])
                elif block_choice == 'Wood Plank':
                    voxel = Voxel(position=self.position + mouse.normal, texture=wood_plank_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 4])
                elif block_choice == 'Leaves':
                    voxel = Voxel(position=self.position + mouse.normal, texture=leaves_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 5])
                elif block_choice == 'Obsidian':
                    voxel = Voxel(position=self.position + mouse.normal, texture=obsidian_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 6])
                elif block_choice == 'Sponge':
                    voxel = Voxel(position=self.position + mouse.normal, texture=sponge_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 7])
                elif block_choice == 'Gold Ore Block':
                    voxel = Voxel(position=self.position + mouse.normal, texture=gold_ore_block_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 8])
                elif block_choice == 'Diamond Ore Block':
                    voxel = Voxel(position=self.position + mouse.normal, texture=diamond_ore_block_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 9])
                elif block_choice == 'Emerald Ore Block':
                    voxel = Voxel(position=self.position + mouse.normal, texture=emerald_ore_block_texture)
                    blocks.append([int(self.position.x + mouse.normal.x), int(self.position.y + mouse.normal.y), int(self.position.z + mouse.normal.z), 0])

            # Press 'Right Click' to 'Remove Block' 
            if key == 'right mouse down':
                # Play Block destroying Sound
                block_sound.play()
                # Save position before destroying
                position_to_remove = [int(self.position.x), int(self.position.y), int(self.position.z)]
                # Destroy Block
                destroy(self)
                # Remove block from the list
                blocks[:] = [block for block in blocks if block[:3] != position_to_remove]

# Declare 'Sky()' Class
class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=sky_texture,
            scale=150,
            double_sided=True
        )
        scene.ambient_color = color.rgb(30, 30, 30)  # Darken the ambient light
        directional_light = DirectionalLight()
        directional_light.look_at(Vec3(1, -1, -1))
        directional_light.color = color.rgb(255, 255, 255)  # Bright light for contrast

# Declare 'Player_Hand()' Class
class Player_Hand(Entity):
        def __init__(self):
                super().__init__(
                    parent=camera.ui,
                    model='cube',
                    scale=(0.02, 0.3, 0.02),
                    # texture='assets/graphic/Player_Arm.png',
                    rotation=Vec3(50, 55, -60),
                    position=Vec2(0.406, -0.42)
                )

        def active(self):
                self.position = Vec2(0.39, -0.39) 

        def passive(self):
                self.position = Vec2(0.406, -0.42)

# Make Area for your 'Minecraft' World
dimension = 32  # 'Dimension' should be of 20X20 Blocks
for i in range(dimension):
    for j in range(dimension):
        # Initialize 'Voxel' class
        voxel = Voxel(position=(i, 0, j))

# Initialize your 'Minecraft' Player using FPP View
minecraft_player = FirstPersonController()
restore_player()  # Place player at the center on start

# Initialize 'Sky' for your 'Minecraft World'
sky = Sky()

# Initialization of 'Player Hand' Class for 'Minecraft Player'
# player_hand = Player_Hand()

# The window title
window.title = 'Minecraft simple Clone | Using Ursina Module'
# Show a border                
window.borderless = False 
# Do not go Fullscreen              
window.fullscreen = False        
# Do not show the in-game red 'X' that 'Closes the Window'       
window.exit_button.visible = False 
# Show the FPS (Frames per second) counter     
window.fps_counter.enabled = True       

# Run 'Minecraft' app
minecraft_app.run()
