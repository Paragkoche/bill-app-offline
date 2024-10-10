
import pandas as pd
import os
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Bill(BaseModel):
    invoiceNo: int
    supplierName: str
    supplierOtherInfo: str
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


def check_excel(file_name: str):
    if not os.path.exists(file_name):
        bill_data_columns = [
            "id",
            "invoiceNo", "taxableValue", "total",
            "total_quantity", "supplierName", "supplierOtherInfo", "createdAt",
            "goods", "hsn_sac", "quantity", "rate", "par",
            "amount", "villagerName", "vehicle_no", "goodType",
            "before_wight", "after_wight", "net_wight",
        ]

        df_bill_data = pd.DataFrame(columns=bill_data_columns)
        df_bill_data.to_csv(file_name, mode='w', index=False)
        return (True, df_bill_data)
    return (True, pd.read_csv(
        file_name,
    ))


def create_bill(file_name: str, data: Bill):
    it_valid_excel, df_bill_data = check_excel(file_name)
    if it_valid_excel == False:
        return False
    new_id = df_bill_data['id'].max()+1 if not df_bill_data.empty else 1
    total_quantity = data.quantity
    total = data.quantity * data.rate
    new_bill = {
        "id": new_id,
        "invoiceNo": data.invoiceNo,
        "taxableValue": total,
        "total": total,
        "total_quantity": total_quantity,
        "supplierName": data.supplierName,
        "supplierOtherInfo": data.supplierOtherInfo,
        "createdAt": datetime.now().strftime("%d-%b-%y"),
        "goods": data.goods,
        "hsn_sac": data.hsn_sac,
        "quantity": data.quantity,
        "rate": data.rate,
        "par": data.par,
        "amount": total,
        "villagerName": data.villager_name,
        "vehicle_no": data.vehicle_no,
        "goodType": data.good_type,
        "before_wight": data.before_wight,
        "after_wight": data.after_wight,
        "net_wight": data.after_wight - data.before_wight

    }
    df_bill_data = pd.concat(
        [df_bill_data, pd.DataFrame([new_bill])],
        ignore_index=True
    )
    df_bill_data.to_csv(file_name, index=False)

    return True


def get_list(file_name: str):
    it_valid_excel, df_bill_data = check_excel(file_name)

    # Create a dictionary of bills with nested items
    bills = df_bill_data
    print(bills)
    # print(bills_with_items)
    return bills.to_dict(orient="records",)


def read_data(file_name: str, id: str):
    it_valid_excel, df_bill_data,  = check_excel(file_name)
    bill = df_bill_data[df_bill_data['id'] == int(id)]
    bill_data = bill.to_dict(orient='records')[0]
    return bill_data


def delete_bill(file_name, bill_id):
    it_valid_excel, df_bill_data = check_excel(file_name)
    if int(bill_id) not in df_bill_data['id'].values:
        print(f"No billData found with id {bill_id}.")
        return False
    print(df_bill_data)
    df_bill_data = df_bill_data[df_bill_data['id'] != int(bill_id)].reset_index(
        drop=True)

    df_bill_data.to_csv(file_name, index=False)
