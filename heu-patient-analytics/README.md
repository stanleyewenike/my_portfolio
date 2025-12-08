# Health Economics Unit Patient Analytics

This repository contains the code and data for the Health Economics Unit (HEU) patient analytics project. The project aims to analyze patient health data to gain insights into patient demographics, diagnoses, and factors influencing missed appointments. The analysis involves data visualization, statistical calculations, and data preparation to explore the dataset and identify patterns and trends. The findings from the analysis can be used to understand the factors influencing missed appointments and develop strategies to reduce no-show rates in healthcare settings. The project also includes documentation related to the recruitment process for a lead data scientist position at the HEU. The project is structured as follows:

```
heu-patient-analytics/
│
├── data/
│   ├── patient_health.csv
├── docs/
│   ├── 00-Pre-Interview test - Lead Data Scientist Test 2025.docx
│   ├── 00-Pre-Interview test - Lead Data Scientist Test 2025.docx
│   ├── 01-Lead Data Scientist-Econometrician - Job Description and Person Specification.pdf
│   ├── 02-A_Lead Data Scientist.pdf
│   ├── 03-Applicant_Recruitment Journey_AC_V4.pdf
├── models/
│   ├── 01-relational-model.md
│   ├── 02-dimensional-model.md
├── notebooks/
│   ├── 01-eda-and-prep-for-predictive-model.ipynb
├── reports/
│   ├── 01-summary-of-findings.md 
│   ├── 02-analysis-plan.md
│── src/
│   ├── iac-templates-azure-sql-db-setup/   
│   │   ├── template.json
│   │   ├── parameters.json
│   │   ├── z-repository_iac.py
│   ├── 01-schema-relational-model.sql
│   ├── 02-schema-dimensional-model.sql
│── utils/
│   ├── .gitattributes
│   ├── LICENSE
│   ├── .gitignore
│   ├── README.md
│   ├── requirements.txt```
```

The project structure is organized into the following directories:

## Data

The data for the project is stored in the `data` directory. The dataset `patient_health.csv` contains information on patients including their `PatientID`, `Age`, `Gender`, `Diagnosis`, `AppointmentDate`, `Outcome`, `GPPractice`, and `MissedAppointment`. The dataset was used for the analysis to explore patient demographics, diagnoses, and factors influencing missed appointments.

## Documentation

The `docs` directory contains additional documentation related to the project. The documentation includes a recruitment journey for a lead data scientist position and a presentation on the applicant recruitment journey. The documentation provides insights into the recruitment process and the requirements for the lead data scientist role.

## Models

The `models` directory contains markdown files describing the relational and dimensional models for the patient health dataset. The models provide an overview of the data structure, relationships between entities, and attributes of the dataset. The models were used to design the database schema and prepare the dataset for analysis.

## Notebooks

The `notebooks` directory contains Jupyter notebooks that were used for the analysis. The notebooks include data preparation, exploratory data analysis, and modeling of the patient health dataset. The notebooks provide a step-by-step guide to the analysis, including data visualization, statistical calculations, and data preparation.

## Reports

The `reports` directory contains markdown files summarizing the findings from the analysis. The reports include an overview of the dataset, missing values, age distribution, no-show

## Source Code

The `src` directory contains source code for the project. The source code includes SQL scripts for creating the relational and dimensional models of the patient health dataset. The scripts define the database schema, tables, and relationships between entities. The source code was used to prepare the dataset for analysis and modeling.

## Utils

The `utils` directory contains utility files for the project. The utility files include a `.gitattributes` file, a `LICENSE` file, a `.gitignore` file, a `README.md` file, and a `requirements.txt` file. The utility files provide information on the project structure, licensing, and dependencies for the project.

 -----------------------------------------------------------------------------------------------------

## Summary of Findings

The analysis of the patient health dataset aimed to explore the characteristics of patients, their diagnoses, and the factors influencing missed appointments. The dataset contains information on patients including their:

- `PatientID`
- `Age`
- `Gender`
- `Diagnosis`
- `AppointmentDate`
- `Outcome`
- `GPPractice`
- `MissedAppointment`

The analysis involved data visualization, statistical calculations, and data preparation to gain insights into the dataset. This summary provides an overview of the key findings from the analysis.

### Dataset Overview

The dataset contains 5000 entries with 8 columns. The columns include `PatientID`, `Age`, `Gender`, `Diagnosis`, `AppointmentDate`, `Outcome`, `GPPractice`, and `MissedAppointment`. The dataset was explored to understand the distribution of data and identify any missing values.

### Missing Values

The dataset contains missing values in several columns. The missing values were visualized using a bar plot and a heatmap to identify the columns with missing data. The `Age` and `Gender` columns each have 3 missing values, `Diagnosis` has 1 missing value, `AppointmentDate` has 2 missing values, and `Outcome` has 2 missing values.

### Age Distribution

The age distribution of patients was visualized using a histogram with a KDE plot. The distribution shows a wide range of ages among the patients, with the majority of patients falling between the ages of 20 and 60.

### No-Show Rates

The no-show rates were calculated and visualized for different diagnoses and GP practices. The analysis revealed that `Asthma` has the highest no-show rate at approximately 51.4%, followed by `Hypertension` and `Diabetes`. Among GP practices, `D012` has the highest no-show rate at approximately 57.2%, while `E345` has the lowest at approximately 43.8%. The no-show rates were visualized using
bar plots.

 -----------------------------------------------------------------------------------------------------
