from pyppeteer import launch
import asyncio
import pdfkit
import httpx
from xhtml2pdf import pisa
import requests
from pyhtml2pdf import converter
import datetime
import io
import os
from typing import Annotated
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import num2words
import pandas as pd
from db import Bill, check_excel, create_bill, delete_bill, get_list, read_data
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


@ app.get("/")
async def read_item(request: Request):
    try:
        files = glob("./database/*.xlsx")
        f = []
        for file in files:
            if not file.split("\\")[-1].startswith("~$"):
                print(file)
                f.append(file)
        chart_data = {
            "labels": [],
            "total_values": []
        }
        total_bills = 0

        # Assuming you're adding total values from the bills as your data source
        for file in f:
            for bill in get_list(file):
                # print(bill)
                print(type(bill['createdAt']) is pd.Timestamp)
                chart_data["labels"].append(bill["createdAt"].strftime(
                    "%d-%b-%y") if type(bill['createdAt']) is pd.Timestamp else bill["createdAt"])
                chart_data["total_values"].append(
                    float(bill['quantity']) * float(bill['rate']))
                total_bills += 1
        return templates.TemplateResponse(
            request=request, name="index.html",
            context={
                "data": [{"id": index+1, "filename": i.split("\\")[-1]} for index, i in enumerate(f)],
                "key": ["id", "filename"],
                "chart_labels": chart_data["labels"],
                "chart_data": chart_data["total_values"],
                "total_bills": total_bills
            }
        )
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            request=request, name="error.html",
            context={
                "message": "error on file replace or delete file {file} or close the file {file}".format(file=file.split("\\")[-1])
            }
        )


@app.get("/bill_print/{file_name}/{id}")
async def bill_print(request: Request, id: str, file_name: str):
    data = read_data(os.path.join("./database", file_name), id)
    return templates.TemplateResponse(
        request=request, name="bill.html",
        context={
            "invoiceNo": data['invoiceNo'],
            "date":  data["createdAt"].strftime(
                "%d-%b-%y") if type(data['createdAt']) is pd.Timestamp else data["createdAt"],
            "supplierName": data['supplierName'],
            "supplierOtherInfo": data['supplierOtherInfo'],
            "items": [{
                "good": data['goods'],
                "hsn_sac": data['hsn_sac'],
                "quantity": float(data['quantity']),
                "rate": float(data['rate']),
                "par": data['par'],
                "amount": float(data['quantity']) * float(data['rate']),
                "vehicle_no": data['vehicle_no'],
                "invoiceNo": data['invoiceNo'],
                "total": float(data['quantity']) * float(data['rate']),
                "amount_in_word": num2words.num2words(float(data['quantity']) * float(data['rate']))

            }],
            "total_quantity": data['quantity'],
            "total_amount": float(data['quantity']) * float(data['rate']),
            "bill_items": [{
                "hsn_sac": data['hsn_sac'],
                "total": float(data['quantity']) * float(data['rate'])
            }],
            "tex_amount": float(data['quantity']) * float(data['rate']),
            "amount_in_word": num2words.num2words(float(data['quantity']) * float(data['rate']), lang="en_IN"),
            "par": data['par']

        }
    )


@app.get("/bill_all_print/{file_name}")
async def bill_print_all(request: Request,  file_name: str):
    data = get_list(os.path.join("./database", file_name))
    return templates.TemplateResponse(
        request=request, name="all_bill.html",
        context={
            "data": [{"invoiceNo": i['invoiceNo'],
                     "date":  i["createdAt"].strftime(
                "%d-%b-%y") if type(i['createdAt']) is pd.Timestamp else i["createdAt"],
                "supplierName": i['supplierName'],
                "supplierOtherInfo": i['supplierOtherInfo'],
                "items": [{
                    "good": i['goods'],
                    "hsn_sac": i['hsn_sac'],
                    "quantity": float(i['quantity']),
                    "rate": float(i['rate']),
                    "par": i['par'],
                    "amount": float(i['quantity']) * float(i['rate']),
                    "vehicle_no": i['vehicle_no'],
                    "invoiceNo": i['invoiceNo'],
                    "total": float(i['quantity']) * float(i['rate']),
                    "amount_in_word": num2words.num2words(float(i['quantity']) * float(i['rate']))

                }],
                "total_quantity": i['quantity'],
                "total_amount": float(i['quantity']) * float(i['rate']),
                "bill_items": [{
                    "hsn_sac": i['hsn_sac'],
                    "total": float(i['quantity']) * float(i['rate'])
                }],
                "tex_amount": float(i['quantity']) * float(i['rate']),
                "amount_in_word": num2words.num2words(float(i['quantity']) * float(i['rate']), lang="en_IN"),
                "par": i['par']} for i in data]

        }
    )


@app.get("/get_pass_print/{file_name}/{id}")
async def get_pass_print(request: Request, id: str, file_name: str):
    data = read_data(os.path.join("./database", file_name), id)

    return templates.TemplateResponse(
        request=request, name="get_pass.html",
        context={

            "items": [{
                "date": data["createdAt"].strftime(
                    "%d-%b-%y") if type(data['createdAt']) is pd.Timestamp else data["createdAt"],
                "good": data['goods'],


                "villagerName": data['villagerName'],


                "vehicle_no": data['vehicle_no'],


            }],


        }
    )


@app.get("/get_all_pass_print/{file_name}")
async def get_pass_print_all(request: Request, file_name: str):
    data = get_list(os.path.join("./database", file_name))

    return templates.TemplateResponse(
        request=request, name="all_get_pass.html",
        context={

            "data": [{"items": [{
                "date": i["createdAt"].strftime(
                    "%d-%b-%y") if type(i['createdAt']) is pd.Timestamp else i["createdAt"],
                "good": i['goods'],


                "villagerName": i['villagerName'],


                "vehicle_no": i['vehicle_no'],


            }]} for i in data],


        }
    )


@app.get("/get_wight_print/{file_name}/{id}")
async def get_wight_print(request: Request, id: str, file_name: str):
    data = read_data(os.path.join("./database", file_name), id)
    v: list[str] = []
    s = []
    for i in [data]:
        if i['vehicle_no'] not in v:
            v.append(i['vehicle_no'])
            s.append(
                {
                    "date": data["createdAt"].strftime(
                        "%d-%b-%y") if type(data['createdAt']) is pd.Timestamp else data["createdAt"],
                    "villagerName": i['villagerName'],
                    "good": i['goods'],
                    "vehicle_no": i['vehicle_no'],
                    "googType": i['goodType'],
                    "before_wight": i['before_wight'],
                    "after_wight": i['after_wight'],
                    "net_wight": i['after_wight'] - i['before_wight']
                })
    return templates.TemplateResponse(
        request=request, name="wight.html",
        context={
            "items": s

        }
    )


@app.get("/get_all_wight_print/{file_name}")
async def get_wight_print_all(request: Request, file_name: str):
    data = get_list(os.path.join("./database", file_name))
    d = []
    for j in data:
        v: list[str] = []
        s = []
        for i in [j]:

            if i['vehicle_no'] not in v:
                v.append(i['vehicle_no'])
                s.append(
                    {
                        "date": j["createdAt"].strftime(
                            "%d-%b-%y") if type(j['createdAt']) is pd.Timestamp else j["createdAt"],
                        "villagerName": i['villagerName'],
                        "good": i['goods'],
                        "vehicle_no": i['vehicle_no'],
                        "googType": i['goodType'],
                        "before_wight": i['before_wight'],
                        "after_wight": i['after_wight'],
                        "net_wight": i['after_wight'] - i['before_wight']
                    })
            d.append(s)
    return templates.TemplateResponse(
        request=request, name="all_wight.html",
        context={
            "data": [{"items": s} for s in d]

        }
    )


@app.post("/submit-bill/{file_name}")
async def submit_bill(file_name: str, bill_data: Bill):
    try:
        print(bill_data)
        # Create the billData entry with related items
        bill = create_bill(file_name=os.path.join("./database", file_name),
                           data=bill_data
                           )

        return {"message": "Bill submitted successfully", "bill": bill}
    except Exception as e:
        # print(f"Error submitting bill: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/upload")
async def upload_excel(request: Request, file: UploadFile = File(...)):

    bill_data_columns = [
        "id", "invoiceNo",  "supplierName", "supplierOtherInfo", "createdAt",
        "goods", "hsn_sac", "quantity", "rate", "par",
        "villagerName", "vehicle_no", "goodType",
        "before_wight", "after_wight"
    ]
    try:
      # Read the uploaded Excel file into DataFrames
        contents = await file.read()
        file_name = file.filename
        # Use `pd.ExcelFile` to read the Excel file with multiple sheets
        excel_file = pd.read_csv(io.BytesIO(contents))
        # Check if both required sheets exist

        # Read the sheets into DataFrames
        df_bill_data = excel_file
        # print(set(bill_data_columns), set(df_bill_data.columns))

        # Validate the columns in bill_data
        if set(bill_data_columns) != set(df_bill_data.columns):
            return templates.TemplateResponse(
                request=request, name="error.html",
                context={
                    "message": "bill_data sheet is missing required columns or has extra columns."
                }
            )
        df_bill_data.to_csv(os.path.join("./database", file_name), index=False)

        return templates.TemplateResponse(
            request=request, name="upload.html",

        )

    except Exception as e:
        # print(e)
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
                "data": data,
                "key":  data[-1].keys() if data.__len__() != 0 else [],
                "filename": filename

            }
        )
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            request=request, name="error.html",
            context={
                "message":  "error on file replace or delete file {file} or close the file {file}".format(file=filename.split("\\")[-1])
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


@app.post("/create-template")
async def create_template(request: Request, filename: str = Form(...)):
    try:
        check_excel(os.path.join("./database", filename+".xlsx"))
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


async def convert_html_to_pdf(source_html, output_filename):
    try:
        # Launch headless browser
        browser = await launch(headless=True, executablePath="C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
        page = await browser.newPage()  # Open a new page
        # await page.setContent(source_html)
        # Set HTML content
        await page.setContent(source_html)
        await page.pdf({'path': output_filename, 'format': 'A4', "margins": {
            'top': '75px',
            'right': '75px',
            'bottom': '75px',
            'left': '75px'
        },
            "printBackground": True,
            "preferCSSPageSize": True
        },

        )  # Save PDF
        await browser.close()  # Close browser
        print(f"PDF successfully generated: {output_filename}")
    except Exception as e:
        print(f"Error generating PDF: {e}")


@app.post("/create-pdf/{filename}")
async def create_pdf(filename: str, request: Request):
    data = get_list(os.path.join("./database", filename))
    base_url = request.base_url

    # Iterate over each bill and create the necessary directories and PDFs
    for i in data:
        invoice_dir = f"./pdf/{i['invoiceNo']}"
        os.makedirs(invoice_dir, exist_ok=True)

        # Define the URLs for bill, get_pass, and wight
        bill_url = f'{base_url}bill_print/{filename}/{i["id"]}'
        get_pass_url = f'{base_url}get_pass_print/{filename}/{i["id"]}'
        wight_url = f'{base_url}get_wight_print/{filename}/{i["id"]}'

        # Fetch the content asynchronously using httpx
        async with httpx.AsyncClient() as client:
            bill_response = await client.get(bill_url)
            get_pass_response = await client.get(get_pass_url)
            wight_response = await client.get(wight_url)

        # If the requests are successful, convert the HTML to PDF
        if bill_response.status_code == 200:
            bill_content = bill_response.text
            await convert_html_to_pdf(bill_content, f"{invoice_dir}/bill.pdf")

        if get_pass_response.status_code == 200:
            get_pass_content = get_pass_response.text
            await convert_html_to_pdf(get_pass_content, f"{invoice_dir}/get_pass.pdf")

        if wight_response.status_code == 200:
            wight_content = wight_response.text
            await convert_html_to_pdf(wight_content, f"{invoice_dir}/wight.pdf")
    return {"message": "PDFs generated successfully"}


@app.on_event("startup")
async def startup():
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
