import io
from math import log
import os
from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import num2words
import pandas as pd
from db import Bill, create_bill, delete_bill, get_list, read_data
from glob import glob
import webbrowser

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# Define a custom enumerate filter


def enumerate_filter(seq):
    return list(enumerate(seq))


# Add the custom filter to the Jinja2 environment
templates.env.filters['enumerate'] = enumerate_filter


@app.get("/")
async def read_item(request: Request):
    files = glob("./database/*.xlsx")

    chart_data = {
        "labels": [],
        "total_values": []
    }
    total_bills = 0

    # Assuming you're adding total values from the bills as your data source
    for file in files:
        for bill in get_list(file):
            chart_data["labels"].append(bill['createdAt'])
            chart_data["total_values"].append(bill['total'])
            total_bills += 1
    print(total_bills)
    print(chart_data)
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={
            "data": [{"id": index+1, "filename": i.split("\\")[-1]} for index, i in enumerate(files)],
            "key": ["id", "filename"],
            "chart_labels": chart_data["labels"],
            "chart_data": chart_data["total_values"],
            "total_bills": total_bills
        }
    )


@app.get("/bill_print/{file_name}/{id}")
async def bill_print(request: Request, id: str, file_name: str):
    data = read_data(os.path.join("./database", file_name), id)

    return templates.TemplateResponse(
        request=request, name="bill.html",
        context={
            "invoiceNo": data['invoiceNo'],
            "date": data['createdAt'],
            "supplierName": data['supplierName'],
            "supplierOtherInfo": data['supplierOtherInfo'],
            "items": [{
                "good": i['goods'],
                "hsn_sac": i['hsn_sac'],
                "quantity": i['quantity'],
                "rate": i['rate'],
                "par": i['par'],
                "amount": i['amount'],
                "vehicle_no": i['vehicle_no'],
                "invoiceNo": data['invoiceNo'],
                "total": data['total'],
                "amount_in_word": num2words.num2words(data['total'])

            } for i in data['items']],
            "total_quantity": data['total_quantity'],
            "total_amount": data['total'],
            "bill_items": [{
                "hsn_sac": i['hsn_sac'],
                "total": i['amount']
            } for i in data['items']],
            "tex_amount": data['taxableValue'],
            "amount_in_word": num2words.num2words(data['total'], lang="en_IN"),
            "par": data['items'][0]['par']

        }
    )


@app.get("/get_pass_print/{file_name}/{id}")
async def get_pass_print(request: Request, id: str, file_name: str):
    data = read_data(os.path.join("./database", file_name), id)

    return templates.TemplateResponse(
        request=request, name="get_pass.html",
        context={

            "items": [{
                "date": data["createdAt"],
                "good": i['goods'],


                "villagerName": i['villagerName'],


                "vehicle_no": i['vehicle_no'],


            } for i in data['items']],


        }
    )


@app.get("/get_wight_print/{file_name}/{id}")
async def get_wight_print(request: Request, id: str, file_name: str):
    data = read_data(os.path.join("./database", file_name), id)
    v: list[str] = []
    s = []
    for i in data['items']:
        if i['vehicle_no'] not in v:
            v.append(i['vehicle_no'])
            s.append(
                {
                    "date": data["createdAt"],
                    "villagerName": i['villagerName'],
                    "good": i['goods'],
                    "vehicle_no": i['vehicle_no'],
                    "googType": i['goodType'],
                    "before_wight": i['before_wight'],
                    "after_wight": i['after_wight'],
                    "net_wight": i['net_wight']
                })
    return templates.TemplateResponse(
        request=request, name="wight.html",
        context={
            "items": s

        }
    )


@app.post("/submit-bill/{file_name}")
async def submit_bill(file_name: str, bill_data: Bill,):
    try:

        # Create the billData entry with related items
        bill = create_bill(file_name=os.path.join("./database", file_name),
                           data=bill_data
                           )

        return {"message": "Bill submitted successfully", "bill": bill}
    except Exception as e:
        print(f"Error submitting bill: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/upload")
async def upload_excel(request: Request, file: UploadFile = File(...)):

    bill_data_columns = [
        "id", "invoiceNo", "taxableValue", "total",
        "total_quantity", "supplierName", "supplierOtherInfo", "createdAt"
    ]
    items_columns = [
        "id", "goods", "hsn_sac", "quantity", "rate", "par",
        "amount", "villagerName", "vehicle_no", "goodType",
        "before_wight", "after_wight", "net_wight", "billDataId"
    ]
    try:
      # Read the uploaded Excel file into DataFrames
        contents = await file.read()
        file_name = file.filename
        # Use `pd.ExcelFile` to read the Excel file with multiple sheets
        excel_file = pd.ExcelFile(contents)
        # Check if both required sheets exist
        if 'bills' not in excel_file.sheet_names or 'items' not in excel_file.sheet_names:
            raise templates.TemplateResponse(
                request=request, name="error.html",
                context={
                    "message": "Excel file must contain 'bill_data' and 'items' sheets."
                }
            )

        # Read the sheets into DataFrames
        df_bill_data = excel_file.parse('bills')
        df_items = excel_file.parse('items')

        # Validate the columns in bill_data
        if set(bill_data_columns) != set(df_bill_data.columns):
            raise templates.TemplateResponse(
                request=request, name="error.html",
                context={
                    "message": "bill_data sheet is missing required columns or has extra columns."
                }
            )

        # Validate the columns in items
        if set(items_columns) != set(df_items.columns):
            raise templates.TemplateResponse(
                request=request, name="error.html",
                context={
                    "message": "items sheet is missing required columns or has extra columns."
                }
            )

        with open(os.path.join("./database", file_name), "ab") as fs:
            fs.write(contents)
            fs.close()
        return templates.TemplateResponse(
            request=request, name="upload.html",

        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request, name="error.html",
            context={
                "message": str(e)
            }
        )


@app.get("/bills/{filename}", response_class=HTMLResponse)
async def bills(request: Request, filename: str,):
    if not os.path.exists(os.path.join("./database", filename)):
        raise templates.TemplateResponse(
            request=request, name="error.html",
            context={
                "message": f"{filename} not found!!", }
        )
    try:
        data = get_list(os.path.join("./database", filename))
        return templates.TemplateResponse(
            request=request, name="bill_data.html",
            context={
                "data": [
                    {**i,

                     "items": i['items'].__len__()
                     }
                    for i in data],
                "key":  data[-1].keys() if data.__len__() != 0 else [],
                "filename": filename

            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            request=request, name="error.html",
            context={
                "message": str(e)
            }
        )


@app.post("/export/{filename}")
async def export_data(filename: str):

    with open(os.path.join("./database", filename), "rb") as file:
        file_bytes = io.BytesIO(file.read())

    # Prepare the StreamingResponse with the BytesIO object
    response = StreamingResponse(
        file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Set the Content-Disposition header for download
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"

    return response


@app.delete("/delete/{filename}/{id}")
async def delete_data(filename: str, id: str):
    try:
        delete_bill(os.path.join("./database", filename), id)
        return {"message": "bill is delete successfully"}
    except:
        return {"message": "bill not found!!"}
