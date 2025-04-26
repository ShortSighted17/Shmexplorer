from url import URL, open_sockets
from renderer import show
                
                
def load(url):
    body = url.request()
    if url.view_source:
        print(body)
    show(body)
    
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = (URL(sys.argv[1]))
    else:
        url = URL("file:///Users/roinu/OneDrive/שולחן העבודה/Side Projects/Shmexplorer/default.html")
        
    load(url)