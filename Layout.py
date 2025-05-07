import tkinter

from Text import Text
from Tag import Tag
from Constants import WIDTH, HEIGHT, HSTEP, VSTEP, DEFAULT_SIZE


# helper function and fonts cache
FONTS = {}
def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
            slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]



class Layout:
    
    def __init__(self, tokens):
        
        self.tokens = tokens
        self.display_list = []
        
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = DEFAUL_SIZE
        
        self.line = []
        self.in_title = False
        self.in_sup = False
        for tok in tokens:
            self.token(tok)
        
        self.flush()
    
    
    def token(self, tok):
        
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)

        # token can only be a text or a tag, so it's a tag
        # different styles and weights
        elif tok.tag == "i":
            style = "italic"
        elif tok.tag == "/i":
            style = "roman"
        elif tok.tag == "b":
            weight = "bold"
        elif tok.tag == "/b":
            weight = "normal"
        
        # different sizes
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        
        # line break
        elif tok.tag == "br":
            self.flush()
        # paragraph
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
        
        # titles
        elif tok.tag == "h1" and tok.attributes.get("class") == "title":
            self.flush()
            self.in_title = True
        elif tok.tag == "/h1":
            self.flush()
            self.in_title = False
            self.cursor_y += VSTEP
            
        # superscripts
        elif tok.tag == "sup":
            self.in_sup = True
            self.size //= 2
        elif tok.tag == "/sup":
            self.in_sup = False
            self.size *= 2
            
    
    # deals with text tokens
    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > WIDTH - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font, self.in_sup))
        self.cursor_x += w + font.measure(" ")
        
        
    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font, was_sup in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        
        # calculate offset to center line (if needed)
        line_width = self.line[-1][0] + self.line[-1][2].measure(self.line[-1][1]) - self.line[0][0]
        offset_x = (WIDTH - line_width) / 2 if self.in_title else 0 
        
        for x, word, font, was_sup in self.line:
            y = baseline - font.metrics("ascent")
            
            # adjust if in superscript
            if was_sup:
                # Target ascent from default font, not current font
                normal_font = get_font(self.size * 2, self.weight, self.style)
                y -= normal_font.metrics("ascent") * 0.35

                
            self.display_list.append((x + offset_x, y, word, font))
        
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        
        self.cursor_x = HSTEP
        self.line = []
        
        


def lex(body):
    out = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer: out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            tag_content = buffer.strip()
            out.append(Tag(tag_content))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out

        
        
        
