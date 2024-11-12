import json
import logging
from pydantic import BaseModel, ValidationError
from sqlalchemy import JSON, Column, Integer, String, Text, DateTime, func
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, List, Optional, Type

from src.models.business_profile import BusinessProfile
from src.config.constants import DATABASE_URL
from src.models.lead import Lead

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def pydantic_to_sqlalchemy(
    pydantic_model: Type[BaseModel], table_name: str, add_profile_data: bool = False
) -> Type[Base]:  # type: ignore
    fields = {
        "__tablename__": table_name,
        "id": Column(Integer, primary_key=True),
        "created_at": Column(DateTime(timezone=True), server_default=func.now()),
    }

    if add_profile_data:
        fields["profile_data"] = Column(Text, nullable=False)

    for field_name, field_type in pydantic_model.__annotations__.items():
        if field_name == "id":
            continue  # Skip if 'id' is already defined

        if hasattr(field_type, "__origin__") and field_type.__origin__ is Optional:
            field_type = field_type.__args__[0]

        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            fields[field_name] = Column(JSON, nullable=True)
        elif field_type == str:
            fields[field_name] = Column(String, nullable=True)
        elif field_type == int:
            fields[field_name] = Column(Integer, nullable=True)
        elif field_type == dict:
            fields[field_name] = Column(JSON, nullable=True)
        else:
            fields[field_name] = Column(Text, nullable=True)

    return type(f"{pydantic_model.__name__}SQL", (Base,), fields)


BusinessProfileSQL = pydantic_to_sqlalchemy(
    BusinessProfile, "business_profiles", add_profile_data=True
)

LeadSQL = pydantic_to_sqlalchemy(Lead, "leads", add_profile_data=False)

Base.metadata.drop_all(bind=engine, tables=[BusinessProfileSQL.__table__])
Base.metadata.drop_all(bind=engine, tables=[LeadSQL.__table__])
Base.metadata.create_all(bind=engine)


def store_business_profile(raw_data: Dict[str, Any]):
    """
    Validate and store a business profile in the database.
    """

    logger.info("Raw Data: %s", json.dumps(raw_data, indent=4))

    def to_json(field):
        return json.dumps(field.dict()) if field else None

    def to_json_list(field_list):
        return json.dumps([item.dict() for item in field_list]) if field_list else None

    try:
        business_profile = BusinessProfile(**raw_data)
        business_profile_dict = business_profile.model_dump()

        profile_data_json = json.dumps(business_profile_dict)
        logger.info("Validated Business Profile: %s", profile_data_json)

        with SessionLocal() as db:
            db_profile = BusinessProfileSQL(
                profile_data=profile_data_json,
                request_email=getattr(business_profile, "request_email", None),
                name=getattr(business_profile, "name", None),
                type=getattr(business_profile, "type", None),
                industry=getattr(business_profile, "industry", None),
                email=getattr(business_profile, "email", None),
                phone=getattr(business_profile, "phone", None),
                headquarter=to_json(getattr(business_profile, "headquarter", None)),
                founded=to_json(getattr(business_profile, "founded", None)),
                employee_count=to_json(
                    getattr(business_profile, "employee_count", None)
                ),
                specialties=to_json_list(getattr(business_profile, "specialties", [])),
                about=to_json_list(getattr(business_profile, "about", [])),
                website=to_json(getattr(business_profile, "website", None)),
                social_media_urls=to_json(
                    getattr(business_profile, "social_media_urls", None)
                ),
                logo=to_json(getattr(business_profile, "logo", None)),
                key_people=to_json_list(getattr(business_profile, "key_people", [])),
                products_and_services=to_json_list(
                    getattr(business_profile, "products_and_services", [])
                ),
                culture=to_json(getattr(business_profile, "culture", None)),
                news_and_updates=to_json_list(
                    getattr(business_profile, "news_and_updates", [])
                ),
                financial_information=to_json(
                    getattr(business_profile, "financial_information", None)
                ),
                affiliates=to_json_list(getattr(business_profile, "affiliates", [])),
                awards=to_json_list(getattr(business_profile, "awards", [])),
                csr_initiatives=to_json_list(
                    getattr(business_profile, "csr_initiatives", [])
                ),
                career_opportunities=to_json_list(
                    getattr(business_profile, "career_opportunities", [])
                ),
                marketing_goals=to_json_list(
                    getattr(business_profile, "marketing_goals", [])
                ),
                sources=json.dumps(getattr(business_profile, "sources", [])),
            )

            db.add(db_profile)
            db.commit()
            db.refresh(db_profile)

            print(f"Stored Business Profile with ID: {db_profile.id}")

    except ValidationError as e:
        logger.error("Validation Error: %s", e.json())


def store_leads(
    query: str,
    keyword: str,
    intent: str,
    score: float,
    scraper_name: str,
    filename: Optional[str],
    lead_data_list: List[Any],  # TODO: Accept any type for now to validate later
) -> None:
    with SessionLocal() as db:
        lead = [
            LeadSQL(
                query=query,
                keyword=keyword,
                intent=intent,
                score=score,
                scraper_name=scraper_name,
                filename=filename,
                results=json.dumps(lead_data_list),
            )
        ]

        db.bulk_save_objects(lead)
        db.commit()
        logger.info(f"Successfully stored {len(lead)} leads.")
