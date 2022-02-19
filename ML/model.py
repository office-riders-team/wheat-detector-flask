import pandas as pd
import os

import torch
import torchvision

from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torch.utils.data import DataLoader

from .model_functions import *


def make_test_df(dir_from):
    d = {'image_id': [], 'PredictionString': []}

    for filename in os.listdir(dir_from):
        f = os.path.join(dir_from, filename)
        if os.path.isfile(f):
            d['image_id'].append(filename)
            d['PredictionString'].append('1.0 0 0 50 50')
    return pd.DataFrame(data=d)


def make_model():
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=False, pretrained_backbone=False)

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    num_classes = 2
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    model.load_state_dict(torch.load('ML/best_model.pth', map_location=torch.device('cpu')))
    model.eval()

    model = model.to(device)
    return model


def make_predictions(dir_from, dir_to, img_heights):

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model = make_model()

    test_dataset = WheatTestDataset(make_test_df(dir_from), dir_from, get_test_transform())

    test_data_loader = DataLoader(
        test_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=0,
        drop_last=False,
        collate_fn=collate_fn
    )

    # ==========================================================
    detection_threshold = 0.4
    filed_lst = []

    for images, image_ids in test_data_loader:
        """
        this function makes predictions
        returns: total wheat amount
        """

        images = list(image.to(device) for image in images)
        outputs = model(images)

        for i, image in enumerate(images):

            boxes = outputs[i]['boxes'].data.cpu().numpy()
            scores = outputs[i]['scores'].data.cpu().numpy()

            boxes = boxes[scores >= detection_threshold].astype(np.int32)
            scores = scores[scores >= detection_threshold]
            image_id = image_ids[i]

            boxes[:, 2] = boxes[:, 2] - boxes[:, 0]
            boxes[:, 3] = boxes[:, 3] - boxes[:, 1]

            boxes = outputs[-1]['boxes'].data.cpu().numpy()
            scores = outputs[-1]['scores'].data.cpu().numpy()

            boxes = boxes[scores >= detection_threshold].astype(np.int32)

            wheat_on_photo = len(boxes)
            photo_area = calculate_photo_area(int(img_heights[image_id]))
            wheat_by_meter = round(wheat_on_photo / photo_area, 5)
            filed_lst.append((image_id, wheat_on_photo, photo_area, wheat_by_meter))

            original_image = cv2.imread(f'{dir_from}/{image_id}')
            for box in boxes:
                cv2.rectangle(original_image,
                              (box[0], box[1]),
                              (box[2], box[3]),
                              (0, 0, 220), 2)

            cv2.imwrite(f'{dir_to}/{image_id}', original_image)

    return filed_lst
