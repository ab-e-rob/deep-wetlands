
import os
import time

import cv2
import numpy as np
import pandas
import tqdm
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from PIL import Image

from wetlands import train_model, utils, viz_utils, map_wetlands


def visualize_predicted_image(image, model, device, file_name, model_name):
    study_area = os.getenv('STUDY_AREA')
    patch_size = int(os.getenv('PATCH_SIZE'))
    width = image.shape[0] - image.shape[0] % patch_size
    height = image.shape[1] - image.shape[1] % patch_size
    if model_name == 'otsu':
        pred_mask = otsu_threshold(image)
    elif model_name == 'otsu_gaussian':
        kernel_size = os.getenv('OTSU_GAUSSIAN_KERNEL_SIZE')
        model_name += '_' + kernel_size
        pred_mask = otsu_gaussian_threshold(image, int(kernel_size))
    else:
        pred_mask = map_wetlands.predict_water_mask(image, model, device)

    unique, counts = np.unique(pred_mask, return_counts=True)
    results = dict(zip(unique, counts))
    image_date = file_name[17:25]
    satellite = file_name[0:3]
    results['Date'] = image_date
    results['Satellite'] = satellite
    results['File_name'] = file_name

    images_dir = f'/tmp/descending_{model_name}_{study_area}_exported_images/'

    if not os.path.isdir(images_dir):
        os.mkdir(images_dir)

    # Plotting SAR
    plt.imshow(image[:width, :height], cmap='gray')
    plt.imsave(images_dir + image_date + '_' + file_name + '_sar.png', image)

    # Plotting prediction
    plt.imshow(pred_mask)
    plt.imsave(images_dir + image_date + '_' + file_name + '_pred.png', pred_mask)
    img = Image.fromarray(np.uint8((pred_mask) * 255), 'L')
    img.save(images_dir + image_date + '_' + file_name + '_pred_bw.png')

    return results


def get_prediction_image(tiff_file, band, model, device, model_name):
    image = viz_utils.load_image(tiff_file, band, ignore_nan=True)

    if image is None:
        return None

    file_name = os.path.basename(tiff_file)
    results = visualize_predicted_image(image, model, device, file_name, model_name)
    return results


def otsu_threshold(image):
    image = ((image - image.min()) * (1 / (image.max() - image.min()) * 255)).astype('uint8')

    # Apply Otsu's thresholding on image
    threshold, thresholded_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresholded_image = 1 - ((thresholded_image - thresholded_image.min()) / (thresholded_image.max() - thresholded_image.min()))

    return thresholded_image


def otsu_gaussian_threshold(image, kernel_size=5):
    image = ((image - image.min()) * (1 / (image.max() - image.min()) * 255)).astype('uint8')

    # Apply Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    threshold, thresholded_image = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresholded_image = 1 - ((thresholded_image - thresholded_image.min()) / (thresholded_image.max() - thresholded_image.min()))

    return thresholded_image


def plot_results(model_name):
    if model_name == 'otsu_gaussian':
        model_name += '_' + os.getenv('OTSU_GAUSSIAN_KERNEL_SIZE')

    study_area = os.getenv('STUDY_AREA')
    # results_file = '/tmp/water_estimates_flacksjon_2018-07.csv'
    results_file = f'/tmp/descending_{model_name}_{study_area}_water_estimates.csv'
    data_frame = pandas.read_csv(results_file, usecols=['1.0', 'Date'], index_col=["Date"],  parse_dates=["Date"])

    data_frame.plot(title=model_name)
    plt.savefig(f'/tmp/charts/descending_{model_name}_{study_area}_water_estimates.png')
    plt.show()


def update_water_estimates(model_name):
    study_area = os.getenv('STUDY_AREA')
    if model_name == 'otsu_gaussian':
        model_name += '_' + os.getenv('OTSU_GAUSSIAN_KERNEL_SIZE')

    with open('/Users/frape/tmp/cropped_images/cropped_images.txt') as file:
        lines = [line.rstrip() for line in file]
        results_file = f'/tmp/descending_{model_name}_{study_area}_water_estimates.csv'
        data_frame = pandas.read_csv(results_file, usecols=['1.0', 'Date', 'File_name'],  parse_dates=["Date"])
        print(data_frame.size)
        print(data_frame.columns.values)
        data_frame = data_frame[~data_frame['File_name'].isin(lines)]
        data_frame.drop(['File_name'], axis=1, inplace=True)
        data_frame = data_frame[data_frame['Date'].dt.month.isin([4, 5, 6, 7, 8, 9, 10, 11])]
        # data_frame = data_frame[data_frame['Date'].dt.year.isin([2018, 2019, 2020, 2021, 2022])]
        print(data_frame.size)
        print(data_frame.columns.values)

        data_frame.plot(x='Date', y='1.0', kind='scatter', title=model_name)
        plt.savefig(f'/tmp/charts/scatter_descending_{model_name}_{study_area}_new_water_estimates_filtered.png')
        plt.show()

        data_frame.to_csv(f'/tmp/descending_{model_name}_{study_area}_new_water_estimates_filtered.csv')


def full_cycle(model_name):
    load_dotenv()

    tiff_dir = os.getenv('BULK_EXPORT_DIR')

    if not os.path.exists(tiff_dir):
        raise FileNotFoundError(f'The folder containing the TIFF files does not exist: {tiff_dir}')

    filenames = next(os.walk(tiff_dir), (None, None, []))[2]  # [] if no file
    print(filenames)

    device = utils.get_device()
    model_file = os.getenv('MODEL_FILE')
    # model_file = '/tmp/fresh-water-204_Orebro lan_mosaic_2018-07-04_sar_VH_20-epochs_0.00005-lr_42-rand.pth'
    study_area = os.getenv('STUDY_AREA')
    sar_polarization = os.getenv('SAR_POLARIZATION')
    model_dir = os.getenv('MODELS_DIR')
    model_name = os.getenv("MODEL_NAME")
    run_name = os.getenv("RUN_NAME")
    model_file = f'{run_name}_{model_name}.pth'
    model_path = os.path.join(model_dir, model_file)
    if model_name not in ['otsu', 'otsu_gaussian']:
        model = train_model.load_model(model_path, device)
    else:
        model = None

    results_list = []
    incomplete_images = 0

    for tiff_file in tqdm.tqdm(sorted(filenames)):
        results = get_prediction_image(tiff_dir + '/' + tiff_file, sar_polarization, model, device, model_name)

        if results is None:
            incomplete_images += 1
        else:
            results_list.append(results)

    print(f'There were a total of {incomplete_images} incomplete images')

    if model_name == 'otsu_gaussian':
        model_name += '_' + os.getenv('OTSU_GAUSSIAN_KERNEL_SIZE')

    data_frame = pandas.DataFrame(results_list)
    data_frame['Date'] = data_frame['Date'].apply(pandas.to_datetime).dt.date
    print(data_frame.head())
    data_frame.to_csv(f'/tmp/descending_{model_name}_{study_area}_water_estimates.csv')


def main():
    load_dotenv()

    # model_name = 'otsu'
    # model_name = 'otsu_gaussian'
    model_name = os.getenv('MODEL_NAME')
    full_cycle(model_name)
    plot_results(model_name)
    update_water_estimates(model_name)
    # viz_utils.transform_ndwi_tiff_to_grayscale_png()
    # viz_utils.transform_rgb_tiff_to_png()
    # study_area = os.getenv('STUDY_AREA')
    # ndwi_tiff_dir = f'/tmp/bulk_export_{study_area}_ndwi/'
    # rgb_tiff_dir = f'/tmp/bulk_export_{study_area}_rgb/'
    # viz_utils.transform_ndwi_tiff_to_grayscale_png(ndwi_tiff_dir, 'NDWI-mask')
    # viz_utils.transform_rgb_tiff_to_png(rgb_tiff_dir)


start = time.time()
main()
end = time.time()
total_time = end - start
print("%s: Total time = %f seconds" % (time.strftime("%Y/%m/%d-%H:%M:%S"), total_time))
