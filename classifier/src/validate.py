from schema import BBoxResult, ValidationStatistics, zero_stat, one_stat
from torchmetrics import Metric, Accuracy, AUROC, F1Score, Precision, Recall
from torchmetrics.detection.iou import IntersectionOverUnion
from typing import List, Dict
from torch import Tensor
from random import random
import logging
import torch
from connectors.chroma import collection


def compute_iou(box1, box2):
    x1_min, y1_min, w1, h1 = box1
    x1_max = x1_min + w1
    y1_max = y1_min + h1

    x2_min, y2_min, w2, h2 = box2
    x2_max = x2_min + w2
    y2_max = y2_min + h2

    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    inter_area = max(inter_x_max - inter_x_min, 0) * max(inter_y_max - inter_y_min, 0)
    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area

    return inter_area / union_area if union_area > 0 else 0


def compute_precision_recall(gt, preds, iou_threshold=0.5):
    TP = 0
    FP = 0
    FN = 0

    for idx in range(len(gt)):
        gt_boxes = gt[idx]["boxes"]
        gt_labels = gt[idx]["labels"]
        pred_boxes = preds[idx]["boxes"]
        pred_labels = preds[idx]["labels"]
        num_gt = len(gt_boxes)
        num_pred = len(pred_boxes)

        gt_matched = torch.zeros(num_gt, dtype=torch.bool)

        iou_matrix = torch.zeros((num_pred, num_gt))
        for i in range(num_pred):
            for j in range(num_gt):
                if pred_labels[i] == gt_labels[j]:
                    iou_matrix[i, j] = compute_iou(pred_boxes[i], gt_boxes[j])

        for i in range(num_pred):
            max_iou, max_j = torch.max(iou_matrix[i], dim=0)
            if max_iou >= iou_threshold and not gt_matched[max_j]:
                TP += 1
                gt_matched[max_j] = True
            else:
                FP += 1

        FN += (~gt_matched).sum().item()

    precision = TP / (TP + FP) if TP + FP > 0 else 0
    recall = TP / (TP + FN) if TP + FN > 0 else 0
    return precision, recall


def box_to_tensor(data: List[BBoxResult]):
    result = []
    for i in data:
        t = Tensor([i.x, i.y, i.w, i.h])
        result.append(t)
    return torch.stack(result)


def label_to_tensor(labels: List[str], reverse_class_maper: Dict[str, int]):
    return (
        torch.stack(
            [
                Tensor([reverse_class_maper.get(i.label, 0)]).to(torch.int16)
                for i in labels
            ]
        )
        .squeeze()
        .reshape(-1)
    )


def validate(
    predict: list[BBoxResult], true_label: list[BBoxResult]
) -> ValidationStatistics:
    if len(predict) == 0 and len(true_label) == 0:
        return one_stat
    if len(predict) == 0 or len(true_label) == 0:
        return zero_stat
    all_metadatas = collection.get(include=["metadatas"]).get("metadatas")
    CLASSES = set([x.get("class") for x in all_metadatas])

    reverse_class_maper = {string: i for i, string in enumerate(CLASSES, 1)}

    iou = IntersectionOverUnion(box_format="xywh")

    preds = [
        {
            "boxes": box_to_tensor(predict),
            "labels": label_to_tensor(predict, reverse_class_maper),
        }
    ]

    gt = [
        {
            "boxes": box_to_tensor(true_label),
            "labels": label_to_tensor(true_label, reverse_class_maper),
        }
    ]

    prec, rec = compute_precision_recall(gt, preds, iou_threshold=0.5)
    if (prec + rec)<0.0000001:
        f1 = 0.0
    else:
        f1 = prec * rec / (prec + rec)

    logging.error("gt" + str(gt))
    logging.error("preds" + str(preds))

    iou.update(preds, gt)
    iou_results = iou.compute()["iou"].item()

    return ValidationStatistics(
        iou=iou_results,
        multiclass_f1_score=f1,
        multiclass_precision=prec,
        multiclass_recall=rec,
    )


if __name__ == "__main__":
    pred = [
        BBoxResult(
            label="Двухцепная башенного типа",
            x=0.1902890625,  # + random() * 0.1,
            y=0.3348229166666667,  # + random() * 0.1,
            w=0.08817187500000001,  # + random() * 0.1,
            h=0.38690624999999995,  # + random() * 0.1
        ),
        BBoxResult(
            label="Двухцепная башенного типа",
            x=0.5357109375 + random() * 0.1,
            y=0.29464583333333333 + random() * 0.1,
            w=0.13616406249999996 + random() * 0.1,
            h=0.4047604166666666 + random() * 0.1,
        ),
        BBoxResult(
            label="Одноцепная башенного типа",
            x=0.490515625 + random() * 0.1,
            y=0.42634375 + random() * 0.1,
            w=0.04129687499999992 + random() * 0.1,
            h=0.12351041666666672 + random() * 0.1,
        ),
    ]

    gt = [
        BBoxResult(
            label="Двухцепная башенного типа",
            x=0.1902890625,  # + random() * 0.1,
            y=0.3348229166666667,  # + random() * 0.1,
            w=0.08817187500000001,  # + random() * 0.1,
            h=0.38690624999999995,  # + random() * 0.1
        ),
        BBoxResult(
            label="Двухцепная башенного типа",
            x=0.5357109375,
            y=0.29464583333333333,
            w=0.13616406249999996,
            h=0.4047604166666666,
        ),
        BBoxResult(
            label="Одноцепная башенного типа",
            x=0.490515625,
            y=0.42634375,
            w=0.04129687499999992,
            h=0.12351041666666672,
        ),
    ]
    print(validate(pred, gt))
