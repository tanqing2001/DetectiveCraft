from PIL import Image


def background_resize(file_path):
    # base_width= 300
    # img = Image.open('somepic.jpg')
    # wpercent = (base_width / float(img.size[0]))
    # hsize = int((float(img.size[1]) * float(wpercent)))
    # img = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
    # img.save('somepic.jpg')
    return file_path


def character_resize(file_path):
    base_height= 500
    
    img = Image.open(file_path)
    if base_height == float(img.size[1]):
        return file_path
    
    wpercent = (base_height / float(img.size[1]))
    wsize = int((float(img.size[0]) * float(wpercent)))
    img = img.resize((wsize, base_height), Image.Resampling.LANCZOS)
    
    new_file = file_path.split('.')[0] + '_resize.' + file_path.split('.')[1]
    img.save(new_file)
    return new_file
    