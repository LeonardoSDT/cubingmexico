Cubingmexico
===

## Características

1. **Inicio de sesión mediante la WCA** - Vincula tu cuenta de la WCA
2. **Rankings nacionales y estatales de México** - Mira los rankings del país o de cada estado
3. **Récords nacionales y estatales de México** - Mira los récords del país o de cada estado
4. **SOR nacional y estatal de México** - Mira la Suma de Rankings del país o de cada estado
5. **Kinch Ranks nacionales y estatales de México** - Mira los Kinch Ranks del país o de cada estado (Próximamente)
6. **UNRs de México** - Mira los Récords Nacionales no Oficiales (Próximamente)

## Información de la WCA

Todos los récords y datos de competencias oficiales pertenecen a la [WCA (World Cube Assocation)](https://www.worldcubeassociation.org).
Ningún récord oficial ha sido modificado/alterado.

## Configuración de desarrollo

### Requerimientos

*  [docker](https://www.docker.com/community-edition#/download)
*  [docker-compose](https://docs.docker.com/compose/install/)

### Instalación

1. Configurar Google Cloud Platform:

  a. Create a new project
  b. Make sure the project has a billing account attached
  c. Download GCP CLI from [here](https://cloud.google.com/sdk/docs/install)
  d. Create a service account:
      As a best practice, we will create a new service account on GCP to run our Cloud Run instance. Go to the GCP console → IAM & Admin → Service Accounts and create a new service account e.g. "cubingmexico_app_dev"
      Next, grant the following permissions to it:
        - Cloud SQL Client
        - Service Account User
        - Cloud Run Invoker
        - Cloud Run Service Agent
        - Secret Manager Secret Accessor
        - Storage Object Admin
      Next, go to the KEYS section. Create a new key and store the JSON file as "creds.json" inside the /gcp folder.
  e. Create a Cloud SQL instance
      Although we can create a database instance using GCP CLI, it’s helpful to use the GUI if doing for the first time. Head to your GCP console → SQL → Create Instance.
      Select a Postgres instance with required capacity (3.75 GB memory and 10 GB SSD). Give an apt name e.g. cubignemxico-dev-db. GCP will take up to 5 minutes to create a new instance, it will also create a default user postgres and a default database postgres.
      Next, create a new user named "cubingmexicodevdbadmin" and a new database called "cubingmexicodevdb". Make sure to note down the password for cubingmexicodevdbadmin.
  f. Create a storage bucket
      We will need to create a Google Cloud Storage bucket to host the static files from Django. Head to GCP console → Cloud Storage → Create bucket, name it "cubingmexico_dev_bucket".

2. Construir y ejecutar:

```
$ docker-compose up --build
```

3. Abrir utilizando: http://localhost:8080

## Desarrollador

Este repositorio es mantenido por [Leonardo Sánchez Del Toro](https://www.facebook.com/leonardo.sanchezdeltoro)
