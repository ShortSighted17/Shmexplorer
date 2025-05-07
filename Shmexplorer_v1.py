import tkinter
import sys

from URL import URL, open_sockets
from Browser import Browser
from HTMLParser import HTMLParser, print_tree
           
            
    
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = (URL(sys.argv[1]))
    else:
        url = URL("view-source:https://browser.engineering/html.html")
        # url = URL("https://browser.engineering/examples/example3-sizes.html") # mixed sizes in one line
        # url = URL("https://browser.engineering/examples/xiyouji.html") # journey to the west
        # url = URL("view-source:file:///Users/roinu/OneDrive/שולחן העבודה/Side Projects/Shmexplorer/default.html") # actual default
        
    Browser().load(url)
    tkinter.mainloop()
    
    
    # body = URL("https://browser.engineering/html.html").request()
    # nodes = HTMLParser(body).parse()
    # print_tree(nodes)