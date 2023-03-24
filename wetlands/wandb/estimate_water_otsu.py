import os
import time

import cv2
import numpy as np
import pandas
import tqdm

from dotenv import load_dotenv
from matplotlib import pyplot as plt
import rasterio as rio
from PIL import Image


def load_image(dir_path, band):

    tiff_image = rio.open(dir_path)
    band_index = tiff_image.descriptions.index(band)

    numpy_image = tiff_image.read(band_index+1)

    # If the image is incomplete and has NaN values we ignore it
    if np.isnan(numpy_image).any():
        return None

    min_value = np.nanpercentile(numpy_image, 1)
    max_value = np.nanpercentile(numpy_image, 99)

    numpy_image[numpy_image > max_value] = max_value
    numpy_image[numpy_image < min_value] = min_value

    array_min, array_max = np.nanmin(numpy_image), np.nanmax(numpy_image)
    normalized_array = (numpy_image - array_min) / (array_max - array_min)
    normalized_array[np.isnan(normalized_array)] = 0

    return normalized_array


def visualize_predicted_image_otsu(image, file_name):
    study_area = os.getenv('STUDY_AREA')

    images_dir = f'/tmp/descending_otsu_{study_area}_exported_images/'

    if not os.path.isdir(images_dir):
        os.mkdir(images_dir)

    patch_size = int(os.getenv('PATCH_SIZE'))
    width = image.shape[0] - image.shape[0] % patch_size
    height = image.shape[1] - image.shape[1] % patch_size
    pred_mask = otsu_gaussian_threshold(image)

    unique, counts = np.unique(pred_mask, return_counts=True)
    results = dict(zip(unique, counts))
    image_date = file_name[17:25]
    satellite = file_name[0:3]
    results['Date'] = image_date
    results['Satellite'] = satellite
    results['File_name'] = file_name

    # Plotting SAR
    plt.imshow(image[:width, :height], cmap='gray')
    plt.imsave(images_dir + image_date + '_' + file_name + '_sar.png', image)

    # Plotting prediction
    plt.imshow(pred_mask)
    plt.imsave(images_dir + image_date + '_' + file_name + 'otsu_pred.png', pred_mask)
    img = Image.fromarray(np.uint8((pred_mask) * 255), 'L')
    img.save(images_dir + image_date + '_' + file_name + 'otsu_pred_bw.png')

    return results


def get_prediction_image_otsu(tiff_file, band):
    # tif_file = os.getenv('SAR_TIFF_FILE')
    image = load_image(tiff_file, band)

    if image is None:
        return None

    file_name = os.path.basename(tiff_file)
    results = visualize_predicted_image_otsu(image, file_name)
    return results


def otsu_gaussian_threshold(image):
    image = ((image - image.min()) * (1 / (image.max() - image.min()) * 255)).astype('uint8')

    # Apply Otsu's thresholding on image
    otsu_threshold, thresholded_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Apply Otsu's thresholding after Gaussian filtering
    # blur = cv2.GaussianBlur(image, (5, 5), 0)
    # otsu_threshold, thresholded_image = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresholded_image = 1 - ((thresholded_image - thresholded_image.min()) / (thresholded_image.max() - thresholded_image.min()))

    return thresholded_image


def full_cycle_otsu():
    load_dotenv()

    tiff_dir = os.getenv('BULK_EXPORT_DIR')

    if not os.path.exists(tiff_dir):
        raise FileNotFoundError(f'The folder containing the TIFF files does not exist: {tiff_dir}')

    filenames = next(os.walk(tiff_dir), (None, None, []))[2]  # [] if no file
    print(filenames)

    study_area = os.getenv('STUDY_AREA')
    sar_polarization = os.getenv('SAR_POLARIZATION')

    results_list = []
    incomplete_images = 0

    for tiff_file in tqdm.tqdm(sorted(filenames)):
        results = get_prediction_image_otsu(tiff_dir + '/' + tiff_file, sar_polarization)

        if results is None:
            incomplete_images += 1
        else:
            results_list.append(results)

    print(f'There were a total of {incomplete_images} incomplete images')

    data_frame = pandas.DataFrame(results_list)
    data_frame['Date'] = data_frame['Date'].apply(pandas.to_datetime).dt.date
    print(data_frame.head())
    data_frame.to_csv(f'/tmp/descending_otsu_{study_area}_water_estimates.csv')


def plot_results():
    model_name = os.getenv('MODEL_NAME')
    study_area = os.getenv('STUDY_AREA')
    model_name = 'otsu'
    # results_file = '/tmp/water_estimates_flacksjon_2018-07.csv'
    results_file = f'/tmp/descending_{model_name}_{study_area}_water_estimates.csv'
    data_frame = pandas.read_csv(results_file, usecols=['1.0', 'Date'], index_col=["Date"],  parse_dates=["Date"])

    data_frame.plot(title=model_name)
    plt.savefig(f'/tmp/charts/descending_{model_name}_{study_area}_water_estimates.png')
    plt.show()


def update_water_estimates():
    model_name = os.getenv('MODEL_NAME')
    study_area = os.getenv('STUDY_AREA')
    model_name = 'otsu'

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

        # data_frame.to_csv(f'/tmp/descending_otsu_{study_area}_new_water_estimates_filtered.csv')


def main():
    load_dotenv()

    full_cycle_otsu()
    plot_results()
    update_water_estimates()


start = time.time()
main()
end = time.time()
total_time = end - start
print("%s: Total time = %f seconds" % (time.strftime("%Y/%m/%d-%H:%M:%S"), total_time))