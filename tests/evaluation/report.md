# Evaluation report

2026-10-14 | assistant `gpt-5.6-luna` | judge `gpt-6-luna` | 24 questions

## Summary

| Metric | Result |
|---|---|
| **Accuracy** (every check passes) | **24 / 24 (100%)** |
| Route correct | 22 / 22 (100%) |
| Required facts present | 32 / 32 (100%) |
| Forbidden content absent | 8 / 8 (100%) |
| Correct sources cited | 13 / 13 (100%) |
| Retrieval hit rate | 11 / 11 (100%) |
| Retrieval MRR | 0.91 |
| Faithfulness (LLM judge) | 21 / 22 (95%) |
| Answer time (avg / median / max) | 4.5s / 4.6s / 7.1s |
| Tokens (in / out) | 66,880 / 2,440 |
| Cost (assistant + judge) | $0.0163 + $0.0030 |

## By question type

| Type | Passed |
|---|---|
| documents | 11 / 11 (100%) |
| data | 7 / 7 (100%) |
| access | 3 / 3 (100%) |
| not_available | 3 / 3 (100%) |

## What the metrics mean

- **Accuracy**: a question passes only if all its checks pass.
- **Route correct**: the assistant used documents, data or refused, as expected.
- **Required facts present**: the exact figures and key facts are in the answer (e.g. `33,34,200`).
- **Forbidden content absent**: no old limits, other companies' figures or leaked numbers.
- **Correct sources cited**: the answer names the right document, and cites nothing when it has no answer.
- **Retrieval hit rate**: for questions that expect a document, it was among the retrieved chunks (top 4 per search).
- **Retrieval MRR**: mean of 1 / position of the first expected document in the retrieved list (1.0 = always first).
- **Faithfulness**: a second model checks that every fact in the answer is backed by what the tools returned. Questions refused before the LLM are not judged.

## Questions

| # | User | Type | Question | Expected | Answer | Route | Sources | Retrieval | Faithful | Time | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | U01 | documents | How do I create a purchase order against a project WBS? | Steps from the Project PO against WBS guide: project must be In process, note the WBS activity number, create PO, select Project ID in header, enter activity number and project category on each line, submit (budget check). | 1. Go to **Project management and accounting > Projects > All projects**, open the project, and confirm its stage is **In process**. POs cannot be created for projects in **Created** or **Finished** stage.<br>2. Open **Plan > Work breakdown structure** and note the activity number for the required WBS task.<br>3. Go to **Procurement and sourcing > Purchase orders > All purchase orders > New**.<br>4. In the header, select the **Project ID**.<br>5. On every PO line, enter the WBS **activity number** and select the appropriate **project category**.<br>6. Save and submit the PO for approval. The system will check the remaining budget for that activity.<br><br>If the budget check fails, do not create the PO without a project ID. Ask the project controller to revise the budget first.<br><br>(Source: Project PO against WBS - user guide v1.2.pdf) | documents | Project PO against WBS - user guide v1.2.pdf | rank 1 | yes | 7.1s | PASS |
| 2 | U01 | data | What is the total value of open POs for Project Riverside? | INR 33,34,200 (6 open lines on Riverside Towers, RIL-PRJ-0007, without GST). | The total value of open POs for Project Riverside is **INR 33,34,200.00** (without GST), across **6 purchase orders**. | data | SQL Server: arete_group.dbo.purchase_order_lines | - | yes | 4.8s | PASS |
| 3 | U01 | documents | What is the PO approval limit for a plant head? | Up to INR 5,00,000 as per Riverside PO Approval Matrix v2.0 (not the old v1.0 limit of 3,00,000, not Greenleaf's 10,00,000). | The PO approval limit for a Plant Head is **up to INR 5,00,000**, including taxes. (Source: Riverside - PO Approval Matrix v2.0.docx) | documents | Riverside - PO Approval Matrix v2.0.docx | rank 1 | yes | 5.6s | PASS |
| 4 | U02 | documents | What is the PO approval limit for a plant head? | Up to INR 10,00,000 as per Greenleaf Purchase Policy 2026 (Coastal Retail has no PO approval limit for a plant head). | - **C02 Greenleaf Pharma Ltd:** Plant Head can approve POs up to **INR 10,00,000**, including taxes. (Source: Greenleaf Purchase Policy 2026.pdf)<br>- **C03 Coastal Retail Ltd:** The available document does not specify a Plant Head approval limit. | documents | Greenleaf Purchase Policy 2026.pdf | rank 1 | yes | 5.6s | PASS |
| 5 | U02 | access | Show open POs for Project Riverside. | Polite refusal: U02 does not have access to C01 Riverside Infra. | Sorry, you do not have access to C01 Riverside Infra Ltd, so I cannot share its documents or data. You have access to: C02 Greenleaf Pharma Ltd, C03 Coastal Retail Ltd. | refused |  | - | - | 0.0s | PASS |
| 6 | U03 | data | Which vendor has the highest PO value across all companies? | Gujarat Steel Rolling (V-00145) with INR 42,34,000 (canceled lines excluded; vendor spelled 3 ways, grouped by vendor account). | Gujarat Steel Rolling (V-00145) has the highest PO value: **INR 42,34,000.00**. | data | SQL Server: arete_group.dbo.purchase_order_lines | - | yes | 4.2s | PASS |
| 7 | U03 | not_available | What is our travel reimbursement policy? | Not available in the documents. | This information is not available in the documents or data you have access to. | documents |  | - | yes | 5.3s | PASS |
| 8 | U01 | documents | I get the error 'Batch number is mandatory' when posting a GRN. What should I do? | Item is batch tracked: open Registration on the line, enter the batch number, then post. | 1. The item is batch-tracked. Open **Registration** on the GRN line and enter the batch number.<br>2. Enter the batch number before posting the GRN.<br><br>(Source: GRN errors and solutions.txt) | documents | GRN errors and solutions.txt | rank 1 | yes | 5.2s | PASS |
| 9 | U02 | documents | Which documents does a new vendor need to submit for onboarding? | PAN card copy, GST registration certificate (if registered), cancelled cheque or bank letter, MSME/Udyam certificate (if applicable). | A new vendor must submit:<br><br>1. PAN card copy  <br>2. GST registration certificate, if registered under GST  <br>3. Cancelled cheque or bank letter on the vendor’s letterhead  <br>4. MSME/Udyam certificate, if applicable  <br><br>(Source: Vendor Onboarding SOP.docx) | documents | Vendor Onboarding SOP.docx | rank 2 | **no** (The SOP says “bank letter on letterhead,” but does not specify that it must be on the vendor’s letterhead.) | 5.3s | PASS |
| 10 | U03 | documents | When does reverse charge (RCM) apply on our purchases? | Legal services from an advocate/law firm, Goods Transport Agency services (if GTA has not opted for forward charge), security services from a non-corporate supplier. | RCM applies when the buyer pays GST to the government instead of the vendor. Common cases across all group companies are:<br><br>- Legal services from an advocate or law firm.<br>- Goods Transport Agency (GTA) services where the GTA has not opted for forward charge.<br>- Security services from a non-corporate supplier—an individual or partnership firm—to a registered company.<br><br>For these purchases, select the **“RCM” item sales tax group** on the PO line or invoice; do not use the normal GST group. If unsure, contact the tax team before posting the invoice.<br><br>(Source: FW RCM applicability on purchases.txt) | documents | FW RCM applicability on purchases.txt | rank 1 | yes | 6.3s | PASS |
| 11 | U02 | data | How many open PO lines does Coastal Retail have and what is their total value? | 4 open lines, INR 3,93,900. | Coastal Retail Ltd has **4 open PO lines** with a total value of **INR 3,93,900.00** (without GST). | data | SQL Server: arete_group.dbo.purchase_order_lines | - | yes | 3.5s | PASS |
| 12 | U02 | data | What is the total PO value with PackWell Industries? | INR 9,16,500 (6 lines across C02 and C03, canceled line excluded; 'PackWell' and 'Packwell' are the same vendor V-00322). | Total PO value with PackWell Industries: **INR 9,16,500.00** (without GST). | data | SQL Server: arete_group.dbo.purchase_order_lines | - | yes | 4.3s | PASS |
| 13 | U03 | data | Give me the total PO value for each company. | C01 INR 61,18,270; C02 INR 24,85,660; C03 INR 19,65,600 (canceled excluded). | 1. C01 Riverside Infra Ltd: **INR 61,18,270.00** — 14 lines  <br>2. C02 Greenleaf Pharma Ltd: **INR 24,85,660.00** — 12 lines  <br>3. C03 Coastal Retail Ltd: **INR 19,65,600.00** — 11 lines  <br><br>Amounts exclude GST and canceled PO lines. | data | SQL Server: arete_group.dbo.purchase_order_lines | - | yes | 4.1s | PASS |
| 14 | U01 | access | What is the total value of open POs for the Plant 2 Upgrade project? | Refusal: Plant 2 Upgrade belongs to a company U01 cannot see (C02). The question does not name the company, so the data tool must catch it. | You do not have access to that company’s data. | data | SQL Server: arete_group.dbo.purchase_order_lines | - | yes | 4.3s | PASS |
| 15 | U03 | documents | Up to what amount can a site engineer at Riverside make an emergency purchase? | Up to INR 25,000, with approval to be taken within 3 working days (Riverside PO Approval Matrix v2.0). | A site engineer at **Riverside Infra Ltd** can make an emergency purchase up to **INR 25,000**. Approval must be obtained within **3 working days**. (Source: Riverside - PO Approval Matrix v2.0.docx) | documents | Riverside - PO Approval Matrix v2.0.docx | rank 1 | yes | 5.5s | PASS |
| 16 | U02 | documents | Up to what amount can a store manager approve purchase requisitions? | Up to INR 30,000; above that the Area Manager approves (Coastal Retail store guidelines). | 1. **C03 Coastal Retail Ltd:** Store managers can approve purchase requisitions up to **INR 30,000**. Above INR 30,000, the Area Manager approves. *(Source: Store stock & reorder guidelines.docx)*<br><br>2. **C02 Greenleaf Pharma Ltd:** The policy does not specify a store manager approval limit. *(Source: Greenleaf Purchase Policy 2026.pdf)* | documents | Greenleaf Purchase Policy 2026.pdf, Store stock & reorder guidelines.docx | rank 2 | yes | 6.4s | PASS |
| 17 | U01 | access | What are the payment terms for MSME vendors at Greenleaf? | Polite refusal: U01 does not have access to C02 Greenleaf Pharma. | Sorry, you do not have access to C02 Greenleaf Pharma Ltd, so I cannot share its documents or data. You have access to: C01 Riverside Infra Ltd. | refused |  | - | - | 0.0s | PASS |
| 18 | U03 | data | How many PO lines were cancelled and what was their total value? | 3 canceled lines, INR 5,26,800. | 3 PO lines were cancelled, with a total value of **INR 5,26,800.00** (without GST). | data | SQL Server: arete_group.dbo.purchase_order_lines | - | yes | 3.7s | PASS |
| 19 | U01 | documents | What is the over-delivery tolerance when receiving material against a PO? | Normally 5%; receive only the PO quantity and send back the extra or ask the buyer to amend the PO. | The over-delivery tolerance is normally **5%** above the PO quantity. (Source: GRN errors and solutions.txt) | documents | GRN errors and solutions.txt | rank 1 | yes | 4.9s | PASS |
| 20 | U03 | not_available | Who is the CEO of Riverside Infra Ltd? | Not available in the documents or data. | This information is not available in the documents or data you have access to. | documents |  | - | yes | 4.2s | PASS |
| 21 | U01 | not_available | What is the approved budget for Project Riverside? | Not available: the PO register has PO values, not project budgets. | This information is not available in the documents or data you have access to. | documents |  | - | yes | 4.3s | PASS |
| 22 | U03 | data | What was the total PO value in August 2026? | INR 28,80,160 (8 lines dated 1-31 Aug 2026, canceled excluded). | The total PO value in August 2026 was **INR 28,80,160.00**, excluding GST, across **8 purchase orders**. | data | SQL Server: arete_group.dbo.purchase_order_lines | - | yes | 3.8s | PASS |
| 23 | U01 | documents | Can I edit a purchase order after it has been confirmed? | Not directly; use Request change from the action pane (D365 PO creation steps). | After confirmation, a purchase order cannot be edited directly. Use **Request change** from the action pane. (Source: D365 PO creation steps.docx) | documents | D365 PO creation steps.docx | rank 1 | yes | 4.4s | PASS |
| 24 | U03 | documents | What is the PO approval limit for a plant head? | Different per company: Riverside up to INR 5,00,000; Greenleaf up to INR 10,00,000. Coastal has no such limit in the documents. | - **C01 Riverside Infra Ltd:** Plant Head / Project Manager — up to **INR 5,00,000**. (Source: Riverside - PO Approval Matrix v2.0.docx)<br>- **C02 Greenleaf Pharma Ltd:** Plant Head — up to **INR 10,00,000**. (Source: Greenleaf Purchase Policy 2026.pdf)<br>- **C03 Coastal Retail Ltd:** This information is not available in the documents or data you have access to. | documents | Riverside - PO Approval Matrix v2.0.docx, Greenleaf Purchase Policy 2026.pdf | rank 1 | yes | 5.3s | PASS |
