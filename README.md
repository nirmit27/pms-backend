# Patient Management System 🏥

This is a **Patient Management System** microservice powered by [**FastAPI**](https://fastapi.tiangolo.com/tutorial/).
> ⚠️ Under Construction ⚠️

## Installation and Setup

### 1. Clone
To clone this repository, run the following command :
```bash
git clone https://github.com/nirmit27/pms-backend.git
```

### 2. Environment
Now, to setup the virtual environment (**recommended**) for running this microsevice locally, follow these steps :

#### 1. Initialise the virtual environment.
```bash
python -m venv name-of-your-choice
```

#### 2. Install the required libraries as mentioned in the [requirements.txt](./requirements.txt) file.
```bash
pip install -r requirements.txt
```

### 3. Development
To start the **development** server, run the following command in the terminal :
```bash
uvicorn main:app --reload
```

- As you make changes to the **Python scripts**, the server will automatically restart the application to reflect those changes, courtesy of the **`--reload`** flag appended to the command.

### 4. Deployment
Follow the official documentation provided by **[Render](https://render.com/docs/deploy-fastapi)** for deployment as a web service.


## Technologies
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/)&nbsp; [![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)&nbsp; [![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://docs.mongodb.com/)&nbsp; [![Render](https://img.shields.io/badge/Render-000?style=for-the-badge&logo=render&logoColor=white)](https://docs.railway.app/)

---
