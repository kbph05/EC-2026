import json
import os
import shutil

from PIL import Image, ImageDraw

MAP_IMG_PATH = r"temp/map.png"
RESULTS_FOLDER = "temp/result"
BLANK_MAP_IMG_PATH = r"resources/map_blank.png"
NODE_POS_FILE_PATH = r"resources/map_element_nodes_pos.json"
EDGE_POS_FILE_PATH = r"resources/map_element_edges_pos.json"

X_COLOR = "#ff0000"
O_COLOR = "#00ff00"
X_SIZE = 8
X_THICKNESS = 3

ROUTE_COLOR = "#ff0000"
ROUTE_THICKNESS = 4


def draw_map_img(user_pos: str, nodes: list, edges: list, output=MAP_IMG_PATH):
    with open(NODE_POS_FILE_PATH) as f:
        node_pos = json.load(f)
    with open(EDGE_POS_FILE_PATH) as f:
        edge_pos = json.load(f)

    points = [node_pos[n] for n in nodes]
    points += [edge_pos["-".join(sorted(e.split("-")))] for e in edges]

    img = Image.open(BLANK_MAP_IMG_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)
    for x, y in points:
        draw.line([(x - X_SIZE, y - X_SIZE), (x + X_SIZE, y + X_SIZE)], fill=X_COLOR, width=X_THICKNESS)
        draw.line([(x - X_SIZE, y + X_SIZE), (x + X_SIZE, y - X_SIZE)], fill=X_COLOR, width=X_THICKNESS)
    if user_pos in node_pos:
        ux, uy = node_pos[user_pos]
    else:
        ux, uy = edge_pos["-".join(sorted(user_pos.split("-")))]
    draw.ellipse([(ux - X_SIZE, uy - X_SIZE), (ux + X_SIZE, uy + X_SIZE)], outline=O_COLOR, width=X_THICKNESS)
    img.save(output)

def draw_route(path: list, output_folder=RESULTS_FOLDER):
    with open(NODE_POS_FILE_PATH) as f:
        node_pos = json.load(f)

    shutil.rmtree(output_folder, ignore_errors=True)
    os.makedirs(output_folder)

    img = Image.open(BLANK_MAP_IMG_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)
    img.save(os.path.join(output_folder, "step0.png"))

    for i in range(1, len(path)):
        start, end = node_pos[path[i - 1]], node_pos[path[i]]
        draw.line([tuple(start), tuple(end)], fill=ROUTE_COLOR, width=ROUTE_THICKNESS)
        img.save(os.path.join(output_folder, f"step{i}.png"))


def main():
    draw_map_img("H",["D", "B", "E"], ["J1-A", "C-E", "K-G"])
    draw_route(["A", "J1", "B"])


if __name__ == "__main__":
    main()
