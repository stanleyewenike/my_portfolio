
CREATE TABLE DimPatient (
    PatientID INT PRIMARY KEY,
    Gender VARCHAR(10),
    DOB DATE
);

CREATE TABLE DimDate (
    DateID INT PRIMARY KEY,
    Date DATE,
    DayOfWeek VARCHAR(15),
    Month VARCHAR(15),
    Year INT
);

CREATE TABLE DimOutcome (
    OutcomeID INT PRIMARY KEY,
    OutcomeDescription VARCHAR(100)
);

CREATE TABLE DimHospital (
    HospitalID INT PRIMARY KEY,
    Name VARCHAR(100),
    Location VARCHAR(100)
);

CREATE TABLE DimStaff (
    StaffID INT PRIMARY KEY,
    Name VARCHAR(100),
    Role VARCHAR(50)
);

CREATE TABLE DimDiagnosis (
    DiagnosisID INT PRIMARY KEY,
    DiagnosisName VARCHAR(100),
    DiagnosisDate DATE
);
CREATE TABLE FactAppointments (
    FactID INT PRIMARY KEY,
    PatientID INT,
    DateID INT,
    OutcomeID INT,
    HospitalID INT,
    StaffID INT,
    DiagnosisID INT,
    NoShowFlag INT,
    FOREIGN KEY (PatientID) REFERENCES DimPatient(PatientID),
    FOREIGN KEY (DateID) REFERENCES DimDate(DateID),
    FOREIGN KEY (OutcomeID) REFERENCES DimOutcome(OutcomeID),
    FOREIGN KEY (HospitalID) REFERENCES DimHospital(HospitalID),
    FOREIGN KEY (StaffID) REFERENCES DimStaff(StaffID),
    FOREIGN KEY (DiagnosisID) REFERENCES DimDiagnosis(DiagnosisID)
);