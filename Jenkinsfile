pipeline {
agent any

environment {
DEV_ENV_ID  = 'cms_image_pipeline_dev_env'
MAIN_ENV_ID = 'cms_image_pipeline_main_env'
}

options {
timestamps()
}

stages {

stage('Checkout') {
steps {
checkout scm
script {
echo "Branch: ${env.BRANCH_NAME}"
}
}
}

stage('Build Docker image') {
steps {
sh 'docker build -t iw-cms-image-pipeline -f Dockerfile .'
}
}

stage('Deploy to dev') {
when {
branch 'dev'
}
environment {
CMS_ENV_CREDENTIAL = "${DEV_ENV_ID}"
}
steps {
script {
withCredentials([file(credentialsId: CMS_ENV_CREDENTIAL, variable: 'ENV_FILE')]) {
        sh '''
        echo "Using dev env from ${ENV_FILE}"

        echo "Stopping existing containers..."
        docker stop cms_image_pipeline_dev || true

        echo "Removing existing containers..."
        docker rm -f cms_image_pipeline_dev || true

        echo "Removing old compose stack..."
        docker compose -f docker-compose.yml down --remove-orphans -v || true

        echo "Starting new containers..."
        docker compose --env-file "$ENV_FILE" -f docker-compose.yml up -d --build
        '''
}
}
}
}

stage('Deploy to main') {
when {
branch 'main'
}
environment {
CMS_ENV_CREDENTIAL = "${MAIN_ENV_ID}"
}
steps {
script {
withCredentials([file(credentialsId: CMS_ENV_CREDENTIAL, variable: 'ENV_FILE')]) {
        sh '''
        echo "Using main env from ${ENV_FILE}"

        echo "Stopping existing containers..."
        docker stop cms_image_pipeline_main || true

        echo "Removing existing containers..."
        docker rm -f cms_image_pipeline_main || true

        echo "Removing old compose stack..."
        docker compose -f docker-compose.main.yml down --remove-orphans -v || true

        echo "Starting new containers..."
        docker compose --env-file "$ENV_FILE" -f docker-compose.main.yml up -d --build
        '''
}
}
}
}

}

post {
failure {
echo 'Pipeline failed.'
}
success {
echo 'Pipeline succeeded.'
}
}
}
