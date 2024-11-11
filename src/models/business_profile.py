from pydantic import BaseModel
from typing import Any, Dict, Optional, List

from src.models.affiliate import Affiliates
from src.models.award import Awards
from src.models.careers import CareerOpportunities
from src.models.csr_initiative import CSRInitiatives
from src.models.culture import CompanyCulture
from src.models.email_workflow import EmailWorkflow
from src.models.financial_info import FinancialInformation
from src.models.headquarter import CompanyHeadquarter
from src.models.key_people import KeyPeople
from src.models.lead import Lead
from src.models.marketing_goal import MarketingGoal
from src.models.news_and_update import NewsAndUpdates
from src.models.product_service import ProductsAndServices
from src.models.social_media_link import CompanySocialMediaLinks


class CompanyFounded(BaseModel):
    year: Optional[
        str
    ]  # Correct to Optional[str], since "year" can be a string or None


class CompanyEmployeeCount(BaseModel):
    range: Optional[str]  # String to represent ranges like "11-50" or "50-100"


class CompanySpecialties(BaseModel):
    fields: List[str]  # Assuming specialties are a list of strings


class CompanyWebsite(BaseModel):
    url: Optional[str]  # URL for the company website


class CompanyLogo(BaseModel):
    url: Optional[str]  # URL for the company logo


class CompanyAbout(BaseModel):
    description: Optional[str]  # Description of the company


class BusinessProfile(BaseModel):
    request_email: Optional[str]  # The email of the requester
    company_name: str  # Company name, mandatory field
    type: Optional[str]  # Company type (e.g., Private, Public)
    industry: Optional[str]  # Industry type
    email: Optional[str]  # Company email
    phone: Optional[str]  # Phone number
    headquarter: Optional[CompanyHeadquarter]  # Company headquarter details
    founded: Optional[CompanyFounded]  # Year the company was founded
    employee_count: Optional[CompanyEmployeeCount]  # Employee count range
    specialties: List[CompanySpecialties] = []  # List of specialties
    about: List[CompanyAbout] = []  # List of company descriptions
    website: Optional[CompanyWebsite]  # Website information
    social_media_urls: Optional[CompanySocialMediaLinks]  # Social media URLs
    logo: Optional[CompanyLogo]  # Logo URL
    key_people: List[KeyPeople] = []  # List of key people (executives, founders)
    products_and_services: List[ProductsAndServices] = (
        []
    )  # List of products and services
    financial_information: Optional[
        FinancialInformation
    ]  # Financial information (e.g., revenue)
    affiliates: List[Affiliates] = []  # List of affiliate companies or partners
    career_opportunities: List[CareerOpportunities] = (
        []
    )  # Career opportunities available
    culture: Optional[CompanyCulture]  # Company culture (values, employee benefits)
    news_and_updates: List[NewsAndUpdates] = []  # Latest news and updates
    awards: List[Awards] = []  # List of awards received
    csr_initiatives: List[CSRInitiatives] = (
        []
    )  # Corporate social responsibility initiatives
    marketing_goals: List[MarketingGoal] = []  # Generated marketing goals
    email_workflows: List[EmailWorkflow] = []  # List of email marketing workflows
    b2b_leads: List[Lead] = []  # B2B leads generated from Google Maps or other sources
    sources: Optional[List[str]] = []  # List of sources used for scraping or profiling
    rank_analysis: Optional[Dict[str, Any]] = None  # Rank analysis results
    generated_keywords: Optional[List[str]] = None  # Generated SEO keywords

    class Config:
        from_attributes = True  # Enable ORM mode if needed for database operations
