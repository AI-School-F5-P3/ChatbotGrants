import json
from aws_connect import *
from sqlalchemy import create_engine, Column, String, Float, Text, or_
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import List, Dict, Any
from dotenv import load_dotenv
import os



# Create base class for declarative models
Base = declarative_base()

# Mapping between Comunidades Autónomas and their database scope values
REGION_TO_SCOPE = {
    "Andalucía": "Andalucía",
    "Aragón": "Aragón",
    "Asturias": "Principado de Asturias",
    "Baleares": "Illes Balears",
    "Canarias": "Canarias",
    "Cantabria": "Cantabria",
    "Castilla-La Mancha": "Castilla - La Mancha",
    "Castilla y León": "Castilla y León",
    "Cataluña": "Cataluña",
    "Ceuta": "Ceuta",
    "Comunidad Valenciana": "Comunitat Valenciana",
    "Extremadura": "Extremadura",
    "Galicia": "Galicia",
    "La Rioja": "La Rioja",
    "Madrid": "Comunidad de Madrid",
    "Melilla": "Melilla",
    "Murcia": "Región de Murcia",
    "Navarra": "Comunidad Foral de Navarra",
    "País Vasco": "País Vasco"
}

class Grant(Base):
    __tablename__ = 'grants'
    
    # Primary key - using slug as it appears to unique
    slug = Column(String(255), primary_key=True)
    
    # Basic information
    formatted_title = Column(String(255))
    status_text = Column(String(255))
    entity = Column(String(100))
    total_amount = Column(Float)
    request_amount = Column(Float)
    
    # Text fields for longer content
    goal_extra = Column(Text)
    scope = Column(String(50))
    publisher = Column(String(255))
    applicants = Column(Text)
    term = Column(Text)
    help_type = Column(Text)
    expenses = Column(Text)
    fund_execution_period = Column(Text)
    line = Column(Text)
    extra_limit = Column(Text)
    info_extra = Column(Text)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Grant object to dictionary for JSON serialization"""
        return {
            "slug": self.slug,
            "title": self.formatted_title,
            "status": self.status_text,
            "entity": self.entity,
            "total_amount": self.total_amount,
            "request_amount": self.request_amount,
            "scope": self.scope,
            "publisher": self.publisher,
            "applicants": self.applicants,
            "term": self.term,
            "help_type": self.help_type,
            "expenses": self.expenses,
            "execution_period": self.fund_execution_period,
            "line": self.line,
            "extra_limit": self.extra_limit,
            "info_extra": self.info_extra
        }

class GrantQueries:
    def __init__(self):
        """
        Initialize connection to the existing database
    
        """
        # Database connection configuration
        self.DB_USER = "admin"
        self.DB_HOST = "bbddgrantsbot.cluster-cb88242ceu61.eu-south-2.rds.amazonaws.com"
        self.DB_NAME = "grants_db"
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")

        # Create the connection URL
        self.db_url = f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"

        self.engine = create_engine(self.db_url)
        # Create the engine

        self.Session = sessionmaker(bind=self.engine)
     
    
    def find_adequate_grants(self, min_amount: float, region: str) -> List[Grant]:
        """
        Find all grants with a request_amount greater than or equal to the specified amount
        AND with a scope that matches either 'Estatal' or the provided region's scope
        
        Parameters:
        min_amount (float): Minimum request amount to search for
        region (str): Region (Comunidad Autónoma) to search for (will also include 'Estatal')
        
        Returns:
        List[Grant]: List of Grant objects matching the criteria
        """
        session = self.Session()
        try:
            # Convert region to scope format
            scope = REGION_TO_SCOPE.get(region)
            if not scope:
                print(f"Warning: Unknown region '{region}'. Only searching for 'Estatal' grants.")
                scope = "UNKNOWN"  # This ensures we'll still get Estatal grants
            
            grants = session.query(Grant)\
                          .filter(Grant.request_amount >= min_amount)\
                          .filter(or_(Grant.scope == 'Estatal', Grant.scope == scope))\
                          .order_by(Grant.request_amount.desc())\
                          .all()
            return grants
        finally:
            session.close()


    def find_unique_grant(self, partial_slug: str) -> Grant:
        """
        Find grants by partial slug match
        
        Parameters:
        partial_slug (str): A substring of the grant slug to search for
        
        Returns:
        Grant: Grant object if found, None if not found
        """
        session = self.Session()
        try:
            # Using LIKE with wildcards for partial matching
            # The % characters mean "match any characters before/after"
            grant = session.query(Grant).filter(Grant.slug.like(f'%{partial_slug}%')).first()
            return grant
        finally:
            session.close()




def find_optimal_grants(user_info: dict) -> dict:
    """
    Find optimal grants by combining SQL filtering with LLM-based analysis of user fit.
    
    Args:
        user_info (dict): Dictionary containing user information such as:
            - Comunidad Autónoma: Region name (must match REGION_TO_SCOPE keys)
            - Tipo de Empresa: Company type
            - Presupuesto del Proyecto: Project budget
           
    
    Returns:
        dict: Dictionary containing:
            - 'recommended_grants': List of grants recommended 
    """
    query = GrantQueries()
    
    # Get grants matching basic criteria
    found_grants = query.find_adequate_grants(
        min_amount=user_info.get('Presupuesto del Proyecto', 0),
        region=user_info.get('Comunidad Autónoma')
    )
    
    # If no adequate grants found, return empty dict
    if not found_grants:
        return {}


    # Prepare minimized context for the LLM - only essential fields
    recommended_grants = [{
        'slug': grant.slug,
        'title': grant.formatted_title,
        'scope': grant.scope[:100] if grant.scope else "",
        'request_amount': grant.request_amount,
        'applicants': grant.applicants[:150] if grant.applicants else "",
        'line': grant.line[:150] if grant.line else ""
    } for grant in found_grants[:15]]  # Limit to top 15 grants

    

    
    # Only return results if we found recommended grants
    if recommended_grants:
        return {
            "recommended_grants": recommended_grants,
        }
    return {}
        
    

def get_grant_detail(slug: str) -> dict:
    """
    Get detailed information about a specific grant by its slug.
    
    Args:
        slug (str): The unique slug identifier of the grant
    
    Returns:
        dict: Dictionary containing all grant details, empty if not found
    """
    query = GrantQueries()
    grant = query.find_unique_grant(slug)
    
    if grant:
        # Convert grant object to dictionary using the existing to_dict method
        return grant.to_dict()
    return {}



