from __future__ import print_function
from PIL import Image
import os
import os.path
import errno
import numpy as np
import sys
if sys.version_info[0] == 2:
    import cPickle as pickle
else:
    import pickle

import torch.utils.data as data
from .data_utils import download_url, check_integrity
import random


class CIFAR100(data.Dataset):
    """`CIFAR10 <https://www.cs.toronto.edu/~kriz/cifar.html>`_ Dataset.

    Args:
        root (string): Root directory of dataset where directory
            ``cifar-10-batches-py`` exists.
        train (bool, optional): If True, creates dataset from training set, otherwise
            creates from test set.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        download (bool, optional): If true, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.

    """

    base_folder = 'cifar-100-python'
    url = "http://www.cs.toronto.edu/~kriz/cifar-100-python.tar.gz"
    filename = "cifar-100-python.tar.gz"
    tgz_md5 = 'eb9058c3a382ffc7106e4002c42a8d85'
    train_list = [
        ['train', '16019d7e3df5f24257cddd939b257f8d'],
    ]

    test_list = [
        ['test', 'f0ef6b0ae62326f3e7ffdfab6717acfc'],
    ]

    def __init__(self, root, train=True,
                 transform=None, target_transform=None,
                 download=False, class_list=None, data_ratio=1.):

        coarse_classes = ('aquatic_mammals', 'fish', 'flowers', 'food_containers', 
                'fruit_and_vegetables', 'household_electrical_devices', 
                'household_furniture', 'insects', 'large_carnivores', 
                'large_man-made_outdoor_things', 'large_natural_outdoor_scenes', 
                'large_omnivores_and_herbivores', 'medium_mammals', 
                'non-insect_invertebrates', 'people', 'reptiles', 'small_mammals', 
                'trees', 'vehicles_1', 'vehicles_2')

        fine_classes = ('apple', 'aquarium_fish', 'baby', 'bear', 'beaver', 'bed', 'bee', 
                        'beetle', 'bicycle', 'bottle', 'bowl', 'boy', 'bridge', 'bus', 
                        'butterfly', 'camel', 'can', 'castle', 'caterpillar', 'cattle', 
                        'chair', 'chimpanzee', 'clock', 'cloud', 'cockroach', 'couch', 
                        'crab', 'crocodile', 'cup', 'dinosaur', 'dolphin', 'elephant', 
                        'flatfish', 'forest', 'fox', 'girl', 'hamster', 'house', 
                        'kangaroo', 'keyboard', 'lamp', 'lawn_mower', 'leopard', 'lion', 
                        'lizard', 'lobster', 'man', 'maple_tree', 'motorcycle', 
                        'mountain', 'mouse', 'mushroom', 'oak_tree', 'orange', 'orchid', 
                        'otter', 'palm_tree', 'pear', 'pickup_truck', 'pine_tree', 
                        'plain', 'plate', 'poppy', 'porcupine', 'possum', 'rabbit', 
                        'raccoon', 'ray', 'road', 'rocket', 'rose', 'sea', 'seal', 
                        'shark', 'shrew', 'skunk', 'skyscraper', 'snail', 'snake', 
                        'spider', 'squirrel', 'streetcar', 'sunflower', 'sweet_pepper', 
                        'table', 'tank', 'telephone', 'television', 'tiger', 'tractor', 
                        'train', 'trout', 'tulip', 'turtle', 'wardrobe', 'whale', 
                        'willow_tree', 'wolf', 'woman', 'worm')

        classes_c2f = {'aquatic_mammals': ['beaver','dolphin','otter','seal','whale'], 
                        'fish': ['aquarium_fish','flatfish','ray','shark','trout'], 
                        'flowers': ['orchid','poppy','rose','sunflower','tulip'], 
                        'food_containers': ['bottle','bowl','can','cup','plate'], 
                        'fruit_and_vegetables': ['apple','mushroom','orange','pear','sweet_pepper'], 
                        'household_electrical_devices': ['clock','keyboard','lamp','telephone','television'], 
                        'household_furniture': ['bed','chair','couch','table','wardrobe'], 
                        'insects': ['bee','beetle','butterfly','caterpillar','cockroach'], 
                        'large_carnivores': ['bear','leopard','lion','tiger','wolf'], 
                        'large_man-made_outdoor_things': ['bridge','castle','house','road','skyscraper'], 
                        'large_natural_outdoor_scenes': ['cloud','forest','mountain','plain','sea'], 
                        'large_omnivores_and_herbivores': ['camel','cattle','chimpanzee','elephant','kangaroo'], 
                        'medium_mammals': ['fox','porcupine','possum','raccoon','skunk'], 
                        'non-insect_invertebrates': ['crab','lobster','snail','spider','worm'], 
                        'people': ['baby','boy','girl','man','woman'], 
                        'reptiles': ['crocodile','dinosaur','lizard','snake','turtle'], 
                        'small_mammals': ['hamster','mouse','rabbit','shrew','squirrel'], 
                        'trees': ['maple_tree','oak_tree','palm_tree','pine_tree','willow_tree'], 
                        'vehicles_1': ['bicycle','bus','motorcycle','pickup_truck','train'], 
                        'vehicles_2': ['lawn_mower','rocket','streetcar','tank','tractor']}

        # classes_f2c = {}
        # for idx,f_class in enumerate(fine_classes):
        #     for jdx,c_class in enumerate(coarse_classes):
        #         if f_class in classes_c2f[c_class]:
        #             classes_f2c[idx] = jdx
        #     if idx not in classes_f2c:
        #         print(idx)
        #         raise ValueError()

        # self.classes_f2c = classes_f2c

        self.root = os.path.expanduser(root)
        self.transform = transform
        self.target_transform = target_transform
        self.train = train  # training set or test set

        if download:
            self.download()

        if not self._check_integrity():
            raise RuntimeError('Dataset not found or corrupted.' +
                               ' You can use download=True to download it')

        # now load the picked numpy arrays
        if self.train:
            self.train_data = []
            self.train_labels = []
            for fentry in self.train_list:
                f = fentry[0]
                file = os.path.join(root, self.base_folder, f)
                fo = open(file, 'rb')
                if sys.version_info[0] == 2:
                    entry = pickle.load(fo)
                else:
                    entry = pickle.load(fo, encoding='latin1')
                self.train_data.append(entry['data'])
                if 'labels' in entry:
                    self.train_labels += entry['labels']
                else:
                    self.train_labels += entry['fine_labels']
                fo.close()

            self.train_data = np.concatenate(self.train_data)
            self.train_data = self.train_data.reshape((50000, 3, 32, 32))
            self.train_data = self.train_data.transpose((0, 2, 3, 1))  # convert to HWC
        else:
            f = self.test_list[0][0]
            file = os.path.join(root, self.base_folder, f)
            fo = open(file, 'rb')
            if sys.version_info[0] == 2:
                entry = pickle.load(fo)
            else:
                entry = pickle.load(fo, encoding='latin1')
            self.test_data = entry['data']
            if 'labels' in entry:
                self.test_labels = entry['labels']
            else:
                self.test_labels = entry['fine_labels']
            fo.close()
            self.test_data = self.test_data.reshape((10000, 3, 32, 32))
            self.test_data = self.test_data.transpose((0, 2, 3, 1))  # convert to HWC

        # get subset of self.train_data, self.train_labels, self.test_data, self.test_labels
        if self.train:
            self.train_labels = np.array(self.train_labels)
            idx = np.zeros(self.train_labels.shape, dtype=bool)
            for a_class in class_list:
                idx = np.logical_or(idx, self.train_labels == a_class)
            self.train_data = self.train_data[idx]
            self.train_labels = self.train_labels[idx]
            label_mapping = {a_class:idx for idx,a_class in enumerate(class_list)}
            self.train_labels = [label_mapping[a_label] for a_label in self.train_labels]
            print('training size: {}'.format(len(self.train_data)))
        else:
            self.test_labels = np.array(self.test_labels)
            idx = np.zeros(self.test_labels.shape, dtype=bool)
            for a_class in class_list:
                idx = np.logical_or(idx, self.test_labels == a_class)
            self.test_data = self.test_data[idx]
            self.test_labels = self.test_labels[idx]
            label_mapping = {a_class:idx for idx,a_class in enumerate(class_list)}
            self.test_labels = [label_mapping[a_label] for a_label in self.test_labels]
            print('testing size: {}'.format(len(self.test_data)))

        # !!!!! reduce data !!!!!
        if self.train and data_ratio < 1.:
            self.train_labels = np.array(self.train_labels)
            idx_left = np.zeros(len(self.train_data), dtype=bool)
            for i in range(len(class_list)):
                idx = np.where(self.train_labels == i)[0]
                print('class {} has {} number of data'.format(i,idx.shape[0]))
                np.random.seed(1234)
                np.random.shuffle(idx)
                idx_left[idx[0:int(len(idx)*data_ratio)]] = True
            self.train_data = self.train_data[idx_left]
            print('reduced training set has {} data'.format(len(self.train_data)))
            self.train_labels = self.train_labels[idx_left]

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        if self.train:
            img, target = self.train_data[index], self.train_labels[index]
        else:
            img, target = self.test_data[index], self.test_labels[index]

        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        img = Image.fromarray(img)

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        # map target
        #target = self.classes_f2c[target]

        #return np.asarray(img), index, target
        #print('img: {}, target: {}'.format(img, target))
        #return np.asarray(img), int(target)
        return img, target


    def __len__(self):
        if self.train:
            return len(self.train_data)
        else:
            return len(self.test_data)

    def _check_integrity(self):
        root = self.root
        for fentry in (self.train_list + self.test_list):
            filename, md5 = fentry[0], fentry[1]
            fpath = os.path.join(root, self.base_folder, filename)
            if not check_integrity(fpath, md5):
                return False
        return True

    def download(self):
        import tarfile

        if self._check_integrity():
            print('Files already downloaded and verified')
            return

        root = self.root
        download_url(self.url, root, self.filename, self.tgz_md5)

        # extract file
        cwd = os.getcwd()
        tar = tarfile.open(os.path.join(root, self.filename), "r:gz")
        os.chdir(root)
        tar.extractall()
        tar.close()
        os.chdir(cwd)

