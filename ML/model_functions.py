from torch.utils.data import Dataset
import cv2
import numpy as np
from math import tan, radians

import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2




class WheatTestDataset(Dataset):

    def __init__(self, dataframe, image_dir, img_format, transforms=None):
        super().__init__()

        self.image_ids = dataframe['image_id'].unique()
        self.df = dataframe
        self.image_dir = image_dir
        self.transforms = transforms
        self.img_format = img_format

    def __getitem__(self, index: int):

        image_id = self.image_ids[index]

        image = cv2.imread(f'{self.image_dir}/{image_id}.{self.img_format}', cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32)
        image /= 255.0

        if self.transforms:
            sample = {
                'image': image,
            }
            sample = self.transforms(**sample)
            image = sample['image']

        return image, image_id

    def __len__(self) -> int:
        return self.image_ids.shape[0]


def get_test_transform():
    """Albumentations"""
    return A.Compose([
        # A.Resize(512, 512),
        ToTensorV2(p=1.0)
    ])


def collate_fn(batch):
    return tuple(zip(*batch))


def format_prediction_string(boxes, scores):
    pred_strings = []
    for j in zip(scores, boxes):
        pred_strings.append("{0:.4f} {1} {2} {3} {4}".format(j[0], j[1][0], j[1][1], j[1][2], j[1][3]))

    return " ".join(pred_strings)


def calculate_photo_area(height):
    height -= 105
    height /= 100
    return round((2*height/tan(radians(30))) * (2*height/tan(radians(55))), 5)
