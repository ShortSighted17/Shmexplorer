import socket
import ssl


class URL:
    
    def __init__(self, url):
        
        # first we deal with "data" case:
        if url.startswith("data:"):
            self.scheme = "data"
            self.data = url[len("data"):]  # skip "data:"
            return
        
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file", "data"]
        
        if self.scheme == "file":
            self.path = url
        
        elif self.scheme == "data":
            self.data = url
        
        else:
            if "/" not in url:
                url = url + "/"
            self.host, url = url.split("/", 1)
            self.path = "/" + url
            
            # checking for custom port
            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)
            # setting port according to scheme
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443
        
        
        
    
    def request(self):
        
        # handling data:
        if self.scheme == "data":
            mediatype, data = self.data.split(",", 1)
            return data
            
        # handling local files:
        if self.scheme == "file":
            with open(self.path, encoding="utf8") as f:
                return f.read()
        
        # handling actual internet addresses
        s = socket.socket(
            family = socket.AF_INET,
            type = socket.SOCK_STREAM,
            proto = socket.IPPROTO_TCP
        )
        s.connect((self.host, self.port))
        
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        
        request = "GET {} HTTP/1.1\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        s.send(request.encode("utf8"))
        
        response = s.makefile("r", encoding = "utf8", newline = "\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {
            "Host": self.host,
            "Connection": "close",
            "User-Agent": "Internet Shmexplorer"
        }
        
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
            
        content = response.read()
        s.close()
        
        return content
    
    
def show(body):
    # buffer holds characters according to longest special case.
    # only prints what we have if wer'e sure it's not a special case
    # at the end of the file, flush the rest of the buffer
    in_tag = False
    buffer = ""
    entity_map = {
        "&lt;": "<",
        "&gt;": ">"
    }
    max_entity_len = max(len(e) for e in entity_map.keys())
    i = 0
    while i < len(body):
        c = body[i]
        if c == "<":
            in_tag = True
            i += 1
            continue
        elif c == ">":
            in_tag = False
            i += 1
            continue
        
        elif not in_tag:
            buffer += c
            
            # check for match with entities
            for entity, replacement in entity_map.items():
                if buffer.endswith(entity):
                    buffer = buffer[:-len(entity)] # trim buffer
                    print(replacement, end="") # print replacement instead
                    break
            
            if len(buffer) > max_entity_len:
                print(buffer[0], end="") # print oldest character
                buffer = buffer[1:] # trim buffer
            
            i += 1 
        else:
            i += 1 # always increment silly
    
    print(buffer, end="") # when done, flush the buffer

                
                
def load(url):
    body = url.request()
    show(body)
    
if __name__ == "__main__":
    import sys
    
    
    if len(sys.argv) > 1:
        url = (URL(sys.argv[1]))
    else:
        url = URL("file:///Users/roinu/OneDrive/שולחן העבודה/Side Projects/Shmexplorer/default.html")
        
    load(url)