import socket
import ssl
import gzip

open_sockets = {}
cache = {}

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
        
        full_url = "{}://{}{}".format(self.scheme, self.host, self.path) if self.scheme in ["http", "https"] else self.path
        if full_url in cache:
            return cache[full_url]
        
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
            request += "Accept-Encoding: gzip\r\n"
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
            
            # handle redirections
            if self.handle_redirect(response_headers, status):
                redirect_counter += 1
                if redirect_counter >= MAX_REDIRECTS:
                    raise Exception("Too many redirects")
                
                continue # if redirected - retry with new url
            
            # check if body is chunked
            if response_headers.get("transfer-encoding", "").lower() == "chunked":
                raw_content = b""
                while True:
                    chunk_size_line = response.readline().decode("utf8").strip()
                    # skip empty lines
                    if chunk_size_line == "":
                        continue
                    chunk_size = int(chunk_size_line, 16) # from hex to decimal
                    # check if done
                    if chunk_size == 0:
                        break
                    # general case:
                    chunk = response.read(chunk_size)
                    raw_content += chunk
                    response.read(2) # read the \r\n that come after the chunk
            
            # if not chunked, just read all of it
            else:
                length = int(response_headers["content-length"])
                raw_content = response.read(length)
            
            # check for compression:
            if response_headers.get("content-encoding", "").lower() == "gzip":
                raw_content = gzip.decompress(raw_content)
                
            content = raw_content.decode("utf8")
            
            # cache content before returning it
            cache_control = response_headers.get("cache-control", "").lower()
            if cache_control:
                if "max-age" in cache_control: # cache before returning. do not cache in the general case.
                    cache[full_url] = content
                    
            return content
        


   
    def handle_redirect(self, response_headers, status):
        """
        Handle 3xx redirects. Updates self fields if needed.
        Returns True if a redirect was followed, False otherwise.
        """
        if status.startswith("3") and "location" in response_headers:
            location = response_headers["location"]

            # location is an absolute path
            if location.startswith("http://") or location.startswith("https://"):
                new_url = URL(location)
            # location is a relative path
            else:
                new_url = URL("{}://{}{}".format(self.scheme, self.host, location))

            # Update self to point to the new location
            self.scheme = new_url.scheme
            self.host = getattr(new_url, 'host', None)
            self.port = getattr(new_url, 'port', None)
            self.path = new_url.path
            self.data = getattr(new_url, 'data', None)

            return True
        return False