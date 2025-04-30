from url import URL, open_sockets
from browser import Browser
import tkinter
import sys
           
            
    
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = (URL(sys.argv[1]))
    else:
        url = URL("https://browser.engineering/examples/example2-rtl.html") # testing rtl
        # url = URL("https://browser.engineering/examples/xiyouji.html") # journey to the west
        # url = URL("file:///Users/roinu/OneDrive/שולחן העבודה/Side Projects/Shmexplorer/default.html") # actual default    
        
        
    Browser().load(url)
    tkinter.mainloop()