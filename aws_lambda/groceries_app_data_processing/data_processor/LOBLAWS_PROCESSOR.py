import re
import numpy as np
import uuid
import datetime
import pytz

def loblaws_cleansing(input_data):
    # Get prd id for Lowblaws and drop duplicates
    df = input_data.copy()
    df['prd_id_in_store'] = df['prd_link'].str.split(r'.*?/(\w+)$', regex=True).apply(lambda x: x[1])
    df.drop_duplicates('prd_id_in_store', inplace=True)
    df.rename({'date': 'scrap_date'}, axis=1, inplace=True)
    df['store'] = 'Loblaws'
    # Categorize on sale products
    df['prd_discount'] = df['prd_discount'].astype(str)
    df['prd_discount'] = df['prd_discount'].apply(
        lambda x: x.split('\n')[0] if x is not None and '\n' in x else x)
    conditions = [
        df['prd_discount'].str.contains('SAVE'),
        df['prd_discount'].str.contains('MIN'),
        df['prd_discount'].str.contains('Member'),
        df['prd_discount'].str.contains('Points')
    ]
    choices = ['SAVING', 'MULTI', 'MEMBER', 'POINT']
    df['on_sale_cat'] = np.select(conditions, choices, default=np.nan)

    # Pricing
    df['prd_price'] = df['prd_price'].astype(str)
    df['prd_price'] = df['prd_price'].apply(
        lambda x: re.search(r'.*?\$(.*)', x).group(1) if x is not None else x).astype(float)
    # Something wrong with Loblaws website, for example $1,200/1 ea, but actually mean $1.2
    df['prd_per_price'] = df['prd_per_price'].astype(str)
    tmp = df['prd_per_price'].str.split(',', expand=True)
    if len(tmp.columns) == 3:
        tmp.columns = ['0', '1', '2']
        tmp['2'] = tmp[['1', '2']].apply(
            lambda x: '.'.join([x['1'], x['2'].replace('.', '')]) if x['2'] is not None else x['1'],
            axis=1
        )
        tmp.drop(['1'], axis=1, inplace=True)
    else:
        tmp.columns = ['0','2']
    tmp['2'] = tmp[['0', '2']].apply(lambda x: x['0'].strip() if x['2'] is None else x['2'].strip(), axis=1)
    tmp['0'] = tmp['0'].apply(lambda x: None if '$' in x else x)
    tmp['2'] = tmp['2'].apply(lambda x: None if '$' not in x else x)
    tmp2 = tmp['2'].str.split(expand=True)
    if len(tmp2.columns) == 2:
        tmp[['2', '3']] = tmp['2'].str.split(expand=True)
        df[['average_unit', 'price_per_unit_1', 'price_per_unit_2']] = tmp[['0', '2', '3']]
    else:
        df['price_per_unit_2'] = None
        df[['average_unit', 'price_per_unit_1']] = tmp[['0', '2']]
    df['unit_price'] = df['price_per_unit_1'].apply(
        lambda x: re.search(r'\$(.*?)/(\d+)(\w+)', x).group(1) if x is not None else None).astype(float)
    df['unit_price_base'] = df['price_per_unit_1'].apply(
        lambda x: re.search(r'\$(.*?)/(\d+)(\w+)', x).group(2) if x is not None else np.nan).astype(float)
    df['average_unit'] = df[
        ['prd_price', 'unit_price', 'price_per_unit_1', 'unit_price_base', 'average_unit']].apply(
        lambda x: f"{round((x['prd_price'] * x['unit_price_base'] / x['unit_price']), 2)} " + re.search(
            r'\$(.*?)/(\d+)(\w+)', x['price_per_unit_1']).group(3) if (
                    x['average_unit'] is None and x['unit_price'] is not None) else x['average_unit'],
        axis=1
    )
    df['price_per_unit_1'] = df[['average_unit', 'prd_price', 'price_per_unit_1']].apply(
        lambda x: ' '.join(['$', str(x['prd_price']), '/', x['average_unit']]) if x['price_per_unit_1'] is None else x[
            'price_per_unit_1'],
        axis=1
    )
    df.drop(['unit_price', 'unit_price_base', 'prd_per_price'], axis=1, inplace=True)
    df['record_id'] = 1
    df['record_id'] = df['record_id'].transform(lambda x: str(uuid.uuid4()))
    toronto_tz = pytz.timezone("America/Toronto")
    df['processing_time'] = datetime.datetime.now(toronto_tz).isoformat()
    #remove wine extra wording
    df['prd_name'] = df['prd_name'].apply(lambda x: re.sub(r'(\(\s*ID required at pick-up\s*\))', '', x))
    return df



