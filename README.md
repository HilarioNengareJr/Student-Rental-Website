# Student Rental Hub - Flask Web Application

## Overview

Student Rental is a feature-rich web application built with Flask, designed to simplify the process of finding and renting student accommodations. Leveraging technologies like HTML, CSS, JavaScript, Elasticsearch, and PostgreSQL, it offers a seamless experience for both tenants and landlords.

## Technologies Used

- **Frontend:**
  - HTML for creating the structure of the web pages
  - CSS for styling and enhancing the user interface
  - JavaScript for client-side interactivity and dynamic content

- **Backend:**
  - Flask as the web framework for Python
  - PostgreSQL as the relational database for storing user and property data
  - Elasticsearch for efficient and powerful search functionality

## Features

1. **User Authentication:**
   - Secure login and registration system for tenants and landlords.

2. **Property Listings:**
   - Browse through a comprehensive list of available student accommodations.

3. **Search and Filter:**
   - Utilize Elasticsearch-powered search to find rentals based on preferences.

4. **Booking System:**
   - Streamlined process for tenants to book their preferred accommodations.

5. **Landlord Dashboard:**
   - Dedicated dashboards for landlords to manage property listings and tenant requests.

## How to Use

1. **Visit the Website:**
   - Access Student Rental Hub through your web browser.

2. **Explore Listings:**
   - Browse available properties and filter results based on your criteria.

3. **Sign Up or Log In:**
   - Create an account or log in to access additional features.

4. **Book Your Accommodation:**
   - Submit booking requests for the desired rental property.

5. **Landlord Management:**
   - Landlords can log in to manage property listings and handle tenant requests.

## Development

To run Student Rental Hub locally, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/HilarioNengareJr/rental-estate-site.git
   ```

2. **Build and Run with Docker Compose:**
- Navigate to the project directory.
- Run the following command to build and start the containers:
  ```
  docker-compose up --build
  ```

3. **Access the Application:**
- Open your web browser and go to:
  ```
  http://localhost:5000
  ```

## Development

To run Student Rental Hub locally without Docker Compose, follow these steps:

1. **Install Dependencies:**
- pip install -r requirements.txt

2. **Set Up PostgreSQL and Elasticsearch:**
- Configure database and search index settings in the Flask app.

3. **Run the Flask App:**

4. **Access the App in Your Browser:**

- http://localhost:5000/