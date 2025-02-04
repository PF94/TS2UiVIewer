import re
import pygame
from pygame.locals import *

from tkinter import filedialog

# convert rgb to hex because i dont wanna deal with it right now
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

# attempt parsing xml structure (this is very fucky since its not *true* xml)
# seems to work with most sims 2 base game ui files, but i havent tested those with any of the
# eps. simcity 4 *could* work but its based on an earlier version of the ui code so maybe not.
def parse_ui_structure(content):
    elements = []

    # this doesnt handle children elements at all. also might get fucky with newer eps?
    pattern = re.compile(r'<(LEGACY)(.*?)>', re.DOTALL)

    for match in pattern.finditer(content):
        tag, attributes = match.groups()

        clsid_match = re.search(r'clsid=([\w]+)', attributes)
        area_match = re.search(r'area=\(([-\d]+),([-\d]+),([-\d]+),([-\d]+)\)', attributes)
        caption_match = re.search(r'caption="(.*?)"', attributes)
        fill_color_match = re.search(r'fillcolor=\((\d+),(\d+),(\d+)\)', attributes)
        font_color_match = re.search(r'colorfontnormal=\((\d+),(\d+),(\d+)\)', attributes)
        hidden_match = re.search(r'winflag_visible=no', attributes)
        image_match = re.search(r'image=\{([\w,]+)}', attributes)

        clsid = clsid_match.group(1) if clsid_match else "Unknown"
        area = tuple(map(int, area_match.groups())) if area_match else (0, 0, 0, 0)
        fillcolor = rgb_to_hex(tuple(map(int, fill_color_match.groups()))) if fill_color_match else '#ffffff'
        fontcolor = rgb_to_hex(tuple(map(int, font_color_match.groups()))) if font_color_match else '#000000'
        caption = caption_match.group(1).strip() if caption_match else ""

        image_filename = False

        image_value = image_match.group(1) if image_match else ""
        if image_value:
            image_parts = image_value.split(',')
            # this is how simpe spits them out. no clue what the fuck is "00000000".
            image_filename = f"00000000-{image_parts[0]}-{image_parts[1]}"

        # this is bad. we should probably get all of the xml shit but whatever.
        element = {
            "clsid": clsid,
            "area": area,
            "caption": caption,
            "fillcolor": fillcolor,
            "fontcolor": fontcolor,
            "image": image_filename,
            "hidden": hidden_match
        }

        elements.append(element)

    return elements


# render ui
def render_ui(elements, screen):
    for elem in elements:
        print(elem)

        if not elem["hidden"]:
            x1, y1, x2, y2 = elem["area"]
            caption = elem["caption"]

            # calculate center?
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # images
            if elem["image"]:
                image_name = elem["image"].upper()  # e.g., '00000000-499db772-c9050010.png'
                image_path = f"assets/{image_name}.tga"

                try:
                    image = pygame.image.load(image_path) # load image

                    # the buttons in ts2 have four states
                    # 1: deactivated, 2: normal, 3: hover, 4: clicked/selected
                    #
                    # as of now, the viewer only displays the second state.
                    if elem["clsid"] == "GZWinBtn":
                        cropped_image = image.subsurface((image.get_width() // 4, 0, image.get_width() // 4, image.get_height()))
                    else:
                        cropped_image = image

                    # position image properly-ish
                    # some ui elements may not be properly placed, but im pretty sure thats because
                    # some of it is handled by ts2 code itself (for resolution) and also because
                    # this code Sucks. -chaziz 2/4/2025
                    image_rect = cropped_image.get_rect(center=(center_x, center_y))
                    screen.blit(cropped_image, image_rect)

                    # ok so some buttons have text included but i cant be arsed right now
                    #font = pygame.font.Font(None, 12)
                    #text = font.render(caption, True, (elem["fontcolor"]))
                    #text_rect = text.get_rect(center=(center_x, center_y))
                    #screen.blit(text, text_rect)

                except FileNotFoundError:
                    # some ui elements call non-existant pngs???
                    print(f"couldnt find image {image_path}!")
                    #pygame.draw.rect(screen, pygame.Color(elem["fillcolor"]), pygame.Rect(x1, y1, width, height))
                    font = pygame.font.Font(None, 12)
                    text = font.render(caption, True, (elem["fontcolor"]))
                    text_rect = text.get_rect(center=(center_x, center_y))
                    screen.blit(text, text_rect)

            else:
                # pygame.draw.rect(screen, pygame.Color(elem["fillcolor"]), pygame.Rect(x1, y1, width, height))
                font = pygame.font.Font(None, 12)
                text = font.render(caption, True, (elem["fontcolor"]))
                text_rect = text.get_rect(center=(center_x, center_y))
                screen.blit(text, text_rect)


# start program
def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF)
    pygame.display.set_caption("TS2 UI Viewer")
    screen.fill((64, 64, 128)) # use ts2 engine background color

    # open dialog
    file_path = filedialog.askopenfilename(title="Open TS2 UI File", filetypes=[("Text Files", "*.txt")])

    if not file_path:
        print("no file selected")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    elements = parse_ui_structure(content)

    render_ui(elements, screen)

    # loop
    running = True
    while running:
        for event in pygame.event.get(): # theres no event rn
            if event.type == QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
