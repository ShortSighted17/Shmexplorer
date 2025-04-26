import socket
import ssl

open_sockets = {}

class URL:
    
    def __init__(self, url):
        
        self.view_source = False
        
        # handling data scheme:
        if url.startswith("data:"):
            self.scheme = "data"
            self.data = url[len("data:"):]
            return
        
        # handling view-source scheme:
        if url.startswith("view-source:"):
            self.view_source = True
            url = url[len("view-source:"):]  # skip "view-source"

        
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file", "data", "view-source"]
        
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
        
        # handling actual internet addresses:
        MAX_REDIRECTS = 10
        redirect_counter = 0
        while True:
            # only create a new socket if there isn't an open one
            if (self.host, self.port) not in open_sockets.keys():
                s = socket.socket(
                    family = socket.AF_INET,
                    type = socket.SOCK_STREAM,
                    proto = socket.IPPROTO_TCP
                )
                s.connect((self.host, self.port))
                
                if self.scheme == "https":
                    ctx = ssl.create_default_context()
                    s = ctx.wrap_socket(s, server_hostname=self.host)
                    
                open_sockets[(self.host, self.port)] = s
            # if socket is in open_sockets just use the open socket
            else:
                s = open_sockets[(self.host, self.port)]
            
            # create and send request
            request = "GET {} HTTP/1.1\r\n".format(self.path)
            request += "Host: {}\r\n".format(self.host)
            request += "Connection: keep-alive\r\n"
            request += "User-Agent: Internet Shmexplorer\r\n"
            request += "\r\n"
            s.send(request.encode("utf8"))
            
            # recieve response
            response = s.makefile("rb", newline=b"\r\n")
            statusline = response.readline().decode("utf8")
            version, status, explanation = statusline.split(" ", 2)
            
            response_headers = {}
            while True:
                line = response.readline()
                line = line.decode("utf8")
                if line == "\r\n":
                    break
                if ":" in line:
                    header, value = line.split(":", 1)
                    response_headers[header.casefold()] = value.strip()
            
            # handle redirects (error codes 300 - 399)
            if status.startswith("3") and "location" in response_headers:
                
                location = response_headers["location"]
                
                # location is an absolute path
                if location.startswith("http://") or location.startswith("https://"):
                    new_url = URL(location)
                # location is a relative path
                else:
                    new_url = URL("{}://{}{}".format(self.scheme, self.host, location))
                    
                self.scheme = new_url.scheme
                self.host = getattr(new_url, 'host', None)
                self.port = getattr(new_url, 'port', None)
                self.path = new_url.path
                self.data = getattr(new_url, 'data', None)
                                
                redirect_counter += 1
                if redirect_counter >= MAX_REDIRECTS:
                    raise Exception("Too many redirects")
                
                continue # if redirected - retry with new url
                    
            
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers
            
            length = int(response_headers["content-length"])
            content = response.read(length).decode("utf8")
            
            return content