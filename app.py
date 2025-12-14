# developed by xradion dynamics
# xradion.com
# 2025
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from transformers import pipeline
import pandas as pd

###############################################################################
# hard coded and in memory disease + symptom data (with synonyms and severity), little novice to do but better when packaging exe
###############################################################################
ALL_DISEASES_WITH_SEVERITY = [
    {"name": "Atrial fibrillation", "synonyms": ["A fib"], "severity": 6},
    {"name": "Abdominal aortic aneurysm", "synonyms": [], "severity": 9},
    {"name": "Hyperhidrosis", "synonyms": ["Excessive sweating"], "severity": 3},
    {"name": "Bartholin's cyst", "synonyms": ["Abscess, Bartholin's"], "severity": 2},
    {"name": "Absence seizure", "synonyms": [], "severity": 7},
    {"name": "Acanthosis nigricans", "synonyms": [], "severity": 5},
    {"name": "Achalasia", "synonyms": [], "severity": 7},
    {"name": "Achilles tendinitis", "synonyms": [], "severity": 4},
    {"name": "Achilles tendon rupture", "synonyms": [], "severity": 8},
    {
        "name": "Acid reflux",
        "synonyms": ["Gastroesophageal reflux disease (GERD)"],
        "severity": 5,
    },
    {"name": "Acid reflux, infant", "synonyms": ["Infant reflux"], "severity": 4},
    {"name": "ACL injury", "synonyms": [], "severity": 6},
    {"name": "Acne", "synonyms": [], "severity": 3},
    {"name": "Acne inversa", "synonyms": ["Hidradenitis suppurativa"], "severity": 7},
    {"name": "Acoustic neuroma", "synonyms": [], "severity": 7},
    {
        "name": "Acquired immunodeficiency syndrome",
        "synonyms": ["HIV/AIDS"],
        "severity": 10,
    },
    {"name": "Acromegaly", "synonyms": [], "severity": 8},
    {"name": "Actinic keratosis", "synonyms": [], "severity": 6},
    {"name": "Acute coronary syndrome", "synonyms": [], "severity": 10},
    {"name": "Acute flaccid myelitis", "synonyms": ["AFM"], "severity": 8},
    {
        "name": "Acute granulocytic leukemia",
        "synonyms": ["Acute myelogenous leukemia"],
        "severity": 10,
    },
    {
        "name": "Acute inflammatory demyelinating polyneuropathy",
        "synonyms": ["Guillain-Barre syndrome"],
        "severity": 8,
    },
    {"name": "Acute kidney injury", "synonyms": [], "severity": 9},
    {"name": "Acute liver failure", "synonyms": [], "severity": 10},
    {
        "name": "Acute lymphoblastic leukemia",
        "synonyms": ["Acute lymphocytic leukemia"],
        "severity": 10,
    },
    {"name": "Acute lymphocytic leukemia", "synonyms": [], "severity": 10},
    {
        "name": "Acute myeloblastic leukemia",
        "synonyms": ["Acute myelogenous leukemia"],
        "severity": 10,
    },
    {"name": "Acute myelogenous leukemia", "synonyms": [], "severity": 10},
    {
        "name": "Acute myeloid leukemia",
        "synonyms": ["Acute myelogenous leukemia"],
        "severity": 10,
    },
    {
        "name": "Acute nonlymphocytic leukemia",
        "synonyms": ["Acute myelogenous leukemia"],
        "severity": 10,
    },
    {
        "name": "Acute radiation sickness",
        "synonyms": ["Radiation sickness"],
        "severity": 10,
    },
    {
        "name": "Acute radiation syndrome",
        "synonyms": ["Radiation sickness"],
        "severity": 10,
    },
    {"name": "Acute renal failure", "synonyms": ["Acute kidney injury"], "severity": 9},
    {
        "name": "Acute respiratory distress syndrome",
        "synonyms": ["ARDS"],
        "severity": 9,
    },
    {"name": "Acute sinusitis", "synonyms": [], "severity": 4},
    {"name": "Addiction, alcohol", "synonyms": ["Alcohol use disorder"], "severity": 7},
    {"name": "Addiction, gambling", "synonyms": ["Compulsive gambling"], "severity": 7},
    {"name": "Addiction, nicotine", "synonyms": ["Nicotine dependence"], "severity": 7},
    {"name": "Addison's disease", "synonyms": [], "severity": 8},
    {
        "name": "Adenitis, mesenteric",
        "synonyms": ["Mesenteric lymphadenitis"],
        "severity": 6,
    },
    {"name": "Adenomyosis", "synonyms": [], "severity": 6},
    {
        "name": "ADHD in children",
        "synonyms": ["Attention-deficit/hyperactivity disorder (ADHD) in children"],
        "severity": 6,
    },
    {
        "name": "ADHD, Adult",
        "synonyms": ["Adult attention-deficit/hyperactivity disorder (ADHD)"],
        "severity": 6,
    },
    {"name": "Adhesive capsulitis", "synonyms": ["Frozen shoulder"], "severity": 5},
    {"name": "Adjustment disorders", "synonyms": [], "severity": 6},
    {"name": "Adnexal tumors", "synonyms": [], "severity": 7},
    {
        "name": "Adolescent schizophrenia",
        "synonyms": ["Childhood schizophrenia"],
        "severity": 8,
    },
    {"name": "Adrenal cancer", "synonyms": [], "severity": 9},
    {"name": "Adrenal mass", "synonyms": ["Benign adrenal tumors"], "severity": 6},
    {"name": "Adrenoleukodystrophy", "synonyms": [], "severity": 10},
    {
        "name": "Adult attention-deficit/hyperactivity disorder (ADHD)",
        "synonyms": [],
        "severity": 6,
    },
    {"name": "Adult Still disease", "synonyms": [], "severity": 8},
    {"name": "AFM", "synonyms": ["Acute flaccid myelitis (AFM)"], "severity": 8},
    {"name": "Age spots", "synonyms": ["Liver spots"], "severity": 3},
    {
        "name": "Age-related macular degeneration, dry",
        "synonyms": ["Dry macular degeneration"],
        "severity": 6,
    },
    {
        "name": "Age-related macular degeneration, wet",
        "synonyms": ["Wet macular degeneration"],
        "severity": 7,
    },
    {
        "name": "Agnogenic myeloid metaplasia",
        "synonyms": ["Myelofibrosis"],
        "severity": 9,
    },
    {"name": "Agoraphobia", "synonyms": [], "severity": 6},
    {"name": "AIDP", "synonyms": ["Guillain-Barre syndrome"], "severity": 8},
    {"name": "AIDS/HIV", "synonyms": [], "severity": 10},
    {"name": "Airplane ear", "synonyms": ["Barotitis media"], "severity": 4},
    {"name": "Albinism", "synonyms": [], "severity": 5},
    {"name": "Alcohol addiction", "synonyms": ["Alcohol use disorder"], "severity": 7},
    {"name": "Alcohol intolerance", "synonyms": [], "severity": 4},
    {"name": "Alcohol poisoning", "synonyms": [], "severity": 10},
    {"name": "Alcohol use disorder", "synonyms": [], "severity": 7},
    {
        "name": "Alcohol-associated hepatitis",
        "synonyms": ["Alcoholic hepatitis"],
        "severity": 9,
    },
    {"name": "Alcoholic hepatitis", "synonyms": [], "severity": 9},
    {
        "name": "Allergic granulomatosis",
        "synonyms": ["Churg-Strauss syndrome"],
        "severity": 7,
    },
    {"name": "Allergic rhinitis", "synonyms": ["Hay fever"], "severity": 4},
    {"name": "Allergies", "synonyms": [], "severity": 4},
    {"name": "Allergy, dust mite", "synonyms": ["Dust mite allergy"], "severity": 5},
    {"name": "Allergy, egg", "synonyms": ["Egg allergy"], "severity": 6},
    {"name": "Allergy, food", "synonyms": [], "severity": 6},
    {"name": "Allergy, latex", "synonyms": ["Latex allergy"], "severity": 6},
    {"name": "Allergy, milk", "synonyms": ["Milk allergy"], "severity": 6},
    {"name": "Allergy, mold", "synonyms": ["Mold allergy"], "severity": 5},
    {"name": "Allergy, nickel", "synonyms": ["Nickel allergy"], "severity": 5},
    {"name": "Allergy, peanut", "synonyms": ["Peanut allergy"], "severity": 7},
    {"name": "Allergy, penicillin", "synonyms": ["Penicillin allergy"], "severity": 7},
    {"name": "Allergy, pet", "synonyms": ["Pet allergy"], "severity": 6},
    {"name": "Allergy, shellfish", "synonyms": ["Shellfish allergy"], "severity": 7},
    {"name": "Allergy, wheat", "synonyms": ["Wheat allergy"], "severity": 6},
    {"name": "Alopecia", "synonyms": ["Hair loss"], "severity": 5},
    {
        "name": "ALS",
        "synonyms": ["Amyotrophic lateral sclerosis (ALS)"],
        "severity": 10,
    },
    {"name": "Alveolar osteitis", "synonyms": ["Dry socket"], "severity": 4},
    {"name": "Alzheimer's disease", "synonyms": [], "severity": 9},
    {"name": "Ambiguous genitalia", "synonyms": [], "severity": 6},
    {"name": "Amblyopia", "synonyms": ["Lazy eye (amblyopia)"], "severity": 6},
    {"name": "Ameloblastoma", "synonyms": [], "severity": 7},
    {"name": "Amenorrhea", "synonyms": [], "severity": 6},
    {"name": "American trypanosomiasis", "synonyms": ["Chagas disease"], "severity": 8},
    {"name": "Amnesia", "synonyms": [], "severity": 5},
    {
        "name": "Amnesia, transient global",
        "synonyms": ["Transient global amnesia"],
        "severity": 6,
    },
    {"name": "Amnestic syndrome", "synonyms": ["Amnesia"], "severity": 5},
    {"name": "Ampullary cancer", "synonyms": [], "severity": 8},
    {"name": "Amyloid disease", "synonyms": ["Amyloidosis"], "severity": 9},
    {"name": "Amyloidosis", "synonyms": [], "severity": 9},
    {
        "name": "Amyotrophic lateral sclerosis (ALS)",
        "synonyms": ["ALS"],
        "severity": 10,
    },
    {"name": "Anal cancer", "synonyms": [], "severity": 9},
    {"name": "Anal fissure", "synonyms": [], "severity": 4},
    {"name": "Anal fistula", "synonyms": [], "severity": 7},
    {"name": "Anal itching", "synonyms": ["Pruritis ani"], "severity": 4},
    {"name": "Anaphylaxis", "synonyms": [], "severity": 10},
    {"name": "Anemia", "synonyms": [], "severity": 5},
    {"name": "Anemia, aplastic", "synonyms": ["Aplastic anemia"], "severity": 9},
    {"name": "Anemia, Cooley's", "synonyms": ["Thalassemia"], "severity": 9},
    {
        "name": "Anemia, iron deficiency",
        "synonyms": ["Iron deficiency anemia"],
        "severity": 6,
    },
    {"name": "Anemia, Mediterranean", "synonyms": ["Thalassemia"], "severity": 9},
    {"name": "Anemia, sickle cell", "synonyms": ["Sickle cell anemia"], "severity": 9},
    {
        "name": "Anemia, vitamin deficiency",
        "synonyms": ["Vitamin deficiency anemia"],
        "severity": 6,
    },
    {
        "name": "Aneurysm, abdominal aortic",
        "synonyms": ["Abdominal aortic aneurysm"],
        "severity": 9,
    },
    {"name": "Aneurysm, aortic", "synonyms": [], "severity": 9},
    {"name": "Aneurysm, brain", "synonyms": ["Brain aneurysm"], "severity": 9},
    {"name": "Aneurysm, cerebral", "synonyms": ["Brain aneurysm"], "severity": 9},
    {"name": "Aneurysm, popliteal", "synonyms": [], "severity": 9},
    {
        "name": "Aneurysm, thoracic aortic",
        "synonyms": ["Thoracic aortic aneurysm"],
        "severity": 9,
    },
    {"name": "Aneurysms", "synonyms": [], "severity": 9},
    {"name": "Angelman syndrome", "synonyms": [], "severity": 8},
    {"name": "Angiitis", "synonyms": ["Vasculitis"], "severity": 8},
    {"name": "Angina", "synonyms": ["Angina pectoris"], "severity": 8},
    {
        "name": "Angioedema and hives",
        "synonyms": ["Hives and angioedema"],
        "severity": 6,
    },
    {
        "name": "Angiofollicular lymph node hyperplasia",
        "synonyms": ["Castleman disease"],
        "severity": 8,
    },
    {"name": "Angiosarcoma", "synonyms": [], "severity": 9},
    {"name": "Ankle fracture", "synonyms": ["Broken ankle"], "severity": 7},
    {"name": "Ankle sprain", "synonyms": ["Sprained ankle"], "severity": 6},
    {
        "name": "Ankyloglossia",
        "synonyms": ["Tongue-tie (ankyloglossia)"],
        "severity": 4,
    },
    {"name": "Ankylosing spondylitis", "synonyms": [], "severity": 8},
    {"name": "Anorexia", "synonyms": ["Anorexia nervosa"], "severity": 9},
    {"name": "Anorexia nervosa", "synonyms": [], "severity": 9},
    {"name": "Anorgasmia in women", "synonyms": [], "severity": 7},
    {
        "name": "Anterior cruciate ligament injury",
        "synonyms": ["ACL injury"],
        "severity": 8,
    },
    {
        "name": "Anterior vaginal prolapse",
        "synonyms": ["Anterior vaginal prolapse (cystocele)"],
        "severity": 6,
    },
    {"name": "Anthrax", "synonyms": [], "severity": 10},
    {
        "name": "Antibiotic-associated colitis",
        "synonyms": ["Pseudomembranous colitis"],
        "severity": 8,
    },
    {"name": "Antibiotic-associated diarrhea", "synonyms": [], "severity": 7},
    {"name": "Antiphospholipid syndrome", "synonyms": [], "severity": 9},
    {"name": "Antisocial personality disorder", "synonyms": [], "severity": 7},
    {
        "name": "Anxiety disorder, generalized",
        "synonyms": ["Generalized anxiety disorder"],
        "severity": 6,
    },
    {"name": "Anxiety disorders", "synonyms": [], "severity": 6},
    {"name": "Aorta stenosis", "synonyms": [], "severity": 8},
    {"name": "Aortic aneurysm", "synonyms": [], "severity": 9},
    {"name": "Aortic dissection", "synonyms": [], "severity": 10},
    {"name": "Aortic stenosis", "synonyms": [], "severity": 8},
    {"name": "Aortic dissection", "synonyms": [], "severity": 10},
    {"name": "Aphasia", "synonyms": [], "severity": 7},
    {"name": "Apnea", "synonyms": ["Sleep apnea"], "severity": 7},
    {"name": "Aplastic anemia", "synonyms": [], "severity": 9},
    {"name": "Appendicitis", "synonyms": [], "severity": 7},
    {"name": "Arrhythmia", "synonyms": [], "severity": 7},
    {"name": "Arterial thrombosis", "synonyms": [], "severity": 8},
    {"name": "Arteritis", "synonyms": ["Vasculitis"], "severity": 8},
    {"name": "Arthritis", "synonyms": [], "severity": 6},
    {"name": "Arthritis, juvenile", "synonyms": ["Juvenile arthritis"], "severity": 6},
    {
        "name": "Arthritis, osteoarthritis",
        "synonyms": ["Osteoarthritis"],
        "severity": 7,
    },
    {"name": "Arthritis, rheumatoid", "synonyms": [], "severity": 8},
    {"name": "Arthritis, psoriatic", "synonyms": [], "severity": 7},
    {"name": "Arthroscopy", "synonyms": [], "severity": 4},
    {"name": "Asbestosis", "synonyms": [], "severity": 9},
    {"name": "Aspiration pneumonia", "synonyms": [], "severity": 8},
    {"name": "Asperger's syndrome", "synonyms": [], "severity": 6},
    {"name": "Asthma", "synonyms": [], "severity": 6},
    {"name": "Astigmatism", "synonyms": [], "severity": 5},
    {"name": "Atherosclerosis", "synonyms": [], "severity": 8},
    {"name": "Atopic dermatitis", "synonyms": ["Eczema"], "severity": 6},
    {"name": "Atrophy", "synonyms": [], "severity": 7},
    {"name": "Autism", "synonyms": [], "severity": 6},
    {"name": "Autoimmune disease", "synonyms": [], "severity": 8},
    {"name": "Autonomic dysfunction", "synonyms": [], "severity": 7},
    {"name": "Avascular necrosis", "synonyms": [], "severity": 8},
    {"name": "Axillary hyperhidrosis", "synonyms": [], "severity": 3},
    {"name": "Babesiosis", "synonyms": [], "severity": 8},
    {"name": "Bacterial vaginosis", "synonyms": [], "severity": 5},
    {"name": "Barrett's esophagus", "synonyms": [], "severity": 8},
    {"name": "Bartonella infection", "synonyms": [], "severity": 7},
    {"name": "Basal cell carcinoma", "synonyms": [], "severity": 7},
    {"name": "Berylliosis", "synonyms": [], "severity": 9},
    {"name": "Bile duct cancer", "synonyms": [], "severity": 9},
    {"name": "Biliary atresia", "synonyms": [], "severity": 8},
    {"name": "Bipolar disorder", "synonyms": [], "severity": 8},
    {"name": "Bladder cancer", "synonyms": [], "severity": 9},
    {"name": "Blepharitis", "synonyms": [], "severity": 5},
    {"name": "Blindness", "synonyms": [], "severity": 9},
    {"name": "Blood clot", "synonyms": [], "severity": 8},
    {"name": "Blood poisoning", "synonyms": ["Sepsis"], "severity": 10},
    {"name": "Blount's disease", "synonyms": [], "severity": 6},
    {"name": "Bowel cancer", "synonyms": [], "severity": 9},
    {"name": "Brachial plexus injury", "synonyms": [], "severity": 8},
    {"name": "Breast cancer", "synonyms": [], "severity": 9},
    {"name": "Bronchitis", "synonyms": [], "severity": 5},
    {"name": "Bronchiectasis", "synonyms": [], "severity": 7},
    {"name": "Bronchiolitis", "synonyms": [], "severity": 5},
    {"name": "Bronchopulmonary dysplasia", "synonyms": [], "severity": 7},
    {"name": "Buerger's disease", "synonyms": [], "severity": 8},
    {"name": "Bulimia", "synonyms": [], "severity": 9},
    {"name": "Bursitis", "synonyms": [], "severity": 6},
    {"name": "Candidiasis", "synonyms": [], "severity": 5},
    {"name": "Carcinoma", "synonyms": [], "severity": 9},
    {"name": "Cardiac arrest", "synonyms": [], "severity": 10},
    {"name": "Cardiomyopathy", "synonyms": [], "severity": 9},
    {"name": "Cataracts", "synonyms": [], "severity": 6},
    {"name": "Celiac disease", "synonyms": [], "severity": 7},
    {"name": "Cellulitis", "synonyms": [], "severity": 6},
    {"name": "Cerebral palsy", "synonyms": [], "severity": 9},
    {"name": "Cervical cancer", "synonyms": [], "severity": 9},
    {"name": "Cervical spondylosis", "synonyms": [], "severity": 7},
    {"name": "Chagas disease", "synonyms": [], "severity": 8},
    {"name": "Charcot-Marie-Tooth disease", "synonyms": [], "severity": 8},
    {"name": "Chest pain", "synonyms": [], "severity": 6},
    {"name": "Chickenpox", "synonyms": [], "severity": 5},
    {"name": "Chronic acid reflux", "synonyms": ["Chronic GERD"], "severity": 7},
    {"name": "Chronic back pain", "synonyms": [], "severity": 6},
    {"name": "Chronic bronchitis", "synonyms": [], "severity": 7},
    {"name": "Chronic constipation", "synonyms": [], "severity": 5},
    {
        "name": "Chronic obstructive pulmonary disease (COPD)",
        "synonyms": [],
        "severity": 9,
    },
    {"name": "Chronic pain syndrome", "synonyms": [], "severity": 6},
    {"name": "Chronic pancreatitis", "synonyms": [], "severity": 8},
    {
        "name": "Chronic renal failure",
        "synonyms": ["Chronic kidney disease"],
        "severity": 9,
    },
    {"name": "Chronic sinusitis", "synonyms": [], "severity": 6},
    {"name": "Cirrhosis", "synonyms": [], "severity": 9},
    {"name": "Cleft lip", "synonyms": [], "severity": 7},
    {"name": "Cleft palate", "synonyms": [], "severity": 7},
    {"name": "Cluster headaches", "synonyms": [], "severity": 6},
    {"name": "Coccidioidomycosis", "synonyms": ["Valley fever"], "severity": 8},
    {"name": "Colitis", "synonyms": [], "severity": 7},
    {"name": "Colorectal cancer", "synonyms": [], "severity": 9},
    {"name": "Congenital heart disease", "synonyms": [], "severity": 9},
    {"name": "Congestive heart failure", "synonyms": [], "severity": 9},
    {"name": "Connective tissue disease", "synonyms": [], "severity": 8},
    {"name": "Constipation", "synonyms": [], "severity": 5},
    {
        "name": "COPD",
        "synonyms": ["Chronic obstructive pulmonary disease"],
        "severity": 9,
    },
    {"name": "Coronary artery disease", "synonyms": [], "severity": 9},
    {"name": "Cough", "synonyms": [], "severity": 4},
    {"name": "Croup", "synonyms": [], "severity": 5},
    {"name": "Cystic fibrosis", "synonyms": [], "severity": 9},
    {"name": "Cystitis", "synonyms": [], "severity": 6},
    {"name": "Cytomegalovirus", "synonyms": [], "severity": 7},
    {"name": "Dandruff", "synonyms": [], "severity": 3},
    {"name": "Dandruff, seborrheic", "synonyms": [], "severity": 3},
    {"name": "Dengue fever", "synonyms": [], "severity": 8},
    {"name": "Depression", "synonyms": [], "severity": 8},
    {"name": "Dermatitis", "synonyms": [], "severity": 5},
    {"name": "Diabetes", "synonyms": [], "severity": 8},
    {"name": "Diabetes type 1", "synonyms": [], "severity": 9},
    {"name": "Diabetes type 2", "synonyms": [], "severity": 8},
    {"name": "Diabetic neuropathy", "synonyms": [], "severity": 8},
    {"name": "Diabetic retinopathy", "synonyms": [], "severity": 8},
    {"name": "Diabetic foot ulcer", "synonyms": [], "severity": 8},
    {"name": "Diarrhea", "synonyms": [], "severity": 5},
    {"name": "Dialysis", "synonyms": [], "severity": 9},
    {"name": "Diphtheria", "synonyms": [], "severity": 10},
    {"name": "Discoid lupus erythematosus", "synonyms": [], "severity": 7},
    {"name": "Diverticulitis", "synonyms": [], "severity": 7},
    {"name": "Diverticulosis", "synonyms": [], "severity": 6},
    {"name": "Dizziness", "synonyms": [], "severity": 5},
    {"name": "Down syndrome", "synonyms": [], "severity": 9},
    {"name": "Dysphagia", "synonyms": [], "severity": 6},
    {"name": "Dystonia", "synonyms": [], "severity": 8},
    {"name": "Eczema", "synonyms": [], "severity": 6},
    {"name": "Endometriosis", "synonyms": [], "severity": 8},
    {"name": "Epilepsy", "synonyms": [], "severity": 7},
    {"name": "Esophageal cancer", "synonyms": [], "severity": 9},
    {"name": "Esophageal reflux", "synonyms": [], "severity": 5},
    {"name": "Essential tremor", "synonyms": [], "severity": 7},
    {"name": "Ewing's sarcoma", "synonyms": [], "severity": 9},
    {"name": "Exophthalmos", "synonyms": [], "severity": 5},
    {"name": "Extradural hematoma", "synonyms": [], "severity": 8},
    {"name": "Fainting", "synonyms": [], "severity": 4},
    {"name": "Fatigue", "synonyms": [], "severity": 5},
    {"name": "Fibromyalgia", "synonyms": [], "severity": 7},
    {"name": "Fibrosis", "synonyms": [], "severity": 7},
    {"name": "Gallbladder disease", "synonyms": [], "severity": 8},
    {"name": "Gastritis", "synonyms": [], "severity": 5},
    {"name": "Gastroenteritis", "synonyms": [], "severity": 5},
    {"name": "Gastroesophageal reflux disease", "synonyms": ["GERD"], "severity": 7},
    {"name": "Gastroparesis", "synonyms": [], "severity": 7},
    {"name": "Gastrostomy", "synonyms": [], "severity": 4},
    {"name": "Gingivitis", "synonyms": [], "severity": 5},
    {"name": "Glaucoma", "synonyms": [], "severity": 7},
    {"name": "Gout", "synonyms": [], "severity": 6},
    {"name": "Graves' disease", "synonyms": [], "severity": 8},
    {"name": "Guillain-Barré syndrome", "synonyms": [], "severity": 8},
    {"name": "Gynocomastia", "synonyms": [], "severity": 5},
    {"name": "H. pylori infection", "synonyms": [], "severity": 6},
    {"name": "Hair loss", "synonyms": [], "severity": 4},
    {"name": "Hand, foot, and mouth disease", "synonyms": [], "severity": 5},
    {"name": "Hansen's disease", "synonyms": ["Leprosy"], "severity": 8},
    {"name": "Hearing loss", "synonyms": [], "severity": 7},
    {"name": "Heart attack", "synonyms": ["Myocardial infarction"], "severity": 10},
    {"name": "Heart failure", "synonyms": [], "severity": 9},
    {"name": "Hemorrhagic stroke", "synonyms": [], "severity": 10},
    {"name": "Hepatitis", "synonyms": [], "severity": 9},
    {"name": "Hepatitis A", "synonyms": [], "severity": 9},
    {"name": "Hepatitis B", "synonyms": [], "severity": 9},
    {"name": "Hepatitis C", "synonyms": [], "severity": 9},
    {"name": "Hepatitis D", "synonyms": [], "severity": 9},
    {"name": "Hepatitis E", "synonyms": [], "severity": 9},
    {"name": "Herpes", "synonyms": [], "severity": 7},
    {"name": "Herpes simplex", "synonyms": [], "severity": 7},
    {"name": "Herpes zoster", "synonyms": ["Shingles"], "severity": 7},
    {"name": "Hodgkin's lymphoma", "synonyms": [], "severity": 9},
    {"name": "Holi syndrome", "synonyms": [], "severity": 7},
    {"name": "Homocystinuria", "synonyms": [], "severity": 9},
    {"name": "Hormonal imbalance", "synonyms": [], "severity": 6},
    {"name": "Hypercalcemia", "synonyms": [], "severity": 8},
    {"name": "Hypercholesterolemia", "synonyms": [], "severity": 7},
    {"name": "Hyperhidrosis", "synonyms": [], "severity": 3},
    {"name": "Hyperkalemia", "synonyms": [], "severity": 9},
    {"name": "Hypertension", "synonyms": [], "severity": 8},
    {"name": "Hyperthyroidism", "synonyms": [], "severity": 8},
    {"name": "Hypocalcemia", "synonyms": [], "severity": 8},
    {"name": "Hypoglycemia", "synonyms": [], "severity": 8},
    {"name": "Hypothyroidism", "synonyms": [], "severity": 8},
    {"name": "Hysterectomy", "synonyms": [], "severity": 6},
    {"name": "Ileitis", "synonyms": [], "severity": 7},
    {"name": "Impotence", "synonyms": [], "severity": 6},
    {"name": "Infections", "synonyms": [], "severity": 8},
    {"name": "Inguinal hernia", "synonyms": [], "severity": 5},
    {"name": "Insomnia", "synonyms": [], "severity": 6},
    {"name": "Intestinal cancer", "synonyms": [], "severity": 9},
    {"name": "Intestinal obstruction", "synonyms": [], "severity": 7},
    {"name": "Irritable bowel syndrome", "synonyms": [], "severity": 6},
    {"name": "Ischemic heart disease", "synonyms": [], "severity": 9},
    {"name": "Ischemic stroke", "synonyms": [], "severity": 10},
    {"name": "Jaundice", "synonyms": [], "severity": 7},
    {"name": "Kidney disease", "synonyms": [], "severity": 9},
    {"name": "Kidney failure", "synonyms": [], "severity": 9},
    {"name": "Knee injury", "synonyms": [], "severity": 6},
    {"name": "Labyrinthitis", "synonyms": [], "severity": 6},
    {"name": "Lactose intolerance", "synonyms": [], "severity": 5},
    {"name": "Laryngeal cancer", "synonyms": [], "severity": 9},
    {"name": "Laryngitis", "synonyms": [], "severity": 5},
    {"name": "Leukemia", "synonyms": [], "severity": 9},
    {"name": "Leukopenia", "synonyms": [], "severity": 7},
    {"name": "Lipoma", "synonyms": [], "severity": 6},
    {"name": "Liver disease", "synonyms": [], "severity": 9},
    {"name": "Liver failure", "synonyms": [], "severity": 9},
    {"name": "Lung cancer", "synonyms": [], "severity": 9},
    {"name": "Lung disease", "synonyms": [], "severity": 8},
    {"name": "Lung infection", "synonyms": [], "severity": 7},
    {"name": "Lupus", "synonyms": [], "severity": 9},
    {"name": "Lymphoma", "synonyms": [], "severity": 9},
    {"name": "Macerated skin", "synonyms": [], "severity": 4},
    {"name": "Malaria", "synonyms": [], "severity": 9},
    {"name": "Mastitis", "synonyms": [], "severity": 6},
    {"name": "Melanoma", "synonyms": [], "severity": 9},
    {"name": "Menopause", "synonyms": [], "severity": 6},
    {"name": "Meningitis", "synonyms": [], "severity": 9},
    {"name": "Meningococcal disease", "synonyms": [], "severity": 10},
    {"name": "Metastasis", "synonyms": [], "severity": 10},
    {"name": "Migraine", "synonyms": [], "severity": 6},
    {"name": "Multiple sclerosis", "synonyms": [], "severity": 9},
    {"name": "Multiple myeloma", "synonyms": [], "severity": 9},
    {"name": "Myasthenia gravis", "synonyms": [], "severity": 8},
    {"name": "Myocardial infarction", "synonyms": ["Heart attack"], "severity": 10},
    {"name": "Myopia", "synonyms": [], "severity": 5},
    {"name": "Narcolepsy", "synonyms": [], "severity": 7},
    {"name": "Nasal polyps", "synonyms": [], "severity": 5},
    {"name": "Nasopharyngeal cancer", "synonyms": [], "severity": 9},
    {"name": "Neck pain", "synonyms": [], "severity": 5},
    {"name": "Nerve damage", "synonyms": [], "severity": 8},
    {"name": "Neurofibromatosis", "synonyms": [], "severity": 9},
    {"name": "Neurosyphilis", "synonyms": [], "severity": 9},
    {"name": "Osteoarthritis", "synonyms": [], "severity": 7},
    {"name": "Osteoporosis", "synonyms": [], "severity": 7},
    {"name": "Otitis media", "synonyms": [], "severity": 5},
    {"name": "Ovarian cancer", "synonyms": [], "severity": 9},
    {"name": "Parkinson's disease", "synonyms": [], "severity": 8},
    {"name": "Pneumonia", "synonyms": [], "severity": 8},
    {"name": "Polycystic kidney disease", "synonyms": [], "severity": 9},
    {"name": "Prostate cancer", "synonyms": [], "severity": 9},
    {"name": "Psoriasis", "synonyms": [], "severity": 6},
    {"name": "Pulmonary embolism", "synonyms": [], "severity": 9},
    {"name": "Pulmonary fibrosis", "synonyms": [], "severity": 8},
    {"name": "Raynaud's disease", "synonyms": [], "severity": 7},
    {"name": "Rheumatoid arthritis", "synonyms": [], "severity": 8},
    {"name": "Rickets", "synonyms": [], "severity": 7},
    {"name": "SARS", "synonyms": [], "severity": 9},
    {"name": "Schizophrenia", "synonyms": [], "severity": 9},
    {"name": "Sepsis", "synonyms": [], "severity": 10},
    {"name": "Shingles", "synonyms": [], "severity": 7},
    {"name": "Sinus infection", "synonyms": [], "severity": 5},
    {"name": "Sinusitis", "synonyms": [], "severity": 5},
    {"name": "Sickle cell anemia", "synonyms": [], "severity": 9},
    {"name": "Sleep apnea", "synonyms": [], "severity": 7},
    {"name": "Sleep disorders", "synonyms": [], "severity": 6},
    {"name": "Spinal cord injury", "synonyms": [], "severity": 8},
    {"name": "Spondylosis", "synonyms": [], "severity": 6},
    {"name": "Stroke", "synonyms": [], "severity": 10},
    {"name": "Systemic lupus erythematosus", "synonyms": [], "severity": 9},
    {"name": "Tachycardia", "synonyms": [], "severity": 7},
    {"name": "Tuberculosis", "synonyms": [], "severity": 9},
    {"name": "Ulcerative colitis", "synonyms": [], "severity": 8},
    {"name": "Urinary tract infection", "synonyms": [], "severity": 5},
    {"name": "Uterine cancer", "synonyms": [], "severity": 9},
    {"name": "Vertigo", "synonyms": [], "severity": 6},
    {"name": "Viral infection", "synonyms": [], "severity": 7},
    {"name": "Viral meningitis", "synonyms": [], "severity": 8},
    {"name": "Vitiligo", "synonyms": [], "severity": 5},
    {"name": "Warts", "synonyms": [], "severity": 4},
    {"name": "Whiplash", "synonyms": [], "severity": 6},
    {"name": "Zika virus", "synonyms": [], "severity": 8},
]

ALL_DISEASE_NAMES = [d["name"] for d in ALL_DISEASES_WITH_SEVERITY]

ALL_SYMPTOMS_WITH_SEVERITY = [
    {"symptom": "itching", "severity": 6},
    {"symptom": "skin rash", "severity": 7},
    {"symptom": "nodal skin eruptions", "severity": 7},
    {"symptom": "continuous sneezing", "severity": 5},
    {"symptom": "shivering", "severity": 6},
    {"symptom": "chills", "severity": 6},
    {"symptom": "joint pain", "severity": 7},
    {"symptom": "stomach pain", "severity": 7},
    {"symptom": "acidity", "severity": 5},
    {"symptom": "ulcers on tongue", "severity": 6},
    {"symptom": "muscle wasting", "severity": 8},
    {"symptom": "vomiting", "severity": 7},
    {"symptom": "burning micturition", "severity": 6},
    {"symptom": "spotting urination", "severity": 5},
    {"symptom": "fatigue", "severity": 7},
    {"symptom": "weight gain", "severity": 5},
    {"symptom": "anxiety", "severity": 8},
    {"symptom": "cold hands and feet", "severity": 6},
    {"symptom": "mood swings", "severity": 7},
    {"symptom": "weight loss", "severity": 8},
    {"symptom": "restlessness", "severity": 7},
    {"symptom": "lethargy", "severity": 7},
    {"symptom": "patches in throat", "severity": 6},
    {"symptom": "irregular sugar level", "severity": 8},
    {"symptom": "cough", "severity": 6},
    {"symptom": "high fever", "severity": 8},
    {"symptom": "sunken eyes", "severity": 7},
    {"symptom": "breathlessness", "severity": 9},
    {"symptom": "sweating", "severity": 6},
    {"symptom": "dehydration", "severity": 8},
    {"symptom": "indigestion", "severity": 5},
    {"symptom": "headache", "severity": 6},
    {"symptom": "yellowish skin", "severity": 8},
    {"symptom": "dark urine", "severity": 7},
    {"symptom": "nausea", "severity": 6},
    {"symptom": "loss of appetite", "severity": 7},
    {"symptom": "pain behind the eyes", "severity": 7},
    {"symptom": "back pain", "severity": 7},
    {"symptom": "constipation", "severity": 6},
    {"symptom": "abdominal pain", "severity": 7},
    {"symptom": "diarrhea", "severity": 6},
    {"symptom": "mild fever", "severity": 5},
    {"symptom": "yellow urine", "severity": 7},
    {"symptom": "yellowing of eyes", "severity": 8},
    {"symptom": "acute liver failure", "severity": 10},
    {"symptom": "fluid overload", "severity": 9},
    {"symptom": "swelling of stomach", "severity": 8},
    {"symptom": "swelled lymph nodes", "severity": 7},
    {"symptom": "malaise", "severity": 6},
    {"symptom": "blurred and distorted vision", "severity": 7},
    {"symptom": "phlegm", "severity": 6},
    {"symptom": "throat irritation", "severity": 5},
    {"symptom": "redness of eyes", "severity": 6},
    {"symptom": "sinus pressure", "severity": 6},
    {"symptom": "runny nose", "severity": 5},
    {"symptom": "congestion", "severity": 6},
    {"symptom": "chest pain", "severity": 9},
    {"symptom": "weakness in limbs", "severity": 7},
    {"symptom": "fast heart rate", "severity": 8},
    {"symptom": "pain during bowel movements", "severity": 7},
    {"symptom": "pain in anal region", "severity": 6},
    {"symptom": "bloody stool", "severity": 8},
    {"symptom": "irritation in anus", "severity": 6},
    {"symptom": "neck pain", "severity": 7},
    {"symptom": "dizziness", "severity": 6},
    {"symptom": "cramps", "severity": 6},
    {"symptom": "bruising", "severity": 6},
    {"symptom": "obesity", "severity": 7},
    {"symptom": "swollen legs", "severity": 8},
    {"symptom": "swollen blood vessels", "severity": 7},
    {"symptom": "puffy face and eyes", "severity": 6},
    {"symptom": "enlarged thyroid", "severity": 7},
    {"symptom": "brittle nails", "severity": 5},
    {"symptom": "swollen extremities", "severity": 8},
    {"symptom": "excessive hunger", "severity": 6},
    {"symptom": "extra marital contacts", "severity": 5},
    {"symptom": "drying and tingling lips", "severity": 6},
    {"symptom": "slurred speech", "severity": 7},
    {"symptom": "knee pain", "severity": 6},
    {"symptom": "hip joint pain", "severity": 7},
    {"symptom": "muscle weakness", "severity": 8},
    {"symptom": "stiff neck", "severity": 7},
    {"symptom": "swelling joints", "severity": 7},
    {"symptom": "movement stiffness", "severity": 8},
    {"symptom": "spinning movements", "severity": 6},
    {"symptom": "loss of balance", "severity": 8},
    {"symptom": "unsteadiness", "severity": 7},
    {"symptom": "weakness of one body side", "severity": 9},
    {"symptom": "loss of smell", "severity": 7},
    {"symptom": "bladder discomfort", "severity": 6},
    {"symptom": "foul smell of urine", "severity": 6},
    {"symptom": "continuous feel of urine", "severity": 5},
    {"symptom": "passage of gases", "severity": 5},
    {"symptom": "internal itching", "severity": 6},
    {"symptom": "toxic look (typhos)", "severity": 9},
    {"symptom": "depression", "severity": 9},
    {"symptom": "irritability", "severity": 7},
    {"symptom": "muscle pain", "severity": 7},
    {"symptom": "altered sensorium", "severity": 9},
    {"symptom": "red spots over body", "severity": 6},
    {"symptom": "belly pain", "severity": 7},
    {"symptom": "abnormal menstruation", "severity": 7},
    {"symptom": "dischromic patches", "severity": 6},
    {"symptom": "watering from eyes", "severity": 5},
    {"symptom": "increased appetite", "severity": 6},
    {"symptom": "polyuria", "severity": 7},
    {"symptom": "family history", "severity": 5},
    {"symptom": "mucoid sputum", "severity": 6},
    {"symptom": "rusty sputum", "severity": 7},
    {"symptom": "lack of concentration", "severity": 7},
    {"symptom": "visual disturbances", "severity": 8},
    {"symptom": "receiving blood transfusion", "severity": 6},
    {"symptom": "receiving unsterile injections", "severity": 7},
    {"symptom": "coma", "severity": 10},
    {"symptom": "stomach bleeding", "severity": 10},
    {"symptom": "distention of abdomen", "severity": 8},
    {"symptom": "history of alcohol consumption", "severity": 6},
    {"symptom": "blood in sputum", "severity": 9},
    {"symptom": "prominent veins on calf", "severity": 7},
    {"symptom": "palpitations", "severity": 8},
    {"symptom": "painful walking", "severity": 7},
    {"symptom": "pus filled pimples", "severity": 6},
    {"symptom": "blackheads", "severity": 5},
    {"symptom": "scarring", "severity": 6},
    {"symptom": "skin peeling", "severity": 7},
    {"symptom": "silver like dusting", "severity": 6},
    {"symptom": "small dents in nails", "severity": 6},
    {"symptom": "inflammatory nails", "severity": 7},
    {"symptom": "blister", "severity": 7},
    {"symptom": "red sore around nose", "severity": 6},
    {"symptom": "yellow crust ooze", "severity": 7},
    {"symptom": "prognosis", "severity": 9},
    {"symptom": "low-grade fever", "severity": 5},
    {"symptom": "hot flashes", "severity": 7},
    {"symptom": "insomnia", "severity": 8},
    {"symptom": "sleep disturbances", "severity": 7},
    {"symptom": "excessive daytime sleepiness", "severity": 6},
    {"symptom": "snoring", "severity": 5},
    {"symptom": "sleep apnea", "severity": 9},
    {"symptom": "hoarseness", "severity": 7},
    {"symptom": "difficulty swallowing", "severity": 7},
    {"symptom": "dysphagia", "severity": 7},
    {"symptom": "shortness of breath on exertion", "severity": 8},
    {"symptom": "postnasal drip", "severity": 5},
    {"symptom": "ear pain", "severity": 6},
    {"symptom": "ear discharge", "severity": 7},
    {"symptom": "tinnitus", "severity": 6},
    {"symptom": "hearing loss", "severity": 8},
    {"symptom": "sore throat", "severity": 6},
    {"symptom": "abdominal bloating", "severity": 6},
    {"symptom": "flatulence", "severity": 5},
    {"symptom": "vomiting blood (hematemesis)", "severity": 10},
    {"symptom": "hematochezia (bright red stool)", "severity": 9},
    {"symptom": "melena (dark, tarry stools)", "severity": 9},
    {"symptom": "nocturia", "severity": 6},
    {"symptom": "urinary retention", "severity": 7},
    {"symptom": "urinary incontinence", "severity": 7},
    {"symptom": "hair loss (alopecia)", "severity": 6},
    {"symptom": "bald patches", "severity": 6},
    {"symptom": "hirsutism (excess facial hair in women)", "severity": 6},
    {"symptom": "sudden confusion", "severity": 9},
    {"symptom": "memory loss", "severity": 8},
    {"symptom": "forgetfulness", "severity": 7},
    {"symptom": "disorientation", "severity": 7},
    {"symptom": "hallucinations", "severity": 9},
    {"symptom": "delusions", "severity": 9},
    {"symptom": "paranoia", "severity": 8},
    {"symptom": "panic attacks", "severity": 8},
    {"symptom": "involuntary movements", "severity": 7},
    {"symptom": "tremor", "severity": 7},
    {"symptom": "resting tremor", "severity": 8},
    {"symptom": "intention tremor", "severity": 8},
    {"symptom": "numbness", "severity": 7},
    {"symptom": "tingling (paresthesia)", "severity": 7},
    {"symptom": "burning sensation", "severity": 6},
    {"symptom": "fainting (syncope)", "severity": 8},
    {"symptom": "lightheadedness", "severity": 6},
    {"symptom": "feeling faint", "severity": 6},
    {"symptom": "lack of motivation", "severity": 7},
    {"symptom": "lack of pleasure (anhedonia)", "severity": 7},
    {"symptom": "swollen glands (lymphadenopathy)", "severity": 8},
    {"symptom": "toothache", "severity": 6},
    {"symptom": "bleeding gums", "severity": 6},
    {"symptom": "gum swelling", "severity": 6},
    {"symptom": "halitosis (bad breath)", "severity": 5},
    {"symptom": "oral ulcers", "severity": 6},
    {"symptom": "canker sores", "severity": 5},
    {"symptom": "dry mouth (xerostomia)", "severity": 6},
    {"symptom": "chest tightness", "severity": 8},
    {"symptom": "wheezing", "severity": 7},
    {"symptom": "stridor", "severity": 7},
    {"symptom": "cyanosis (bluish skin/lips)", "severity": 9},
    {"symptom": "pallor (pale skin)", "severity": 7},
    {"symptom": "photophobia (light sensitivity)", "severity": 6},
    {"symptom": "double vision (diplopia)", "severity": 7},
    {"symptom": "eye pain", "severity": 7},
    {"symptom": "excessive tearing", "severity": 6},
    {"symptom": "dry eyes", "severity": 6},
    {"symptom": "floaters in vision", "severity": 7},
    {"symptom": "pelvic pain", "severity": 7},
    {"symptom": "vaginal discharge", "severity": 7},
    {"symptom": "heavy menstrual bleeding (menorrhagia)", "severity": 7},
    {"symptom": "painful periods (dysmenorrhea)", "severity": 7},
    {"symptom": "vaginal dryness", "severity": 7},
    {"symptom": "dyspareunia (pain during intercourse)", "severity": 8},
    {"symptom": "brown patches on skin (melasma)", "severity": 7},
    {"symptom": "white patches on skin (vitiligo)", "severity": 6},
    {"symptom": "involuntary muscle spasms", "severity": 8},
    {"symptom": "muscle twitching", "severity": 7},
    {"symptom": "muscle cramps", "severity": 7},
    {"symptom": "drop attacks", "severity": 9},
    {"symptom": "blackouts", "severity": 8},
    {"symptom": "seizures (convulsions)", "severity": 9},
    {"symptom": "fits", "severity": 9},
    {"symptom": "hypersomnia (excessive sleeping)", "severity": 7},
    {"symptom": "dry, scaly skin (xeroderma)", "severity": 7},
    {"symptom": "eczema", "severity": 6},
    {"symptom": "night sweats", "severity": 7},
    {"symptom": "dribbling of urine", "severity": 7},
    {"symptom": "incomplete emptying of bladder", "severity": 8},
    {"symptom": "shock (cold, clammy skin)", "severity": 10},
    {"symptom": "flattened affect", "severity": 8},
    {"symptom": "cognitive decline", "severity": 9},
    {"symptom": "compulsive behavior", "severity": 8},
    {"symptom": "obsessions", "severity": 7},
    {"symptom": "ritualistic behavior", "severity": 7},
    {"symptom": "mania (elevated mood episodes)", "severity": 9},
    {"symptom": "rapid/pressured speech", "severity": 8},
    {"symptom": "nosebleed (epistaxis)", "severity": 5},
    {"symptom": "fragile skin", "severity": 7},
    {"symptom": "skin tears", "severity": 6},
    {"symptom": "skin dryness", "severity": 7},
    {"symptom": "mole changes (ABCDE of melanoma)", "severity": 9},
    {"symptom": "fibroids (uterine)", "severity": 7},
    {"symptom": "ascites (fluid in abdomen)", "severity": 8},
    {"symptom": "lack of coordination (ataxia)", "severity": 9},
    {"symptom": "incontinence (lack of bowel or bladder control)", "severity": 9},
    {"symptom": "lack of impulse control", "severity": 8},
    {"symptom": "delirium", "severity": 9},
    {"symptom": "incoherence", "severity": 8},
    {"symptom": "fear of water (hydrophobia)", "severity": 7},
    {"symptom": "fear of closed spaces (claustrophobia)", "severity": 8},
    {"symptom": "fear of heights (acrophobia)", "severity": 8},
    {"symptom": "fear of open spaces (agoraphobia)", "severity": 8},
    {"symptom": "fear of social situations (social phobia)", "severity": 7},
    {"symptom": "fear of spiders (arachnophobia)", "severity": 7},
    {"symptom": "fear of snakes (ophidiophobia)", "severity": 7},
    {"symptom": "fear of blood (hemophobia)", "severity": 7},
    {"symptom": "fear of injections (trypanophobia)", "severity": 7},
    {"symptom": "flank pain", "severity": 7},
    {"symptom": "urethral discharge", "severity": 7},
    {"symptom": "vaginal odor", "severity": 7},
    {"symptom": "white vaginal discharge (leucorrhea)", "severity": 7},
    {"symptom": "pelvic pressure", "severity": 7},
    {"symptom": "frequent infections", "severity": 8},
    {"symptom": "hyperventilation", "severity": 7},
    {"symptom": "gasping", "severity": 7},
    {"symptom": "cold, clammy extremities", "severity": 8},
    {"symptom": "milk discharge from breasts (galactorrhea)", "severity": 7},
    {"symptom": "nipple discharge", "severity": 7},
    {"symptom": "nipple retraction", "severity": 8},
    {"symptom": "nipple pain", "severity": 7},
    {"symptom": "cracked nipples", "severity": 7},
    {"symptom": "rectal discharge", "severity": 8},
    {"symptom": "mucus in stool", "severity": 7},
    {"symptom": "anal itching (pruritus ani)", "severity": 7},
    {"symptom": "proctalgia (rectal pain)", "severity": 8},
    {"symptom": "tooth sensitivity", "severity": 7},
    {"symptom": "chapped lips", "severity": 6},
    {"symptom": "cold sores (herpes labialis)", "severity": 6},
    {"symptom": "globus sensation (lump in throat)", "severity": 7},
    {"symptom": "angina (burning chest pain)", "severity": 9},
    {"symptom": "trismus (jaw tightness)", "severity": 7},
    {"symptom": "rapid weight changes", "severity": 8},
    {"symptom": "cachexia (loss of muscle mass)", "severity": 9},
    {"symptom": "hepatomegaly (enlarged liver)", "severity": 8},
    {"symptom": "splenomegaly (enlarged spleen)", "severity": 8},
    {"symptom": "yellowish nails", "severity": 6},
    {"symptom": "blue nails", "severity": 8},
    {"symptom": "sore tongue", "severity": 7},
    {"symptom": "burning tongue (glossitis)", "severity": 7},
    {"symptom": "strawberry tongue", "severity": 8},
    {"symptom": "black hairy tongue", "severity": 7},
    {"symptom": "scalp tenderness", "severity": 7},
    {"symptom": "ear itching", "severity": 6},
    {"symptom": "ingrown nails", "severity": 7},
    {"symptom": "onychomycosis (nail fungus)", "severity": 7},
    {"symptom": "koilonychia (spoon nails)", "severity": 8},
    {"symptom": "hammer toe", "severity": 7},
    {"symptom": "bunions (hallux valgus)", "severity": 7},
    {"symptom": "corns/calluses", "severity": 7},
    {"symptom": "heel pain (heel spur)", "severity": 7},
    {"symptom": "carpal tunnel syndrome (hand numbness/pain)", "severity": 8},
    {"symptom": "Raynaud’s phenomenon (fingers turning white or blue)", "severity": 8},
    {"symptom": "photosensitivity (sun sensitivity)", "severity": 7},
    {"symptom": "milia (milk spots)", "severity": 6},
    {"symptom": "premature hair graying (canities)", "severity": 6},
    {"symptom": "paronychia (infection around nails)", "severity": 7},
    {"symptom": "onion breath", "severity": 5},
    {"symptom": "foot odor", "severity": 5},
    {"symptom": "acetone breath (keto breath)", "severity": 7},
    {"symptom": "kidney pain", "severity": 9},
    {"symptom": "penile discharge", "severity": 7},
    {"symptom": "erectile dysfunction", "severity": 8},
    {"symptom": "priapism (prolonged erection)", "severity": 9},
    {"symptom": "lack of libido", "severity": 7},
    {"symptom": "anorgasmia (lack of orgasm)", "severity": 8},
    {"symptom": "painful orgasm", "severity": 7},
    {"symptom": "lack of lubrication", "severity": 7},
    {"symptom": "fear/phobias (general)", "severity": 6},
    {"symptom": "lack of orientation to time/place/person", "severity": 9},
    {"symptom": "lack of social interaction", "severity": 9},
    {"symptom": "social withdrawal", "severity": 8},
    {"symptom": "anger outbursts", "severity": 7},
    {"symptom": "aggression", "severity": 8},
    {"symptom": "negativism", "severity": 8},
    {"symptom": "hoarding behavior", "severity": 7},
    {"symptom": "painful scalp", "severity": 6},
    {"symptom": "lack of tears (alacrima)", "severity": 7},
    {"symptom": "anhidrosis (lack of sweating)", "severity": 7},
    {"symptom": "hyperhidrosis (excessive sweating)", "severity": 8},
]

ALL_SYMPTOMS = [item["symptom"] for item in ALL_SYMPTOMS_WITH_SEVERITY]

###############################################################################
# Biobert pipeline for disease and symptom suggestions
###############################################################################
ner_pipeline = pipeline(
    "ner", model="dmis-lab/biobert-v1.1", tokenizer="dmis-lab/biobert-v1.1"
)


def get_biobert_suggestions(text):
    results = ner_pipeline(text)
    bio_diseases = []
    bio_symptoms = []
    for res in results:
        entity = res["word"].strip()
        if len(entity) > 2:
            # For demonstration, add them to both categories.
            bio_diseases.append(entity)
            bio_symptoms.append(entity)
    bio_diseases = list(set(bio_diseases))
    bio_symptoms = list(set(bio_symptoms))
    return bio_diseases, bio_symptoms


###############################################################################
# Flask app setup for web server on python and SQLAlchemy models -- i tried php SQL but this one seems easier and more features
###############################################################################
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///medical.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    other_info = db.Column(db.Text, nullable=True)
    records = db.relationship("Record", backref="patient", lazy=True)


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    disease = db.Column(db.String(200), nullable=False)
    symptoms = db.Column(db.String(500))
    severity = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)


###############################################################################
# approximate severity from diseases and symptoms strings -- mean of diseases and symptoms, we can further expand this by some sort of non-linear stuff too
# story for another day maybe
###############################################################################
def approximate_record_severity(diseases_str, symptoms_str):
    disease_list = [d.strip() for d in diseases_str.split(",") if d.strip()]
    symptom_list = [s.strip() for s in symptoms_str.split(",") if s.strip()]

    disease_severities = []
    for d in disease_list:
        match = next(
            (
                x
                for x in ALL_DISEASES_WITH_SEVERITY
                if x["name"].lower() == d.lower()
                or d.lower() in [syn.lower() for syn in x["synonyms"]]
            ),
            None,
        )
        if match:
            disease_severities.append(match["severity"])
    avg_disease_severity = (
        sum(disease_severities) / len(disease_severities) if disease_severities else 1
    )

    symptom_severities = []
    for s in symptom_list:
        match = next(
            (
                x
                for x in ALL_SYMPTOMS_WITH_SEVERITY
                if x["symptom"].lower() == s.lower()
            ),
            None,
        )
        if match:
            symptom_severities.append(match["severity"])
    avg_symptom_severity = (
        sum(symptom_severities) / len(symptom_severities) if symptom_severities else 1
    )

    overall = (avg_disease_severity + avg_symptom_severity) / 2
    overall = int(round(overall))
    return min(overall, 10)


# callbacks
# home page for patient registration with a "View Existing Patients" button.
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        dob = datetime.strptime(request.form["dob"], "%Y-%m-%d")
        gender = request.form["gender"]
        other_info = request.form.get("other_info", "")
        patient = Patient(name=name, dob=dob, gender=gender, other_info=other_info)
        db.session.add(patient)
        db.session.commit()
        return redirect(url_for("patient", patient_id=patient.id))
    return render_template("index.html")


@app.route("/patients", methods=["GET"])
def patients():
    patients_list = Patient.query.order_by(Patient.name).all()
    return render_template("patients.html", patients=patients_list)


@app.route("/patient/<int:patient_id>", methods=["GET", "POST"])
def patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == "POST":
        diseases = request.form.get("diseases", "")
        symptoms = request.form.get("symptoms", "")
        severity = approximate_record_severity(diseases, symptoms)
        record = Record(
            patient_id=patient_id,
            disease=diseases,
            symptoms=symptoms,
            severity=severity,
        )
        db.session.add(record)
        db.session.commit()
    records = (
        Record.query.filter_by(patient_id=patient_id).order_by(Record.date.desc()).all()
    )
    return render_template("patient.html", patient=patient, records=records)


@app.route("/edit_patient/<int:patient_id>", methods=["GET", "POST"])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == "POST":
        patient.name = request.form["name"]
        patient.dob = datetime.strptime(request.form["dob"], "%Y-%m-%d")
        patient.gender = request.form["gender"]
        patient.other_info = request.form.get("other_info", "")
        db.session.commit()
        return redirect(url_for("patient", patient_id=patient.id))
    return render_template("edit_patient.html", patient=patient)


# edit an existing record
@app.route("/edit_record/<int:record_id>", methods=["GET", "POST"])
def edit_record(record_id):
    record = Record.query.get_or_404(record_id)
    if request.method == "POST":
        diseases = request.form.get("diseases", "")
        symptoms = request.form.get("symptoms", "")
        severity = approximate_record_severity(diseases, symptoms)
        record.disease = diseases
        record.symptoms = symptoms
        record.severity = severity
        db.session.commit()
        return redirect(url_for("patient", patient_id=record.patient_id))
    return render_template("edit_record.html", record=record)


@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("query", "").lower().strip()
    suggestions = []

    if query == "":
        for d in ALL_DISEASES_WITH_SEVERITY:
            suggestions.append(
                {
                    "type": "disease",
                    "value": d["name"],
                    "synonyms": d["synonyms"],
                    "severity": d["severity"],
                }
            )
        for s in ALL_SYMPTOMS_WITH_SEVERITY:
            suggestions.append(
                {
                    "type": "symptom",
                    "value": s.get("symptom", ""),
                    "severity": s.get("severity", 5),
                }
            )
    else:
        for d in ALL_DISEASES_WITH_SEVERITY:
            if query in d["name"].lower() or any(
                query in syn.lower() for syn in d["synonyms"]
            ):
                suggestions.append(
                    {
                        "type": "disease",
                        "value": d["name"],
                        "synonyms": d["synonyms"],
                        "severity": d["severity"],
                    }
                )
        for s in ALL_SYMPTOMS_WITH_SEVERITY:
            symptom_text = s.get("symptom", "")
            if query in symptom_text.lower():
                suggestions.append(
                    {
                        "type": "symptom",
                        "value": symptom_text,
                        "severity": s.get("severity", 5),
                    }
                )
        bio_diseases, bio_symptoms = get_biobert_suggestions(query)
        for d in bio_diseases:
            if not any(
                d.lower() == sug["value"].lower()
                for sug in suggestions
                if sug["type"] == "disease"
            ):
                suggestions.append({"type": "disease", "value": d, "severity": 5})
        for s in bio_symptoms:
            if not any(
                s.lower() == sug["value"].lower()
                for sug in suggestions
                if sug["type"] == "symptom"
            ):
                suggestions.append({"type": "symptom", "value": s, "severity": 5})

    return jsonify(suggestions)


# app call exe
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
