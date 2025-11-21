from PIL import Image
import glob, os
root = r'd:\Polyu program\Judgment in Fifteen Days'
patterns = ['* day.png', 'Text box.png', 'option.png', '1 day.png']
print('Scanning image files in', root)
for pattern in patterns:
    for p in glob.glob(os.path.join(root, pattern)):
        try:
            im = Image.open(p)
            print(os.path.basename(p).ljust(20), im.size, 'mode=', im.mode)
        except Exception as e:
            print('Error reading', p, e)
# also list all day images
print('\nAll day images:')
for p in sorted(glob.glob(os.path.join(root, '* day.png'))):
    try:
        im = Image.open(p)
        print(os.path.basename(p).ljust(20), im.size, 'mode=', im.mode)
    except Exception as e:
        print('Error reading', p, e)
