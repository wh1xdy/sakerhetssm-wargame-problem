from PIL import Image
from PIL import ImageFilter
from PIL import ImageColor

im = Image.open("image.png")

# manually picked the colors, might not have worked with photo of the poster
colors = ['#ff7e86', '#D64551', '#860f23', '#ff9500', '#cb5b00', '#7e2600', '#e6b900', '#a27b00', '#614200', '#89d739', '#539400', '#235600', '#00e4a9', '#009f6f', '#005e3a' ,'#00deff', '#0099b6', '#005970', '#09c6ff', '#0085e2', '#004991', '#ada8ff', '#736be6']

for c in colors:
    col = ImageColor.getrgb(c)


    im2 = im.copy()
    for x in range(im2.height):
        for y in range(im2.width):

            if im2.getpixel((y, x))[:3] != col:
                im2.putpixel((y,x), (0,0,0))

    im2.show()


# flag: SSM{färg-affischionado}