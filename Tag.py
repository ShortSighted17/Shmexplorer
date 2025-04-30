class Tag:
    def __init__(self, tag):
        parts = tag.split()
        self.tag = parts[0]
        self.attributes = {}
        for part in part[1:]:
            if "=" in part:
                key, value = part.split('=', 1)
                self.attributes[key] = value.strip('"')