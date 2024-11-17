from typing import Dict, Any


def business_profile_parser(
    business_profile: Dict[str, Any], additional_profile: Dict[str, Any]
) -> Dict[str, Any]:
    def get_value(key, default="Unknown"):
        return (
            business_profile.get(key)
            if business_profile.get(key) != "NA"
            else additional_profile.get(key, default)
        )

    def get_nested_value(parent_key, child_key, default="Unknown"):
        parent = business_profile.get(parent_key, {})
        return (
            parent.get(child_key)
            if parent.get(child_key) != "NA"
            else additional_profile.get(f"{parent_key}.{child_key}", default)
        )

    key_people = business_profile.get(
        "key_people", additional_profile.get("key_people", [])
    )
    funding_rounds = get_nested_value("financial_information", "funding_rounds", [])

    # Convert specialties (list of strings) into a list of CompanySpecialties models
    specialties = get_value("specialties", [])
    specialties = [{"fields": [specialty]} for specialty in specialties]

    # Convert about (string) into a list of CompanyAbout models
    about = get_value("about")
    if isinstance(about, str):
        about = [{"description": about}]

    # Convert logo string (URL) into CompanyLogo dictionary
    logo = get_value("company_logo_url")
    if isinstance(logo, str):
        logo = {"url": logo}

    # Ensure culture is provided (required field)
    culture = get_value("company_culture", {}) or {
        "core_values": ["Innovation", "Community", "Support"],
        "employee_benefits": ["Flexible working hours", "Remote work options"],
        "diversity_and_inclusion": "NA",
    }

    # Ensure "website" is properly formatted as a model
    website = get_value("website")
    if isinstance(website, str):
        website = {
            "url": website
        }  # Convert string to dictionary for CompanyWebsite model

    return {
        "request_email": business_profile.get("request_email"),
        "name": get_value("company_name", "Not Available"),
        "type": get_value("company_type"),
        "industry": get_value("industry"),
        "email": get_value("email"),
        "phone": get_value("phone"),
        "headquarter": {
            field: get_nested_value("headquarter", field)
            for field in ["street", "city", "state", "zip_code", "country"]
        },
        "founded": {"year": get_value("founded")},
        "employee_count": {"range": get_value("employee_count")},
        "specialties": specialties,
        "about": about,
        "website": website,
        "social_media_urls": {
            **get_value("social_media_urls", {}),
            **additional_profile.get("social_media_urls", {}),
        },
        "logo": logo,
        "key_people": [
            {
                field: (
                    person.get(field)
                    if person.get(field) != "NA"
                    else get_value(f"person.{field}")
                )
                for field in ["name", "position", "linkedin_profile"]
            }
            for person in key_people
        ],
        "products_and_services": list(get_value("products_and_services", [])),
        "financial_information": {
            "revenue": get_nested_value("financial_information", "revenue"),
            "valuation": get_nested_value("financial_information", "valuation"),
            "funding_rounds": [
                {
                    "round": (
                        funding_round.get("round")
                        if funding_round.get("round") != "NA"
                        else get_value("funding_round.round")
                    ),
                    "amount": (
                        funding_round.get("amount")
                        if funding_round.get("amount") != "NA"
                        else get_value("funding_round.amount")
                    ),
                    "investors": [
                        {"name": investor}
                        for investor in funding_round.get("investors", [])
                        if investor != "NA"
                    ],
                }
                for funding_round in funding_rounds
            ],
        },
        "affiliates": [
            {
                field: (
                    get_value(f"affiliate.{field}")
                    if affiliate.get(field) != "NA"
                    else get_value(f"affiliate.{field}")
                )
                for field in ["partner_name", "description", "url"]
            }
            for affiliate in get_value("affiliates", [])
        ],
        "career_opportunities": [
            {
                field: (
                    get_value(f"career_opportunity.{field}")
                    if opportunity.get(field) != "NA"
                    else get_value(f"career_opportunity.{field}")
                )
                for field in ["position", "location", "job_type", "url"]
            }
            for opportunity in get_value("career_opportunities", [])
        ],
        "culture": {
            **get_value("company_culture", {}),
            **additional_profile.get("company_culture", {}),
        },
        "news_and_updates": list(
            get_value(
                "news_and_updates", **additional_profile.get("news_and_updates", {})
            )
        ),
        "awards": get_value("awards", **additional_profile.get("awards", {})),
        "csr_initiatives": get_value(
            "csr_initiatives", **additional_profile.get("csr_initiatives", {})
        ),
        "sources": get_value("sources", **additional_profile.get("sources", {})),
    }
