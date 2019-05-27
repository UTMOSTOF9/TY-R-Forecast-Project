## import useful tools
import os
import time
import numpy as np
import pandas as pd
pd.set_option('precision', 4)
import logging

## import torch modules
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms, utils

# import our model and dataloader
from src.utils.utils import createfolder, remove_file, Adam16
from src.utils.GRUs_hparams import TRAJGRU_HYPERPARAMs, CONVGRU_HYPERPARAMs, MYMODEL_HYPERPARAMs

def get_dataloader(args, train_num=None):
    '''
    This function is used to get trainloader and testloader.
    '''
    from src.dataseters.GRUs import TyDataset, ToTensor, Normalize

    # transform
    transform = transforms.Compose([ToTensor(), Normalize(args)])
    if train_num is None:
        train_num = args.train_num

    traindataset = TyDataset(args=args, train=True, train_num=train_num, transform=transform)
    testdataset = TyDataset(args=args, train=False, train_num=train_num, transform=transform)

    # dataloader
    train_kwargs = {'num_workers': 4, 'pin_memory': True} if args.able_cuda else {}
    test_kwargs = {'num_workers': 1, 'pin_memory': True} if args.able_cuda else {}
    trainloader = DataLoader(dataset=traindataset, batch_size=args.batch_size, shuffle=True, **train_kwargs)
    testloader = DataLoader(dataset=testdataset, batch_size=args.batch_size, shuffle=False, **test_kwargs)
    
    return trainloader, testloader


def get_model(args=None):
    if args.model.upper() == 'TRAJGRU':
        from src.operators.trajGRU import Multi_unit_Model as Model
        print('Model:', args.model.upper())
        TRAJGRU = TRAJGRU_HYPERPARAMs(args=args)
        model = Model(n_encoders=args.input_frames, n_forecasters=args.target_frames, gru_link_size=TRAJGRU.gru_link_size,
                encoder_input_channel=TRAJGRU.encoder_input_channel, encoder_downsample_channels=TRAJGRU.encoder_downsample_channels,
                encoder_gru_channels=TRAJGRU.encoder_gru_channels, encoder_downsample_k=TRAJGRU.encoder_downsample_k,
                encoder_downsample_s=TRAJGRU.encoder_downsample_s, encoder_downsample_p=TRAJGRU.encoder_downsample_p, 
                encoder_gru_k=TRAJGRU.encoder_gru_k, encoder_gru_s=TRAJGRU.encoder_gru_s, encoder_gru_p=TRAJGRU.encoder_gru_p, 
                encoder_n_cells=TRAJGRU.encoder_n_cells, forecaster_input_channel=TRAJGRU.forecaster_input_channel, 
                forecaster_upsample_channels=TRAJGRU.forecaster_upsample_channels, forecaster_gru_channels=TRAJGRU.forecaster_gru_channels,
                forecaster_upsample_k=TRAJGRU.forecaster_upsample_k, forecaster_upsample_s=TRAJGRU.forecaster_upsample_s, 
                forecaster_upsample_p=TRAJGRU.forecaster_upsample_p, forecaster_gru_k=TRAJGRU.forecaster_gru_k, forecaster_gru_s=TRAJGRU.forecaster_gru_s,
                forecaster_gru_p=TRAJGRU.forecaster_gru_p, forecaster_n_cells=TRAJGRU.forecaster_n_cells, forecaster_output=TRAJGRU.forecaster_output_channels, 
                forecaster_output_k=TRAJGRU.forecaster_output_k, forecaster_output_s=TRAJGRU.forecaster_output_s, 
                forecaster_output_p=TRAJGRU.forecaster_output_p, forecaster_output_layers=TRAJGRU.forecaster_output_layers, 
                batch_norm=args.batch_norm, device=args.device, value_dtype=args.value_dtype).to(args.device, dtype=args.value_dtype)

    elif args.model.upper() == 'CONVGRU':
        from src.operators.convGRU import Multi_unit_Model as Model
        print('Model:', args.model.upper())
        CONVGRU = CONVGRU_HYPERPARAMs(args=args)
        model = Model(n_encoders=args.input_frames, n_forecasters=args.target_frames,
                encoder_input_channel=CONVGRU.encoder_input_channel, encoder_downsample_channels=CONVGRU.encoder_downsample_channels,
                encoder_gru_channels=CONVGRU.encoder_gru_channels, encoder_downsample_k=CONVGRU.encoder_downsample_k,
                encoder_downsample_s=CONVGRU.encoder_downsample_s, encoder_downsample_p=CONVGRU.encoder_downsample_p, 
                encoder_gru_k=CONVGRU.encoder_gru_k,encoder_gru_s=CONVGRU.encoder_gru_s, encoder_gru_p=CONVGRU.encoder_gru_p, 
                encoder_n_cells=CONVGRU.encoder_n_cells, forecaster_input_channel=CONVGRU.forecaster_input_channel, 
                forecaster_upsample_channels=CONVGRU.forecaster_upsample_channels, forecaster_gru_channels=CONVGRU.forecaster_gru_channels,
                forecaster_upsample_k=CONVGRU.forecaster_upsample_k, forecaster_upsample_s=CONVGRU.forecaster_upsample_s, 
                forecaster_upsample_p=CONVGRU.forecaster_upsample_p, forecaster_gru_k=CONVGRU.forecaster_gru_k, forecaster_gru_s=CONVGRU.forecaster_gru_s,
                forecaster_gru_p=CONVGRU.forecaster_gru_p, forecaster_n_cells=CONVGRU.forecaster_n_cells, forecaster_output=CONVGRU.forecaster_output_channels, 
                forecaster_output_k=CONVGRU.forecaster_output_k, forecaster_output_s=CONVGRU.forecaster_output_s, 
                forecaster_output_p=CONVGRU.forecaster_output_p, forecaster_output_layers=CONVGRU.forecaster_output_layers, 
                batch_norm=args.batch_norm, device=args.device, value_dtype=args.value_dtype).to(args.device, dtype=args.value_dtype)
    
    elif args.model.upper() == 'MYMODEL':
        from src.operators.mymodel import my_multi_GRU as Model
        print('Model:', args.model.upper())
        MYMODEL = MYMODEL_HYPERPARAMs(args)
        model = Model(MYMODEL.input_frames, MYMODEL.target_frames, MYMODEL.TyCatcher_input, MYMODEL.TyCatcher_hidden, MYMODEL.TyCatcher_n_layers, 
                    MYMODEL.encoder_input, MYMODEL.encoder_downsample, MYMODEL.encoder_gru, MYMODEL.encoder_downsample_k, MYMODEL.encoder_downsample_s, 
                    MYMODEL.encoder_downsample_p, MYMODEL.encoder_gru_k, MYMODEL.encoder_gru_s, MYMODEL.encoder_gru_p, MYMODEL.encoder_n_cells, 
                    MYMODEL.forecaster_upsample_cin, MYMODEL.forecaster_upsample_cout, MYMODEL.forecaster_upsample_k, MYMODEL.forecaster_upsample_p, 
                    MYMODEL.forecaster_upsample_s, MYMODEL.forecaster_n_layers, MYMODEL.forecaster_output_cout, MYMODEL.forecaster_output_k, 
                    MYMODEL.forecaster_output_s, MYMODEL.forecaster_output_p, MYMODEL.forecaster_n_output_layers, 
                    batch_norm=args.batch_norm, device=args.device, value_dtype=args.value_dtype).to(device=args.device, dtype=args.value_dtype)
    
    return model


def get_optimizer(args, model):
    # set optimizer
    if args.optimizer == 'Adam16':
        optimizer = Adam16(model.parameters(), lr=args.lr, weight_decay=args.weight_decay, device=args.device)
    else:
        optimizer = getattr(optim, args.optimizer)
        if args.optimizer == 'Adam16':
            optimizer = optimizer(model.parameters(), lr=args.lr, eps=1e-07, weight_decay=args.weight_decay)
        elif args.optimizer == 'SGD':
            optimizer = optimizer(model.parameters(), lr=args.lr, momentum=0.6, weight_decay=args.weight_decay)
        else:
            optimizer = optimizer(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    return optimizer


def get_train_logger(filename):
    # create logger
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create file handler and set level to debug
    f = logging.FileHandler(filename=filename)
    f.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(message)s')

    # add formatter
    ch.setFormatter(formatter)
    f.setFormatter(formatter)

    # add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(f)

    return logger


def train(model, optimizer, trainloader, testloader, args):
    '''
    This function is to train the model.
    '''
    # set file path for saveing some info.
    createfolder(args.result_folder)
    createfolder(args.params_folder)

    log_file = os.path.join(args.result_folder, 'log.txt')
    result_file = os.path.join(args.result_folder, 'result_df.csv')
    params_file = os.path.join(args.result_folder, 'params_counts.csv')
    remove_file(log_file)
    remove_file(result_file)
    remove_file(params_file)

    logger = get_train_logger(log_file)
    # Set scheduler
    if args.lr_scheduler:
        scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[x for x in range(1, args.max_epochs) if x % 7 == 0], gamma=0.7)
    
    total_batches = len(trainloader)
    
    # To create a pd.DataFrame to store training, validating loss, and learning rate.
    result_df = pd.DataFrame([], index=pd.Index(range(1, args.max_epochs+1), name='epoch'), columns=['train_loss', 'val_loss', 'lr'])

    if args.parallel_compute:
        model = torch.nn.DataParallel(model, device_ids=[0, 1])

    for epoch in range(args.max_epochs):
        # turn on train mode
        model.train(True)

        # store time
        time1 = time.time()
        
        # update the learning rate
        if args.lr_scheduler:
            scheduler.step()

        # Save the learning rate per epoch
        result_df.iloc[epoch, 2] = optimizer.param_groups[0]['lr']
        logger.debug('lr: {:.1e}'.format(optimizer.param_groups[0]['lr']))
        
        # initilaize loss
        train_loss = 0.
        running_loss = 0.

        for idx, data in enumerate(trainloader, 0):
            inputs = data['inputs'].to(device=args.device, dtype=args.value_dtype)  # inputs.shape = [batch_size, input_frames, input_channel, H, W]
            labels = data['targets'].to(device=args.device, dtype=args.value_dtype)  # labels.shape = [batch_size, target_frames, H, W]

            if args.model.upper() == 'MYMODEL':
                ty_infos = data['ty_infos'].to(device=args.device, dtype=args.value_dtype)
                radar_map = data['radar_map'].to(device=args.device, dtype=args.value_dtype)
                outputs = model(encoder_inputs=inputs, ty_infos=ty_infos, radar_map=radar_map)
            else:
                outputs = model(inputs)                           # outputs.shape = [batch_size, target_frames, H, W]

            optimizer.zero_grad()
            outputs = outputs.view(-1, outputs.shape[1]*outputs.shape[2]*outputs.shape[3])
            labels = labels.view(-1, labels.shape[1]*labels.shape[2]*labels.shape[3])

            if args.normalize_target:
                outputs = (outputs - args.min_values['QPE']) / (args.max_values['QPE'] - args.min_values['QPE'])
            
            # calculate loss function
            loss = args.loss_function(outputs, labels)
            train_loss += loss.item()/len(trainloader)
            running_loss += loss.item()/40

            # optimize model
            loss.backward()
            # 'clip_grad_norm' helps prevent the exploding gradient problem in grus or LSTMs.
            if args.clip:
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=args.clip_max_norm)
            optimizer.step()

            # print training loss per 40 batches.
            if (idx+1) % 40 == 0:
                # print the trainging results to the log file.
                logger.debug('{}|  Epoch [{}/{}], Step [{}/{}], Loss: {:.3f}'.format(args.model, epoch+1, args.max_epochs, idx+1, total_batches, running_loss))
                running_loss = 0.
        
        # save the training results.
        result_df.iloc[epoch,0] = train_loss
        logger.debug('{}|  Epoch [{}/{}], Train Loss: {:8.3f}'.format(args.model, epoch+1, args.max_epochs, train_loss))

        # Save the test loss per epoch
        test_loss = test(model, testloader=testloader, args=args)
        # print out the testing results.
        logger.debug('{}|  Epoch [{}/{}], Test Loss: {:8.3f}'.format(args.model, epoch+1, args.max_epochs, test_loss))
        # save the testing results.
        result_df.iloc[epoch,1] = test_loss.item()

        # output results per 1 epoch.
        result_df.to_csv(result_file)

        time2 = time.time()
        logger.debug('The computing time of this epoch = {:.3f} sec'.format(time2-time1))
        logger.debug(('Max allocated memory:{:.3f}GB'.format(int(torch.cuda.max_memory_allocated(device=args.gpu)/1024/1024/1024))))

        if (epoch+1) % 10 == 0 or (epoch+1) == args.max_epochs:
            params_pt = os.path.join(args.params_folder, 'params_{}.pt'.format(epoch+1))
            remove_file(params_pt)
            # save the params per 10 epochs.
            torch.save({'epoch': epoch+1,
                        'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'loss':loss},
                        params_pt
                        )

        if (epoch+1) == args.max_epochs:
            # counts the number of model weightings.
            total_params = sum(p.numel() for p in model.parameters())
            logger.debug('\{}|  Total_params: {:.2e}'.format(args.model, total_params))
            # save the number of model weightings.
            f_params = open(params_file, 'a')
            f_params.writelines('Total_params: {:.2e}\n'.format(total_params))
            f_params.close()

    print('Training process has finished!')

def continue_train(model, optimizer, trainloader, testloader, epoch, args):
    pass






def test(model, testloader, args):
    '''
    Arguments: this function is about to test the given model on test data.
    model(nn.Module): trained model
    testloader(Dataloader): the dataloader for test process.
    loss_function: loss function
    device: the device where the training process takes.
    '''
    # set evaluating process
    model.eval()
    loss = 0
    n_batch = len(testloader)

    with torch.no_grad():
        for _, data in enumerate(testloader, 0):
            inputs, labels = data['inputs'].to(args.device, dtype=args.value_dtype), data['targets'].to(args.device, dtype=args.value_dtype)
            if args.model.upper() == 'MYMODEL':
                ty_infos = data['ty_infos'].to(device=args.device, dtype=args.value_dtype)
                radar_map = data['radar_map'].to(device=args.device, dtype=args.value_dtype)
                outputs = model(encoder_inputs=inputs, ty_infos=ty_infos, radar_map=radar_map)
            else:
                outputs = model(inputs)                           # outputs.shape = [batch_size, target_frames, H, W]

            if args.normalize_target:
                outputs = (outputs - args.min_values['QPE']) / (args.max_values['QPE'] - args.min_values['QPE'])
            loss += args.loss_function(outputs, labels)/n_batch

    return loss
