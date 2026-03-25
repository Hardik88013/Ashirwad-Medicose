import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce2.settings')
django.setup()

from store.models import Product

def populate():
    # Clear existing products
    Product.objects.all().delete()

    products = [
        # Medicines
        {"name": "Paracetamol 500mg", "description": "Relieve pain and fever.", "price": 40.0, "category": "medicine", "image": "products/medicine.png"},
        {"name": "Amoxicillin 250mg", "description": "Antibiotic for bacterial infections.", "price": 120.0, "category": "medicine", "image": "products/medicine.png"},
        {"name": "Cetirizine 10mg", "description": "Antihistamine for allergies.", "price": 35.0, "category": "medicine", "image": "products/medicine.png"},
        {"name": "Ibuprofen 400mg", "description": "Nonsteroidal anti-inflammatory drug (NSAID).", "price": 55.0, "category": "medicine", "image": "products/medicine.png"},
        
        # First Aid
        {"name": "Adhesive Bandages", "description": "Box of 50 sterile bandages.", "price": 150.0, "category": "firstaid", "image": "products/firstaid.png"},
        {"name": "Antiseptic Liquid 500ml", "description": "For cleaning wounds.", "price": 180.0, "category": "firstaid", "image": "products/firstaid.png"},
        {"name": "Medical Tape", "description": "Micropore tape for dressing.", "price": 60.0, "category": "firstaid", "image": "products/firstaid.png"},
        
        # Personal Care
        {"name": "Aloe Vera Gel", "description": "Soothing gel for skin.", "price": 220.0, "category": "personal", "image": "products/personal.png"},
        {"name": "Hand Sanitizer 500ml", "description": "70% Alcohol based sanitizer.", "price": 250.0, "category": "personal", "image": "products/personal.png"},
        {"name": "Anti-Dandruff Shampoo", "description": "Effective scalp care.", "price": 320.0, "category": "personal", "image": "products/personal.png"},
        
        # Baby Care
        {"name": "Baby Diapers (Small)", "description": "Pack of 40 diapers.", "price": 450.0, "category": "baby", "image": "products/baby.png"},
        {"name": "Baby Lotion 200ml", "description": "Gentle on newborn skin.", "price": 280.0, "category": "baby", "image": "products/baby.png"},
        {"name": "Baby Powder 100g", "description": "Prevents diaper rash.", "price": 120.0, "category": "baby", "image": "products/baby.png"},
        
        # Devices
        {"name": "Digital Thermometer", "description": "Fast and accurate temperature reading.", "price": 190.0, "category": "device", "image": "products/device.png"},
        {"name": "Blood Pressure Monitor", "description": "Automatic upper arm BP monitor.", "price": 2400.0, "category": "device", "image": "products/device.png"},
        {"name": "Pulse Oximeter", "description": "Measures blood oxygen levels.", "price": 950.0, "category": "device", "image": "products/device.png"},
    ]

    for p in products:
        Product.objects.create(**p)
    
    print(f"Successfully added {len(products)} medical products with images.")

if __name__ == "__main__":
    populate()
