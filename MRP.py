# MRP Program
# Purpose to read in csv inputs supplying SKU + quantity demanded,
# output total component items needed based on most recent BOM revision
import driver
from driver import sql, sql2, sql_ima_type, sql_oh_qty, sql_get_quote_items, sql_getCrmQuote
import pandas as pd
from datetime import datetime
import time
from csv_to_html import write_to_html_file
import re

system_SKU_dict = {}
#conn = driver.Sqlconnection(1)    # connect to backup database mpserver6

def connect_to_db(login_user):
    if login_user == 1:
        conn = driver.Sqlconnection(login_user)
    if login_user == 2:
        conn = driver.Sqlconnection(login_user)
    return conn


# loading data
def load_data():
    df = pd.read_csv('input/mrp1.csv')
    keys = [SKU for SKU in df['ItemNo']]
    demand_qtys = [qty for qty in df['Demand1']]
    inputs_dict = {key:value for key,value in zip(keys,demand_qtys)} # create input data structure
    return inputs_dict


def update_dict(key, value, bom_dict):
    if value == 0:  # ignore values with bom_qty = 0
        return bom_dict
    if (key not in bom_dict):
        bom_dict[key] = value
    return bom_dict


# if ima type is O or Y, return True to initiate expanading sub-bom
def get_ima_type(compitem, conn):
    query = conn.fetchSPPDict(sql_ima_type, compitem)
    print(f'ima type of {compitem} is {query[0]["ima_type"]}')
    if (query[0]['ima_type'].replace(' ','').upper() in ['Y','O','A']):
        return True
    else:
        return False


def get_bom_quantity(sku, input_value, conn):
    nested_bom_dict = {}
    for row in conn.fetchSPPDict(sql, sku):
          if ((row['bom_compitem'] not in nested_bom_dict) and (get_ima_type(row['bom_compitem'], conn))):  # checking if component is already in dict, or if item needs to be expanded
                print(f'accessing component BOM for {row["bom_compitem"]}')
                if conn.fetchSPPDict(sql, row['bom_compitem']): # checking if component BOM exists
                    update_bom_quantity(row['bom_compitem'], nested_bom_dict, input_value * row['bom_qty'], conn)    # recursive call
                    continue
                update_dict(row['bom_compitem'], row['bom_qty'] * input_value, nested_bom_dict)

          if not get_ima_type(row['bom_compitem'], conn):
              update_dict(row['bom_compitem'], row['bom_qty'] * input_value, nested_bom_dict)

    # removing parent components if ima_type is 'Y', 'O', 'A' (desired output only contains raw components)
    for key in list(nested_bom_dict.keys()):
          hasBOM = conn.fetchSPPDict(sql2, key)
          if hasBOM[0]['bom_itemno'] is not None and get_ima_type(key, conn):
                print(f'removing parent SKU: {key}')
                nested_bom_dict.pop(key)
    return nested_bom_dict


def update_bom_quantity(query_SKU, component_dict, input_value, conn):
    if conn.fetchSPPDict(sql, query_SKU) and get_ima_type([query_SKU], conn):  # prints parent component SKU#, and prints all BOM items for SKU
        print(f'query SKU exists : {query_SKU}')
        for component_row in conn.fetchSPPDict(sql, query_SKU):
            # print(f'sub-bom component: {component_row}')
            print(component_row['bom_compitem'])
            if (component_row['bom_compitem'] not in component_dict):
                key = component_row['bom_compitem']
                value = component_row['bom_qty'] * input_value
                if value == 0:
                    continue
                component_dict[key] = value
                if not get_ima_type(key, conn):
                    print(f'no further BOM expansion needed for {key}')
                    continue
                print(f'expanding BOM for {key}')
                update_bom_quantity(key, component_dict, input_value, conn)  # recursive checking for sub component BOMs
    return component_dict


def combine_dicts(dict1, dict2):
    output_dict = {}
    for key in dict1.keys() | dict2.keys():
        output_dict[key] = dict1.get(key,0) + dict2.get(key,0)
      #  print(output_dict[key], key)
    return output_dict


def get_oh_qty(sku, table_parameter, conn):
    result = conn.fetchSPPDict(sql_oh_qty, sku)
    output = []
    try:
        result[0][table_parameter]
    except:
        sku = sku[:-2]
        result = conn.fetchSPPDict(sql_oh_qty, sku)

    if table_parameter == 'ima_netoh':
            return result[0][table_parameter]

    if table_parameter == 'pos_confirmation':
        date_qty_format = '[0-9]+\/[0-9]+\/[0-9]+\s*\(\s*\d*\s*\/\s*\d*\s*\)'
        for i in range(len(result)):
            shipment_eta = result[i][table_parameter]
            if shipment_eta is None:
                output.append(shipment_eta)
                continue
            all_shipments = re.findall(date_qty_format, shipment_eta)
            for shipment in all_shipments:
                shipment_date = shipment[0:10]
                if(shipment_date < datetime.now().strftime('%m/%d/%Y')):
                    print(shipment_date)
                    continue
                output.append(shipment.replace(' ',''))
        return output

    for i in range(len(result)):
        output.append(result[i][table_parameter])

    return output


def BO_calculation(list1, list2):
    output_int = 0
    if list1[0] is None:
        return '-'
    for i in range(len(list1)):
        output_int += (list2[i]-list1[i])
    return output_int


def list_to_string(lst):
    output_string = ''
    if len(lst) == 0 or (lst[0] is None and len(lst) < 2):
        return '-'
    output_string = '; '.join([str(elem) for elem in lst])
    return output_string
#datetime.today().strftime


# outputs total quantities needed for drilled-down components (does not expand type A,O,or Y parts)
def build_output(system_SKU_dict, login_user):
    conn = connect_to_db(login_user)
    MRP_dict = {}
    for input_key, input_value in system_SKU_dict.items():
        print(f'Now analyzing: {input_key}, demanded value: {input_value}')
        temp_dict = get_bom_quantity(input_key, input_value, conn)

        cumulative_MRP_dict = combine_dicts(MRP_dict, temp_dict)
        temp_dict = {}
        MRP_dict = cumulative_MRP_dict

    sortedDict = dict(sorted(MRP_dict.items(), key=lambda x: x[0].lower()))
    df = pd.DataFrame.from_dict(sortedDict, orient='index', columns=['Qty Needed'])

    component_skus = df.index.values
    df['Net OH Qty'] = [get_oh_qty(sku, 'ima_netoh', conn) for sku in component_skus]
    df['OO Qty'] = [get_oh_qty(sku, 'pos_qtyord', conn) for sku in component_skus]
    df['OO Received'] = [get_oh_qty(sku, 'pos_qtyacc', conn) for sku in component_skus]
    df['BO'] = [BO_calculation(df['OO Received'][i], df['OO Qty'][i]) for i in range(len(df['OO Qty']))]
    df['BO ETA'] = [get_oh_qty(sku, 'pos_confirmation', conn) for sku in component_skus]
    df.drop(columns=['OO Qty', 'OO Received'], inplace=True)

    # reformatting columns for output file
    df['BO ETA'] = [list_to_string(df['BO ETA'][i]) for i in range(len(df['BO ETA']))]
    df.to_csv('templates/outputs/output.csv')
    write_to_html_file(df)
    return True

# outputs total number of completed made parts/add on component quantities needed from supplied quote
def get_quote_items(quote_number, login_user):
    input_dict = {}
    conn = driver.Sqlconnection(login_user)
    result = conn.fetchSPPDict(sql_get_quote_items, quote_number)
    for row in result:
        key = row['SMC_MATERIAL_ID']
        value = int(row['QUANTITY'])
        if key not in input_dict:
            input_dict[key] = value
        else:
            continue
    return input_dict

# adding -P suffix for MBD and AOC components; database net OH references -P for purchased raw components
def convert_component_suffix(component_list, connection):
    for i in range(len(component_list)):
        if get_oh_qty(component_list[i], 'ima_netoh', connection):
            continue
        if component_list[i][0:3] in ['MBD', 'AOC'] and component_list[i][-1] not in ['O', 'P', 'B']:
            component_list[i] = component_list[i] + '-P'
        elif component_list[i][-1] in ['O', 'B']:
            component_list[i] = component_list[i].replace('-B', '-P', 1)
            component_list[i] = component_list[i].replace('-O', '-P', 1)
    return component_list

def build_top_level_output(quote_SKU_dict, login_user, quote_num):
    conn = connect_to_db(login_user)
    MRP_dict = quote_SKU_dict

    sortedDict = dict(sorted(MRP_dict.items(), key=lambda x: x[0].lower()))
    df = pd.DataFrame.from_dict(sortedDict, orient='index', columns=['Demanded Qty'])

    component_skus = df.index.values
    convert_component_suffix(component_skus, conn)

    df['Net OH Qty'] = [get_oh_qty(sku, 'ima_netoh', conn) for sku in component_skus]
    df['OO Qty'] = [get_oh_qty(sku, 'pos_qtyord', conn) for sku in component_skus]
    df['OO Received'] = [get_oh_qty(sku, 'pos_qtyacc', conn) for sku in component_skus]
    df['BO'] = [BO_calculation(df['OO Received'][i], df['OO Qty'][i]) for i in range(len(df['OO Qty']))]
    df['BO ETA'] = [get_oh_qty(sku, 'pos_confirmation', conn) for sku in component_skus]
    df.drop(columns=['OO Qty', 'OO Received'], inplace=True)

    # reformatting columns for output file
    df['BO ETA'] = [list_to_string(df['BO ETA'][i]) for i in range(len(df['BO ETA']))]

    path_to_output = 'templates/outputs/' + str(quote_num) + '_MRP.csv'
    df.to_csv(path_to_output)
    df.to_csv('templates/outputs/output.csv')

    write_to_html_file(df, title=quote_num)
    return True


if __name__ == '__main__':
    start_time = time.time()
    conn = driver.Sqlconnection(1)    # connect to database
    system_SKU_dict = load_data()

    #build_output(system_SKU_dict, 1)
    mydict = get_quote_items('8600459116', 2)
    print(build_top_level_output(mydict, 1, '8600459116'))
    runtime = time.time() - start_time
    print(f'---- Program execution time: {runtime} ----')

