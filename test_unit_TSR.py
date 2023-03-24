import os
import random
import sys
from glob import glob

import cv2
import numpy as np
import torchvision.transforms.functional as F
from skimage.color import rgb2gray
from skimage.feature import canny
from torch.utils.data import Dataset
import pickle
import skimage.draw
import torch
from torch.utils.data.distributed import DistributedSampler
from torch.utils.data.dataloader import DataLoader

sys.path.append('..')


def to_int(x):
    return tuple(map(int, x))

class ContinuousEdgeLineDatasetMask_video(Dataset):

    def __init__(self, pt_dataset, mask_path=None, test_mask_path=None, is_train=False, mask_rates=None,
                 frame_size=256, line_path=None):

        self.is_train = is_train
        self.pt_dataset = pt_dataset # image dataset (a .txt file that indicates the directory of each images)

        self.video_id_list = []  # create 2D arrays [video, frames]
        n_video = 0
        frames = []
        with open(self.pt_dataset) as f:
            for line in f:
                if "video " in line:  # a new video case
                    if n_video != 0:
                        self.video_id_list.append(frames)
                        frames = []
                    n_video += 1
                else: frames.append(line.strip())  # 從指定的training image txt讀入所有要訓練的image的路徑，此list裡面每一個element就是一張RGB圖片
            self.video_id_list.append(frames)  # append the last

        if is_train:
            # training mask TYPE1: irregular mask
            self.irregular_mask_list = []
            with open(mask_path[0]) as f:
                for line in f:
                    self.irregular_mask_list.append(line.strip())
            self.irregular_mask_list = sorted(self.irregular_mask_list, key=lambda x: x.split('/')[-1])
            # training mask TYPE2: segmentation mask
            # self.segment_mask_list = []
            # with open(mask_path[1]) as f:
            #     for line in f:
            #         self.segment_mask_list.append(line.strip())
            # self.segment_mask_list = sorted(self.segment_mask_list, key=lambda x: x.split('/')[-1])
        else:  # TBD: change to video version
            self.mask_list = glob(test_mask_path + '/*')  # 在測試時，mask的路徑預設為一個資料夾，因此在建立mask list時要將參數給定的mask路徑下所有個圖片都讀入，glob為取得所有的檔案的路徑
            self.mask_list = sorted(self.mask_list, key=lambda x: x.split('/')[-1])

        self.frame_size = frame_size  # 設定圖片大小：預設訓練的圖片大小為固定
        self.training = is_train  # 是否為訓練模式
        # self.mask_rates = mask_rates  # 設定mask的比例, 'irregular rate, coco rate, addition rate': 0.4, 0.8, 1.0
        self.mask_rates = [1.0, 0., 0.]
        self.line_path = line_path  # 設定預先使用wireframe偵測儲存下來的圖片
        self.wireframe_th = 0.85

    def __len__(self):
        return len(self.video_id_list)  # 有多少組訓練影片

    def resize(self, img, height, width, center_crop=False):  # resize成正方形
        imgh, imgw = img.shape[0:2]

        if center_crop and imgh != imgw:
            # center crop
            side = np.minimum(imgh, imgw)
            j = (imgh - side) // 2
            i = (imgw - side) // 2
            img = img[j:j + side, i:i + side, ...]

        if imgh > height and imgw > width:
            inter = cv2.INTER_AREA
        else:
            inter = cv2.INTER_LINEAR
        img = cv2.resize(img, (height, width), interpolation=inter)
        return img

    def load_mask(self, img, video_idx, frame_idx):
        imgh, imgw = img.shape[0:2]

        # test mode: load mask non random
        if self.training is False:
            mask = cv2.imread(self.mask_list[video_idx][frame_idx], cv2.IMREAD_GRAYSCALE)  # 以灰階的模式取得mask的路徑
            mask = cv2.resize(mask, (imgw, imgh), interpolation=cv2.INTER_NEAREST)
            mask = (mask > 127).astype(np.uint8) * 255
            return mask
        else:  # train mode: 40% mask with random brush, 40% mask with coco mask, 20% with additions
            rdv = random.random()
            if rdv < self.mask_rates[0]:
                mask_index = random.randint(0, len(self.irregular_mask_list) - 1)
                mask = cv2.imread(self.irregular_mask_list[mask_index],
                                  cv2.IMREAD_GRAYSCALE)
            elif rdv < self.mask_rates[1]:
                mask_index = random.randint(0, len(self.segment_mask_list) - 1)
                mask = cv2.imread(self.segment_mask_list[mask_index],
                                  cv2.IMREAD_GRAYSCALE)
            else:
                mask_index1 = random.randint(0, len(self.segment_mask_list) - 1)
                mask_index2 = random.randint(0, len(self.irregular_mask_list) - 1)
                mask1 = cv2.imread(self.segment_mask_list[mask_index1],
                                   cv2.IMREAD_GRAYSCALE).astype(np.float)
                mask2 = cv2.imread(self.irregular_mask_list[mask_index2],
                                   cv2.IMREAD_GRAYSCALE).astype(np.float)
                mask = np.clip(mask1 + mask2, 0, 255).astype(np.uint8)  # 混合irregular mask和segmentation mask兩種

            if mask.shape[0] != imgh or mask.shape[1] != imgw:
                mask = cv2.resize(mask, (imgw, imgh), interpolation=cv2.INTER_NEAREST)
            mask = (mask > 127).astype(np.uint8) * 255  # threshold due to interpolation
            return mask

    def load_irregular_mask(self, img, irr_dx):
        imgh, imgw = img.shape[0:2]

        mask = cv2.imread(self.irregular_mask_list[irr_dx], cv2.IMREAD_GRAYSCALE)
        if mask.shape[0] != imgh or mask.shape[1] != imgw:
            mask = cv2.resize(mask, (imgw, imgh), interpolation=cv2.INTER_NEAREST)
        mask = (mask > 127).astype(np.uint8) * 255  # threshold due to interpolation
        return mask

    def to_tensor(self, img, norm=False):
        # img = Image.fromarray(img)
        img_t = F.to_tensor(img).float()
        if norm:
            img_t = F.normalize(img_t, mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        return img_t

    def load_edge(self, img):
        return canny(img, sigma=2, mask=None).astype(np.float)

    def load_wireframe(self, video_idx, frame_idx, size):
        selected_video_frame_name = self.video_id_list[video_idx][frame_idx]
        video_case, frame_no = selected_video_frame_name.split("/")[-2:]
        line_name = os.path.join(self.line_path, video_case, frame_no).replace('.png', '.pkl').replace('.jpg', '.pkl')
        wf = pickle.load(open(line_name, 'rb'))  # 讀入對應的wireframe檔
        lmap = np.zeros((size, size))
        for i in range(len(wf['scores'])):  # 所有偵測到的線條
            if wf['scores'][i] > self.wireframe_th:  # 依序檢查，有超過threshold的線條才會拿來使用
                line = wf['lines'][i].copy()
                line[0] = line[0] * size
                line[1] = line[1] * size
                line[2] = line[2] * size
                line[3] = line[3] * size
                rr, cc, value = skimage.draw.line_aa(*to_int(line[0:2]), *to_int(line[2:4]))
                lmap[rr, cc] = np.maximum(lmap[rr, cc], value)
        return lmap

    def __getitem__(self, idx):
        # selected_img_name = self.image_id_list[idx]  # 目前訓練的image case名字
        video_name, frame_no = self.video_id_list[idx][0].split("/")[-2:]
        selected_video = self.video_id_list[idx]  # 目前訓練的image case名字
        frame_list = []  # 最後用np.stact(frame_list) 把所有的三維frame(H, W, C)疊成 video(t H, W, C)
        edge_list = []
        line_list = []
        mask_list = []
        irr_mask_index = random.randint(0, len(self.irregular_mask_list) - 1)  # 只適用在假設每個影片的frame都被遮擋同樣的固定區塊

        for frame_idx, frame_name in enumerate(selected_video):
            frame = cv2.imread(frame_name)  # 讀取此image的rgb版本
            while frame is None:
                print('Bad image {}...'.format(frame_name))
                idx = random.randint(0, len(selected_video) - 1)
                frame = cv2.imread(selected_video[idx])
            frame = frame[:, :, ::-1]  # RGB轉成BGR

            frame = self.resize(frame, self.frame_size, self.frame_size, center_crop=False)  # 切割成正方形

            frame_gray = rgb2gray(frame)
            edge = self.load_edge(frame_gray)  # canny edge
            line = self.load_wireframe(video_idx=idx, frame_idx=frame_idx, size=self.frame_size)
            # load mask
            # mask = self.load_mask(img=img, video_idx=idx, frame_idx=frame_idx)
            mask = self.load_irregular_mask(img=frame, irr_dx=irr_mask_index)

            # augment data -> 左右反射
            # if self.training is True:
            #     if random.random() < 0.5:
            #         img = img[:, ::-1, ...].copy()
            #         edge = edge[:, ::-1].copy()
            #         line = line[:, ::-1].copy()
            #     if random.random() < 0.5:
            #         mask = mask[:, ::-1, ...].copy()
            #     if random.random() < 0.5:
            #         mask = mask[::-1, :, ...].copy()

            frame = self.to_tensor(frame.copy(), norm=True)  # 不加copy會錯，不知道為何
            edge = self.to_tensor(edge.copy())
            line = self.to_tensor(line.copy())
            mask = self.to_tensor(mask.copy())
            frame_list.append(frame)
            edge_list.append(edge)
            line_list.append(line)
            mask_list.append(mask)

        meta = {'frames': torch.stack(frame_list), 'masks': torch.stack(mask_list), 'edges': torch.stack(edge_list), 'lines': torch.stack(line_list),
                'name': os.path.join(video_name, frame_no)}
        return meta
    
if __name__=="__main__":
    data_path = "./data_list/davis_train_list.txt"
    mask_path = ["./data_list/irregular_mask_list.txt"]
    mask_rates = [1.0, 0., 0.]
    image_size = 256
    line_path = "./datasets/DAVIS/JPEGImages/Full-Resolution_wireframes_pkl"
    train_dataset = ContinuousEdgeLineDatasetMask_video(data_path, mask_path=mask_path, is_train=True,
                                                      mask_rates=mask_rates, frame_size=image_size,
                                                      line_path=line_path)
    
    # DistributedSampler(train_dataset, num_replicas=1,
    #                                             rank=1, shuffle=True)
    
    train_loader = DataLoader(train_dataset, pin_memory=True,
                                  batch_size=1 // 1,  # BS of each GPU  在影片中batch size只能設1
                                  num_workers=1)

    # items = next(iter(train_loader))
    for i, items in enumerate(train_loader):
        img, mask, edge, line, name = items['img'].cuda(), items['mask'].cuda(), items['edge'].cuda(), items['line'].cuda(), items['name']
        print(f"type img: {(img.shape)}")
        print(f"type mask: {(mask.shape)}")
        print(f"type edge: {(edge.shape)}")
        print(f"type line: {(line.shape)}")