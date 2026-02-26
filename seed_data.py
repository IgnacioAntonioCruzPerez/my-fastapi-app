"""Populate database with test data. Run after migrations: python seed_data.py"""
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from models import Base, Building, Activity, Organization, OrganizationPhone, organization_activities

def get_url():
    url = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

def seed():
    url = get_url()
    connect_args = {} if url.startswith("postgresql") else {"check_same_thread": False}
    engine = create_engine(url, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)  # idempotent if tables exist
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Skip if data already present
        if db.query(Building).first():
            print("Data already present, skipping seed.")
            return

        # Buildings (address, lat, lon)
        buildings = [
            Building(address="g. Moscow, ul. Lenina 1, office 3", latitude=55.7558, longitude=37.6173),
            Building(address="Blukhera, 32/1", latitude=55.7512, longitude=37.6189),
            Building(address="Saint Petersburg, Nevsky 10", latitude=59.9343, longitude=30.3351),
        ]
        for b in buildings:
            db.add(b)
        db.commit()
        for b in buildings:
            db.refresh(b)

        # Activities (tree, max 3 levels). Example from spec:
        # - Food → Meat products, Dairy products
        # - Cars → Freight, Passenger cars, Spare parts, Accessories
        food = Activity(name="Food", parent_id=None, level=1)
        cars = Activity(name="Cars", parent_id=None, level=1)
        db.add_all([food, cars])
        db.commit()
        db.refresh(food)
        db.refresh(cars)

        # Level 2 under Food: Meat products, Dairy products
        meat_products = Activity(name="Meat products", parent_id=food.id, level=2)
        dairy_products = Activity(name="Dairy products", parent_id=food.id, level=2)
        db.add_all([meat_products, dairy_products])
        db.commit()
        db.refresh(meat_products)
        db.refresh(dairy_products)

        # Level 2 under Cars: Freight, Passenger cars, Spare parts, Accessories
        freight = Activity(name="Freight", parent_id=cars.id, level=2)
        passenger_cars = Activity(name="Passenger cars", parent_id=cars.id, level=2)
        spare_parts = Activity(name="Spare parts", parent_id=cars.id, level=2)
        accessories = Activity(name="Accessories", parent_id=cars.id, level=2)
        db.add_all([freight, passenger_cars, spare_parts, accessories])
        db.commit()
        db.refresh(freight)
        db.refresh(passenger_cars)
        db.refresh(spare_parts)
        db.refresh(accessories)

        # Organizations (more data for testing)
        b1, b2, b3 = buildings[0], buildings[1], buildings[2]
        org1 = Organization(name='OOO "Horns and Hooves"', building_id=b2.id)
        org2 = Organization(name="Meat & Dairy Co", building_id=b1.id)
        org3 = Organization(name="Auto Parts Plus", building_id=b3.id)
        org4 = Organization(name="Food Market", building_id=b2.id)
        org5 = Organization(name="City Dairy", building_id=b1.id)
        org6 = Organization(name="Prime Meat House", building_id=b1.id)
        org7 = Organization(name="Truck Depot", building_id=b3.id)
        org8 = Organization(name="Passenger Cars Center", building_id=b3.id)
        db.add_all([org1, org2, org3, org4, org5, org6, org7, org8])
        db.commit()
        for o in [org1, org2, org3, org4, org5, org6, org7, org8]:
            db.refresh(o)

        # Phones (multiple per org)
        phones = [
            OrganizationPhone(organization_id=org1.id, phone_number="2-222-222"),
            OrganizationPhone(organization_id=org1.id, phone_number="3-333-333"),
            OrganizationPhone(organization_id=org1.id, phone_number="8-923-666-13-13"),
            OrganizationPhone(organization_id=org2.id, phone_number="8-495-111-22-33"),
            OrganizationPhone(organization_id=org3.id, phone_number="8-812-444-55-66"),
            OrganizationPhone(organization_id=org4.id, phone_number="8-495-777-88-99"),
            OrganizationPhone(organization_id=org5.id, phone_number="8-495-000-11-22"),
            OrganizationPhone(organization_id=org6.id, phone_number="8-495-333-44-55"),
            OrganizationPhone(organization_id=org7.id, phone_number="8-812-999-00-11"),
            OrganizationPhone(organization_id=org8.id, phone_number="8-812-222-33-44"),
        ]
        db.add_all(phones)
        db.commit()

        # Link organizations to activities
        links = [
            # Horns and Hooves – car spare parts
            {"organization_id": org1.id, "activity_id": cars.id},
            {"organization_id": org1.id, "activity_id": spare_parts.id},
            # Meat & Dairy Co – general food + both detailed products
            {"organization_id": org2.id, "activity_id": food.id},
            {"organization_id": org2.id, "activity_id": meat_products.id},
            {"organization_id": org2.id, "activity_id": dairy_products.id},
            # Auto Parts Plus – cars + accessories
            {"organization_id": org3.id, "activity_id": cars.id},
            {"organization_id": org3.id, "activity_id": accessories.id},
            # Food Market – food + dairy products
            {"organization_id": org4.id, "activity_id": food.id},
            {"organization_id": org4.id, "activity_id": dairy_products.id},
            # City Dairy – dairy products only
            {"organization_id": org5.id, "activity_id": dairy_products.id},
            # Prime Meat House – meat products only
            {"organization_id": org6.id, "activity_id": meat_products.id},
            # Truck Depot – freight
            {"organization_id": org7.id, "activity_id": freight.id},
            # Passenger Cars Center – passenger cars
            {"organization_id": org8.id, "activity_id": passenger_cars.id},
        ]
        for row in links:
            db.execute(insert(organization_activities).values(**row))
        db.commit()
        print("Seed data created successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
