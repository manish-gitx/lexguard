#!/usr/bin/env python3
"""Generate India-oriented fictional legal/compliance PDFs for demos."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "original_samples"
PAGE_W, PAGE_H = LETTER


def styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(
        name="DocTitle",
        parent=base["Title"],
        fontName="Times-Bold",
        fontSize=16,
        leading=19,
        alignment=TA_CENTER,
        spaceAfter=9,
        textColor=colors.HexColor("#111111"),
    ))
    base.add(ParagraphStyle(
        name="DocSubtitle",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=8.5,
        leading=10.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#333333"),
    ))
    base.add(ParagraphStyle(
        name="Section",
        parent=base["Heading2"],
        fontName="Times-Bold",
        fontSize=11,
        leading=13,
        spaceBefore=9,
        spaceAfter=5,
    ))
    base.add(ParagraphStyle(
        name="Body",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=9.2,
        leading=11.7,
        spaceAfter=5,
    ))
    base.add(ParagraphStyle(
        name="Small",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=7.6,
        leading=9.2,
        textColor=colors.HexColor("#333333"),
    ))
    base.add(ParagraphStyle(
        name="Field",
        parent=base["Normal"],
        fontName="Times-Bold",
        fontSize=9,
        leading=11,
    ))
    base.add(ParagraphStyle(
        name="RightSmall",
        parent=base["Small"],
        alignment=TA_RIGHT,
    ))
    base.add(ParagraphStyle(
        name="TableCell",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=7.7,
        leading=9,
    ))
    base.add(ParagraphStyle(
        name="TableHead",
        parent=base["TableCell"],
        fontName="Times-Bold",
        alignment=TA_CENTER,
    ))
    return base


ST = styles()


def p(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(text, ST[style])


def checkbox(label: str, checked: bool = False) -> Paragraph:
    mark = "X" if checked else "&nbsp;"
    return p(f'<font name="Helvetica">[{mark}]</font>&nbsp; {label}', "Body")


def base_canvas(canvas, doc, footer: str, watermark: str = "SAMPLE"):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#222222"))
    canvas.setLineWidth(0.8)
    canvas.rect(0.45 * inch, 0.42 * inch, PAGE_W - 0.9 * inch, PAGE_H - 0.84 * inch)

    canvas.setFillColor(colors.HexColor("#D8D8D8"))
    if hasattr(canvas, "setFillAlpha"):
        canvas.setFillAlpha(0.22)
    canvas.translate(PAGE_W / 2, PAGE_H / 2)
    canvas.rotate(38)
    canvas.setFont("Helvetica-Bold", 64)
    canvas.drawCentredString(0, 0, watermark)
    canvas.rotate(-38)
    canvas.translate(-PAGE_W / 2, -PAGE_H / 2)

    if hasattr(canvas, "setFillAlpha"):
        canvas.setFillAlpha(1)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.setFont("Helvetica", 6.8)
    canvas.drawString(0.55 * inch, 0.25 * inch, footer)
    canvas.drawRightString(PAGE_W - 0.55 * inch, 0.25 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(filename: str, story, footer: str):
    OUT.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT / filename),
        pagesize=LETTER,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title=filename.replace("_", " ").replace(".pdf", ""),
        author="LexGuard Demo",
    )
    doc.build(
        story,
        onFirstPage=lambda c, d: base_canvas(c, d, footer),
        onLaterPages=lambda c, d: base_canvas(c, d, footer),
    )


def stamp_box(title: str, lines: list[str]):
    rows = [[p(f'<font color="#8B1A1A"><b>{title}</b></font>', "TableHead")]]
    rows.extend([[p(f'<font color="#8B1A1A">{line}</font>', "Small")] for line in lines])
    table = Table(rows, colWidths=[1.7 * inch])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#8B1A1A")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#8B1A1A")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def seal_table(title: str):
    return Table(
        [[p(title, "TableHead")], [p("FAMILY COURT", "Small")], [p("DEMO COPY", "Small")]],
        colWidths=[1.15 * inch],
        style=TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#555555")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F5F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
    )


def divorce_document():
    story = [
        Table(
            [[seal_table("MUMBAI"), p(
                "IN THE FAMILY COURT AT BANDRA, MUMBAI<br/>MARRIAGE PETITION NO. A-1842 OF 2026",
                "DocSubtitle",
            ), stamp_box("PRESENTED", ["05/07/2026", "FAMILY COURT REGISTRY"])]],
            colWidths=[1.25 * inch, 3.85 * inch, 1.9 * inch],
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]),
        ),
        Spacer(1, 0.1 * inch),
        p("JOINT PETITION FOR DIVORCE BY MUTUAL CONSENT", "DocTitle"),
        p("Under Section 13B of the Hindu Marriage Act, 1955", "DocSubtitle"),
        Spacer(1, 0.08 * inch),
        Table(
            [[p("Petitioner No. 1 / Husband", "TableHead"), p("Petitioner No. 2 / Wife", "TableHead"), p("Jurisdiction Details", "TableHead")],
             [p("Arjun Mehta<br/>Age: 35 years<br/>Occupation: Product Manager<br/>Aadhaar: XXXX XXXX 1842", "TableCell"),
              p("Nisha Rao Mehta<br/>Age: 33 years<br/>Occupation: Architect<br/>Aadhaar: XXXX XXXX 7721", "TableCell"),
              p("Last matrimonial home:<br/>Flat 1204, Sapphire Heights,<br/>Andheri West, Mumbai 400053", "TableCell")],
             [p("Current address:<br/>B-804, Palm Grove CHS,<br/>Powai, Mumbai 400076", "TableCell"),
              p("Current address:<br/>903, Sea View Residency,<br/>Bandra West, Mumbai 400050", "TableCell"),
              p("Date of marriage: 18 February 2017<br/>Place: Mumbai, Maharashtra<br/>Date of separation: 12 January 2025", "TableCell")]],
            colWidths=[2.25 * inch, 2.25 * inch, 2.3 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#444444")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]),
        ),
        p("The Petitioners above named respectfully submit as follows:", "Body"),
        p("1. The marriage between the Petitioners was solemnised according to Hindu rites and ceremonies at Mumbai on 18 February 2017 and was registered with the Municipal Corporation of Greater Mumbai.", "Body"),
        p("2. The Petitioners last resided together within the territorial jurisdiction of this Hon'ble Court. They have been living separately since 12 January 2025 and have not resumed cohabitation thereafter.", "Body"),
        p("3. The Petitioners state that they have been unable to live together and have mutually agreed that the marriage should be dissolved by a decree of divorce by mutual consent under Section 13B of the Hindu Marriage Act, 1955.", "Body"),
        p("4. There is one minor child, Tara Mehta, born on 04 June 2020. The parties have agreed on parenting time, education expenses, medical insurance, and decision-making as recorded in the settlement schedule annexed hereto.", "Body"),
        p("5. All articles, stridhan, bank accounts, household items, insurance policies, liabilities, and claims for permanent alimony or maintenance have been settled voluntarily as set out in Annexure A.", "Body"),
        p("6. The Petitioners declare that this petition is filed without force, fraud, coercion, undue influence, or collusion and that there is no other matrimonial proceeding pending between them except the present petition.", "Body"),
        p("PRAYER", "Section"),
        p("The Petitioners therefore pray that this Hon'ble Court may be pleased to pass a decree dissolving the marriage solemnised between the Petitioners on 18 February 2017 by mutual consent and pass such other orders as may be just and proper.", "Body"),
        Spacer(1, 0.08 * inch),
        Table(
            [[p("Mumbai<br/>Date: 05 July 2026", "Body"), p("Petitioner No. 1<br/><br/>/s/ Arjun Mehta", "Body"), p("Petitioner No. 2<br/><br/>/s/ Nisha Rao Mehta", "Body")],
             [p("Advocate for Petitioners", "Small"), p("/s/ Kavita Deshpande<br/>Enrolment No. MAH/1842/2011", "Small"), p("Verified before registry<br/>Demo filing reference: FC-MUM-2026-1842", "Small")]],
            colWidths=[2.0 * inch, 2.4 * inch, 2.4 * inch],
            rowHeights=[0.72 * inch, 0.42 * inch],
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
        ),
        PageBreak(),
        p("ANNEXURE A: TERMS OF SETTLEMENT", "DocTitle"),
        Table(
            [[p("Subject", "TableHead"), p("Agreed Term", "TableHead")],
             [p("Custody and access", "TableCell"), p("Mother to have primary care and residence of the minor child. Father to have alternate weekend access, shared school holidays, and video calls on Wednesday and Sunday.", "TableCell")],
             [p("Education and medical expenses", "TableCell"), p("Education expenses, tuition, books, uniforms, and agreed extracurricular activities to be shared equally. Existing medical insurance to be continued by Petitioner No. 1.", "TableCell")],
             [p("Permanent alimony", "TableCell"), p("Full and final settlement amount of INR 18,00,000 payable in two tranches: INR 9,00,000 at first motion and INR 9,00,000 at second motion.", "TableCell")],
             [p("Stridhan and articles", "TableCell"), p("Jewellery and personal articles listed in inventory dated 20 June 2026 handed over to Petitioner No. 2. Household items divided by possession.", "TableCell")],
             [p("Future claims", "TableCell"), p("Subject to orders concerning the minor child, both parties waive future civil and matrimonial claims arising from the marriage.", "TableCell")]],
            colWidths=[1.8 * inch, 5.0 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#444444")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]),
        ),
        p("VERIFICATION", "Section"),
        p("We, Arjun Mehta and Nisha Rao Mehta, verify that the contents of paragraphs 1 to 6 and Annexure A are true to our knowledge and belief and that no material fact has been concealed.", "Body"),
        Spacer(1, 0.18 * inch),
        Table(
            [[p("Verified at Mumbai on 05 July 2026", "Body"), p("/s/ Arjun Mehta", "Body"), p("/s/ Nisha Rao Mehta", "Body")]],
            colWidths=[2.4 * inch, 2.2 * inch, 2.2 * inch],
        ),
        Spacer(1, 0.14 * inch),
        p("Note: This fictional document is drafted only for LexGuard product demonstration. It is not a court form, legal advice, or a filing-ready petition.", "Small"),
    ]
    build_pdf(
        "01_india_mutual_consent_divorce_petition_sample.pdf",
        story,
        "LexGuard demo sample | Fictional Indian mutual-consent divorce petition | Not a legal document",
    )


def rental_document():
    story = [
        Table(
            [[p("LEAVE AND LICENCE AGREEMENT", "DocTitle")],
             [p("Maharashtra residential premises | Fictional demo original", "DocSubtitle")]],
            colWidths=[6.8 * inch],
            style=TableStyle([
                ("BOX", (0, 0), (-1, -1), 1.1, colors.HexColor("#1F2933")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F6F8")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]),
        ),
        Spacer(1, 0.1 * inch),
        Table(
            [[p("<b>Execution Date:</b> 05 July 2026<br/><b>Place:</b> Mumbai, Maharashtra", "Body"),
              p("<b>e-Registration Token:</b> LNL-MH-DEMO-2026-7712<br/><b>Stamp Duty:</b> Demo calculated under Article 36A", "Body")],
             [p("<b>Licensor:</b> Rohan Shah<br/>PAN: AABPS1842K<br/>Address: 18 Lotus Court, Juhu, Mumbai 400049", "Body"),
              p("<b>Licensee:</b> Priya Nair<br/>PAN: BCNPN7721Q<br/>Address: 42 Green Park, Pune 411007", "Body")]],
            colWidths=[3.4 * inch, 3.4 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.55, colors.HexColor("#555555")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]),
        ),
        p("1. <b>Licensed Premises.</b> The Licensor grants the Licensee leave and licence to use Flat No. 703, Silver Orchid CHS Ltd., Linking Road, Bandra West, Mumbai 400050, together with one covered car parking space, for residential use only.", "Body"),
        p("2. <b>Term.</b> The licence period shall be eleven months commencing on 01 August 2026 and ending on 30 June 2027, unless terminated earlier in accordance with this Agreement.", "Body"),
        p("3. <b>Licence Fee.</b> The Licensee shall pay a monthly licence fee of INR 72,000 on or before the fifth day of each English calendar month by bank transfer to the Licensor's nominated account.", "Body"),
        p("4. <b>Security Deposit.</b> The Licensee shall pay an interest-free refundable security deposit of INR 2,16,000. The Licensor may deduct unpaid licence fees, utilities, repair costs beyond normal wear, or society dues attributable to the Licensee.", "Body"),
        p("5. <b>Registration.</b> The parties record that leave-and-licence agreements in Maharashtra are required to be in writing and registered. The Licensor shall cooperate in e-registration and the parties shall bear statutory charges as stated in the payment schedule.", "Body"),
        p("6. <b>Use and Occupancy.</b> The Licensee shall not transfer, assign, sub-license, create tenancy rights, conduct business, store hazardous articles, or alter the premises without prior written permission.", "Body"),
        p("7. <b>Maintenance and Utilities.</b> Electricity, piped gas, internet, and usage-based charges shall be paid by the Licensee. Society maintenance charges and property taxes shall be borne by the Licensor unless specifically billed for Licensee usage.", "Body"),
        p("8. <b>Termination.</b> Either party may terminate by giving thirty days' written notice. Upon termination or expiry, the Licensee shall hand over vacant and peaceful possession with keys, access cards, and parking tags.", "Body"),
        p("9. <b>Inspection.</b> The Licensor may inspect the premises after giving reasonable prior notice, except in emergencies affecting safety, leakage, fire, security, or building compliance.", "Body"),
        p("10. <b>Dispute Resolution.</b> Disputes shall be subject to competent courts and authorities at Mumbai, Maharashtra, without prejudice to applicable rent control, registration, and stamp laws.", "Body"),
        p("PAYMENT AND STATUTORY SUMMARY", "Section"),
        Table(
            [[p("Particular", "TableHead"), p("Amount / Detail", "TableHead"), p("Responsibility", "TableHead")],
             [p("Monthly licence fee", "TableCell"), p("INR 72,000", "TableCell"), p("Licensee", "TableCell")],
             [p("Security deposit", "TableCell"), p("INR 2,16,000", "TableCell"), p("Licensee; refundable subject to deductions", "TableCell")],
             [p("Stamp duty", "TableCell"), p("Demo amount: INR 2,198", "TableCell"), p("Shared equally", "TableCell")],
             [p("Registration fee and DHC", "TableCell"), p("Demo amount: INR 1,300", "TableCell"), p("Shared equally", "TableCell")]],
            colWidths=[2.3 * inch, 2.0 * inch, 2.5 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#333333")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]),
        ),
        PageBreak(),
        p("LEAVE AND LICENCE AGREEMENT - EXECUTION PAGE", "DocTitle"),
        p("SCHEDULE OF PREMISES", "Section"),
        Table(
            [[p("Building / Society", "TableHead"), p("Silver Orchid Co-operative Housing Society Ltd.", "TableCell")],
             [p("Flat", "TableHead"), p("Flat No. 703, seventh floor, carpet area approx. 760 sq. ft.", "TableCell")],
             [p("Fixtures", "TableHead"), p("Two wardrobes, modular kitchen cabinets, geyser, ceiling fans, lights, video door phone, and one parking access card.", "TableCell")],
             [p("Police intimation", "TableHead"), p("The Licensee shall provide identity proof and photographs required for society records and local police intimation, where applicable.", "TableCell")]],
            colWidths=[1.9 * inch, 4.9 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#444444")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F1F2")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]),
        ),
        p("WITNESSES AND SIGNATURES", "Section"),
        Table(
            [[p("Licensor", "TableHead"), p("Licensee", "TableHead"), p("Witnesses", "TableHead")],
             [p("Rohan Shah<br/><br/>/s/ Rohan Shah<br/>Date: 05 July 2026", "Body"),
              p("Priya Nair<br/><br/>/s/ Priya Nair<br/>Date: 05 July 2026", "Body"),
              p("1. /s/ Neel Shah<br/>2. /s/ Asha Menon<br/><br/>Biometric and Aadhaar authentication: Demo only", "Body")]],
            colWidths=[2.25 * inch, 2.25 * inch, 2.3 * inch],
            rowHeights=[0.25 * inch, 1.15 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.55, colors.HexColor("#444444")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]),
        ),
        Spacer(1, 0.12 * inch),
        p("Document ID: MH-LNL-DEMO-2026-703 | This is a fictional product-demo document and not a registered instrument.", "Small"),
    ]
    build_pdf(
        "02_india_maharashtra_leave_and_licence_sample.pdf",
        story,
        "LexGuard demo sample | Fictional Maharashtra leave-and-licence agreement | Not registered",
    )


def privacy_document():
    rights = [
        "Access information about personal data processed by the Data Fiduciary.",
        "Request correction, completion, updating, or erasure of eligible personal data.",
        "Withdraw consent for future processing where processing is based on consent.",
        "Use grievance redressal and escalation channels stated in this notice.",
        "Nominate another individual to exercise rights in the event of death or incapacity.",
    ]
    story = [
        Table(
            [[p("BHARAT BAZAAR DIGITAL PRIVATE LIMITED", "DocTitle")],
             [p("DATA PRINCIPAL NOTICE AND CONSENT REQUEST", "DocSubtitle")],
             [p("Digital Personal Data Protection Act, 2023 and DPDP Rules, 2025 | Fictional demo original", "DocSubtitle")]],
            colWidths=[6.8 * inch],
            style=TableStyle([
                ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor("#263238")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF4F2")),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]),
        ),
        Spacer(1, 0.1 * inch),
        p("This notice explains how Bharat Bazaar Digital Private Limited, acting as a Data Fiduciary, processes personal data of customers using its shopping app and website. All names, contacts, and facts in this document are fictional.", "Body"),
        p("DATA FIDUCIARY AND CONTACTS", "Section"),
        Table(
            [[p("Registered Office", "TableHead"), p("Grievance Contact", "TableHead"), p("Consent Manager / Portal", "TableHead")],
             [p("Bharat Bazaar Digital Pvt. Ltd.<br/>4th Floor, Indus Tech Park,<br/>Outer Ring Road, Bengaluru 560103", "TableCell"),
              p("Grievance Officer: Meera Iyer<br/>Email: privacy@bharatbazaar-demo.example<br/>Phone: 080-5555-1842", "TableCell"),
              p("Portal: privacy.bharatbazaar-demo.example<br/>Request ID format: BBD-DP-YYYY-NNNN<br/>Languages: English, Hindi, Kannada", "TableCell")]],
            colWidths=[2.25 * inch, 2.25 * inch, 2.3 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#444444")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E8E3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]),
        ),
        p("NOTICE OF PROCESSING", "Section"),
        Table(
            [[p("Personal Data", "TableHead"), p("Purpose", "TableHead"), p("Lawful Basis / Retention", "TableHead")],
             [p("Name, mobile number, email, delivery address", "TableCell"), p("Account creation, delivery, customer support, fraud checks", "TableCell"), p("Consent and legitimate uses; account life plus 3 years", "TableCell")],
             [p("Order history, returns, wallet balance, invoices", "TableCell"), p("Fulfil orders, refunds, accounting, tax compliance", "TableCell"), p("Legal compliance and service delivery; up to 8 financial years", "TableCell")],
             [p("Device ID, app logs, approximate location", "TableCell"), p("Security, diagnostics, service personalisation, abuse prevention", "TableCell"), p("Consent where required; generally 24 months", "TableCell")],
             [p("Payment token and UPI reference", "TableCell"), p("Payment completion, refund processing, dispute handling", "TableCell"), p("Processed through payment partners; retained as required by law", "TableCell")]],
            colWidths=[2.05 * inch, 2.35 * inch, 2.4 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#444444")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E8E3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]),
        ),
        p("DATA PRINCIPAL RIGHTS", "Section"),
        ListFlowable([ListItem(p(item, "Body"), leftIndent=12) for item in rights], bulletType="1", start="1", leftIndent=18),
        p("DISCLOSURES", "Section"),
        p("Personal data may be shared with delivery partners, payment aggregators, customer support vendors, cloud hosting providers, analytics processors, auditors, law enforcement authorities, and professional advisers only for stated purposes or legal compliance.", "Body"),
        p("CONSENT CAPTURE", "Section"),
        Table(
            [[checkbox("I consent to processing for account creation, order fulfilment, delivery, support, and fraud prevention.", True)],
             [checkbox("I consent to receiving personalised offers and recommendations by email, SMS, WhatsApp, and app notifications.", False)],
             [checkbox("I consent to use of approximate location for nearby store availability and faster delivery estimates.", True)]],
            colWidths=[6.8 * inch],
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
        ),
        PageBreak(),
        p("DATA PRINCIPAL RIGHTS REQUEST FORM", "DocTitle"),
        p("For access, correction, erasure, withdrawal of consent, grievance, or nomination requests", "DocSubtitle"),
        Spacer(1, 0.08 * inch),
        Table(
            [[p("Request Type", "TableHead"), p("Select", "TableHead"), p("Particulars", "TableHead")],
             [p("Access information", "TableCell"), checkbox("", True), p("Provide summary of personal data, processing purposes, and third-party disclosures.", "TableCell")],
             [p("Correction / update", "TableCell"), checkbox("", False), p("Correct mobile number from 98765 00000 to 98765 11111.", "TableCell")],
             [p("Erasure", "TableCell"), checkbox("", False), p("Delete eligible personal data after closure of active orders and statutory retention checks.", "TableCell")],
             [p("Withdraw consent", "TableCell"), checkbox("", True), p("Withdraw marketing and recommendation consent with immediate prospective effect.", "TableCell")],
             [p("Grievance", "TableCell"), checkbox("", False), p("Escalate delayed response or unresolved request.", "TableCell")]],
            colWidths=[1.55 * inch, 0.75 * inch, 4.5 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#444444")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E8E3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]),
        ),
        Spacer(1, 0.1 * inch),
        Table(
            [[p("Data Principal Name", "TableHead"), p("Ananya Sharma", "TableCell")],
             [p("Registered Mobile", "TableHead"), p("+91 98765 00000", "TableCell")],
             [p("Email", "TableHead"), p("ananya.sharma@example.invalid", "TableCell")],
             [p("Customer ID", "TableHead"), p("BBD-CUST-4482091", "TableCell")],
             [p("State / City", "TableHead"), p("Karnataka / Bengaluru", "TableCell")],
             [p("Preferred Response Mode", "TableHead"), p("Secure app inbox and email notification", "TableCell")]],
            colWidths=[2.0 * inch, 4.8 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#444444")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4F3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]),
        ),
        p("DECLARATION", "Section"),
        p("I confirm that I am the Data Principal identified above or am lawfully authorised to act on their behalf. I understand that Bharat Bazaar Digital may verify my identity before acting on this request.", "Body"),
        Spacer(1, 0.2 * inch),
        Table(
            [[p("Signature: /s/ Ananya Sharma", "Body"), p("Date: 05 July 2026", "Body")],
             [p("Request ID: BBD-DP-2026-0715", "Body"), p("Internal Queue: Privacy Ops > Verification > Fulfilment", "Body")]],
            colWidths=[3.4 * inch, 3.4 * inch],
        ),
    ]
    build_pdf(
        "03_india_dpdp_consumer_privacy_notice_sample.pdf",
        story,
        "LexGuard demo sample | Fictional Indian DPDP notice and rights request | Not legal advice",
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old_pdf in OUT.glob("*.pdf"):
        old_pdf.unlink()

    divorce_document()
    rental_document()
    privacy_document()

    (OUT / "README.txt").write_text(
        "LexGuard demo original samples - India edition\n"
        "Generated fictional PDF documents for demos only.\n\n"
        "Files:\n"
        "- 01_india_mutual_consent_divorce_petition_sample.pdf\n"
        "- 02_india_maharashtra_leave_and_licence_sample.pdf\n"
        "- 03_india_dpdp_consumer_privacy_notice_sample.pdf\n\n"
        "Legal references used for styling/context:\n"
        "- Hindu Marriage Act, 1955, Section 13B, mutual-consent divorce\n"
        "- Maharashtra Rent Control Act, 1999, Section 55, leave-and-licence registration context\n"
        "- Maharashtra Stamp Act, Article 36A, leave-and-licence stamp duty context\n"
        "- Digital Personal Data Protection Act, 2023 and DPDP Rules, 2025\n\n"
        "All names, case numbers, addresses, signatures, companies, and facts are fake.\n",
        encoding="utf-8",
    )
    for pdf in sorted(OUT.glob("*.pdf")):
        print(pdf)


if __name__ == "__main__":
    main()
