from PIL import Image

image = Image.open("image.png")

print(image)

for i in range(23):
    col = image.getpixel((125 + i*26, 575))

    char_im = Image.new(size=(818, 600), mode="RGB")
    
    for x in range(818):
        for y in range(606):
            if image.getpixel((x, y)) == col:
                char_im.putpixel((x, y), col)
    
    char_im.save("./lelle-pictures/" + str(i), "PNG")
    print(col)

image.close()