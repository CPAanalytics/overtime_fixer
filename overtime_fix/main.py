import os
from pathlib import Path
from pprint import pprint
import click as click
import pandas as pd


def file_path(filename):
    user_path = os.path.expanduser('~')
    file_path = os.path.join(user_path, 'Downloads')
    file_name = os.path.join(file_path, filename)
    Path(file_path).mkdir(parents=True, exist_ok=True)
    return file_name


def fix_horrific_overtime_calc_mess(file_path_org, file_path_recalc, filter_columns_to_keep, filter_columns_to_drop):
    df_actual_from_prod = pd.read_csv(file_path_org)
    df_recalculated = pd.read_csv(file_path_recalc)
    print(f'production:  {df_actual_from_prod.shape[0]} rows {df_actual_from_prod.shape[1]} columns')
    print(f'recalculated: {df_recalculated.shape[0]} rows {df_recalculated.shape[1]} columns')
    # Find columns that don't match between the two files
    missing_columns_prod = [column for column in df_actual_from_prod.columns if column not in df_recalculated.columns]
    missing_columns_recalc = [column for column in df_recalculated.columns if column not in df_actual_from_prod.columns]

    # Employees that don't match between the two files
    missing_employess = [employee for employee in df_actual_from_prod['Employee'].unique() if
                         employee not in df_recalculated['Employee'].unique()]
    missing_employess_recalc = [employee for employee in df_recalculated['Employee'].unique() if
                                employee not in df_actual_from_prod['Employee'].unique()]

    # Create a new dataframe with the missing columns
    dict = {'Missing Columns in Production': missing_columns_prod,
            'Missing Columns in Recalculated': missing_columns_recalc,
            'Missing Employees in Production': missing_employess,
            'Missing Employees in Recalculated': missing_employess_recalc}

    discrepancies = pd.DataFrame.from_dict(dict, orient='index')
    discrepancies = discrepancies.transpose()
    discrepancies.to_csv(file_path('discrepancies.csv'))

    # Filter proudction dataframe to only include the columns that are in the recalculated dataframe
    df_actual_from_prod = df_actual_from_prod[df_actual_from_prod.columns.intersection(df_recalculated.columns)]
    df_actual_from_prod = df_actual_from_prod[~df_actual_from_prod['Employee'].isin(missing_employess)]

    # Filter recalculated dataframe to only include the columns that are in the production dataframe`
    df_recalculated = df_recalculated[df_recalculated.columns.intersection(df_actual_from_prod.columns)]
    df_recalculated = df_recalculated[~df_recalculated['Employee'].isin(missing_employess_recalc)]

    print('Filtered production dataframe to only include the columns that are in the recalculated dataframe')
    print('Filtered recalculated dataframe to only include the columns that are in the production dataframe')
    print(f'production:  {df_actual_from_prod.shape[0]} rows {df_actual_from_prod.shape[0]} columns')
    print(f'recalculated: {df_recalculated.shape[0]} rows {df_recalculated.shape[0]} columns')

    # Reset Indexes to employee
    df_actual_from_prod = df_actual_from_prod.groupby(['Employee']).sum().reset_index()
    df_recalculated = df_recalculated.groupby(['Employee']).sum().reset_index()

    # I don't Know why this is necessary, but it is
    df_recalculated = df_recalculated[df_recalculated.columns.intersection(df_actual_from_prod.columns)]

    print('Reset Indexes to employee')
    print(f'production:  {df_actual_from_prod.shape[0]} rows {df_actual_from_prod.shape[1]} columns')
    print(f'recalculated: {df_recalculated.shape[0]} rows {df_recalculated.shape[1]} columns')

    # Set index to employee
    df_actual_from_prod.set_index('Employee', inplace=True)
    df_recalculated.set_index('Employee', inplace=True)

    # Sort the dataframes by column and row so that they are identical for subtraction operation
    df_actual_from_prod.sort_index(inplace=True)
    df_actual_from_prod.sort_index(inplace=True, axis=1)
    df_recalculated.sort_index(inplace=True)
    df_recalculated.sort_index(inplace=True, axis=1)

    # Calculate the difference between the two dataframes
    df_diff = df_actual_from_prod - df_recalculated

    # Add suffixes to the columns
    df_actual_from_prod = df_actual_from_prod.add_suffix('_prod')
    df_recalculated = df_recalculated.add_suffix('_recalc')
    df_diff = df_diff.add_suffix('_diff')

    # Concatentate the dataframes and sort the columns
    concat_df = pd.concat([df_actual_from_prod, df_recalculated, df_diff], axis=1)
    print(f'final: {concat_df.shape[0]} rows {concat_df.shape[1]} columns')
    concat_df.sort_index(inplace=True, axis=1)

    if filter_columns_to_keep:
        concat_df = concat_df.filter(like=filter_columns_to_keep, axis=1)
    print(f'dropping columns that contain string {filter_columns_to_drop}')
    print(f'final: {concat_df.shape[0]} rows {concat_df.shape[1]} columns')

    if filter_columns_to_drop:
        concat_df = concat_df[concat_df.columns.drop(list(concat_df.filter(like=filter_columns_to_drop).columns))]
    print(f'dropping columns that contain string {filter_columns_to_drop}')
    print(f'final: {concat_df.shape[0]} rows {concat_df.shape[1]} columns')

    # drop columns where _diff is all zeros
    concat_df = concat_df.loc[:, concat_df.any()]
    filter_df = concat_df.filter(like='_diff', axis=1)
    filter_df = filter_df.loc[:, concat_df.any()]
    filter_list = list(filter_df.columns)
    filter_list = [x.split('_diff')[0] for x in filter_list]
    print('Dropping columns where _diff is all zeros')
    pprint(filter_list)
    concat_df = concat_df[concat_df.columns.drop(list(concat_df.filter(like=filter_columns_to_drop).columns))]
    print(f'final: {concat_df.shape[0]} rows {concat_df.shape[1]} columns')

    # drop 0 rows
    concat_df = concat_df.loc[~(concat_df == 0).all(axis=1)]
    print('dropping 0 rows')
    print(f'final: {concat_df.shape[0]} rows {concat_df.shape[1]} columns')
    concat_df.to_csv(file_path('diff.csv'))
    print('Saved ' + file_path('diff.csv'))

    # prettify the variances and output to a .txt file.
    with open(file_path('diff.txt'), 'w') as f:
        for index, rows in concat_df.iterrows():
            rows = rows[rows != 0]
            f.write(str(index) + '\n' * 2)
            for income, value in rows.iteritems():
                string = str.ljust(str(income), 30) + ': ' + str(round(value, 2))
                f.write(string + '\n')
            f.write('\n')


@click.command()
@click.option('--prod', required=True, help='Production file to compare')
@click.option('--recalc', required=True, help='Recalculated file to compare')
@click.option('--keep', help='Columns to keep.  Functions like a sql like statement')
@click.option('--drop', help='Columns to drop.  Functions like a sql like statement')
def overtime_fix(prod, recalc, keep, drop):
    fix_horrific_overtime_calc_mess(prod, recalc, keep, drop)


if __name__ == "__main__":
    overtime_fix(
        ['--prod', '../csv_files/prod.csv', '--recalc', '../csv_files/recalc.csv', '--keep', 'Overtime ', '--drop',
         'Overtime Units'])
