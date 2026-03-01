import sys
sys.path.append(".")

from src.indexing import get_qdrant_client, COLLECTION_NAME, index_documents
from qdrant_client.models import Distance, VectorParams

# Hardcoded scheme data from official government sources
SCHEMES = [
    {
        "title": "PM Kisan Samman Nidhi (PM-KISAN)",
        "source": "manual",
        "content": """PM Kisan Samman Nidhi (PM-KISAN) is a Central Sector Scheme launched in 2019.
It provides income support of Rs 6000 per year to all landholding farmer families across the country.
The amount is paid in three equal installments of Rs 2000 every four months directly into farmers bank accounts via Direct Benefit Transfer (DBT).

Eligibility:
- All landholding farmers families with cultivable land are eligible.
- The scheme covers Small and Marginal Farmers as well as large farmers.
- The farmer must be an Indian citizen.
- Farmers with cultivable landholding in their name are eligible.

Who is NOT eligible:
- Institutional landholders.
- Farmer families where one or more members are income tax payers.
- Current or former holders of constitutional posts.
- Current or former Ministers, MPs, MLAs, Mayors.
- Government employees (Central or State) except Multi Tasking Staff, Class IV, Group D employees.
- Professionals like doctors, engineers, lawyers, chartered accountants with professional bodies.
- Retired pensioners with monthly pension above Rs 10,000.

How to Apply:
- Visit the nearest Common Service Centre (CSC) with Aadhaar card and land records.
- Apply online at pmkisan.gov.in
- Contact the local Patwari or Revenue Officer.
- Required documents: Aadhaar card, bank account details, land ownership documents.

Benefits:
- Rs 6000 per year in three installments of Rs 2000 each.
- Money credited directly to bank account.
- No middlemen involved."""
    },
    {
        "title": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
        "source": "manual",
        "content": """Pradhan Mantri Jan Dhan Yojana (PMJDY) is a National Mission for Financial Inclusion launched in 2014.
It ensures access to financial services like banking, savings, credit, insurance, and pension to every household in India.

Key Features:
- Zero balance bank account can be opened at any bank branch or Business Correspondent outlet.
- RuPay Debit Card provided to account holders.
- Accidental insurance cover of Rs 2 lakh.
- Overdraft facility up to Rs 10,000 after 6 months of satisfactory operation.
- Access to Pension and Insurance products.
- Life insurance cover of Rs 30,000 for accounts opened between August 2014 and January 2015.

Eligibility:
- Any Indian citizen above 10 years of age can open an account.
- No minimum balance required.
- Valid for people who do not have a bank account.

How to Apply:
- Visit any bank branch or Business Correspondent outlet.
- Fill the account opening form.
- Required documents: Aadhaar card (preferred), or Voter ID, Driving License, PAN card, NREGA job card.
- Account can be opened with zero balance.

Benefits:
- Free RuPay debit card.
- Accidental insurance of Rs 2 lakh.
- Overdraft up to Rs 10,000.
- Direct benefit transfer of government subsidies."""
    },
    {
        "title": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
        "source": "manual",
        "content": """Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY) is a life insurance scheme launched in 2015.
It offers renewable one year life insurance cover for death due to any reason.

Coverage:
- Life insurance cover of Rs 2 lakh on death due to any cause.
- Coverage period is from June 1 to May 31 every year.

Eligibility:
- Age between 18 to 50 years.
- Must have a savings bank account.
- Must give consent to join and enable auto-debit.

Premium:
- Rs 436 per year (revised from Rs 330).
- Premium is auto-debited from bank account once a year.

How to Apply:
- Visit your bank branch where you have a savings account.
- Fill the enrollment cum auto-debit form.
- Can also enroll through net banking or mobile banking.
- Submit nomination details.

How to Claim:
- Nominee must inform the bank.
- Submit death certificate and claim form.
- Claim settled within 30 days."""
    },
    {
        "title": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "source": "manual",
        "content": """Pradhan Mantri Suraksha Bima Yojana (PMSBY) is an accidental insurance scheme launched in 2015.
It provides accidental death and disability cover.

Coverage:
- Rs 2 lakh for accidental death or permanent total disability.
- Rs 1 lakh for permanent partial disability.

Eligibility:
- Age between 18 to 70 years.
- Must have a savings bank account.
- Must give auto-debit consent.

Premium:
- Only Rs 20 per year (very affordable).
- Auto-debited from bank account annually.

How to Apply:
- Visit your bank branch.
- Fill the enrollment form.
- Available through net banking and mobile banking apps.

How to Claim:
- Inform bank within 30 days of accident.
- Submit FIR copy, disability certificate, discharge summary from hospital.
- Claim form signed by bank account holder or nominee."""
    },
    {
        "title": "Atal Pension Yojana (APY)",
        "source": "manual",
        "content": """Atal Pension Yojana (APY) is a pension scheme launched in 2015 focused on unorganized sector workers.
It provides a guaranteed minimum monthly pension after retirement.

Pension Benefits:
- Guaranteed monthly pension of Rs 1000, Rs 2000, Rs 3000, Rs 4000 or Rs 5000 after age 60.
- Pension amount depends on contribution amount and age at joining.
- After subscriber death, spouse receives same pension.
- After both die, accumulated corpus returned to nominee.

Eligibility:
- Indian citizen between 18 to 40 years of age.
- Must have a savings bank account or post office savings account.
- Must have a mobile number linked to bank account.
- Cannot be an income tax payer (rule added in 2022).

Contribution:
- Monthly contribution varies based on age and chosen pension amount.
- Example: For Rs 5000 pension, if joining at age 18, monthly contribution is Rs 210.
- If joining at age 30, monthly contribution for Rs 5000 pension is Rs 577.

How to Apply:
- Visit your bank branch or post office.
- Fill APY registration form.
- Provide Aadhaar and mobile number.
- Choose pension amount between Rs 1000 to Rs 5000.
- Set up auto-debit from savings account."""
    },
    {
        "title": "Pradhan Mantri Awas Yojana Gramin (PMAY-G)",
        "source": "manual",
        "content": """Pradhan Mantri Awas Yojana Gramin (PMAY-G) provides housing assistance to rural poor for construction of pucca houses.

Benefits:
- Financial assistance of Rs 1.20 lakh in plain areas.
- Rs 1.30 lakh in hilly states, difficult areas, and Integrated Action Plan districts.
- Includes toilet construction under Swachh Bharat Mission (Rs 12,000 additional).
- MGNREGA support for unskilled labour (90 days in plain areas, 95 days in hilly areas).

Eligibility (based on SECC 2011 data):
- Houseless households.
- Households with 0, 1 or 2 room kutcha house with kutcha wall and roof.
- Priority to SC/ST, freed bonded labourers, minorities, widows, ex-servicemen, disabled persons.
- Must not own a pucca house anywhere in India.

How to Apply:
- Beneficiaries are selected from SECC 2011 data by Gram Panchayat.
- Gram Sabha approves the final list.
- You cannot apply directly - selection is automatic based on government data.
- Contact your Gram Panchayat or Block Development Officer to check eligibility.

Payment:
- Money released in installments directly to bank account.
- Linked to construction progress verified by geo-tagged photographs."""
    },
    {
        "title": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "source": "manual",
        "content": """Pradhan Mantri Matru Vandana Yojana (PMMVY) is a maternity benefit programme providing cash incentives to pregnant and lactating mothers.

Benefits:
- Rs 5000 in three installments for first living child.
- First installment Rs 1000 on early registration of pregnancy.
- Second installment Rs 2000 after 6 months of pregnancy and attending one antenatal check-up.
- Third installment Rs 2000 after child birth registration and first cycle of vaccination.
- Additional Rs 6000 for institutional delivery under Janani Suraksha Yojana.

Eligibility:
- All pregnant women and lactating mothers for first living child.
- Age 19 years and above.
- Government employees not eligible (they have paid maternity leave).

How to Apply:
- Register at the nearest Anganwadi Centre (AWC) or approved health facility.
- Fill the application form (Form 1-A for first installment).
- Required documents: MCP card, identity proof (Aadhaar), bank account details, husband Aadhaar.
- Submit forms for subsequent installments as conditions are met.

Purpose:
- Compensate wage loss during pregnancy and lactation.
- Encourage proper nutrition and health practices."""
    },
    {
        "title": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "source": "manual",
        "content": """Indira Gandhi National Old Age Pension Scheme (IGNOAPS) provides monthly pension to senior citizens living below the poverty line.

Benefits:
- Rs 200 per month for beneficiaries aged 60 to 79 years.
- Rs 500 per month for beneficiaries aged 80 years and above.
- State governments add their own contribution, so actual amount varies by state.

Eligibility:
- Age 60 years and above.
- Must belong to a household Below Poverty Line (BPL) as per state government criteria.
- Indian citizen.

How to Apply:
- Visit your local Gram Panchayat office (rural areas) or Municipal office (urban areas).
- Fill the application form with:
  - Age proof (birth certificate, Aadhaar, school certificate)
  - BPL certificate or ration card
  - Bank account details or post office account
  - Passport size photograph
  - Residence proof
- Applications verified by Block Development Officer or equivalent.
- Approved beneficiaries added to pension list.

Payment:
- Pension credited to bank account monthly or quarterly depending on state.
- Can also be collected from post office in some states."""
    },
    {
        "title": "Beti Bachao Beti Padhao (BBBP)",
        "source": "manual",
        "content": """Beti Bachao Beti Padhao (BBBP) is a scheme launched in 2015 to address declining Child Sex Ratio and promote the welfare of girl child.

Objectives:
- Prevent gender biased sex selective elimination.
- Ensure survival and protection of the girl child.
- Ensure education and participation of the girl child.

Key Components:
- Sukanya Samriddhi Yojana: Special savings scheme for girl child.
  * Account can be opened for girl child below 10 years.
  * Current interest rate around 8% per annum.
  * Tax benefits under Section 80C.
  * Minimum deposit Rs 250 per year, maximum Rs 1.5 lakh per year.
  * Maturity after 21 years from opening or when girl turns 18 for marriage.
  * Partial withdrawal of 50% allowed after girl turns 18 for education.

- Awareness campaigns against female foeticide and child marriage.
- Scholarships and incentives for girl child education.

How to Open Sukanya Samriddhi Account:
- Visit any post office or authorized bank branch.
- Girl child must be below 10 years of age.
- Documents: Birth certificate of girl child, Aadhaar of parents and girl, address proof.
- Minimum Rs 250 to open account."""
    },
    {
        "title": "National Family Benefit Scheme (NFBS)",
        "source": "manual",
        "content": """National Family Benefit Scheme (NFBS) provides lump sum family benefit to bereaved households below poverty line on death of primary breadwinner.

Benefit:
- One time payment of Rs 20,000 to the bereaved family.
- Payment made within 45 days of application approval.

Eligibility:
- Family must be Below Poverty Line (BPL).
- Deceased must be the primary breadwinner of the family.
- Age of deceased must be between 18 to 64 years.
- Death can be due to any cause (natural or accidental).

How to Apply:
- Apply within 90 days of death of breadwinner.
- Visit the District Social Welfare Office.
- Required documents:
  * Death certificate of deceased
  * Age proof of deceased
  * BPL ration card or BPL certificate
  * Proof that deceased was primary breadwinner
  * Bank account details of applicant
  * Relationship proof with deceased
  * Residence proof
- Application verified by District Collector or designated authority.

Payment:
- Amount credited directly to bank account of next of kin."""
    }
]

if __name__ == "__main__":
    print("Step 1: Deleting old collection...")
    client = get_qdrant_client()
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Old collection deleted.")
    except:
        print("No existing collection to delete.")

    print("\nStep 2: Indexing fresh scheme data...")
    index_documents(SCHEMES)
    print("\nDone! Re-run test_rag.py to verify.")  