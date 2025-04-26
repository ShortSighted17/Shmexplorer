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
