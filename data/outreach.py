"""
Institutional Outreach & Campus Sales Module:
Allows uploading Excel (.xlsx) or CSV sheets with Institute Name, Address, and Email Address.
Generates brilliant, personalized sales drafts from priyaanoopranjan@gmail.com signed by Priya Gupta
to sell this C# Azure AI & Forward Deployed Engineering portal to colleges, universities, and institutes,
with an exclusive early-bird offer for the first 100 customer institutes plus complimentary companion website access.
"""

import io
import csv
import urllib.parse
import zipfile
import xml.etree.ElementTree as ET

DEFAULT_SENDER = "priyaanoopranjan@gmail.com"
SIGN_OFF_NAME = "Priya Gupta"
SIGN_OFF_ROLE = "Head of Institutional Partnerships & Corporate Alliances"

SAMPLE_INSTITUTIONS = [
    {
        "name": "Indian Institute of Technology Delhi (IIT Delhi)",
        "address": "Hauz Khas, New Delhi, Delhi - 110016",
        "email": "dean.academics@iitd.ac.in"
    },
    {
        "name": "Birla Institute of Technology and Science (BITS Pilani)",
        "address": "Vidya Vihar, Pilani, Rajasthan - 333031",
        "email": "placement@pilani.bits-pilani.ac.in"
    },
    {
        "name": "National Institute of Technology Tiruchirappalli (NIT Trichy)",
        "address": "Tanjore Main Road, National Highway 67, Tiruchirappalli, Tamil Nadu - 620015",
        "email": "hodcse@nitt.edu"
    },
    {
        "name": "Vellore Institute of Technology (VIT University)",
        "address": "Vellore Campus, Tiruvalam Road, Katpadi, Vellore, Tamil Nadu - 632014",
        "email": "dean.scope@vit.ac.in"
    },
    {
        "name": "Delhi Technological University (DTU)",
        "address": "Shahbad Daulatpur, Main Bawana Road, Delhi - 110042",
        "email": "training.placement@dtu.ac.in"
    }
]


def generate_sales_email(institute_name: str, address: str, email: str) -> dict:
    """
    Generates a high-converting, professional institutional sales draft tailored to the institution.
    """
    institute_clean = (institute_name or "Esteemed Institution").strip()
    address_clean = (address or "Campus Headquarters").strip()
    email_clean = (email or "academic.office@institute.edu").strip()

    subject = f"Exclusive Institutional Partnership: Industry-Ready C# Azure AI & Forward Deployed Engineering (FDE) Curriculum for {institute_clean}"

    body = f"""Dear Dean of Academics / Head of Department,
{institute_clean}
{address_clean}

I hope this message finds you well.

I am reaching out to propose an exclusive industry-academia partnership for {institute_clean} designed to accelerate your engineering students and technical faculty into one of the highest-paying, most sought-after emerging technical domains globally: Forward Deployed Engineering (FDE) + Azure AI + Enterprise Cybersecurity Advisory.

---

### What Makes This Learning Portal Transformational?

While traditional university curricula and generic bootcamps teach isolated toy Python scripts or theoretical cloud concepts, global Fortune 500 enterprises and AI scale-ups run on mission-critical C# / .NET architecture integrated with Microsoft Azure.

Our "Forward Deployed Engineer (FDE) + AI + Cybersecurity Advisor Portal" provides a rigorous, 35-day structured, project-driven conversion framework:

1. 100% Enterprise C# & .NET Focus:
   - Hands-on machine learning with ML.NET in C#.
   - Multi-agent AI orchestration using Microsoft Semantic Kernel in C#.
   - Production Generative AI & Azure OpenAI .NET SDK integration with guardrails.
   - Event-driven serverless APIs via C# Azure Functions and Azure Service Bus.

2. Cloud Security & Enterprise SIEM/SOAR:
   - Microsoft Sentinel cloud SIEM ingestion, Kusto Query Language (KQL), and automated Logic Apps SOAR containment.
   - Microsoft Defender for Cloud (CSPM/CWPP) and CIS/NIST compliance posture management.
   - Zero Trust architecture: Microsoft Entra ID modern authentication, Privileged Identity Management (PIM), and Private Link.

3. Complete Production Capstones & Placement Studio:
   - 3 tangible production portfolio blueprints with full Infrastructure-as-Code (Bicep/Terraform).
   - Interactive Technical Interview Studio featuring executive pitch scripts, Architecture Review Board (ARB) simulations, and rapid-fire Q&A.
   - Day-by-day interactive labs, verified Microsoft official video deep dives, and an integrated progress tracker.

---

### Special Introductory Offer: First 100 Customer Institutions

To foster early adoption and empower the incoming graduating batch:
- We are offering an exclusive, highly subsidized institutional package at our CHEAPEST INTRODUCTORY RATE for the first 100 partner institutions that join us.
- COMPLIMENTARY BONUS: Enrolled institutions will receive complementary full-access licenses to our companion Technical Interview & Architecture Preparation Portal for all registered students at zero extra cost!

---

### Next Steps & How to Claim This Offer

We would be delighted to schedule a brief 15-minute virtual walkthrough for your placement team, academic coordinators, or departmental heads to demonstrate how this curriculum will drastically elevate your student placement packages and technical capability.

Kindly reply directly to this email ({DEFAULT_SENDER}) to secure your institution's spot among the first 100 partners and receive our detailed institutional prospectus with early-bird pricing.

Thank you for your dedication to engineering excellence. We look forward to collaborating with {institute_clean}!

Thanks and Regards,
{SIGN_OFF_NAME}
{SIGN_OFF_ROLE}
Official Email: {DEFAULT_SENDER}
Official Portal: Forward Deployed Engineer (FDE) + Azure AI Transformation System
"""

    # Prepare encoded mailto URL
    mailto_params = urllib.parse.urlencode({
        "subject": subject,
        "body": body
    })
    mailto_url = f"mailto:{email_clean}?{mailto_params}"

    return {
        "institute_name": institute_clean,
        "address": address_clean,
        "email": email_clean,
        "to_email": email_clean,
        "sender": DEFAULT_SENDER,
        "from_email": DEFAULT_SENDER,
        "sign_off": SIGN_OFF_NAME,
        "subject": subject,
        "body": body,
        "mailto_url": mailto_url
    }


def _find_column_index(headers: list, target_keywords: list) -> int:
    for idx, header in enumerate(headers):
        h_clean = str(header).lower().strip().replace("_", " ").replace("-", " ")
        for kw in target_keywords:
            if kw in h_clean:
                return idx
    return -1


def parse_csv_stream(file_stream) -> list:
    """Parses a CSV stream and extracts institute data."""
    text_data = file_stream.read()
    if isinstance(text_data, bytes):
        text_data = text_data.decode("utf-8", errors="replace")
    
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(text_data[:2048])
    except Exception:
        dialect = "excel"
        
    reader = csv.reader(io.StringIO(text_data), dialect=dialect)
    rows = [r for r in reader if any(field.strip() for field in r)]
    if not rows:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    name_idx = _find_column_index(headers, ["institute", "college", "university", "school", "name", "organization", "institution"])
    addr_idx = _find_column_index(headers, ["address", "location", "city", "state", "place", "campus"])
    email_idx = _find_column_index(headers, ["email", "mail", "contact"])

    # Fallback to column positions if headers don't match keywords
    if name_idx == -1 and len(headers) > 0:
        name_idx = 0
    if addr_idx == -1 and len(headers) > 1:
        addr_idx = 1
    if email_idx == -1 and len(headers) > 2:
        email_idx = 2

    institutes = []
    for r in data_rows:
        name = r[name_idx].strip() if name_idx != -1 and name_idx < len(r) else ""
        addr = r[addr_idx].strip() if addr_idx != -1 and addr_idx < len(r) else ""
        email = r[email_idx].strip() if email_idx != -1 and email_idx < len(r) else ""
        if name or email:
            institutes.append({
                "name": name or "Partner Institution",
                "address": addr or "Campus",
                "email": email or ""
            })

    return institutes


def parse_xlsx_stream(file_stream) -> list:
    """Parses an Excel (.xlsx) file stream natively with zipfile and ElementTree."""
    file_bytes = file_stream.read()
    if not isinstance(file_bytes, bytes):
        file_bytes = file_bytes.encode("utf-8")

    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in tree.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                texts = [t.text for t in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text]
                shared_strings.append(''.join(texts))
        
        sheet_files = [f for f in z.namelist() if f.startswith('xl/worksheets/sheet') and f.endswith('.xml')]
        if not sheet_files:
            return []
        sheet_data = z.read(sorted(sheet_files)[0])
        tree = ET.fromstring(sheet_data)
        
        rows = []
        for row in tree.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            row_vals = []
            for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                t = c.get('t')
                v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                if v is not None and v.text is not None:
                    if t == 's':
                        idx = int(v.text)
                        row_vals.append(shared_strings[idx] if idx < len(shared_strings) else '')
                    else:
                        row_vals.append(v.text)
                else:
                    is_t = c.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    if is_t is not None and is_t.text:
                        row_vals.append(is_t.text)
                    else:
                        row_vals.append('')
            if any(str(x).strip() for x in row_vals):
                rows.append(row_vals)

    if not rows:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    name_idx = _find_column_index(headers, ["institute", "college", "university", "school", "name", "organization", "institution"])
    addr_idx = _find_column_index(headers, ["address", "location", "city", "state", "place", "campus"])
    email_idx = _find_column_index(headers, ["email", "mail", "contact"])

    if name_idx == -1 and len(headers) > 0:
        name_idx = 0
    if addr_idx == -1 and len(headers) > 1:
        addr_idx = 1
    if email_idx == -1 and len(headers) > 2:
        email_idx = 2

    institutes = []
    for r in data_rows:
        name = str(r[name_idx]).strip() if name_idx != -1 and name_idx < len(r) else ""
        addr = str(r[addr_idx]).strip() if addr_idx != -1 and addr_idx < len(r) else ""
        email = str(r[email_idx]).strip() if email_idx != -1 and email_idx < len(r) else ""
        if name or email:
            institutes.append({
                "name": name or "Partner Institution",
                "address": addr or "Campus",
                "email": email or ""
            })

    return institutes


def parse_institutes_from_upload(file_storage) -> list:
    """Detects file type and parses institutes accordingly."""
    filename = (file_storage.filename or "").lower()
    if filename.endswith(".xlsx"):
        return parse_xlsx_stream(file_storage.stream)
    else:
        # Defaults to CSV parser
        return parse_csv_stream(file_storage.stream)


def get_sample_csv_template() -> str:
    """Generates standard CSV template content."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Institute Name", "Address", "Email Address"])
    for inst in SAMPLE_INSTITUTIONS:
        writer.writerow([inst["name"], inst["address"], inst["email"]])
    return output.getvalue()
