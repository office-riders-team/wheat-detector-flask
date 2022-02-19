# USE ONLY IN NOTEBOOKS WHILE TRAINING THE MODELS

import numpy as np
import cv2
import albumentations as A
import torch
import random
import matplotlib.pyplot as plt
from utils import transform_bounding_boxes, draw_bboxes


class Dataset:
    def __init__(self, pathes, bboxes=None, bboxes_format="pascal_voc", bboxes_format_return="pascal_voc", transforms=None):
        self.pathes = pathes
        self.bboxes = bboxes
        self.transforms = transforms
        self.bboxes_format = bboxes_format
        self.bboxes_format_return = bboxes_format_return
        
    def __len__(self):
        return len(self.pathes)
    
    @staticmethod
    def get_bboxes(bboxes_string):
        if bboxes_string != "no_box":
            bboxes = bboxes_string.split(";")
            new_bboxes = []
            for bbox in bboxes:
                new_bbox = bbox.split()
                new_bboxes.append(new_bbox)
        else:
            new_bboxes = []

        new_bboxes = np.asarray(new_bboxes, dtype=np.int32)
        return new_bboxes
    
    def __getitem__(self, index):
        path = self.pathes[index]
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        
        if self.bboxes is not None:
            bboxes = self.bboxes[index]
            bboxes = Dataset.get_bboxes(bboxes)
            labels = np.ones(shape=(bboxes.shape[0], ), dtype=np.int32)
            
            if self.transforms is not None:
                height, width, channels = image.shape
                bboxes = A.normalize_bbox(bboxes, cols=width, rows=height)
                augmented = self.transforms(image=image, bboxes=bboxes, class_labels=labels, class_categories=labels)
                image, bboxes = augmented["image"], augmented["bboxes"]
                bboxes = transform_bounding_boxes(bboxes, source_format=self.bboxes_format, target_format=self.bboxes_format_return)
        
            labels = np.ones(shape=(bboxes.shape[0], ), dtype=np.int32)

            image = torch.tensor(image)
            bboxes = torch.tensor(bboxes)
            labels = torch.tensor(labels)
            
            target = {
                "bboxes": bboxes,
                "labels": labels,
            }
            
            return image, target
        
        return image
    
    
    def show_samples(self, rows=1, columns=1, color=(0, 255, 255), thickness=1, coef=3):
        fig = plt.figure(figsize=(columns*coef, rows*coef))
        n_iterations = rows * columns
        n_samples = len(self)
        
        for i in range(n_iterations):
            index = random.randint(0, n_samples-1)
            path = self.pathes[index]
            image = cv2.imread(path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if self.bboxes is not None:
                bboxes = self.bboxes[index]
                bboxes = Dataset.get_bboxes(bboxes)
                image = draw_bboxes(image, bboxes, source_format="pascal_voc", color=color, thickness=thickness)
                
            ax = fig.add_subplot(rows, columns, i+1)
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
            ax.set_title(f"Sample's index: {index}", loc="left")
            ax.imshow(image)
        
        fig.show()
    
    @staticmethod
    def collate_batch(batch, inputs_device="cpu", targets_device="cpu"):
        if len(batch) == 2:
            inputs, targets = batch
            inputs = inputs.to(inputs_device)
            targets["bbox"] = [bbox.to(targets_device).float() for bbox in targets["bbox"]]
            targets["cls"] = [label.to(targets_device).float() for label in targets["cls"]]
            
            return inputs, targets
        else:
            return batch.to(inputs_device)
        
    @staticmethod
    def collate_fn(batch):
        all_images, all_bboxes, all_labels = [], [], []
        for sample in batch:
            if len(sample) == 2:
                image, target = sample
                all_images.append(image.numpy())
                
                bboxes = target["bboxes"]
                all_bboxes.append(bboxes)
                
                labels = target["labels"]
                all_labels.append(labels)
                
            else:
                image = sample
                all_images.append(image.numpy())
                
        all_images = torch.tensor(all_images, dtype=torch.float32)
        
        if (len(all_bboxes) != 0) and (len(all_labels) != 0):
            all_targets = {
                "bbox": all_bboxes,
                "cls": all_labels,
            }
        
            return all_images, all_targets
        
        return all_images
