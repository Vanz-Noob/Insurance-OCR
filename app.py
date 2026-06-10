import os
import base64
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="Insurance OCR")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.ap-southeast.bytepluses.com/api/v3")
MODEL = os.getenv("MODEL", "seed-2-0-pro-260328")


def get_client():
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise ValueError("ARK_API_KEY is not set. Please set it in .env or as environment variable.")
    return OpenAI(api_key=api_key, base_url=ARK_BASE_URL)

DOCUMENT_PROMPTS = {
    "insurance_card": """You are an expert OCR system for insurance card documents. Extract all information from this insurance card image.
Return the result as a JSON object with these fields if found:
- plan_name: the insurance plan name
- health_plan_code: health plan code number
- plan_reference_number: plan reference number
- member_name: name of the member
- member_id: member ID number
- group_number: group number
- pcp_name: primary care physician name
- pcp_phone: primary care physician phone
- payer_id: payer ID
- rx_bin: pharmacy BIN number
- rx_grp: pharmacy group number
- rx_pcn: pharmacy PCN number
- issuer: insurance issuer/administrator
- other_fields: any additional fields found

Also provide a markdown formatted version of the extracted data.""",

    "medical_invoice": """You are an expert OCR system for medical insurance invoices. Extract all information from this medical invoice image.
Return the result as a JSON object with these fields if found:
- hospital_name: name of hospital/provider
- issuer_contact: issuer contact person name
- issuer_address: issuer street address
- issuer_city_state: issuer city and state
- issuer_zip: issuer ZIP code
- issuer_phone: issuer phone number
- issuer_email: issuer email
- invoice_number: invoice number/ID
- invoice_date: invoice date
- bill_to_name: recipient/billed person name
- bill_to_address: recipient street address
- bill_to_city_state: recipient city and state
- bill_to_zip: recipient ZIP code
- items: array of line items, each with description and amount
- subtotal: subtotal amount
- discount: discount amount
- tax: tax amount
- total: total amount
- support_phone: support contact phone
- support_email: support contact email
- other_fields: any additional fields found

Also provide a markdown formatted version of the extracted data.""",

    "cms1500": """You are an expert OCR system for CMS-1500 (HCFA-1500) health insurance claim forms. Extract all information from this claim form image.
Return the result as a JSON object with these fields if found:
- insurance_type: checked insurance type (Medicare, Medicaid, CHAMPUS, CHAMPVA, Group Health Plan, FECA Black Lung, Other)
- insured_id_number: insured's ID number (field 1a)
- patient_name: patient's name - Last, First, Middle (field 2)
- patient_dob: patient's date of birth (field 3)
- patient_sex: patient's sex (field 3)
- insured_name: insured's name (field 4)
- patient_address: patient street address (field 5)
- patient_city: patient city (field 5)
- patient_state: patient state (field 5)
- patient_zip: patient ZIP (field 5)
- patient_phone: patient phone (field 5)
- patient_relationship: relationship to insured (field 6)
- insured_address: insured street address (field 7)
- insured_city_state_zip: insured city, state, ZIP (field 7)
- insured_phone: insured phone (field 7)
- patient_marital_status: marital status (field 8)
- insured_policy_group_number: policy/group/FECA number (field 11)
- insured_dob: insured date of birth (field 11a)
- insured_sex: insured sex (field 11a)
- insurance_plan_name: insurance plan name (field 11c)
- another_health_benefit_plan: yes/no (field 11d)
- patient_signature: patient signature (field 12)
- patient_signature_date: signature date (field 12)
- insured_signature: insured signature (field 13)
- date_of_current_illness: date of current illness/injury (field 14)
- first_date_similar_illness: first date of same/similar illness (field 15)
- referring_provider: referring provider name (field 17)
- diagnosis_codes: array of ICD diagnosis codes (field 21)
- service_lines: array of service line items, each with from_date, to_date, place_of_service, type_of_service, cpt_code, diagnosis_pointer, charges, days_units (field 24)
- total_charge: total charge (field 28)
- provider_name: rendering provider name (field 33)
- provider_npi: provider NPI (field 33)
- other_fields: any additional fields found

Also provide a markdown formatted version of the extracted data.""",

    "drivers_license": """You are an expert OCR system for driver's license / ID card documents. Extract all information from this driver's license image.
Return the result as a JSON object with these fields if found:
- document_type: type of document (e.g. "Driver License")
- expiration_date: expiration date
- license_number: driver's license number
- license_class: license class
- endorsements: endorsements
- last_name: last name
- first_name: first name
- address_street: street address
- address_city_state_zip: city, state, ZIP
- date_of_birth: date of birth
- sex: sex
- hair_color: hair color
- eye_color: eye color
- height: height
- weight: weight
- organ_donor: organ donor status
- other_fields: any additional fields found

Also provide a markdown formatted version of the extracted data.""",

    "medical_record": """You are an expert OCR system for medical records. Extract all information from this medical record document.
Return the result as a JSON object with relevant fields found in the document such as:
- patient_info
- visit_date
- provider
- diagnosis
- treatment
- medications
- notes
- other_fields: any additional fields found

Also provide a markdown formatted version of the extracted data.""",

    "receipt": """You are an expert OCR system for medical receipts/kuitansi. Extract all information from this receipt image.
Return the result as a JSON object with these fields if found:
- receipt_number
- date
- patient_name
- total_amount
- items: array of line items
- payment_method
- provider
- other_fields: any additional fields found

Also provide a markdown formatted version of the extracted data.""",

    "prescription": """You are an expert OCR system for prescription/medication detail documents. Extract all information from this document.
Return the result as a JSON object with these fields if found:
- patient_name
- prescriber
- date
- medications: array with name, dosage, frequency, quantity, instructions
- pharmacy
- other_fields: any additional fields found

Also provide a markdown formatted version of the extracted data.""",

    "lab_result": """You are an expert OCR system for laboratory result documents. Extract all information from this lab result document.
Return the result as a JSON object with these fields if found:
- patient_name
- test_date
- ordering_provider
- lab_name
- tests: array with test_name, result, unit, reference_range, status
- notes
- other_fields: any additional fields found

Also provide a markdown formatted version of the extracted data.""",

    "other": """You are an expert OCR system for insurance/medical documents. Extract all information from this document image.
Return the result as a JSON object with all relevant fields found in the document.
Also provide a markdown formatted version of the extracted data.""",
}


def encode_image(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")


def call_ocr(image_base64: str, doc_type: str) -> dict:
    prompt = DOCUMENT_PROMPTS.get(doc_type, DOCUMENT_PROMPTS["other"])

    system_prompt = """You are an expert OCR system. You must respond with a valid JSON object containing exactly two keys:
1. "markdown" - a string containing the extracted data formatted in markdown
2. "json" - an object containing the structured extracted data

Make sure the JSON is valid and properly formatted. Do not include any text outside the JSON object."""

    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            },
        ],
        max_tokens=4096,
    )

    result_text = response.choices[0].message.content.strip()

    # Try to parse JSON from the response
    # Handle cases where the model wraps JSON in markdown code blocks
    if result_text.startswith("```"):
        lines = result_text.split("\n")
        # Remove first and last lines (code block markers)
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        result_text = "\n".join(lines)

    try:
        parsed = json.loads(result_text)
        return parsed
    except json.JSONDecodeError:
        return {
            "markdown": result_text,
            "json": {"raw_text": result_text},
        }


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r") as f:
        return f.read()


@app.post("/api/ocr")
async def ocr_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
):
    file_bytes = await file.read()
    image_base64 = encode_image(file_bytes)

    result = call_ocr(image_base64, doc_type)

    return {
        "doc_type": doc_type,
        "filename": file.filename,
        "result": result,
    }


@app.post("/api/ocr/batch")
async def ocr_batch(
    insurance_card: UploadFile = File(None),
    medical_invoice: UploadFile = File(None),
):
    results = {}

    if insurance_card:
        file_bytes = await insurance_card.read()
        image_base64 = encode_image(file_bytes)
        results["insurance_card"] = {
            "doc_type": "insurance_card",
            "filename": insurance_card.filename,
            "result": call_ocr(image_base64, "insurance_card"),
        }

    if medical_invoice:
        file_bytes = await medical_invoice.read()
        image_base64 = encode_image(file_bytes)
        results["medical_invoice"] = {
            "doc_type": "medical_invoice",
            "filename": medical_invoice.filename,
            "result": call_ocr(image_base64, "medical_invoice"),
        }

    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
