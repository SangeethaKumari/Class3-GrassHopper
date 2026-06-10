 # CONTEXT
I am building a specialized evaluation and training dataset for a DSPy (Declarative Self-Improving Language Programs) hackathon. The participants are software engineers (ages 25-60) who are optimizing AI agents to categorize health conditions. To demonstrate the power of prompt optimization, the dataset must contain nuanced, high-quality clinical data that a simple "Zero-Shot" prompt would likely misclassify.

# OBJECTIVE
Generate {count} unique, non-duplicate clinical patient vignettes specifically for the high-level category: {category}. 

# STYLE
Write as a Senior Medical Board Examiner. Use professional medical terminology (e.g., 'dyspnea' instead of 'shortness of breath', 'metamorphopsia' instead of 'wavy vision') while simulating the slightly disjointed nature of an Electronic Health Record (EHR) intake note.

# TONE
Analytical, clinical, and precise. Avoid being overly dramatic; focus on the data points that a physician would use to differentiate a diagnosis.

# AUDIENCE
Software Engineers and AI Developers. The content must be medically complex enough to require "Chain of Thought" reasoning, but the structure must be 100% reliable for programmatic JSON parsing.

# RESPONSE
Output exactly {count} rows in JSON format. 

CRITICAL: 'patient_notes' MUST be a long paragraph (at least 3 sentences) describing the patient. 
Example: "72yo male presenting with polyuria and blurred vision. Patient has a BMI of 32..."

Each object must follow this EXACT structure:
{{
  "patient_notes": "Full clinical narrative here",
  "reasoning": "Step-by-step clinical logic here",
  "label": "{category}"
}}

# REQUIREMENTS
1. DEMOGRAPHICS: Force a wide distribution of ages (10-90) and genders across the {count} samples.
2. DIFFICULTY: Ensure 30% of cases are 'Hard Negatives' or 'Clinical Mimics'. These should feature symptoms that overlap heavily with other categories (like Cardiovascular or Diabetes) but have one or two 'gold' markers that confirm they belong to {category}.
3. NO DUPLICATES: Each vignette must have a distinct patient profile and narrative structure.