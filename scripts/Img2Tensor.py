import torchvision.transforms as transforms
import torch
import cv2 as cv

img = cv.imread("imgs\Test.png")
print(img.shape)

transform = transforms.ToTensor()
tensor = transform(img)
print(tensor.shape)

# save
torch.save(tensor, "imgs/Test.pt")