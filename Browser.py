import tkinter
from tkinter import PhotoImage
import tkinter.font
import os

from URL import URL
from Layout import Layout, lex

from Constants import WIDTH, HEIGHT, HSTEP, VSTEP, SCROLL_STEP


class Browser:
    def __init__(self):        
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack(fill="both", expand=True)
        self.window.bind("<Configure>", self.on_resize)
        self.scroll = 0
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<MouseWheel>", self.mouse_scroll)
        
        self.emojis_images = {}

    def load(self, url):
        try:
            body = url.request()
        except Exception:
            url = URL("about:blank")
            body = url.request()
        
        
        if url.view_source:
            tokens = body
        else:
            tokens = lex(body)
        
        self.tokens = tokens # for use on resize if needed
        self.display_list = Layout(tokens).display_list
        self.draw()
        
            
    def draw(self):
        
        # clear previous screen
        self.canvas.delete("all")
        
        # draw text
        for x, y, word, font in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + font.metrics("linespace") < self.scroll: continue
            
            # if isinstance(c, str) and c.startswith("emoji-"):
            #     emoji_name = c[len("emoji-"):]

            #     if emoji_name not in self.emojis_images:
            #         try:
            #             path = os.path.join("emojis", "{}.png".format(emoji_name))
            #             self.emojis_images[emoji_name] = PhotoImage(file=path)
            #         except Exception:
            #             # If emoji image doesn't exist, skip it
            #             # TODO add a little default image to emojis folder to display in this case
            #             continue

            #     self.canvas.create_image(x, y - self.scroll, image=self.emojis_images[emoji_name], anchor="nw")

            # else:
            self.canvas.create_text(x, y - self.scroll, text=word, font=font, anchor="nw")
        
        # draw scrollbar
        full_height = self.content_height()
        if full_height <= HEIGHT:
            return
        
        scroll_fraction = self.scroll / (full_height - HEIGHT)
        bar_height = HEIGHT * (HEIGHT / full_height)
        bar_top = scroll_fraction * (HEIGHT - bar_height)
        
        self.canvas.create_rectangle(
            WIDTH - 10, bar_top, WIDTH, bar_top + bar_height,
            fill="blue", outline="blue"
        )
                   
    #resizing handler
    def on_resize(self, e):
        global WIDTH, HEIGHT
        WIDTH = e.width
        HEIGHT = e.height
        self.display_list = Layout(self.tokens).display_list
        self.draw()
    
    # scrolling handlers
    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        if self.scroll < 0:
            self.scroll = 0
        self.draw()
    
    def scrolldown(self, e):
        max_scroll = max(0, self.content_height() - HEIGHT)
        self.scroll = min(self.scroll + SCROLL_STEP, max_scroll)
        self.draw()
        
    def mouse_scroll(self, e):
        if e.delta > 0:
            self.scroll -= SCROLL_STEP
        else:
            self.scroll += SCROLL_STEP
        self.scroll = max(0, min(self.scroll, self.content_height() - HEIGHT))
        self.draw()
    
    # helper method for scrolling purposes
    def content_height(self):
        return max((y for x, y, word, font in self.display_list), default=0) + VSTEP
    
                

        
        
        

            
           
# emoji helper method
def is_emoji(c):
    return ord(c) >= 0x1F300

        
         