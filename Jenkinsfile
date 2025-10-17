pipeline {
    agent any

    environment {
        APP_NAME = "flask-cicd-demo"
        APP_DIR = "/home/ubuntu/vlearn-cicd-jenkins"
        GIT_REPO = "https://github.com/prafulkharat23/vlearn-cicd-jenkins.git"
        GIT_BRANCH = "main"
        DOCKER_IMAGE = "flask-cicd-demo:latest"
        CONTAINER_NAME = "flask-cicd-container"
        APP_PORT = "5000"
        SERVER_CREDENTIALS='praful-b12-cicd'
        REMOTE_USER="ubuntu"
        REMOTE_HOST="15.222.236.169"
        NOTIFICATION_EMAIL="praful.kharat@gmail.com"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: "${GIT_REPO}"
            }
        }

        stage('Install Dependencies on Remote') {
            steps {
                echo 'Deploying application to remote server...'
                sshagent (credentials: ["${SERVER_CREDENTIALS}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} '
                        set -e
                        echo "Checking and installing dependencies..."

                        # Update package list
                        sudo apt-get update

                        # Install Docker if not present
                        if ! command -v docker &> /dev/null; then
                            echo "Docker not found. Installing docker.io..."
                            sudo apt-get install -y docker.io
                            sudo systemctl start docker
                            sudo systemctl enable docker
                            sudo usermod -aG docker ubuntu
                            echo "Docker installed successfully"
                        else
                            echo "Docker already installed: \$(docker --version)"
                        fi

                        # Install Nginx if not present
                        if ! command -v nginx &> /dev/null; then
                            echo "Nginx not found. Installing..."
                            sudo apt-get install -y nginx
                            echo "Nginx installed successfully"
                        else
                            echo "Nginx already installed: \$(nginx -v 2>&1)"
                        fi

                        # Install Git if not present
                        if ! command -v git &> /dev/null; then
                            echo "Git not found. Installing..."
                            sudo apt-get install -y git
                            echo "Git installed successfully"
                        else
                            echo "Git already installed: \$(git --version)"
                        fi

                        echo "All dependencies checked/installed successfully"
                    '
                    """
                }
            }
        }
        stage('Checkout Code on Remote') {
            steps {
                echo 'Checking out code on remote server...'
                sshagent (credentials: ["${SERVER_CREDENTIALS}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "
                        set -e
                        APP_DIR=${APP_DIR}

                        if [ -d ${APP_DIR} ]; then
                            echo 'Repository exists, pulling latest changes...'
                            cd ${APP_DIR} && git reset --hard && git pull origin main
                        else
                            echo 'Cloning repository...'
                            cd ~/ && git clone -b main ${GIT_REPO} \$APP_DIR
                        fi
                    "
                    """
                }
            }
        }
        stage('Build & Test') {
            steps {
                echo 'Checking out code on remote server...'
                sshagent (credentials: ["${SERVER_CREDENTIALS}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "
                        cd ${APP_DIR}
                        echo "Building Docker image..."
                        sudo docker build -t ${DOCKER_IMAGE} .
                    "
                    """
                }
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying container and NGINX setup...'
                sshagent (credentials: ["${SERVER_CREDENTIALS}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} '
                        set -e
                        cd ${APP_DIR}

                        echo "Stopping and removing old container if exists..."
                        sudo docker rm -f ${CONTAINER_NAME} || true

                        echo "Running new container..."
                        sudo docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:5000 ${DOCKER_IMAGE}

                        echo "Copying NGINX config..."
                        sudo cp ${APP_DIR}/nginx.conf /etc/nginx/conf.d/app.conf
                        sudo rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default
                        
                        echo "Testing NGINX configuration..."
                        sudo nginx -t

                        echo "Restarting NGINX..."
                        sudo systemctl restart nginx

                        echo "✅ Deployment completed successfully!"
                    '
                    """
                }
            }
        }
        stage('Health Check') {
            steps {
                script {
                    echo "Performing Health Check from Jenkins server..."

                    def healthUrl = "http://${REMOTE_HOST}"
                    def responseCode = sh(script: "curl -s -o /dev/null -w '%{http_code}' ${healthUrl}", returnStdout: true).trim()

                    if (responseCode == "200") {
                        echo "✅ Health Check Passed! Application is reachable at ${healthUrl}"
                    } else {
                        error "❌ Health Check Failed! HTTP status code: ${responseCode}"
                    }
                }
            }
        }
    }

    post {
        success {
            emailext (
                to: "${NOTIFICATION_EMAIL}",
                subject: "SUCCESS: Jenkins Build #${env.BUILD_NUMBER}",
                body: "The build and deployment succeeded for ${env.JOB_NAME} #${env.BUILD_NUMBER}."
            )
        }
        failure {
            emailext (
                to: "${NOTIFICATION_EMAIL}",
                subject: "FAILED: Jenkins Build #${env.BUILD_NUMBER}",
                body: "The build failed for ${env.JOB_NAME} #${env.BUILD_NUMBER}. Please check the logs."
            )
        }
    }
}