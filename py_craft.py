from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random
import os
import csv

___version___ = "0.2.3" # 2025/01

DEBUG = True
SCREEN_DEBUG = True
WORLD_SIZE = 32 
# SEED = 12345
SEED = 0x0c1e24e5917779d297e14d45f14e1a1a # Andreas
# seed = random.randint(1, 1000)
DEFAULT_GAME_FILE = os.path.join(os.path.dirname(__file__), 'games/default.csv')
active_game_file = DEFAULT_GAME_FILE

noise = PerlinNoise(octaves=3, seed=SEED)
app = Ursina() #create an instance of the ursina app

selected_block = "grass"
energy_temp = 100
blocks = []


def setup_game_file():
    global active_game_file, info_text

    # Function to handle file name setting
    def set_game_file():
        global active_game_file
        user_input = input_field.text.strip()
        if user_input:
            active_game_file = os.path.normpath(
                os.path.join(os.path.dirname(__file__), f"games/{user_input}.csv")
            )
            print(f"Game file set to: {active_game_file}")
        else:
            active_game_file = os.path.normpath(DEFAULT_GAME_FILE)
            print(f"Using default game file: {active_game_file}")
        
        # Update info_text dynamically
        info_text.text = f"Active file: {active_game_file}"

        # Disable input field and button
        input_field.enabled = False
        ok_button.enabled = False

    # Create an input field
    input_field = InputField(
        parent=camera.ui,
        position=(0, 0.2),
        placeholder='Enter game file name or leave empty for default'
    )
    #input_field.scale = (0.5, 0.1)  # Manually set the scale to avoid conflict
    input_field.scale = (0.5, 0.05)  
    # input_field.font = 'assets/fonts/your_font_file.ttf'  
    input_field.text_color = color.gray
    input_field.background_color = color.black  

    # Automatically focus on the input field
    input_field.active = True

    # Create an OK button
    ok_button = Button(
        text="OK",
        parent=camera.ui,
        scale=(0.2, 0.1),
        position=(0, 0),
        on_click=set_game_file
    )


block_textures = {
    "grass": load_texture("assets/textures/groundEarth.png"),
    "dirt": load_texture("assets/textures/groundMud.png"),
    "stone": load_texture("assets/textures/wallStone.png"),
    "bedrock": load_texture("assets/textures/stone07.png"),
    "stone05": load_texture("assets/textures/stone05.png"),
    "stone06": load_texture("assets/textures/stone06.png"),
    "wallbrick01": load_texture("assets/textures/wallBrick01.png"),
    "ice01": load_texture("assets/textures/ice01.png"),
    "lava01": load_texture("assets/textures/lava01.png"),
    "water": load_texture("assets/textures/water.png")
}

# Define a list of blocks and their associated keys
block_types = [
    ("grass", "1"),
    ("dirt", "2"),
    ("stone", "3"),
    ("wallbrick01", "4"),
    ("stone05", "5"),
    ("stone06", "6"),
    ("lava01", "7"),
    ("ice01", "8"),
    ("water", "9")
]

# Create a black bar at the bottom of the screen
info_bar = Entity(
    parent=camera.ui,
    model='quad',
    color=color.black,
    scale=(window.aspect_ratio, 0.1),  # Height of approximately 50px
    position=(0, -0.45)  # Positioned near the bottom of the screen
)

#  position 20px = 20 * (2 / 1080) ≈ 0.037.
pixel_to_relative_x = 30 * (2 / window.size[0])

# loading_text = Text(text='', position=(0.7, 0.45), origin=(0, 0), scale=1.5, color=color.white, background=True)
position_text = Text(text='', parent=camera.ui,
    position=(-0.9+pixel_to_relative_x, -0.39),  # Top-left corner
    origin=(-0.5, 0), scale=1, color=color.white)
cursor_position_text = Text(text='', parent=camera.ui,
    position=(-0.9+pixel_to_relative_x, -0.36),  # Top-left corner
    origin=(-0.5, 0), scale=1, color=color.white)

info_text = Text(text=active_game_file, world_parent=camera.ui, color=color.white, scale=1,
    origin=(-0.5, 0), position=(-0.9+pixel_to_relative_x, -0.43))
info_text2 = Text(text="::", world_parent=camera.ui, color=color.white, scale=1,
    origin=(-0.5, 0), position=(-0.9+pixel_to_relative_x, -0.46))


class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent = scene, model = 'sphere',
            texture = load_texture('assets/textures/sky.png'),
            scale = 150, double_sided = True
        )


class Block(Entity):
    def __init__(self, position, block_type):
        super().__init__(
            position=position,
            model="assets/models/block_model",
            scale=1,
            origin_y=-0.5,
            texture=block_textures.get(block_type),
            collider="box",
            color=color.white if block_type not in ["water", "ice01"] else (
                color.rgba(255, 255, 255, 200) if block_type == "water" else color.rgba(255, 255, 255, 128)
            )
        )
        self.block_type = block_type


def save_blocks():
    with open(os.path.normpath(active_game_file), 'w', newline='') as file:
        writer = csv.writer(file)
        for block in blocks:
            block_type_index = next((i for i, (name, _) in enumerate(block_types) if name == block[3]), None)
            if block_type_index is not None:
                writer.writerow(block[:3] + [block_type_index])
    print("Game saved to", active_game_file)


def load_blocks():
    global blocks
    info_text2.text = "[ Load ]"
    try:
        with open(os.path.normpath(active_game_file), 'r') as file:
            reader = list(csv.reader(file))
            total_blocks = len(reader)
            for index, row in enumerate(reader):
                x, y, z, block_type_index = row
                block_type_index = int(block_type_index)
                block_type = block_types[block_type_index][0]
                blocks.append([float(x), float(y), float(z), block_type])
                Block(position=(float(x), float(y), float(z)), block_type=block_type)

                if (index + 1) % 10 == 0 or index + 1 == total_blocks:
                    #loading_text.text = f"Loaded {index + 1} of {total_blocks} blocks"
                    info_text2.text = f"Loaded {index + 1} of {total_blocks} blocks"
                    app.step()
        print("Game loaded.")
        # loading_text.text = ""
        info_text2.text = str(index+1)
    except FileNotFoundError:
        print(f"No save file found at: {active_game_file}")


# Clear function
def clear_blocks():
    for entity in scene.entities:
        if hasattr(entity, 'block_type') and entity.block_type != "bedrock":
            destroy(entity)
    global blocks
    blocks = []
    print("All blocks cleared.")


# Clear below specific level
def clear_below_level(level):
    global blocks
    blocks_to_remove = [block for block in blocks if block[1] < level]
    for block in blocks_to_remove:
        for entity in scene.entities:
            if (int(entity.position.x), int(entity.position.y), int(entity.position.z)) == (int(block[0]), int(block[1]), int(block[2])):
                destroy(entity)
        blocks.remove(block)
    print(f"Blocks below level {level} cleared.")


# Restore function
def restore_player():
    info_text2.text = "[ Restore ]"
    player.position = Vec3(0, 20, 0)
    print("Player restored to center.")


def generate_noise():
    global selected_block  # Přístup k aktuálně vybranému bloku

    if not selected_block:
        print("No block selected. Defaulting to 'grass'.")
        selected_block = "grass"

    for _ in range(20):
        x = random.randint(-int(WORLD_SIZE / 2), int(WORLD_SIZE / 2))
        z = random.randint(-int(WORLD_SIZE / 2), int(WORLD_SIZE / 2))
        y = random.randint(1, int(WORLD_SIZE / 2))

        # Vytvoření bloku na náhodné pozici
        block = Block(position=(x, y - 7, z), block_type=selected_block)
        blocks.append([x, y, z, selected_block])
    print(f"Noise generated with block type: {selected_block}")


def add_square(parent, x, z, color, square_size=10, scale_factor=2, width_scale_factor=2, z_offset=0, previous_entity=None):

    if previous_entity:
        destroy(previous_entity)  # Ukončí předchozí entitu

    x_offset = (x - WORLD_SIZE // 2) * (square_size * scale_factor * width_scale_factor) / window.size[0]
    z_offset_base = (z - WORLD_SIZE // 2) * (square_size * scale_factor) / window.size[1]

    entity = Entity(
        parent=parent,
        model='quad',
        color=color,
        always_on_top=True,
        scale=((square_size * scale_factor * width_scale_factor) / window.size[0],
               (square_size * scale_factor) / window.size[1]),
        position=(x_offset, z_offset_base, z_offset)
    )
    # print(f"Square added at ({x},{z}) -> {entity.position} with color {color}, z_offset={z_offset}")
    return entity


def display_map():
    info_text2.text = "[ Map ] close: x"
    global map_panel
    if 'map_panel' in globals() and map_panel.enabled:
        return

    matrix_size = WORLD_SIZE
    square_size = 10
    border_size = 20  # Posun mapy
    scale_factor = 2
    width_scale_factor = 2
    min_depth = 0  # Nejvyšší bod je bílý
    max_depth = -16  # Nejnižší bod je černý

    # Vytvoření panelu mapy
    map_panel = Entity(
        parent=camera.ui,
        model='quad',
        color=color.black,
        scale=((matrix_size * square_size * scale_factor * width_scale_factor + 2 * border_size) / window.size[0],
               (matrix_size * square_size * scale_factor + 2 * border_size) / window.size[1]),
        position=(0, 0)
    )

    for x in range(matrix_size):
        for z in range(matrix_size):
            highest_block = max(
                (block[1] for block in blocks if int(block[0]) == x - int(matrix_size / 2)
                 and int(block[2]) == z - int(matrix_size / 2) and block[3] in ["stone", "grass"]),
                default=max_depth
            )

            normalized_height = abs(highest_block) * 20  # Normalizace od 1 (bílá) do 0 (černá)
            gray_value = int(255 - normalized_height)
            block_color = color.rgb(gray_value, gray_value, gray_value)

            square = add_square(map_panel, x, z, block_color, square_size, scale_factor, width_scale_factor, z_offset=0.002)
            if DEBUG:
                print(f"({x},{z},{highest_block})")

    # **Přidání barevných bodů**
    add_square(map_panel, 3, 5, color.red, square_size, scale_factor, width_scale_factor)
    add_square(map_panel, 0, 0, color.blue, square_size, scale_factor, width_scale_factor)
    add_square(map_panel, 31, 31, color.green, square_size, scale_factor, width_scale_factor)


def display_perlin_map():
    global map_panel  # Umožní přístup k panelu pro zavírání klávesou
    if 'map_panel' in globals() and map_panel.enabled:  # Pokud již mapa existuje, neotevírej ji znovu
        return

    # Rozměry mapy
    matrix_size = WORLD_SIZE
    square_size = 10
    border_size = 20
    scale_factor = 2
    width_scale_factor = 2

    scene_width = (matrix_size * square_size * scale_factor * width_scale_factor) + (2 * border_size)
    scene_height = (matrix_size * square_size * scale_factor) + (2 * border_size)

    map_panel = Entity(
        parent=camera.ui,
        model='quad',
        color=color.black,
        scale=(scene_width / window.size[0], scene_height / window.size[1]),
        position=(0, 0)
    )

    max_val = 16
    for x in range(matrix_size):
        for z in range(matrix_size):
            # Vypočítání výšky na základě Perlinova šumu
            height = noise([x * 0.1, z * 0.1]) * max_val  # Maximální výška
            height = max(0, min(max_val, height))  # Oříznutí hodnoty na rozsah 0–10

            # Normalizace výšky na odstín šedé
            gray_value = int(255 * (height / 16)) # 10
            block_color = color.rgb(gray_value, gray_value, gray_value)

            # Přidání čtverečku
            square = Entity(
                parent=map_panel,
                model='quad',
                color=block_color,
                scale=((square_size * scale_factor * width_scale_factor) / window.size[0],
                       (square_size * scale_factor) / window.size[1]),
                position=(
                    (x - matrix_size // 2) * (square_size * scale_factor * width_scale_factor) / window.size[0],
                    (z - matrix_size // 2) * (square_size * scale_factor) / window.size[1]
                )
            )


#create player
player = FirstPersonController(
    mouse_sensitivity=Vec2(100, 100),
    position=(0, 5, 0)
)

mini_block = Entity(
    parent=camera,
    model="assets/models/block_model",
    scale=0.2,
    texture=block_textures.get(selected_block),
    position=(0.35, -0.25, 0.5),
    rotation=(-15, -30, -5)
)

#create the ground
min_height = -5
for x in range(-int(WORLD_SIZE/2), int(WORLD_SIZE/2)):
    for z in range(-int(WORLD_SIZE/2), int(WORLD_SIZE/2)):
        height = noise([x * 0.02, z * 0.02])
        height = math.floor(height * 7.5)
        for y in range(height, min_height - 1, -1):
            if y == min_height:
                block = Block((x, y + min_height, z), "bedrock")
            elif y == height:
                block = Block((x, y + min_height, z), "grass")
                blocks.append([x, y + min_height, z, "grass"])
            elif height - y > 2:
                block = Block((x, y + min_height, z), "stone")
                blocks.append([x, y + min_height, z, "stone"])
            else:
                block = Block((x, y + min_height, z), "dirt")
                blocks.append([x, y + min_height, z, "dirt"])


def input(key):
    global selected_block, map_panel, energy_temp
    # Check if the key matches any in block_types
    for block, block_key in block_types:
        if key == block_key:
            selected_block = block
            break

    # Place block
    if key == "left mouse down":
        energy_temp = energy_temp - 1
        info_text2.text = str(energy_temp)
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            block = Block(hit_info.entity.position + hit_info.normal, selected_block)
            blocks.append([hit_info.entity.position.x + hit_info.normal.x,
                           hit_info.entity.position.y + hit_info.normal.y,
                           hit_info.entity.position.z + hit_info.normal.z,
                           selected_block])

    # Delete block
    if key == "right mouse down" and mouse.hovered_entity:
        energy_temp = energy_temp - 1
        info_text2.text = str(energy_temp)
        if not mouse.hovered_entity.block_type == "bedrock":
            position = mouse.hovered_entity.position
            blocks[:] = [b for b in blocks if b[:3] != [position.x, position.y, position.z]]
            destroy(mouse.hovered_entity)

    # Additional functionalities
    if key == 's': save_blocks()
    if key == 'l': load_blocks()
    if key == 'c': clear_blocks()
    if key == 'r': restore_player()
    if key == 'n': generate_noise()
    if key == 'm': display_map()
    if key == 'p': display_perlin_map()
    if key == 'x' and 'map_panel' in globals() and map_panel.enabled: map_panel.disable()

def update():
    global position_text, cursor_position_text
    
    if SCREEN_DEBUG:
        player_position = player.position
        position_text.text = f"P: x={player_position.x:.2f}, y={player_position.y:.2f}, z={player_position.z:.2f}"

        # Perform a raycast to get the block the cursor is pointing at
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            # Get the position of the block and convert it to integers
            block_position = hit_info.entity.position
            cursor_position_text.text = f"C: x={int(block_position.x)}, y={int(block_position.y)}, z={int(block_position.z)}"
        else:
            cursor_position_text.text = "Cursor: Not pointing at a block"

    mini_block.texture = block_textures.get(selected_block)


def color_block(x, y, z, color=color.red):
 
    block = Entity(
        model='cube',
        position=(x, y, z),  # Upravena pozice, aby odpovídala výšce scény
        color=color,  # Nastavení barvy bloku
        parent=scene,
        scale=1,
        collider='box'
    )

    # Přidání bloku do seznamu
    blocks.append([x, y, z, "colored_block"])

    return block  # Funkce vrátí vytvořený blok (pro případné další použití)


# The window setup
window.title = 'Minecraft simple Clone | Using Ursina Module'
window.borderless = False 
window.fullscreen = True
window.exit_button.visible = True 
window.fps_counter.enabled = True

"""
# Initialize the player after a delay
def initialize_player():
    restore_player()
    print("Player initialized.")
invoke(initialize_player, delay=1) # Schedule the initialization
"""
setup_game_file()
sky = Sky()

color_block(3, -3, 5, color.red)
color_block(31, -3, 31, color.rgba(0, 0, 255, 150))

# start the app
app.run()