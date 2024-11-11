DEFAULT_SCRAPING_PROMPT = """Extract comprehensive business profile information from the following source data using the provided schema structure. For each field, return the corresponding data key, with the same name as the schema without descriptions. If the information is not available, return "NA" for that field. Include all relevant details even if they are partially available.

{
  "company_name": "Company Name",
  "industry": "Industry of the Company",
  "company_type": "Type of Company (Public/Private, etc.)",
  "email": "Email Address",
  "phone": "Contact Phone Number (Return 'NA' if unavailable)",
  "headquarter": {
    "street": "Street Address",
    "city": "City",
    "state": "State",
    "zip_code": "ZIP Code",
    "country": "Country"
  },
  "location": {
    "street": "Street Address",
    "city": "City",
    "state": "State",
    "zip_code": "ZIP Code",
    "country": "Country"
  },
  "founded": "Year Founded",
  "employee_count": "Employee Range (e.g. 51-200)",
  "specialties": [
    "Specialty 1",
    "Specialty 2",
    "Specialty 3"
  ],
  "about": "Detailed description of the company",
  "website": "Company Website URL",
  "social_media_urls": {
      "linkedin": "LinkedIn Profile URL",
      "facebook": "Facebook Profile URL",
      "instagram": "Instagram Profile URL",
      "twitter": "Twitter Profile URL",
      "youtube": "YouTube Profile URL",
  }
  "company_logo_url": "Company Logo URL",
  "key_people": [
    {
      "name": "Person Name",
      "position": "Job Title",
      "linkedin_profile": "LinkedIn Profile URL"
    }
  ],
  "products_and_services": [
    {
      "name": "Product/Service Name",
      "description": "Brief description of the product or service",
      "url": "URL to product/service page"
    }
  ],
  "company_culture": {
    "core_values": [
      "Description of the core values",
      "Core Value 1",
      "Core Value 2"
    ],
    "employee_benefits": [
      "Description of the employee benefits",
       "Benefit 1",
       "Benefit 2"
    ],
    "diversity_and_inclusion": "Description of the diversity and inclusion statement"
  },
  "news_and_updates": [
    {
      "title": "News Title",
      "description": "Brief description of the news",
      "date": "News Date",
      "url": "News Link"
    }
  ],
  "financial_information": {
    "revenue": "Annual Revenue (Return 'NA' if not disclosed)",
    "valuation":  "Company Valuation (Return 'NA' if not disclosed)",
    "funding_rounds": [
      {
        "round": "Funding Round",
        "amount": "Amount Raised",
        "investors": [
          "Investor 1",
          "Investor 2"
        ]
      }
    ]
  },
  "affiliates": [
    {
      "partner_name": "Partner Company",
      "description": "Description of the partnership",
      "url": "Partnership URL"
    }
  ],
  "awards": [
    {
      "title": "Award Title",
      "description": "Brief description of the award",
      "date": "Award Date",
      "url": "Award Link"
    }
  ],
  "csr_initiatives": [
    {
      "initiative_name": "CSR Initiative",
      "description": "Brief description of the initiative",
      "url": "Initiative URL"
    }
  ],
  "career_opportunities": [
    {
      "position": "Job Title",
      "location": "Job Location",
      "job_type": "Job Type (e.g. Full-time, Remote)",
      "url": "Job Posting URL"
    }
  ]
}"""
