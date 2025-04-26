from url import URL, open_sockets
from browser import Browser
import tkinter             
            
    
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = (URL(sys.argv[1]))
    else:
        # url = URL("https://httpbin.org/stream/20") # chunked
        # url = URL("http://browser.engineering/redirect") # testing redirection
        url = URL("https://browser.engineering/examples/xiyouji.html") # journey to the west
        # url = URL("file:///Users/roinu/OneDrive/שולחן העבודה/Side Projects/Shmexplorer/default.html") # actual default
        
        
    Browser().load(url)
    tkinter.mainloop()