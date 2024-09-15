# 21BCE7665_ML
Backend for document retrieval which can be used as context for LLMs 
## API Readme

This Flask API provides endpoints for scraping news articles from Google news website.
It includes background tasks to periodically scrape news depending on the query and a mechanism to log API requests and track user call frequency.

Setup Instructions
Prerequisites

    Python 3.7 or higher
    Docker (optional, for containerization)
    Flask
    SQLite

The API will be available at http://127.0.0.1:5000.

# API Endpoints
/health: Checks if the server is active, if it is it displays status as active.
![image](https://github.com/user-attachments/assets/c16e385b-bb92-4929-afe1-e54eddc64c4d)

/search: search function takes few parameters such as 
              data 
              text 
              top_k 
              threshold
              user_id
        in order to perform the query.
        since there is no frontend implemented yet this can be accessed via the terminal using the following command.
        on powershell :
        
                        Invoke-RestMethod -Uri http://127.0.0.1:5000/search -Method Post -Body '{
                        "text": "testing",
                        "top_k": 3,
                        "threshold": 0.8,
                        "user_id": "user123"
                      }' -ContentType "application/json"  
on Linux:    

                        curl -X POST http://127.0.0.1:5000/search \
                         -H "Content-Type: application/json" \
                         -d '{
                               "text": "testing",
                               "top_k": 3,
                               "threshold": 0.8,
                               "user_id": "user123"
                             }'  
The results will be displayed as:     
        ![image](https://github.com/user-attachments/assets/65e4f890-012c-48b6-855b-245923fa33f6)
If the user api limit is hit then:
      ![image](https://github.com/user-attachments/assets/2aec7173-bcfb-4944-8e23-a24df84ac7e3)

The program first parses the articles database inorder to check if the query has been called before. If it has it returns the data from the database.
If the query is not found then the scraper is run and data is added to articles.db in an effort to optimize.

# Database Structure
articles.db

    Table: articles
    Columns:
        id: INTEGER PRIMARY KEY AUTOINCREMENT
        link: TEXT
    Purpose: Stores news articles associated with queries.
![image](https://github.com/user-attachments/assets/897ee452-b250-4ccc-b6fd-1354f858951f)

api_requests.db

    Table: api_requests
    Columns:
        id: INTEGER PRIMARY KEY AUTOINCREMENT
        user_id: TEXT
        query: TEXT
        results: TEXT
        inference_time: REAL
        timestamp: DATETIME DEFAULT CURRENT_TIMESTAMP
    Purpose: Logs API requests including query, results, and inference time.
![image](https://github.com/user-attachments/assets/f4ad00c9-6082-40bc-84ac-973497153384)

user_calls.db

    Table: user_calls
    Columns:
        user_id: TEXT PRIMARY KEY
        call_frequency: INTEGER
    Purpose: Tracks the frequency of API calls per user.
![image](https://github.com/user-attachments/assets/22ac0ecc-c018-494f-a283-cd26a12d5e43)

# Dockerization
The docker image can be built as:
    docker build -t example
    
    docker build -t example
To run the docker container:

    docker run -p 5000:5000 my-flask-app

Docker image:
![image](https://github.com/user-attachments/assets/0028eedb-de19-400a-9445-deab7a9a1cc6)

The application can be accessed at http://localhost:5000.

