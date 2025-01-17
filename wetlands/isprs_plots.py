import math
import os
import time

import imageio
import numpy
import pandas
import seaborn
from dotenv import load_dotenv
from matplotlib import pyplot as plt


def plot_scatter():

    data_dir = os.getenv('DATA_DIR') + '/'
    model_name = os.getenv('MODEL_NAME')

    # model_2018_results = '/tmp/descending_Orebro lan_mosaic_2018-07-04_sar_VH_20-epochs_new_water_estimates_filtered.csv'
    # model_2020_results = '/tmp/descending_Orebro lan_mosaic_2020-06-23_sar_VH_20-epochs_new_water_estimates_filtered.csv'
    model_2018_results = '/tmp/descending_Orebro lan_mosaic_2018-07-04_sar_VH_20-epochs_0.00005-lr_42-rand_new_water_estimates_filtered.csv'
    model_2020_results = '/tmp/descending_Orebro lan_mosaic_2020-06-23_sar_VH_20-epochs_0.00005-lr_42-rand_new_water_estimates_filtered.csv'

    df_2018 = pandas.read_csv(model_2018_results, header=0, names=['Index', 'Extension', 'Date'])
    df_2018.drop('Index', axis=1, inplace=True)
    df_2018.sort_values(by='Date', inplace=True)
    df_2018['Date'] = pandas.to_datetime(df_2018['Date'])
    df_2018 = df_2018.drop(df_2018[df_2018['Date'] < '2018-01-01'].index)
    df_2018 = df_2018.drop(df_2018[df_2018['Date'] > '2019-12-31'].index)
    print(df_2018.head())
    print(df_2018.tail())

    df_2020 = pandas.read_csv(model_2020_results, header=0, names=['Index', 'Extension', 'Date'])
    df_2020.drop('Index', axis=1, inplace=True)
    df_2020.sort_values(by='Date', inplace=True)
    df_2020['Date'] = pandas.to_datetime(df_2020['Date'])
    df_2020 = df_2020.drop(df_2020[df_2020['Date'] < '2020-01-01'].index)
    print(df_2020.head())
    print(df_2020.tail())

    df_2020 = df_2020.reset_index(drop=True)
    # full_df = df_2018.append(df_2020)
    full_df = pandas.concat([df_2018, df_2020])

    print('2018 DF', len(df_2018))
    print('2020 DF', len(df_2020))
    print('Full DF', len(full_df))
    # full_df = full_df.drop(full_df[full_df['Date'] < '2016-01-01'].index)
    print(full_df.head())
    print(full_df.dtypes)
    ax = full_df.plot(x='Date', y='Extension', kind='scatter', title='Flacksjon water extension in time')
    ax.set_ylabel("Water extension in m2")
    plt.tight_layout()
    plt.scatter(['2020-08-04', '2018-04-24', '2021-11-21'], [62330, 134579, 86235], c='#ff0000')
    # plt.scatter(['2017-04-16', '2020-08-04', '2018-04-24', '2021-11-21'], [115044, 62330, 134579, 86235], c='#ff0000', s=35)
    # plt.scatter(['2017-04-16', '2020-08-04', '2018-04-24', '2021-11-21'], [115044, 62330, 134579, 86235], c='#ff0000', s=80)
    # plt.savefig('/tmp/flacksjon_water_estimates.pdf')
    # seaborn.regplot(data=full_df, x='Date', y='Extension')

    plt.show()


def count_ndwi_water():
    folder = '/tmp/bulk_export_flacksjon_ndwi/'
    # file_name = '20150813T101020_20160319T132810_T33VWG.png'

    results_list = []

    if not os.path.exists(folder):
        raise FileNotFoundError(f'The folder contaning the TIFF files does not exist: {folder}')

    filenames = next(os.walk(folder), (None, None, []))[2]  # [] if no file
    for file_name in filenames:
        if file_name.endswith('.png'):
            continue
        ndwi_mask = imageio.imread(folder + file_name)
        unique, counts = numpy.unique(ndwi_mask, return_counts=True)
        results = dict(zip(unique, counts))
        # print('Date', image_date, 'Counts = ', results)

        has_nan = False
        for key in results.keys():
            if math.isnan(key):
                print('Found a NaN')
                has_nan = True

        if has_nan:
            continue

        image_date = file_name[0:8]
        results['Date'] = image_date
        results['Date'] = image_date
        results['File_name'] = file_name
        results_list.append(results)

    data_frame = pandas.DataFrame(results_list)
    data_frame['Date'] = data_frame['Date'].apply(pandas.to_datetime)
    data_frame.rename(columns={0.5: 'No_water', 1.0: 'Water'}, inplace=True)
    print(data_frame.head())
    print(data_frame.columns.values)

    data_frame = data_frame[data_frame['Date'].dt.month.isin([4, 5, 6, 7, 8, 9, 10, 11])]
    data_frame = data_frame.drop(data_frame[data_frame['Date'] < '2018-01-01'].index)
    data_frame = data_frame.drop(data_frame[data_frame['Date'] > '2022-12-31'].index)
    ax = data_frame.plot(x='Date', y='Water', kind='scatter', title='Flacksjon water extension in time22', c='red')


    #
    #
    #
    #
    #
    #
    # model_2018_results = '/tmp/descending_Orebro lan_mosaic_2018-07-04_sar_VH_20-epochs_new_water_estimates_filtered.csv'
    # model_2020_results = '/tmp/descending_Orebro lan_mosaic_2020-06-23_sar_VH_20-epochs_new_water_estimates_filtered.csv'
    model_2018_results = '/tmp/descending_Orebro lan_mosaic_2018-07-04_sar_VH_20-epochs_0.00005-lr_42-rand_new_water_estimates_filtered.csv'
    model_2020_results = '/tmp/descending_Orebro lan_mosaic_2020-06-23_sar_VH_20-epochs_0.00005-lr_42-rand_new_water_estimates_filtered.csv'

    df_2018 = pandas.read_csv(model_2018_results, header=0, names=['Index', 'Extension', 'Date'])
    df_2018.drop('Index', axis=1, inplace=True)
    df_2018.sort_values(by='Date', inplace=True)
    df_2018['Date'] = pandas.to_datetime(df_2018['Date'])
    df_2018 = df_2018.drop(df_2018[df_2018['Date'] < '2018-01-01'].index)
    df_2018 = df_2018.drop(df_2018[df_2018['Date'] > '2019-12-31'].index)
    print(df_2018.head())
    print(df_2018.tail())

    df_2020 = pandas.read_csv(model_2020_results, header=0, names=['Index', 'Extension', 'Date'])
    df_2020.drop('Index', axis=1, inplace=True)
    df_2020.sort_values(by='Date', inplace=True)
    df_2020['Date'] = pandas.to_datetime(df_2020['Date'])
    df_2020 = df_2020.drop(df_2020[df_2020['Date'] < '2020-01-01'].index)
    print(df_2020.head())
    print(df_2020.tail())

    df_2020 = df_2020.reset_index(drop=True)
    # full_df = df_2018.append(df_2020)
    full_df = pandas.concat([df_2018, df_2020])

    print('2018 DF', len(df_2018))
    print('2020 DF', len(df_2020))
    print('Full DF', len(full_df))
    # full_df = full_df.drop(full_df[full_df['Date'] < '2016-01-01'].index)
    print(full_df.head())
    print(full_df.dtypes)
    full_df.plot(x='Date', y='Extension', kind='scatter', title='Flacksjon water extension in time', ax=ax)

    # Add lines to the plot to connect the scatter dots
    data_frame.plot(x='Date', y='Water', c='red', ax=ax)
    full_df.plot(x='Date', y='Extension', ax=ax)

    # plt.savefig('/tmp/open_vegetated_water.pdf')
    plt.show()


def main():
    load_dotenv()
    plot_scatter()
    count_ndwi_water()


start = time.time()
main()
end = time.time()
total_time = end - start
print("%s: Total time = %f seconds" % (time.strftime("%Y/%m/%d-%H:%M:%S"), total_time))
