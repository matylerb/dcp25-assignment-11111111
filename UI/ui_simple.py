import py5

MY_TUNES = [
    {"title": "The Morning Star", "key": "A", "notes": [58, 60, 70, 60, 58, 48, 58]},
    {"title": "The Cooley's Reel", "key": "G", "notes": [20, 30, 20, 30, 30, 40, 20]},
    {"title": "The Banshee",     "key": "D", "notes": [80, 70, 60, 50, 40, 30, 40]}
]

# Variable to remember which tune the user clicked on
current_tune = None

def setup():
    py5.size(500, 500)
    py5.window_title("Simple Tune Viewer")
    py5.text_size(16)

def draw():
    py5.background(220) #light grey background

    # draw sidebar
    py5.fill(50)
    py5.rect(0, 0, 200, py5.height) #dark sidebar area

    # loop through our simple list and draw the titles
    for i, tune in enumerate(MY_TUNES):
        # highlight the tune if it is the currently selected one
        if tune == current_tune:
            py5.fill(100, 255, 100) # green
        else:
            py5.fill(255)           # white

        # draw the text at a specific y position based on its index
        x_position = 20
        y_position = 40 * (i + 1)
        py5.text(tune['title'], x_position, y_position)


    # if nothing is selected yet
    if current_tune is None:
        py5.fill(0)
        py5.text("Please click a tune on the left.", 280, 250)
    else:
        # if a tune is selected, show its details
        py5.fill(0)
        py5.text_size(16)
        py5.text(current_tune['title'], 250, 80)

        py5.text_size(26)
        py5.text(f"Key: {current_tune['key']}", 250, 120)

        # draw a simple graph representing the notes
        py5.stroke(0)
        py5.no_fill()
        py5.begin_shape()
        for i, note_value in enumerate(current_tune['notes']):
            x = 250 + (i * 50)
            y = 400 - (note_value * 2) # higher value = higher on screen
            py5.vertex(x, y)
            py5.ellipse(x, y, 5, 5) #draw a dot at the vertex
        py5.end_shape()


def mouse_clicked(e):
    global current_tune

    # only if mouse is inside the sidebar (width 200)
    if py5.mouse_x < 200:
        # calculate which item index was clicked based on Y position
        index = int((py5.mouse_y - 20) / 40)

        # make sure the index actually exists in our list
        if 0 <= index < len(MY_TUNES):
            current_tune = MY_TUNES[index]
            print(f"Selected: {current_tune['title']}")


if __name__ == "__main__":
    py5.run_sketch()