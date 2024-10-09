
import pandas as pd
import os
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Items(BaseModel):
    goods: str
    hsn_sac: str
    quantity: int
    rate: float
    par: str
    villager_name: str
    vehicle_no: str
    good_type: str
    before_wight: float
    after_wight: float


class Bill(BaseModel):
    invoiceNo: int
    supplierName: str
    supplierOtherInfo: str
    items: Optional[list[Items]]


def check_excel(file_name: str):
    if not os.path.exists(file_name):
        bill_data_columns = [
            "id", "invoiceNo", "taxableValue", "total",
            "total_quantity", "supplierName", "supplierOtherInfo", "createdAt"
        ]
        items_columns = [
            "id", "goods", "hsn_sac", "quantity", "rate", "par",
            "amount", "villagerName", "vehicle_no", "goodType",
            "before_wight", "after_wight", "net_wight", "billDataId"
        ]
        df_bill_data = pd.DataFrame(columns=bill_data_columns)
        df_items = pd.DataFrame(columns=items_columns)
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df_bill_data.to_excel(
                writer, sheet_name='bills', index=False)
            df_items.to_excel(writer, sheet_name='items', index=False)
        return (True, df_bill_data, df_items)
    return (True, pd.read_excel(
        file_name, sheet_name='bills', engine='openpyxl'
    ),  pd.read_excel(
        file_name, sheet_name='items', engine='openpyxl'
    ))


def create_bill(file_name: str, data: Bill):
    it_valid_excel, df_bill_data, df_items = check_excel(file_name)
    if it_valid_excel == False:
        return False
    new_id = df_bill_data['id'].max()+1 if not df_bill_data.empty else 1
    total_quantity = 0
    total = 0
    for i in data.items:
        item_new_id = df_items['id'].max() + 1 if not df_items.empty else 1
        total += i.rate * i.quantity
        total_quantity += i.quantity
        item_new_item = {
            "id": item_new_id,
            "goods": i.goods,
            "hsn_sac": i.hsn_sac,
            "quantity": i.quantity,
            "rate": i.rate,
            "par": i.par,
            "amount": i.rate * i.quantity,
            "villagerName": i.villager_name,
            "vehicle_no": i.vehicle_no,
            "goodType": i.good_type,
            "before_wight": i.before_wight,
            "after_wight": i.after_wight,
            "net_wight": i.before_wight - i.after_wight,
            "billDataId": new_id
        }
        df_items = pd.concat(
            [df_items, pd.DataFrame([item_new_item])],
            ignore_index=True
        )

    new_bill = {
        "id": new_id,
        "invoiceNo": data.invoiceNo,
        "taxableValue": total,
        "total": total,
        "total_quantity": total_quantity,
        "supplierName": data.supplierName,
        "supplierOtherInfo": data.supplierOtherInfo,
        "createdAt": datetime.now().strftime("%d-%b-%y"),
    }
    df_bill_data = pd.concat(
        [df_bill_data, pd.DataFrame([new_bill])],
        ignore_index=True
    )
    print(df_bill_data, df_items)
    with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
        df_bill_data.to_excel(writer, sheet_name="bills", index=False)
        df_items.to_excel(writer, sheet_name="items", index=False)
    return True


def get_list(file_name: str):
    it_valid_excel, df_bill_data, df_items = check_excel(file_name)

    bills_with_items = pd.merge(
        df_bill_data, df_items,  left_on='id', right_on='billDataId', how='left')
    # Create a dictionary of bills with nested items
    bills = []
    for bill_id, group in bills_with_items.groupby('id_x'):
        # Get bill details from the first row of the group
        bill_data = group.iloc[0][[
            'id_x', 'invoiceNo', 'supplierName', "taxableValue", "total", "total_quantity", "supplierName", "supplierOtherInfo", "createdAt"]].to_dict()

        # Collect all items associated with the current bill
        items = group[["id_y", 'goods', "hsn_sac", 'quantity', "rate", "par", "amount", "villagerName",
                       "vehicle_no", "goodType", "before_wight", "after_wight", "net_wight"]].to_dict(orient='records')

        # Add items under the 'items' key in bill_data
        bill_data['items'] = items
        bills.append(bill_data)

    # print(bills_with_items)
    return bills


def read_data(file_name: str, id: str):
    it_valid_excel, df_bill_data, df_items = check_excel(file_name)
    bill = df_bill_data[df_bill_data['id'] == int(id)]
    bill_data = bill.to_dict(orient='records')[0]

    items = df_items[df_items['billDataId'] == int(id)]
    bill_data['items'] = items.to_dict(orient='records')
    return bill_data


def delete_bill(file_name, bill_id):
    it_valid_excel, df_bill_data, df_items = check_excel(file_name)
    if int(bill_id) not in df_bill_data['id'].values:
        print(f"No billData found with id {bill_id}.")
        return False
    print(df_bill_data, df_items)
    df_bill_data = df_bill_data[df_bill_data['id'] != int(bill_id)].reset_index(
        drop=True)
    # Also delete related items
    df_items = df_items[df_items['billDataId'] != int(bill_id)].reset_index(
        drop=True)
    print(df_bill_data, df_items)
    with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
        df_bill_data.to_excel(writer, sheet_name="bills", index=False)
        df_items.to_excel(writer, sheet_name="items", index=False)
