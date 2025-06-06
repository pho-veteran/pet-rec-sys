import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

def generate_pet_data(num_pets=2000):
    """Generate pet_adoption_data.csv with realistic pet attributes and expanded breeds."""
    pet_types = ['Dog', 'Cat', 'Rabbit', 'Bird']
    breeds = {
        'Dog': [
            'Labrador', 'Poodle', 'Bulldog', 'Beagle', 'German Shepherd',
            'Golden Retriever', 'Rottweiler', 'Dachshund', 'Boxer', 'Siberian Husky',
            'Pomeranian', 'Shih Tzu', 'Yorkshire Terrier', 'Chihuahua', 'Australian Shepherd'
        ],
        'Cat': [
            'Persian', 'Maine Coon', 'Siamese', 'Tabby', 'Sphynx',
            'Bengal', 'Ragdoll', 'Abyssinian', 'British Shorthair', 'Scottish Fold',
            'Russian Blue', 'Birman', 'Oriental Shorthair', 'Manx', 'American Shorthair'
        ],
        'Rabbit': [
            'Holland Lop', 'Netherland Dwarf', 'Flemish Giant', 'Lionhead',
            'Mini Rex', 'Angora', 'English Lop', 'Dutch', 'Havana',
            'Californian', 'New Zealand', 'Rex', 'Mini Lop', 'Polish'
        ],
        'Bird': [
            'Parakeet', 'Cockatiel', 'Canary', 'Lovebird',
            'African Grey', 'Macaw', 'Conure', 'Finch', 'Quaker Parrot',
            'Amazon Parrot', 'Eclectus Parrot', 'Pionus Parrot', 'Caique', 'Budgerigar'
        ]
    }
    sizes = ['Small', 'Medium', 'Large']
    health_conditions = ['Healthy', 'Minor Issues', 'Special Needs']
    energy_levels = ['Low', 'Medium', 'High']

    data = {
        'PetID': range(1, num_pets + 1),
        'PetType': np.random.choice(pet_types, num_pets, p=[0.4, 0.3, 0.2, 0.1]),
        'Breed': [],
        'Size': np.random.choice(sizes, num_pets, p=[0.3, 0.4, 0.3]),
        'AgeMonths': np.random.normal(36, 24, num_pets).clip(1, 120).astype(int),
        'WeightKg': np.random.normal(12, 6, num_pets).clip(0.5, 50).round(2),
        'TimeInShelterDays': np.random.exponential(30, num_pets).clip(0, 180).astype(int),
        'AdoptionFee': np.random.normal(120, 50, num_pets).clip(50, 500).round(2),
        'HealthCondition': np.random.choice(health_conditions, num_pets, p=[0.7, 0.2, 0.1]),
        'EnergyLevel': np.random.choice(energy_levels, num_pets, p=[0.3, 0.4, 0.3])
    }

    # Assign breeds based on PetType
    for pet_type in data['PetType']:
        data['Breed'].append(np.random.choice(breeds[pet_type]))

    pet_df = pd.DataFrame(data)
    # Ensure unique PetID
    if pet_df['PetID'].duplicated().any():
        raise ValueError("Duplicate PetID generated")
    
    return pet_df

def generate_user_data(num_users=500):
    """Generate synthetic_user_data.csv with diverse user profiles."""
    pet_types = ['Dog', 'Cat', 'Rabbit', 'Bird']
    living_spaces = ['Apartment', 'House', 'Small Space']
    activity_levels = ['Low', 'Moderate', 'High']
    experience_levels = ['None', 'Some', 'Experienced']

    data = {
        'UserID': range(1, num_users + 1),
        'PreferredPetType': np.random.choice(pet_types, num_users, p=[0.4, 0.3, 0.2, 0.1]),
        'LivingSpace': np.random.choice(living_spaces, num_users, p=[0.4, 0.4, 0.2]),
        'Allergies': np.random.choice([0, 1], num_users, p=[0.8, 0.2]),
        'ActivityLevel': np.random.choice(activity_levels, num_users, p=[0.3, 0.4, 0.3]),
        'PastPetExperience': np.random.choice(experience_levels, num_users, p=[0.3, 0.4, 0.3]),
        'MaxAdoptionFee': np.random.normal(200, 75, num_users).clip(50, 400).round(2)
    }

    user_df = pd.DataFrame(data)
    # Ensure unique UserID
    if user_df['UserID'].duplicated().any():
        raise ValueError("Duplicate UserID generated")
    
    return user_df

def generate_adoption_history(user_df, pet_df, num_adoptions=25000, preference_weight=0.7):
    """Generate adoption_history.csv with preference-driven adoptions, ensuring each pet is adopted at most once."""
    adoptions = []
    user_prefs = user_df.set_index('UserID').to_dict()['PreferredPetType']
    pet_types_map = pet_df.set_index('PetID').to_dict()['PetType']
    user_max_fees = user_df.set_index('UserID').to_dict()['MaxAdoptionFee']
    pet_fees_map = pet_df.set_index('PetID').to_dict()['AdoptionFee']

    available_pet_ids = set(pet_df['PetID'])
    
    # Cap num_adoptions to the number of available pets
    num_adoptions = min(num_adoptions, len(pet_df))

    # Ensure every user has at least 2 adoptions (cold start mitigation) if possible
    for user_id in user_df['UserID']:
        if len(adoptions) >= num_adoptions or not available_pet_ids:
            break 
        preferred_type = user_prefs[user_id]
        max_fee = user_max_fees[user_id]
        
        # Find suitable, unadopted pets
        potential_pets_for_user = [
            pid for pid in available_pet_ids
            if pet_types_map[pid] == preferred_type and pet_fees_map[pid] <= max_fee
        ]
        
        if potential_pets_for_user:
            num_initial = np.random.randint(2, 4)  # Try for 2–3 initial adoptions
            selected_count = 0
            for _ in range(num_initial):
                if not potential_pets_for_user or len(adoptions) >= num_adoptions:
                    break
                pet_id_to_adopt = np.random.choice(potential_pets_for_user)
                adoptions.append({'UserID': user_id, 'PetID': pet_id_to_adopt})
                available_pet_ids.remove(pet_id_to_adopt)
                potential_pets_for_user.remove(pet_id_to_adopt) # Remove from local list for this user's initial batch
                selected_count +=1
                if not available_pet_ids: # No more pets anywhere
                    break
            if not available_pet_ids and len(adoptions) >= num_adoptions:
                 break


    # Generate remaining adoptions
    user_ids_list = list(user_df['UserID']) # For efficient random choice
    while len(adoptions) < num_adoptions and available_pet_ids:
        user_id = np.random.choice(user_ids_list)
        preferred_type = user_prefs[user_id]
        max_fee = user_max_fees[user_id]
        
        # Filter affordable and available pets
        affordable_available_pets = [
            pid for pid in available_pet_ids if pet_fees_map[pid] <= max_fee
        ]
        if not affordable_available_pets:
            continue
        
        # Prefer matching pets
        matching_pets = [pid for pid in affordable_available_pets if pet_types_map[pid] == preferred_type]
        non_matching_pets = [pid for pid in affordable_available_pets if pet_types_map[pid] != preferred_type]
        
        pet_id_to_adopt = None
        if np.random.random() < preference_weight and matching_pets:
            pet_id_to_adopt = np.random.choice(matching_pets)
        elif non_matching_pets:
            pet_id_to_adopt = np.random.choice(non_matching_pets)
        elif matching_pets: # Fallback if random chance missed but matching exist
            pet_id_to_adopt = np.random.choice(matching_pets)
        else: # No suitable pet for this user at this time
            continue
        
        if pet_id_to_adopt:
            adoptions.append({'UserID': user_id, 'PetID': pet_id_to_adopt})
            available_pet_ids.remove(pet_id_to_adopt)

    adoption_df = pd.DataFrame(adoptions)
    # Remove duplicates (should be minimal with new logic, but good for safety)
    initial_len = len(adoption_df)
    adoption_df = adoption_df.drop_duplicates(subset=['UserID', 'PetID'], keep='first')
    # Ensure PetID is unique in adoptions (primary constraint)
    adoption_df = adoption_df.drop_duplicates(subset=['PetID'], keep='first')
    
    print(f"Removed {initial_len - len(adoption_df)} duplicate or already-adopted-pet entries")
    
    # Trim to target size if overshot (less likely now, but as a safeguard)
    if len(adoption_df) > num_adoptions:
        adoption_df = adoption_df.sample(n=num_adoptions, random_state=42)
    
    # Validate foreign keys
    invalid_adoptions = adoption_df[
        (~adoption_df['UserID'].isin(user_df['UserID'])) |
        (~adoption_df['PetID'].isin(pet_df['PetID']))
    ]
    if not invalid_adoptions.empty:
        raise ValueError(f"Invalid adoptions detected: {len(invalid_adoptions)}")
    
    return adoption_df

def validate_datasets(pet_df, user_df, adoption_df):
    """Validate generated datasets for consistency and quality."""
    print("Validating datasets...")
    
    # Check sizes
    print(f"Pet dataset: {len(pet_df)} rows")
    print(f"User dataset: {len(user_df)} rows")
    print(f"Adoption dataset: {len(adoption_df)} rows")
    
    # Check duplicates
    if pet_df['PetID'].duplicated().any():
        raise ValueError("Duplicate PetID found")
    if user_df['UserID'].duplicated().any():
        raise ValueError("Duplicate UserID found")
    if adoption_df.duplicated(subset=['UserID', 'PetID']).any():
        raise ValueError("Duplicate UserID-PetID pairs found")
    if adoption_df['PetID'].duplicated().any():
        raise ValueError("Duplicate PetID found in adoptions - a pet was adopted more than once")
    
    # Check matrix density
    density = len(adoption_df) / (len(user_df) * len(pet_df)) * 100
    print(f"User-Pet Matrix density: {density:.2f}%")
    
    # Check adoption distribution
    adoptions_per_user = adoption_df.groupby('UserID').size()
    print("Adoptions per user stats:")
    print(adoptions_per_user.describe())
    
    # Check breed diversity
    print("Number of unique breeds:", pet_df['Breed'].nunique())
    print("Breed distribution:")
    print(pet_df['Breed'].value_counts())
    
    # Check preference alignment
    merged = adoption_df.merge(user_df[['UserID', 'PreferredPetType']], on='UserID')
    merged = merged.merge(pet_df[['PetID', 'PetType']], on='PetID')
    matching_adoptions = (merged['PreferredPetType'] == merged['PetType']).mean()
    print(f"Percentage of adoptions matching PreferredPetType: {matching_adoptions * 100:.2f}%")

def main():
    """Generate and save all datasets."""
    print("Generating datasets...")
    
    # Generate datasets
    pet_df = generate_pet_data(num_pets=20000) # Increased
    user_df = generate_user_data(num_users=10000) # Increased
    # num_adoptions will be capped by num_pets if it's higher
    adoption_df = generate_adoption_history(user_df, pet_df, num_adoptions=15000) # Increased
    
    # Validate
    validate_datasets(pet_df, user_df, adoption_df)
    
    # Save to CSV
    pet_df.to_csv('pet_adoption_data.csv', index=False)
    user_df.to_csv('synthetic_user_data.csv', index=False)
    adoption_df.to_csv('adoption_history.csv', index=False)
    
    print("Datasets saved: pet_adoption_data.csv, synthetic_user_data.csv, adoption_history.csv")

if __name__ == "__main__":
    main()