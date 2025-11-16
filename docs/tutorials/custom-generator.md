# Custom Generator Tutorial

Learn how to create custom data generators for your specific domain requirements using the Dataset Generator framework.

## Overview

The Dataset Generator provides a flexible framework for creating domain-specific data generators. This tutorial walks through creating a custom generator from scratch.

## Prerequisites

- Python 3.12+
- Dataset Generator installed
- Understanding of data modeling concepts
- Basic familiarity with Polars/Pandas

## Generator Architecture

### Core Components

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PartitionSpec:
    """Specifies how to partition data by time"""
    start_date: date
    end_date: date
    partition_by: List[str] = ["year", "month", "day"]

class GeneratorBase(ABC):
    """Base class for all data generators"""
    
    @abstractmethod
    def generate(self, partition_spec: PartitionSpec) -> Dict[str, pl.DataFrame]:
        """Generate data for a given partition"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, pl.Schema]:
        """Return schema definitions for all tables"""
        pass
```

### Factory Registration

```python
from dataset_generator.core.factory import register_generator

@register_generator("custom_domain")
class CustomGenerator(GeneratorBase):
    """Custom domain-specific generator"""
    pass
```

## Creating a Healthcare Generator

Let's create a healthcare domain generator for hospital data:

### 1. Define the Generator Class

```python
import marimo as mo
import datetime
from dataset_generator.core.interfaces import GeneratorBase, PartitionSpec
from dataset_generator.core.factory import register_generator
import polars as pl
import numpy as np
from typing import Dict, Any
import uuid

@register_generator("healthcare")
class HealthcareGenerator(GeneratorBase):
    """Generator for hospital healthcare data"""
    
    def __init__(self, 
                 seed: Optional[int] = None,
                 n_patients: int = 10000,
                 n_doctors: int = 500,
                 n_departments: int = 20,
                 admissions_per_day: int = 50,
                 avg_length_of_stay: float = 4.5):
        self.seed = seed
        self.n_patients = n_patients
        self.n_doctors = n_doctors
        self.n_departments = n_departments
        self.admissions_per_day = admissions_per_day
        self.avg_length_of_stay = avg_length_of_stay
        
        # Set random seed for reproducibility
        if seed is not None:
            np.random.seed(seed)
            pl.Series([seed]).shuffle(seed)
        
        # Initialize generators
        self._initialize_generators()
    
    def _initialize_generators(self):
        """Initialize random generators for various data fields"""
        self.patient_gen = self._create_patient_generator()
        self.doctor_gen = self._create_doctor_generator()
        self.department_gen = self._create_department_generator()
```

### 2. Implement Patient Generation

```python
def _create_patient_generator(self):
    """Create patient data generator"""
    
    def generate_patients(n: int):
        # Generate demographics
        ages = np.random.normal(45, 20, n).astype(int)
        ages = np.clip(ages, 0, 100)
        
        genders = np.random.choice(['M', 'F'], n, p=[0.48, 0.52])
        
        # Generate addresses
        streets = [f"{np.random.randint(1, 9999)} {np.random.choice(['Main', 'Oak', 'Elm', 'Pine', 'Maple'])} St" 
                   for _ in range(n)]
        cities = np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], n)
        states = np.random.choice(['NY', 'CA', 'IL', 'TX', 'AZ'], n)
        zip_codes = [f"{np.random.randint(10000, 99999)}" for _ in range(n)]
        
        # Generate medical information
        blood_types = np.random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'], 
                                      n, p=[0.34, 0.06, 0.09, 0.02, 0.38, 0.07, 0.03, 0.01])
        
        # Generate IDs and timestamps
        patient_ids = [f"PT-{str(uuid.uuid4())[:8].upper()}" for _ in range(n)]
        
        return pl.DataFrame({
            'patient_id': patient_ids,
            'first_name': self._generate_names(n, 'first'),
            'last_name': self._generate_names(n, 'last'),
            'date_of_birth': self._generate_dates_of_birth(ages),
            'gender': genders,
            'blood_type': blood_types,
            'phone': [f"{np.random.randint(200, 999)}-{np.random.randint(200, 999)}-{np.random.randint(1000, 9999)}" 
                     for _ in range(n)],
            'email': [f"patient{i}@example.com" for i in range(n)],
            'address': streets,
            'city': cities,
            'state': states,
            'zip_code': zip_codes,
            'insurance_id': [f"INS-{str(uuid.uuid4())[:8].upper()}" for _ in range(n)],
            'created_at': [datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 365*5)) 
                          for _ in range(n)],
            'updated_at': [datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 30)) 
                          for _ in range(n)]
        })
    
    return generate_patients

def _generate_names(self, n: int, name_type: str) -> List[str]:
    """Generate realistic names"""
    first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
                   'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 
                  'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas']
    
    if name_type == 'first':
        return np.random.choice(first_names, n)
    else:
        return np.random.choice(last_names, n)

def _generate_dates_of_birth(self, ages: np.ndarray) -> List[datetime.date]:
    """Generate dates of birth based on ages"""
    today = datetime.date.today()
    return [datetime.date(today.year - age - np.random.randint(0, 365), 
                          today.month, 
                          today.day) for age in ages]
```

### 3. Implement Doctor Generation

```python
def _create_doctor_generator(self):
    """Create doctor data generator"""
    
    def generate_doctors(n: int):
        specialties = np.random.choice([
            'Cardiology', 'Neurology', 'Oncology', 'Pediatrics', 'Surgery',
            'Emergency Medicine', 'Internal Medicine', 'Radiology', 'Anesthesiology',
            'Dermatology', 'Psychiatry', 'Orthopedics', 'Gastroenterology', 'Endocrinology'
        ], n)
        
        experience_years = np.random.randint(1, 40, n)
        
        return pl.DataFrame({
            'doctor_id': [f"DR-{str(uuid.uuid4())[:8].upper()}" for _ in range(n)],
            'first_name': self._generate_names(n, 'first'),
            'last_name': self._generate_names(n, 'last'),
            'specialty': specialties,
            'license_number': [f"MD{np.random.randint(100000, 999999)}" for _ in range(n)],
            'experience_years': experience_years,
            'department_id': [f"DEPT-{np.random.randint(1, self.n_departments):03d}" for _ in range(n)],
            'phone': [f"{np.random.randint(200, 999)}-{np.random.randint(200, 999)}-{np.random.randint(1000, 9999)}" 
                     for _ in range(n)],
            'email': [f"doctor{i}@hospital.com" for i in range(n)],
            'created_at': [datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 365*20)) 
                          for _ in range(n)],
            'updated_at': [datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 30)) 
                          for _ in range(n)]
        })
    
    return generate_doctors
```

### 4. Implement Department Generation

```python
def _create_department_generator(self):
    """Create department data generator"""
    
    def generate_departments(n: int):
        dept_names = [
            'Emergency', 'Cardiology', 'Neurology', 'Oncology', 'Pediatrics',
            'Surgery', 'ICU', 'Radiology', 'Laboratory', 'Pharmacy',
            'Physical Therapy', 'Mental Health', 'Maternity', 'Orthopedics',
            'Gastroenterology', 'Pulmonology', 'Nephrology', 'Endocrinology',
            'Infectious Disease', 'General Medicine'
        ]
        
        selected_names = np.random.choice(dept_names, min(n, len(dept_names)), replace=False)
        
        return pl.DataFrame({
            'department_id': [f"DEPT-{i+1:03d}" for i in range(min(n, len(dept_names)))],
            'name': selected_names,
            'floor': np.random.randint(1, 10, min(n, len(dept_names))),
            'capacity': np.random.randint(20, 100, min(n, len(dept_names))),
            'head_doctor_id': [f"DR-{str(uuid.uuid4())[:8].upper()}" for _ in range(min(n, len(dept_names)))],
            'phone': [f" ext.{np.random.randint(1000, 9999)}" for _ in range(min(n, len(dept_names)))],
            'created_at': [datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 365*10)) 
                          for _ in range(min(n, len(dept_names)))],
            'updated_at': [datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 30)) 
                          for _ in range(min(n, len(dept_names)))]
        })
    
    return generate_departments
```

### 5. Implement Main Generation Logic

```python
def generate(self, partition_spec: PartitionSpec) -> Dict[str, pl.DataFrame]:
    """Generate healthcare data for the specified partition"""
    
    # Generate master data
    patients = self.patient_gen(self.n_patients)
    doctors = self.doctor_gen(self.n_doctors)
    departments = self.department_gen(self.n_departments)
    
    # Generate transactional data for each date in the partition
    admissions = []
    treatments = []
    medications = []
    
    current_date = partition_spec.start_date
    while current_date <= partition_spec.end_date:
        # Generate admissions for this day
        day_admissions = self._generate_daily_admissions(current_date, patients, doctors, departments)
        admissions.append(day_admissions)
        
        # Generate treatments for these admissions
        day_treatments = self._generate_daily_treatments(day_admissions, doctors)
        treatments.append(day_treatments)
        
        # Generate medications
        day_medications = self._generate_daily_medications(day_treatments)
        medications.append(day_medications)
        
        current_date += datetime.timedelta(days=1)
    
    # Combine daily data
    all_admissions = pl.concat(admissions) if admissions else pl.DataFrame()
    all_treatments = pl.concat(treatments) if treatments else pl.DataFrame()
    all_medications = pl.concat(medications) if medications else pl.DataFrame()
    
    return {
        'patients': patients,
        'doctors': doctors,
        'departments': departments,
        'admissions': all_admissions,
        'treatments': all_treatments,
        'medications': all_medications
    }

def _generate_daily_admissions(self, date: datetime.date, patients: pl.DataFrame, 
                              doctors: pl.DataFrame, departments: pl.DataFrame):
    """Generate admissions for a specific day"""
    
    n_admissions = np.random.poisson(self.admissions_per_day)
    
    if n_admissions == 0:
        return pl.DataFrame()
    
    # Select random patients
    selected_patients = patients.sample(n_admissions, with_replacement=False)
    
    # Generate admission details
    admission_types = np.random.choice(['Emergency', 'Scheduled', 'Transfer'], n_admissions)
    priorities = np.random.choice(['Low', 'Medium', 'High', 'Critical'], n_admissions, 
                                  p=[0.3, 0.4, 0.2, 0.1])
    
    # Calculate discharge dates based on length of stay
    lengths_of_stay = np.random.exponential(self.avg_length_of_stay, n_admissions).astype(int)
    discharge_dates = [date + datetime.timedelta(days=los) for los in lengths_of_stay]
    
    return pl.DataFrame({
        'admission_id': [f"ADM-{str(uuid.uuid4())[:8].upper()}" for _ in range(n_admissions)],
        'patient_id': selected_patients['patient_id'],
        'department_id': np.random.choice(departments['department_id'], n_admissions),
        'admission_date': [date] * n_admissions,
        'discharge_date': discharge_dates,
        'admission_type': admission_types,
        'priority': priorities,
        'attending_doctor_id': np.random.choice(doctors['doctor_id'], n_admissions),
        'room_number': [f"{np.random.randint(100, 999)}{np.random.choice(['A', 'B', 'C'])}" 
                        for _ in range(n_admissions)],
        'status': np.where([d <= datetime.date.today() for d in discharge_dates], 
                          'Discharged', 'Admitted'),
        'created_at': [datetime.datetime.combine(date, datetime.time(9, 0)) + 
                      datetime.timedelta(minutes=np.random.randint(0, 480)) 
                      for _ in range(n_admissions)],
        'updated_at': [datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 1)) 
                      for _ in range(n_admissions)]
    })
```

### 6. Define Schema

```python
def get_schema(self) -> Dict[str, pl.Schema]:
    """Return schema definitions for all tables"""
    
    schemas = {
        'patients': pl.Schema({
            'patient_id': pl.Utf8,
            'first_name': pl.Utf8,
            'last_name': pl.Utf8,
            'date_of_birth': pl.Date,
            'gender': pl.Utf8,
            'blood_type': pl.Utf8,
            'phone': pl.Utf8,
            'email': pl.Utf8,
            'address': pl.Utf8,
            'city': pl.Utf8,
            'state': pl.Utf8,
            'zip_code': pl.Utf8,
            'insurance_id': pl.Utf8,
            'created_at': pl.Datetime,
            'updated_at': pl.Datetime
        }),
        'doctors': pl.Schema({
            'doctor_id': pl.Utf8,
            'first_name': pl.Utf8,
            'last_name': pl.Utf8,
            'specialty': pl.Utf8,
            'license_number': pl.Utf8,
            'experience_years': pl.Int32,
            'department_id': pl.Utf8,
            'phone': pl.Utf8,
            'email': pl.Utf8,
            'created_at': pl.Datetime,
            'updated_at': pl.Datetime
        }),
        'departments': pl.Schema({
            'department_id': pl.Utf8,
            'name': pl.Utf8,
            'floor': pl.Int32,
            'capacity': pl.Int32,
            'head_doctor_id': pl.Utf8,
            'phone': pl.Utf8,
            'created_at': pl.Datetime,
            'updated_at': pl.Datetime
        }),
        'admissions': pl.Schema({
            'admission_id': pl.Utf8,
            'patient_id': pl.Utf8,
            'department_id': pl.Utf8,
            'admission_date': pl.Date,
            'discharge_date': pl.Date,
            'admission_type': pl.Utf8,
            'priority': pl.Utf8,
            'attending_doctor_id': pl.Utf8,
            'room_number': pl.Utf8,
            'status': pl.Utf8,
            'created_at': pl.Datetime,
            'updated_at': pl.Datetime
        }),
        'treatments': pl.Schema({
            'treatment_id': pl.Utf8,
            'admission_id': pl.Utf8,
            'doctor_id': pl.Utf8,
            'treatment_code': pl.Utf8,
            'treatment_name': pl.Utf8,
            'treatment_date': pl.Date,
            'cost': pl.Float64,
            'status': pl.Utf8,
            'created_at': pl.Datetime,
            'updated_at': pl.Datetime
        }),
        'medications': pl.Schema({
            'medication_id': pl.Utf8,
            'treatment_id': pl.Utf8,
            'drug_name': pl.Utf8,
            'dosage': pl.Utf8,
            'frequency': pl.Utf8,
            'start_date': pl.Date,
            'end_date': pl.Date,
            'status': pl.Utf8,
            'created_at': pl.Datetime,
            'updated_at': pl.Datetime
        })
    }
    
    return schemas
```

### 7. Add Helper Methods

```python
def _generate_daily_treatments(self, admissions: pl.DataFrame, doctors: pl.DataFrame):
    """Generate treatments for given admissions"""
    
    if len(admissions) == 0:
        return pl.DataFrame()
    
    n_treatments = np.random.poisson(2.5, len(admissions))
    
    treatments = []
    for i, (admission, n_treat) in enumerate(zip(admissions.iter_rows(), n_treatments)):
        for j in range(n_treat):
            treatments.append({
                'treatment_id': f"TRT-{str(uuid.uuid4())[:8].upper()}",
                'admission_id': admission[0],  # admission_id
                'doctor_id': np.random.choice(doctors['doctor_id']),
                'treatment_code': f"T{np.random.randint(1000, 9999)}",
                'treatment_name': np.random.choice(['X-Ray', 'Blood Test', 'MRI', 'CT Scan', 'Ultrasound', 
                                                   'ECG', 'Surgery', 'Physical Therapy', 'Counseling']),
                'treatment_date': admission[3],  # admission_date
                'cost': np.random.uniform(100, 5000),
                'status': np.random.choice(['Scheduled', 'In Progress', 'Completed']),
                'created_at': datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 7)),
                'updated_at': datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 1))
            })
    
    return pl.DataFrame(treatments)

def _generate_daily_medications(self, treatments: pl.DataFrame):
    """Generate medications for given treatments"""
    
    if len(treatments) == 0:
        return pl.DataFrame()
    
    medications = []
    for treatment in treatments.iter_rows():
        if np.random.random() > 0.3:  # 70% chance of medication
            medications.append({
                'medication_id': f"MED-{str(uuid.uuid4())[:8].upper()}",
                'treatment_id': treatment[0],  # treatment_id
                'drug_name': np.random.choice(['Aspirin', 'Ibuprofen', 'Amoxicillin', 'Lisinopril', 
                                              'Metformin', 'Amlodipine', 'Simvastatin', 'Omeprazole']),
                'dosage': np.random.choice(['50mg', '100mg', '250mg', '500mg']),
                'frequency': np.random.choice(['Once daily', 'Twice daily', 'Three times daily', 'As needed']),
                'start_date': treatment[4],  # treatment_date
                'end_date': treatment[4] + datetime.timedelta(days=np.random.randint(1, 30)),
                'status': np.random.choice(['Active', 'Completed', 'Discontinued']),
                'created_at': datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 7)),
                'updated_at': datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 1))
            })
    
    return pl.DataFrame(medications)
```

## Using the Custom Generator

### 1. Register and Use

```python
from dataset_generator import create_generator, create_writer, write_dataset
from datetime import date

# The healthcare generator is automatically registered
generator = create_generator(
    "healthcare",
    seed=42,
    n_patients=5000,
    n_doctors=200,
    n_departments=15,
    admissions_per_day=25,
    avg_length_of_stay=4.0
)

# Create writer
writer = create_writer("parquet", output_uri="./healthcare_data")

# Generate data
write_dataset(generator, writer)
```

### 2. Query the Data

```python
import polars as pl

# Read generated data
patients = pl.read_parquet("healthcare_data/patients/*.parquet")
admissions = pl.read_parquet("healthcare_data/admissions/**/*.parquet")
doctors = pl.read_parquet("healthcare_data/doctors/*.parquet")

# Analyze admission patterns
admission_analysis = (
    admissions
    .group_by("admission_date", "admission_type")
    .agg(pl.count("admission_id").alias("daily_admissions"))
    .sort("admission_date")
)

# Department performance
dept_performance = (
    admissions
    .join(doctors, left_on="attending_doctor_id", right_on="doctor_id")
    .group_by("department_id", "specialty")
    .agg([
        pl.count("admission_id").alias("total_admissions"),
        pl.mean("priority").alias("avg_priority_score")
    ])
)

print(f"Generated {len(patients)} patients")
print(f"Generated {len(admissions)} admissions")
print(f"Generated {len(doctors)} doctors")
```

## Testing Your Generator

### 1. Unit Tests

```python
import unittest
from datetime import date, timedelta

class TestHealthcareGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = HealthcareGenerator(
            seed=42,
            n_patients=100,
            n_doctors=10,
            n_departments=5
        )
    
    def test_patient_generation(self):
        partition_spec = PartitionSpec(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        data = self.generator.generate(partition_spec)
        patients = data['patients']
        
        self.assertEqual(len(patients), 100)
        self.assertIn('patient_id', patients.columns)
        self.assertIn('first_name', patients.columns)
        
        # Check data quality
        self.assertTrue(all(patients['age'] >= 0))
        self.assertTrue(all(patients['age'] <= 100))
    
    def test_schema_validation(self):
        schema = self.generator.get_schema()
        self.assertIn('patients', schema)
        self.assertIn('doctors', schema)
        self.assertIn('admissions', schema)

if __name__ == '__main__':
    unittest.main()
```

### 2. Integration Tests

```python
def test_end_to_end_generation():
    """Test complete generation pipeline"""
    
    # Create generator
    generator = create_generator(
        "healthcare",
        seed=42,
        n_patients=1000,
        admissions_per_day=10
    )
    
    # Generate data
    partition_spec = PartitionSpec(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 7)
    )
    
    data = generator.generate(partition_spec)
    
    # Verify all tables are generated
    expected_tables = ['patients', 'doctors', 'departments', 'admissions', 'treatments', 'medications']
    for table in expected_tables:
        assert table in data, f"Missing table: {table}"
        assert len(data[table]) > 0, f"Empty table: {table}"
    
    # Test data integrity
    admissions = data['admissions']
    patients = data['patients']
    
    # Check referential integrity
    assert set(admissions['patient_id']).issubset(set(patients['patient_id']))

if __name__ == '__main__':
    test_end_to_end_generation()
    print("Integration test passed!")
```

## Best Practices

### 1. Performance Optimization

```python
def generate_batch(self, partition_specs: List[PartitionSpec]) -> Dict[str, pl.DataFrame]:
    """Generate multiple partitions efficiently"""
    
    all_data = {}
    
    # Generate master data once
    patients = self.patient_gen(self.n_patients)
    doctors = self.doctor_gen(self.n_doctors)
    departments = self.department_gen(self.n_departments)
    
    all_data['patients'] = patients
    all_data['doctors'] = doctors
    all_data['departments'] = departments
    
    # Generate transactional data for each partition
    all_admissions = []
    all_treatments = []
    
    for partition_spec in partition_specs:
        partition_data = self._generate_partition_data(partition_spec, patients, doctors, departments)
        all_admissions.append(partition_data['admissions'])
        all_treatments.append(partition_data['treatments'])
    
    all_data['admissions'] = pl.concat(all_admissions)
    all_data['treatments'] = pl.concat(all_treatments)
    
    return all_data
```

### 2. Configuration Management

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class HealthcareGeneratorConfig:
    """Configuration for healthcare generator"""
    n_patients: int = 10000
    n_doctors: int = 500
    n_departments: int = 20
    admissions_per_day: int = 50
    avg_length_of_stay: float = 4.5
    seed: Optional[int] = None
    
    # Domain-specific options
    specialty_distribution: Dict[str, float] = None
    admission_type_distribution: Dict[str, float] = None
    age_distribution: Dict[str, float] = None

@register_generator("healthcare")
class HealthcareGenerator(GeneratorBase):
    def __init__(self, config: HealthcareGeneratorConfig):
        self.config = config
        self._initialize_generators()
```

### 3. Error Handling

```python
def generate_with_validation(self, partition_spec: PartitionSpec) -> Dict[str, pl.DataFrame]:
    """Generate data with validation and error handling"""
    
    try:
        data = self.generate(partition_spec)
        
        # Validate data integrity
        self._validate_data(data)
        
        return data
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise RuntimeError(f"Healthcare data generation failed: {e}")

def _validate_data(self, data: Dict[str, pl.DataFrame]):
    """Validate generated data for consistency"""
    
    # Check referential integrity
    admissions = data.get('admissions', pl.DataFrame())
    patients = data.get('patients', pl.DataFrame())
    
    if len(admissions) > 0 and len(patients) > 0:
        missing_patients = set(admissions['patient_id']) - set(patients['patient_id'])
        if missing_patients:
            raise ValueError(f"Missing patients for admissions: {missing_patients}")
    
    # Check data quality
    for table_name, df in data.items():
        if len(df) > 0:
            # Check for null values in key columns
            key_columns = self._get_key_columns(table_name)
            for col in key_columns:
                if col in df.columns and df[col].null_count() > 0:
                    raise ValueError(f"Null values found in {table_name}.{col}")
```

## Next Steps

- **[E-commerce Dataset](ecommerce-dataset.md)** - Detailed e-commerce generator examples
- **[S3 with MinIO](s3-minio.md)** - Store datasets in cloud storage
- **[Examples](../examples/jupyter.md)** - Interactive notebook examples
- **[API Reference](../api/core.md)** - Complete API documentation

## Related Resources

- [Polars Documentation](https://pola.rs/docs/)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Abstract Base Classes](https://docs.python.org/3/library/abc.html)
- [Factory Pattern in Python](https://refactoring.guru/design-patterns/factory-method/python/example)
