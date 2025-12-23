# Kannada Idioms & Phrases Translation System

## Overview

The **Kannada Idioms & Phrases Translation System** is a language-focused software application designed to accurately interpret Kannada idioms, proverbs, and phrases, and provide their **contextual meaning in both Kannada and English**. Unlike word-to-word translators, this project focuses on preserving cultural context, figurative meaning, and linguistic nuance, making it useful for students, researchers, and non-native speakers learning Kannada.

The system integrates text input, idiom detection, and bilingual meaning generation through a clean and user-friendly interface.

---

## Problem Statement

Direct translation systems often fail to correctly interpret Kannada idioms and phrases because idioms carry meanings that are **not literal**. This creates misunderstanding for learners and translators.

**Objective:**
To build an intelligent translation system that accurately identifies Kannada idioms and provides their true meanings in Kannada and English.

---

## Objectives

* To identify Kannada idioms and commonly used phrases from user input
* To provide accurate Kannada explanations for idioms
* To generate correct English meanings with preserved context
* To design a scalable and user-friendly application
* To support language learning and cultural understanding

---

## Features

* Kannada idiom and phrase recognition
* Accurate Kannada-to-Kannada meaning generation
* Kannada-to-English contextual translation
* Simple and clean web-based interface
* Modular and extensible code structure
* Error handling for invalid or unknown inputs

---

## System Architecture

The system follows a modular architecture:

1. **User Interface Module** – Accepts Kannada text input
2. **Preprocessing Module** – Cleans and tokenizes input text
3. **Idiom Detection Module** – Matches idioms using dataset/rules
4. **Translation Module** – Generates Kannada and English meanings
5. **Output Module** – Displays translated results

---

## Technology Stack

* **Programming Language:** Python
* **Backend Framework:** Flask
* **Frontend:** HTML, CSS, JavaScript
* **Database:** MySQL (for idiom and phrase storage)
* **Libraries & Tools:**

  * NLTK / custom NLP logic
  * JSON for structured data
  * Git & GitHub for version control

---

## Dataset Description

The dataset is stored and managed using a **MySQL relational database**, consisting of:

* Kannada idioms and phrases
* Kannada explanations
* English contextual meanings

The database schema is designed to support efficient lookup, scalability, and future expansion while maintaining linguistic accuracy and cultural relevance.

---

## Database Configuration

Before running the application, ensure that MySQL is installed and running.

* Create a MySQL database for the project
* Update database credentials (host, username, password, database name) in the application configuration file
* Import the provided SQL schema or allow the application to initialize tables automatically

---

## Installation & Setup

### Prerequisites

* Python 3.8 or above
* pip package manager

### Steps

```bash
# Clone the repository
git clone <repository-url>

# Navigate to project directory
cd kannada-idiom-translator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

---

## Usage

1. Launch the application in the browser
2. Enter a Kannada idiom or phrase
3. Submit the input
4. View accurate Kannada and English meanings

---

## Results

* Correct identification of Kannada idioms
* Efficient and reliable data retrieval using MySQL database
* High accuracy in contextual translation
* Improved understanding of Kannada language expressions

---

## Limitations

* Limited to idioms available in the dataset
* Does not yet support speech input
* Context outside idioms is minimally handled

---

## Future Enhancements

* Expansion of idiom database
* Integration of OCR for image-based text input
* Speech-to-text and text-to-speech support
* Machine learning-based idiom detection
* Mobile application deployment

---

## Applications

* Kannada language learning platforms
* Translation and linguistic research
* Educational institutions
* Cultural documentation systems

---

## Project Team

* **Team Size:** 4 Members
* **Guide:** Prof. Thrupthika S
* **Department:** Computer Science & Engineering

---

## Academic Information

* **Semester:** VII

---

## Conclusion

The Kannada Idioms & Phrases Translation System successfully addresses the challenge of idiom translation by focusing on contextual meaning rather than literal translation. This project contributes to preserving linguistic richness and supports effective Kannada language learning.

---

## License

This project is developed for academic purposes. All rights reserved by the project team.
