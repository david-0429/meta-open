import torch
import torchvision
import torchvision.transforms as transforms

from torch.utils.data import DataLoader

from dataset.miniimagenet import miniImagenet
from dataset.sampler import MetaSampler


def data_loader(opts, opts_runtime, split):

    if split == 'train':
        _curr_str = 'Train data ...'
        augment = opts.data.augment
        is_train = True
        batch_size = opts.train.batch_size
        is_shuffle = True
    elif split == 'val':
        _curr_str = 'Val data ...'
        augment = opts.data.augment_val
        is_train = False
        batch_size = opts.train.batch_size_val
        is_shuffle = False
    else:  # split == 'test':
        _curr_str = 'Test data ...'
        augment = opts.data.augment_test
        is_train = False
        batch_size = opts.train.batch_size_test
        is_shuffle = False

    # create data_loader
    if opts.data.name == 'miniimagenet':

        relative_path = 'dataset/miniImageNet/'

        opts.logger(_curr_str)
        data = miniImagenet(
            root=relative_path,
            resize=opts.data.im_size, split=split, mode=opts.train.mode, augment=augment)
        opts.logger('\t\tFind {:d} closed samples'.format(data.closed_samples))
        if data.open_samples > 0:
            opts.logger('\t\tFind {:d} open samples'.format(data.open_samples))

    elif opts.data.name == 'cifar100':
        train_transform = transforms.Compose(
                  [transforms.ToTensor(),
                   transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4),
                   transforms.RandomHorizontalFlip(0.5),
                   transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    
        val_transform = transforms.Compose(
                  [transforms.ToTensor(),
                  transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

        trainset = torchvision.datasets.CIFAR100(root='dataset/cifar10', train=True,
                                        download=True, transform=train_transform)
        data = torch.utils.data.DataLoader(trainset, batch_size=opts.train.batch_size,
                                          shuffle=True, num_workers=2)

        testset = torchvision.datasets.CIFAR100(root='dataset/cifar10', train=False,
                                       download=True, transform=val_transform)
        testloader = torch.utils.data.DataLoader(testset, batch_size=opts.train.batch_size,
                                         shuffle=False, num_workers=2)

    else:
        raise NameError('Unknown dataset ({})!'.format(opts.dataset.name))

    # turn data_loader into db
    if opts.train.mode == 'openfew':
        data_sampler = MetaSampler(data, opts_runtime, train=is_train)
        db = DataLoader(data, batch_sampler=data_sampler, num_workers=8, pin_memory=True)
    elif opts.train.mode == 'openmany':
        data_sampler = MetaSampler(data, opts_runtime, train=is_train)
        db = DataLoader(data, batch_sampler=data_sampler, num_workers=8, pin_memory=True)
    elif opts.train.mode == 'regular':
        db = DataLoader(data, batch_size, shuffle=is_shuffle, num_workers=8, pin_memory=True)

    return db
