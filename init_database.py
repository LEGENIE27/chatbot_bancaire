from pymongo import MongoClient
from config import Config
import hashlib
from datetime import datetime
import uuid

def init_database():
    try:
        client = MongoClient(Config.MONGO_URI)
        db = client[Config.DATABASE_NAME]
        users_collection = db.users

        sample_users = [
            {
                "user_id": str(uuid.uuid4()),
                "name": "Jean Dupont",
                "email": "jean.dupont@email.com",
                "balance": 2450.67,
                "card_status": "active",
                "created_at": datetime.now().isoformat(),
                "phone": "+33 1 23 45 67 89",
                "password": hashlib.sha256("password123".encode()).hexdigest(),
                "transactions": [
                    {"date": "2025-11-25", "description": "AMAZON", "amount": -45.99, "category": "Shopping"},
                    {"date": "2025-11-24", "description": "STATION ESSENCE", "amount": -65.00, "category": "Transport"},
                    {"date": "2025-11-23", "description": "VIREMENT REÇU", "amount": 500.00, "category": "Income"},
                    {"date": "2025-11-20", "description": "SUPERMARCHE", "amount": -125.40, "category": "Food"},
                    {"date": "2025-11-18", "description": "FACTURE ELECTRICITE", "amount": -85.30, "category": "Services"}
                ]
            },
            {
                "user_id": str(uuid.uuid4()),
                "name": "Marie Martin", 
                "email": "marie.martin@email.com",
                "balance": 1850.25,
                "card_status": "active",
                "created_at": datetime.now().isoformat(),
                "phone": "+33 1 34 56 78 90",
                "password": hashlib.sha256("secret456".encode()).hexdigest(),
                "transactions": [
                    {"date": "2025-11-26", "description": "SUPERMARCHE", "amount": -125.40, "category": "Food"},
                    {"date": "2025-11-25", "description": "FACTURE TELEPHONE", "amount": -45.00, "category": "Services"},
                    {"date": "2025-11-24", "description": "SALAIRE", "amount": 2500.00, "category": "Income"},
                    {"date": "2025-11-22", "description": "RESTAURANT", "amount": -75.50, "category": "Leisure"},
                    {"date": "2025-11-20", "description": "CARBURANT", "amount": -60.00, "category": "Transport"}
                ]
            },
            {
                "user_id": str(uuid.uuid4()),
                "name": "Sophie Leroy",
                "email": "sophie.leroy@email.com",
                "balance": 3200.80,
                "card_status": "blocked",  
                "created_at": datetime.now().isoformat(),
                "phone": "+33 1 45 67 89 01",
                "password": hashlib.sha256("banque789".encode()).hexdigest(),
                "transactions": [
                    {"date": "2025-11-27", "description": "REMBOURSEMENT", "amount": 150.00, "category": "Income"},
                    {"date": "2025-11-25", "description": "LOYER", "amount": -750.00, "category": "Housing"},
                    {"date": "2025-11-24", "description": "CENTRE COMMERCIAL", "amount": -230.75, "category": "Shopping"},
                    {"date": "2025-11-22", "description": "INTERETS", "amount": 12.50, "category": "Income"},
                    {"date": "2025-11-20", "description": "ASSURANCE", "amount": -45.00, "category": "Services"}
                ]
            }
        ]
        existing_users = list(users_collection.find({}, {"email": 1, "name": 1}))
        
        if existing_users:
            print(" Utilisateurs existants dans la base :")
            for user in existing_users:
                print(f"   - {user['name']} ({user['email']})")
            response = input("Voulez-vous ajouter des utilisateurs de test ? (oui/non): ")
            if response.lower() != 'oui':
                print(" Base de données conservée")
                return
        result = users_collection.insert_many(sample_users)
        
        print(f"{len(result.inserted_ids)} utilisateurs insérés dans la base de données")
        print("\n Identifiants de test :")
        print("   Email: jean.dupont@email.com / Mot de passe: password123")
        print("   Email: marie.martin@email.com / Mot de passe: secret456") 
        print("   Email: sophie.leroy@email.com / Mot de passe: banque789")
        print("\n Soldes de test :")
        print("   Jean Dupont : 2 450,67 €")
        print("   Marie Martin : 1 850,25 €")
        print("   Sophie Leroy : 3 200,80 €")
        
        # Vérifier l'insertion
        count = users_collection.count_documents({})
        print(f"\n Total utilisateurs dans la base : {count}")
        
    except Exception as e:
        print(f" Erreur lors de l'initialisation : {e}")

if __name__ == '__main__':
    init_database()