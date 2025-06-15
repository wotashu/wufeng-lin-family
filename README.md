# Wufeng Lin Family Graph Interactive App

This application provides an interactive interface for visualizing and managing family member data for the Wufeng Lin lineage. Users can view a family graph, add or update member documents stored in MongoDB Atlas, and edit JSON data through a built-in editor.

## See the application in action

(The url for the app is [here]https://wufeng.streamlit.app/)

## Features

- **Interactive Family Graph:**  
  Visualize family connections using various layouts (default, hierarchical, and spring).  
  - Customize node appearance based on member attributes (house, generation, gender, etc.).
  - Spouse nodes are clustered together using invisible edges.

- **Member Management:**  
  - **Add Member:** Fill out a form to create a new family member document.
  - **Update Member:** Look up an existing document by its ID, edit its JSON representation, and update the document with new data.

- **Editable JSON Form:**  
  Display member document JSON (including the MongoDB ObjectId) for direct editing, then save changes back to MongoDB.

## Prerequisites

- Python 3.8+
- A MongoDB Atlas account and a configured cluster.
- [Streamlit](https://streamlit.io/) installed.
- [uv](https://github.com/yourusername/uv) (a lightweight dependency installer) installed globally.
- Required Python packages as listed in `requirements.txt`:
  - `streamlit`
  - `pymongo`
  - `pydantic`
  - `pyvis`
  - `unidecode`

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/wufeng-lin-family.git
   cd wufeng-lin-family
   ```

2. **Install Dependencies Using uv**

   It is recommended to use a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   .venv\Scripts\activate  # On Windows
   ```

   Then, install dependencies using uv:

   ```bash
   uv install
   ```

   (Ensure that your `requirements.txt` is up-to-date; uv will read it and install the listed dependencies.)

3. **Configure MongoDB Connection**

   Create a file at `.streamlit/secrets.toml` in the root of your repository with your MongoDB connection string. For example:

   ```toml
   [mongodb]
   uri = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/my_new_family_db?retryWrites=true&w=majority&tls=true"
   ```

## Running the Application

Launch the Streamlit app using the following command:

```bash
streamlit run app.py
```

This will open your default browser with a sidebar for navigation. Choose between the Home page (graph display) and the Add / Update Document page.

## Folder Structure

- **app.py:** Main application entry point with sidebar navigation.
- **src/**
  - **graph_create.py:** Functions to create a NetworkX graph from family member data.
  - **graph_render.py:** Renders the interactive family graph using Pyvis.
  - **member_page.py:** Contains forms and functionality for adding/updating member documents.
  - **models.py:** Pydantic models for family member data.
- **data/**  
  Contains JSON files representing the family members (optional if migrating data to MongoDB).

## Deployment

The application is designed to run on Streamlit Cloud (free tier). Ensure that your MongoDB credentials are stored securely in the secrets file as described above.

## Troubleshooting

- **SSL/TLS Errors:**  
  If you encounter SSL handshake errors connecting to MongoDB, verify your Atlas IP whitelist and ensure that your connection string forces TLS (`tls=true`).

- **Form Submission Issues:**  
  Ensure each form uses a unique key (e.g., "add_member_form" versus "update_member_form") to avoid missing submit buttons.

- **ObjectId Serialization:**  
  The application uses Pydantic validators and custom JSON encoders to handle MongoDB ObjectIds. If you run into serialization errors, verify the configuration in your Pydantic model.

## Contributing

Feel free to fork this repository and submit pull requests with improvements or additional features. For major changes, please open an issue first to discuss your ideas.

## License

This project is licensed under the MIT License.