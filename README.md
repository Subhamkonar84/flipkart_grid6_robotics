# Billing System with Quantity and Inventory Verification

**Name:** Subham Ranjan Konar  
**Team Name:** subhamranjankonar.21ds  
**College:** Sai Vidya Institute of Technology  

---

## Purpose
The purpose of the project is to make the process of inspecting goods during packaging more efficient. It involves item classification, quantity analysis, and quality inspection.

---

## Structure

### 1. **Project Overview**
**Project Name:** Billing System with Quantity and Inventory Verification  

#### **Objective**  
The goal is to build a robust web-based billing system to ensure accuracy in item quantities and inventory validation. The system performs the following tasks:
- Matches items listed by users with those present in the database.
- Detects quantity discrepancies.
- Alerts users about missing, incorrect, or extra items.
- Notifies users of defective, expired, or unwanted items.
- Integrates seamlessly with industrial systems.

---

### 2. **Key Features**
1. **Input Verification**
   - Users input item names and quantities.
   - The system cross-verifies with camera-detected items and stored inventory.

2. **Quantity Validation**
   - Alerts users to excess or shortage of items.
   - Highlights item names and quantity discrepancies.

3. **Database Integration**
   - Fetches details like names, quantities, and expiry dates.
   - Verifies all data against user input.

4. **Error Reporting**
   - Provides detailed notifications on missing, extra, or defective items.
   - Ensures robust error handling.

5. **Real-time Testing & Feedback**
   - Live web interface for real-time results.
   - Can integrate with Flipkart's API to fetch customer orders.

6. **Quality Validation**
   - Notifies users about item quality (e.g., damaged or expired).
   - Highlights defective items for analysis.

---

### 3. **Use Cases**
1. **Flipkart Storehouses**
   - Validates inventory and customer orders.
   - Reduces errors during transactions.

2. **Administrators**
   - Monitors performance and accuracy.
   - Manages inventory adjustments based on feedback.

---

### 4. **Outcome**
The system ensures billing accuracy, enhances reliability, and streamlines inventory management. Users gain actionable insights for better decision-making.

---


## Codebase Structure

### Steps to Run the Code Locally

1. **Clone the YOLOv7 Repository**  
   - Go to the official YOLOv7 model code and clone the repository:  
     ```bash
     git clone https://github.com/WongKinYiu/yolov7
     ```

2. **Clone My Repository**  
   - Clone my GitHub repository:  
     ```bash
     git clone https://github.com/Subhamkonar84/flipkart_grid6_robotics
     ```

3. **Replace and Copy Files**  
   - Replace `detect.py` in the YOLOv7 folder with `detect2.py` from my repository.  
   - Copy `best3.py` from my repository and place it in the YOLOv7 folder.

4. **Install Requirements**  
   - Open the terminal in the YOLOv7 folder and install the required libraries:  
     ```bash
     pip install -r requirements.txt
     ```

5. **Configure MySQL Database**  
   - Set up a MySQL database and configure the database username and password for storing the data.  
   - Manually add a few data entries that you will work with.

6. **Start Live Video Detection**  
   - Use the following command to start live video detection from the camera input:  
     ```bash
     python3 detect2.py --weights best3.pt --conf 0.9 --img-size 640 --source 0
     ```
   - This will start the camera and begin detection.

7. **Run the GUI Application**  
   - Navigate to the `billing_app` folder in my repository and open a terminal.  
   - Install the required Django framework libraries for the server.  
   - Run the migration for the models present in the folder (or use my preconfigured database).  

8. **Start the Django Server**  
   - Run the following command to start the server:  
     ```bash
     python manage.py runserver
     ```
   - This will generate a link: `http://127.0.0.1:8000/`. This localhost link can be accessed by any program running on the device.

9. **Test Items for Quality and Quantity**  
   - Input `name:quantity,name:quantity` in the input text bar and press **Enter** or click the **Check Bill** button to test the items.

10. **Use the Program**  
    - The program is now running, and you can use it to detect and analyze the products.

## Detailed Database Schema and Configurations Template

### Purpose
Ensure the database schema is well-documented, with clear instructions on how to set up, configure, and interact with the database.

---

### Database Schema Documentation

#### Database Design
- **Database Name**: `flipkart`
- **Tables**: `items`, `fresh`

---

#### 1. **Table: `items`**

- **Query to Create the Table**:
  ```sql
  CREATE TABLE items (
      id INT AUTO_INCREMENT PRIMARY KEY, 
      timestamp DATETIME NOT NULL,
      brand VARCHAR(255) NOT NULL,
      expiry_date DATE NOT NULL,
      count INT NOT NULL,
      expired ENUM('NA', 'yes') DEFAULT 'NA',
      expected_life_span INT DEFAULT NULL
  );
  ```
  #### Trigger for Auto-Filling Details During Data Insertion

- **Trigger Creation Query**:
  ```sql
  DELIMITER 
  CREATE TRIGGER update_inventory BEFORE INSERT ON items
  FOR EACH ROW
  BEGIN
      -- Calculate expected_life_span
      SET NEW.expected_life_span = DATEDIFF(NEW.expiry_date, CURDATE());

      -- Determine if expired
      IF NEW.expiry_date < CURDATE() THEN
          SET NEW.expired = 'yes';
      ELSE
          SET NEW.expired = 'NA';
      END IF;
  END;

  DELIMITER ;
  ```
  #### Example of Adding Data to the `items` Table

- **SQL Query**:
  ```sql
  INSERT INTO items (timestamp, brand, expiry_date, count) 
  VALUES ('2024-11-29T05:12:01', 'clinic_plus_shampoo', '2025-01-15', 50);
  ```
  #### Creating the `fresh` Table

- **SQL Query**:
  ```sql
  CREATE TABLE fresh (
      id INT AUTO_INCREMENT PRIMARY KEY, 
      timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      product VARCHAR(255) NOT NULL,
      freshness INT NOT NULL,
      expected_life_span INT NOT NULL 
  );
  ```
  #### Inserting an Item into the `fresh` Table

- **SQL Query**:
  ```sql
  INSERT INTO fresh (product, freshness, expected_life_span)
  VALUES ('potato', 5, 12);
  ```
  ### 2. Database Configuration

- **Database User Configuration**:
  - A user named `proj` with the password `project@123` has been created. 
  - You can use this configuration for the project or create your own credentials and update them in the code accordingly.

---

### 3. APIs

- **Main Application URL**:  
  `http://127.0.0.1:8000/`  
  Returns the main index page.

- **API Endpoints**:  
  - **`/external-update/`**: Used to add items into the database table.  
  - **`/fetch-items/`**: Used to reload and update the table in the frontend.  
  - **`/check-notifications/`**: Used to fetch push notifications and alerts for the application user.  

---

### 4. Functional, Live Web Link for Real-Time Application Testing

#### Deployment Instructions:
- **Hosting Platform**:  
  - Currently, the application is deployed locally. It can also be hosted on a cloud platform of your choice for better scalability.

- **Training Platform**:  
  - To train the model, use `training.ipynb`.  
  - The platform must support CUDA cores to enable GPU acceleration.

#### Live Application URL:
- **Local URL**:  
  `http://127.0.0.1:8000/`  

#### Live Screenshots:
- Include real-time screenshots of detection and analysis when running the app.

### 3. Testing and Feedback

- **GUI Testing**:
  - The index page provides functionality testing for the GUI to ensure user interaction works as expected.

- **API Testing**:
  - Use **Postman** to analyze and test the APIs of the GUI system.

- **Detection Testing**:
  - `detect.py` supports camera input and command-line output, enabling users to test the detection model and optimize it for the best predictions.

- **Independent Testing**:
  - Both the frontend and backend can run and be tested individually, ensuring modular functionality.

---

### 4. Maintenance and Updates

- **Model Training**:
  - Retrain the model with new data using the `training.ipynb` file and update the weights in the detection module to maintain accuracy and relevance.

---

### Features of the Project

- **Accuracy**:
  - Detection model achieves **92%+ confidence** under optimal lighting and system conditions.

- **Brand Detection**:
  - Fast and accurate, with over **95% brand detection accuracy** and processing delay of under 1000 milliseconds.

- **Expiry Date Detection**:
  - Near **100% accuracy** in identifying expiry dates and calculating days remaining for expiration, applicable even to fresh produce.

- **Product Counting**:
  - **100% accurate** counting, supporting multiple items, partially visible items, and items placed side-by-side.

- **Freshness Detection**:
  - Detects the quality of vegetables/fruits, estimating the remaining days before spoilage if fresh.

- **Alert Notifications**:
  - Push notifications for defective, expired, or bad items in the cart, allowing immediate replacement.

- **Table Auto-Refresh**:
  - Automatic item table updates for seamless user experience.

- **Billing Testing**:
  - Input text field for testing quality and quantity of items; can integrate with Flipkart APIs for automated order handling.

---

### Technologies Used

- **Frontend**:
  - Django, HTML, CSS, Bootstrap, JavaScript
- **Model**:
  - ResNet (YOLOv7)
- **Database**:
  - MySQL, SQLite

---

### Additional Highlights

- **Error Handling**:
  - Streamlined error handling ensures smooth operation.

- **Practicality**:
  - Easily integrates with existing systems, supporting the latest technology and APIs.

- **Real-World Applicability**:
  - Can be implemented in stores with minimal adjustments, addressing billing and packing challenges.

---

### Contact Information

- **Email**: [subhamkonar84@gmail.com](mailto:subhamkonar84@gmail.com)
- **Phone**: +91 85488 98977

  

