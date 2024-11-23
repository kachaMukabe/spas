```markdown
# Sanitary Pad Dispensing System (SPDS)

[![Deploy to Cloud Run](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

SPDS is a chatbot-based system that simplifies access to sanitary pads, particularly in resource-limited communities. Inspired by the "One Pad per Girl" project in Zambia, SPDS leverages technology to provide a discreet, efficient, and scalable solution for managing menstrual hygiene.

## Features

* **WhatsApp Integration:** Users can request sanitary pads discreetly via WhatsApp.
* **Automated Order Processing:** The system guides users through a simple menu, collects necessary information, and processes orders efficiently.
* **Order Tracking:**  Unique order IDs allow users to check the status of their deliveries.
* **RapidPro Integration:** Manages conversational flows and triggers backend actions.
* **FastAPI Backend:**  Provides a robust and scalable API for handling requests and integrations.
* **Google Gemini Integration (optional):** Enhances the chatbot with natural language understanding and personalized recommendations.
* **SQLite Database:**  Stores order information securely.
* **Dockerized Deployment:**  Easy deployment to Google Cloud Run or other containerized environments.


## Getting Started

### Prerequisites

* Python 3.12
* Docker
* Google Cloud account (for Cloud Run deployment)
* RapidPro server
* WhatsApp Business account
* Google Gemini API key (optional)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/spds.git
   cd spds
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (see `.env.example` for a template):

    - Create a `.env` file in the project root and fill in the required variables.
    - **Highly recommended:** Use Google Cloud Secret Manager to store sensitive information like API keys and tokens.


### Running Locally

1. Create and initialize your SQLite database (see `main.py` for database setup).
2. Run the FastAPI application:

    ```bash
    uvicorn main:app --reload 
    ```


### Deploying to Google Cloud Run

1. Build the Docker image:

    ```bash
    gcloud builds submit --tag gcr.io/[YOUR_PROJECT_ID]/spds
    ```

2. Deploy to Cloud Run:

    ```bash
    gcloud run deploy spds \
        --image gcr.io/[YOUR_PROJECT_ID]/spds \
        --region [YOUR_REGION] \
        --platform managed \
        --allow-unauthenticated \  # Or configure appropriate authentication.
        --set-secrets=YOUR_SECRET_NAME=your-secret-name # use secrets to manage api keys.
    ```
   
    *   Replace placeholders like `[YOUR_PROJECT_ID]` and `[YOUR_REGION]`.
    *   Configure appropriate authentication if needed.  The `--allow-unauthenticated` flag makes the service publicly accessible.


## Configuration

* **RapidPro:** Configure webhooks to trigger actions in the FastAPI backend.
* **WhatsApp Cloud API:** Set up the webhook URL in the Facebook Developer portal.
* **Google Gemini:** Enable the API and obtain an API key (if using).
* **Database:** Configure the database connection string in the `.env` file.



## Contributing

Contributions are welcome! Please open an issue or submit a pull request.


## Acknowledgements


* Inspiration: One Pad per Girl project, Zambia

