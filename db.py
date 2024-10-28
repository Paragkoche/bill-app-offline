import pandas as pd
import os
from datetime import datetime
from pydantic import BaseModel
from openpyxl import Workbook, load_workbook
from typing import Optional

# Set Pandas display options
pd.set_option('display.max_columns', 1000, 'display.width',
              1000, 'display.max_rows', 1000)

# Define the Bill model using Pydantic with all fields as strings


class Bill(BaseModel):
    invoiceNo: str
    supplierName: str
    supplierOtherInfo: str
    goods: str
    hsn_sac: str
    quantity: float
    rate: float
    par: str
    farmerName: str
    vehicle_no: str
    farmerCode: str
    before_wight: str
    after_wight: str

# Function to check if the Excel file exists and create it if it does not


def check_excel(file_name: str):
    if not os.path.exists(file_name):
        bill_data_columns = [
            "id",
            "invoiceNo",
            "supplierName",
            "supplierOtherInfo",
            "goods",
            "hsn_sac",
            "quantity",
            "rate",
            "par",
            "farmerName",
            "vehicle_no",
            "farmerCode",
            "before_wight",
            "after_wight",
            "createdAt",
        ]

        # Create an empty DataFrame with the specified columns
        df_bill_data = pd.DataFrame(columns=bill_data_columns)

        # Save the DataFrame to an Excel file
        df_bill_data.to_excel(file_name, index=False, sheet_name='Sheet1')

        # Set column widths using openpyxl
        workbook = load_workbook(file_name)
        worksheet = workbook.active
        column_widths = {
            'A': 10,  # id
            'B': 20,  # invoiceNo
            'C': 30,  # supplierName
            'D': 30,  # supplierOtherInfo
            'E': 15,  # goods
            'F': 15,  # hsn_sac
            'G': 10,  # quantity
            'H': 10,  # rate
            'I': 10,  # par
            'J': 20,  # villagerName
            'K': 15,  # vehicle_no
            'L': 15,  # goodType
            'M': 15,  # before_wight
            'N': 15,  # after_wight
            'O': 20,  # createdAt
        }

        # Set column widths
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

        # Save the workbook
        workbook.save(file_name)

        return (True, df_bill_data)

    # If the file exists, read and return the data
    df_bill_data = pd.read_excel(file_name)
    return (True, df_bill_data)

# Function to create a new bill entry


def create_bill(file_name: str, data: Bill):
    it_valid_excel, df_bill_data = check_excel(file_name)
    if not it_valid_excel:
        return False

    new_id = df_bill_data['id'].max() + 1 if not df_bill_data.empty else 1

    new_bill = {
        "id": str(new_id),
        "invoiceNo": data.invoiceNo,

        "supplierName": data.supplierName,
        "supplierOtherInfo": data.supplierOtherInfo,
        "createdAt": datetime.now(),
        "goods": data.goods,
        "hsn_sac": data.hsn_sac,
        "quantity": data.quantity,
        "rate": data.rate,
        "par": data.par,

        "farmerName": data.farmerName,
        "vehicle_no": data.vehicle_no,
        "farmerCode": data.farmerCode,
        "before_wight": data.before_wight,
        "after_wight": data.after_wight,

    }
    # Append the new bill to the DataFrame
    df_bill_data = pd.concat(
        [df_bill_data, pd.DataFrame([new_bill])], ignore_index=True)
    try:
        with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
            df_bill_data.to_excel(writer, index=False, sheet_name='Sheet1')

            # Access the XlsxWriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']

            # Set the date format for the 'createdAt' column
            date_format = workbook.add_format(
                {'num_format': 'dd-mmm-yy'})  # Set format to '15-Oct-24'
            # Adjust column width and set format (E is the 5th column)
            worksheet.set_column('O:O', 12, date_format)

    except Exception as e:
        print(f"Error saving to Excel file: {e}")
        return False
    # df_bill_data.to_excel(file_name, index=False, sheet_name='Sheet1')

    return True

# Function to get a list of bills


def get_list(file_name: str):
    it_valid_excel, df_bill_data = check_excel(file_name)
    return df_bill_data.to_dict(orient="records")

# Function to read a specific bill by ID


def read_data(file_name: str, bill_id: str):
    it_valid_excel, df_bill_data = check_excel(file_name)
    bill = df_bill_data[df_bill_data['id'] == int(bill_id)]
    bill_data = bill.to_dict(orient='records')[0] if not bill.empty else None
    return bill_data

# Function to delete a bill by ID


def delete_bill(file_name: str, bill_id: str):
    it_valid_excel, df_bill_data = check_excel(file_name)
    if int(bill_id) not in df_bill_data['id'].values:
        return False

    df_bill_data = df_bill_data[df_bill_data['id']
                                != int(bill_id)].reset_index(drop=True)
    # print(df_bill_data)
    df_bill_data.to_excel(file_name, index=False, sheet_name='Sheet1')

    return True
