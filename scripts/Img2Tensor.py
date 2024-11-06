import torchvision.transforms as transforms
import torch
import PIL.Image as Image

img = Image.open("imgs/Test.jpg")
print(img.size)

transform = transforms.ToTensor()
tensor = transform(img)
print(tensor.shape)

# save
torch.save(tensor, "imgs/Test.pt")