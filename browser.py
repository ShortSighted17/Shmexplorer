import tkinter

from renderer import lex

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)

    def load(self, url):
        body = url.request()
        # view source will not work, it just prints to the terminal instead of the screen
        if url.view_source:
            text = (body)
        else:
            text = lex(body)
        self.display_list = layout(text)
        self.draw()
        
            
    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)
            
    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()
            
           




def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH + HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list
        
        
         