import pandas as pd
import os
from datetime import datetime


class BillingSystem:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.initialize_excel()
        self.load_data()

    def initialize_excel(self):
        """Initialize the Excel file with required sheets if it doesn't exist."""
        if not os.path.exists(self.excel_file):
            print(
                f"Excel file '{self.excel_file}' does not exist. Creating a new one.")
            bill_data_columns = [
                "id", "invoiceNo", "taxableValue", "total",
                "total_quantity", "supplierName", "supplierOtherInfo", "createdAt"
            ]
            items_columns = [
                "id", "goods", "hsn_sac", "quantity", "rate", "par",
                "amount", "villagerName", "vehicle_no", "goodType",
                "before_wight", "after_wight", "net_wight", "billDataId"
            ]
            df_billData = pd.DataFrame(columns=bill_data_columns)
            df_items = pd.DataFrame(columns=items_columns)
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                df_billData.to_excel(
                    writer, sheet_name='billData', index=False)
                df_items.to_excel(writer, sheet_name='items', index=False)
            print(
                f"Initialized Excel file '{self.excel_file}' with 'billData' and 'items' sheets.")

    def load_data(self):
        """Load data from Excel into DataFrames."""
        try:
            self.df_billData = pd.read_excel(
                self.excel_file, sheet_name='billData', engine='openpyxl'
            )
            self.df_items = pd.read_excel(
                self.excel_file, sheet_name='items', engine='openpyxl'
            )
            print("Data loaded successfully from Excel.")
        except ValueError as ve:
            print(f"Error loading data: {ve}")
            print("Attempting to reinitialize the Excel file.")
            self.initialize_excel()
            self.df_billData = pd.read_excel(
                self.excel_file, sheet_name='billData', engine='openpyxl'
            )
            self.df_items = pd.read_excel(
                self.excel_file, sheet_name='items', engine='openpyxl'
            )

    def save_data(self):
        """Save DataFrames back to Excel."""
        try:
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                self.df_billData.to_excel(
                    writer, sheet_name='billData', index=False)
                self.df_items.to_excel(writer, sheet_name='items', index=False)
            print("Data saved successfully to Excel.")
        except Exception as e:
            print(f"Error saving data: {e}")

    ### === billData CRUD Operations === ###

    def create_bill(self, invoiceNo, taxableValue, total, total_quantity,
                    supplierName, supplierOtherInfo):
        """Create a new billData entry."""
        new_id = self.df_billData['id'].max(
        ) + 1 if not self.df_billData.empty else 1
        new_bill = {
            "id": new_id,
            "invoiceNo": invoiceNo,
            "taxableValue": taxableValue,
            "total": total,
            "total_quantity": total_quantity,
            "supplierName": supplierName,
            "supplierOtherInfo": supplierOtherInfo,
            "createdAt": datetime.now()
        }
        # Using pd.concat instead of append
        self.df_billData = pd.concat(
            [self.df_billData, pd.DataFrame([new_bill])],
            ignore_index=True
        )
        self.save_data()
        print(f"Created new billData with id {new_id}.")
        return new_id

    def read_bill(self, bill_id):
        """Read a billData entry by id."""
        bill = self.df_billData[self.df_billData['id'] == bill_id]
        if bill.empty:
            print(f"No billData found with id {bill_id}.")
            return None
        print(bill)
        return bill

    def update_bill(self, bill_id, **kwargs):
        """Update a billData entry by id."""
        index = self.df_billData[self.df_billData['id'] == bill_id].index
        if index.empty:
            print(f"No billData found with id {bill_id}.")
            return False
        for key, value in kwargs.items():
            if key in self.df_billData.columns:
                self.df_billData.at[index[0], key] = value
            else:
                print(f"Column '{key}' does not exist in 'billData'.")
        self.save_data()
        print(f"Updated billData with id {bill_id}.")
        return True

    def delete_bill(self, bill_id):
        """Delete a billData entry by id."""
        if bill_id not in self.df_billData['id'].values:
            print(f"No billData found with id {bill_id}.")
            return False
        self.df_billData = self.df_billData[self.df_billData['id'] != bill_id].reset_index(
            drop=True)
        # Also delete related items
        self.df_items = self.df_items[self.df_items['billDataId'] != bill_id].reset_index(
            drop=True)
        self.save_data()
        print(f"Deleted billData with id {bill_id} and its related items.")
        return True

    ### === items CRUD Operations === ###

    def create_item(self, goods, hsn_sac, quantity, rate, par,
                    amount, villagerName, vehicle_no, goodType,
                    before_wight, after_wight, net_wight, billDataId):
        """Create a new items entry."""
        # Check if billDataId exists
        if billDataId not in self.df_billData['id'].values:
            print(f"billDataId {billDataId} does not exist.")
            return None
        new_id = self.df_items['id'].max(
        ) + 1 if not self.df_items.empty else 1
        new_item = {
            "id": new_id,
            "goods": goods,
            "hsn_sac": hsn_sac,
            "quantity": quantity,
            "rate": rate,
            "par": par,
            "amount": amount,
            "villagerName": villagerName,
            "vehicle_no": vehicle_no,
            "goodType": goodType,
            "before_wight": before_wight,
            "after_wight": after_wight,
            "net_wight": net_wight,
            "billDataId": billDataId
        }
        # Using pd.concat instead of append
        self.df_items = pd.concat(
            [self.df_items, pd.DataFrame([new_item])],
            ignore_index=True
        )
        self.save_data()
        print(
            f"Created new item with id {new_id} linked to billDataId {billDataId}.")
        return new_id

    def read_item(self, item_id):
        """Read an items entry by id."""
        item = self.df_items[self.df_items['id'] == item_id]
        if item.empty:
            print(f"No item found with id {item_id}.")
            return None
        print(item)
        return item

    def update_item(self, item_id, **kwargs):
        """Update an items entry by id."""
        index = self.df_items[self.df_items['id'] == item_id].index
        if index.empty:
            print(f"No item found with id {item_id}.")
            return False
        for key, value in kwargs.items():
            if key in self.df_items.columns:
                if key == "billDataId" and value not in self.df_billData['id'].values:
                    print(f"Cannot set billDataId to {value}: does not exist.")
                    continue
                self.df_items.at[index[0], key] = value
            else:
                print(f"Column '{key}' does not exist in 'items'.")
        self.save_data()
        print(f"Updated item with id {item_id}.")
        return True

    def delete_item(self, item_id):
        """Delete an items entry by id."""
        if item_id not in self.df_items['id'].values:
            print(f"No item found with id {item_id}.")
            return False
        self.df_items = self.df_items[self.df_items['id'] != item_id].reset_index(
            drop=True)
        self.save_data()
        print(f"Deleted item with id {item_id}.")
        return True

    ### === Additional Helper Methods === ###

    def list_bills_with_items(self):
        """List all billData entries along with their items."""
        # Assuming there's a common 'bill_id' column between df_billData and df_billItems
        # Merge df_billData with df_billItems based on 'bill_id'
        bills_with_items = pd.merge(
            self.df_billData, self.df_billItems, on='bill_id', how='left')

        # print(bills_with_items)
        return bills_with_items

    def list_items(self, billDataId=None):
        """List all items, optionally filtered by billDataId."""
        if billDataId:
            items = self.df_items[self.df_items['billDataId'] == billDataId]
        else:
            items = self.df_items
        print(items)
        return items
