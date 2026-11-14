
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'mediscan-ai'
        CONTAINER_NAME = 'mediscan-container'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Stop Old Container') {
            steps {
                bat 'docker rm -f %CONTAINER_NAME% || exit /b 0'
            }
        }

        stage('Deploy Container') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'GEMINI_API_KEY',
                        variable: 'GEMINI_API_KEY'
                    )
                ]) {
                    bat 'docker run -d --name %CONTAINER_NAME% -p 8501:8501 -e GEMINI_API_KEY=%GEMINI_API_KEY% %IMAGE_NAME%:%BUILD_NUMBER%'
                }
            }
        }
    }

    post {
        success {
            echo 'Medical Image Analysis deployed successfully!'
        }

        failure {
            echo 'Deployment failed. Check console output.'
        }
    }
}
